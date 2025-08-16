# src/train.py
import os, joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
import lightgbm as lgb

from features import (
    reduce_mem, build_base_frame, add_group_stats, add_frequency_encodings,
    label_encode_fit_transform, label_encode_apply
)

DATA_DIR = 'data'
MODEL_DIR = 'models'

SEED = 42
N_FOLDS = 5

def main():
    trans = pd.read_csv(f'{DATA_DIR}/train_transaction.csv')
    iden  = pd.read_csv(f'{DATA_DIR}/train_identity.csv')
    test_trans = pd.read_csv(f'{DATA_DIR}/test_transaction.csv')
    test_iden  = pd.read_csv(f'{DATA_DIR}/test_identity.csv')

    y = trans['isFraud'].astype('int8')
    trans.drop(columns=['isFraud'], inplace=True)

    train = build_base_frame(trans, iden)
    test  = build_base_frame(test_trans, test_iden)

    # Get all categorical columns (object dtype)
    cat_cols = []
    for df in [train, test]:
        cat_cols.extend(df.select_dtypes(include=['object']).columns.tolist())
    cat_cols = list(set(cat_cols))  # Remove duplicates
    
    # Label-encode all categorical columns (fit on union!)
    encoders = {}
    for c in cat_cols:
        if c in train.columns and c in test.columns:
            le, tr = label_encode_fit_transform(train[c], test[c])
            encoders[c] = le
            train[c] = tr
            test[c]  = label_encode_apply(le, test[c])
        elif c in train.columns:
            # Column only in train, fill test with a default value
            le, tr = label_encode_fit_transform(train[c], pd.Series(['NA'] * len(test)))
            encoders[c] = le
            train[c] = tr
            test[c] = 0  # Default encoded value
        elif c in test.columns:
            # Column only in test, fill train with a default value
            le, tr = label_encode_fit_transform(pd.Series(['NA'] * len(train)), test[c])
            encoders[c] = le
            train[c] = 0  # Default encoded value
            test[c] = label_encode_apply(le, test[c])

    # Frequency encodings
    train, test = add_frequency_encodings(train, test, cat_cols)

    # Group stats (unsupervised): keys chosen per domain intuition / winning tips
    group_keys = ['card1','card2','card3','card5','P_emaildomain','DeviceName','addr1']
    num_cols   = ['TransactionAmt','TransactionAmt_log1p','DT_D']
    train, test = add_group_stats(train, test, group_keys, num_cols, suffix='stats')

    # Reduce memory
    train = reduce_mem(train)
    test  = reduce_mem(test)

    # Columns to drop (IDs, raw time seconds)
    drop_cols = ['TransactionID', 'TransactionDT']
    feats = [c for c in train.columns if c not in drop_cols]

    # CV by month-like group to respect time
    groups = train['DT_M'].values
    gkf = GroupKFold(n_splits=N_FOLDS)

    oof = np.zeros(len(train))
    test_pred = np.zeros(len(test))

    lgb_params = dict(
        objective='binary',
        metric='auc',
        boosting_type='gbdt',
        learning_rate=0.02,
        num_leaves=256,
        max_depth=-1,
        min_data_in_leaf=200,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=1,
        lambda_l1=1.0,
        lambda_l2=1.0,
        verbose=-1,
        n_jobs=-1,
        seed=SEED
    )

    models = []
    for fold, (tr_idx, va_idx) in enumerate(gkf.split(train, y, groups=groups), 1):
        X_tr, X_va = train.iloc[tr_idx][feats], train.iloc[va_idx][feats]
        y_tr, y_va = y.iloc[tr_idx], y.iloc[va_idx]

        dtr = lgb.Dataset(X_tr, label=y_tr)
        dva = lgb.Dataset(X_va, label=y_va, reference=dtr)

        model = lgb.train(
            lgb_params,
            dtr,
            valid_sets=[dtr, dva],
            valid_names=['train','valid'],
            num_boost_round=20000,
            early_stopping_rounds=500,
            verbose_eval=500
        )
        models.append(model)

        oof[va_idx] = model.predict(X_va, num_iteration=model.best_iteration)
        test_pred  += model.predict(test[feats], num_iteration=model.best_iteration) / N_FOLDS

        auc = roc_auc_score(y_va, oof[va_idx])
        print(f'Fold {fold} AUC: {auc:.5f}')

    full_auc = roc_auc_score(y, oof)
    print(f'OOF AUC: {full_auc:.5f}')

    os.makedirs(MODEL_DIR, exist_ok=True)
    # Save pipeline artifacts
    joblib.dump({'models': models, 'features': feats, 'encoders': encoders}, f'{MODEL_DIR}/lgbm_pipeline.joblib')
    # (Optional) Save test predictions for Kaggle submission
    sub = pd.DataFrame({'TransactionID': test['TransactionID'], 'isFraud': test_pred})
    sub.to_csv(f'{MODEL_DIR}/submission.csv', index=False)

if __name__ == "__main__":
    main()
