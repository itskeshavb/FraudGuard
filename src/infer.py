# src/infer.py
import joblib, pandas as pd
from features import build_base_frame, label_encode_apply, reduce_mem

ART = joblib.load('models/lgbm_pipeline.joblib')
MODELS  = ART['models']
FEATS   = ART['features']
ENCODERS= ART['encoders']

def predict_proba(trans_csv, id_csv, out_csv='pred.csv'):
    trans = pd.read_csv(trans_csv)
    iden  = pd.read_csv(id_csv)
    df = build_base_frame(trans, iden)

    # apply saved encoders (if a column was missing during training, fill NA)
    for c, le in ENCODERS.items():
        if c not in df.columns:
            df[c] = 'NA'
        df[c] = label_encode_apply(le, df[c])

    df = reduce_mem(df)
    P = sum(m.predict(df[FEATS], num_iteration=m.best_iteration) for m in MODELS) / len(MODELS)
    pd.DataFrame({'TransactionID': df['TransactionID'], 'isFraud': P}).to_csv(out_csv, index=False)
    return out_csv

if __name__ == "__main__":
    predict_proba('data/test_transaction.csv', 'data/test_identity.csv', 'models/submission.csv')
