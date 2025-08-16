# src/features.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# -------- memory helpers ----------
def reduce_mem(df):
    for col in df.columns:
        col_type = df[col].dtype
        if col_type == 'float64':
            df[col] = df[col].astype('float32')
        elif col_type == 'int64':
            df[col] = df[col].astype('int32')
    return df

def label_encode_fit_transform(train_col, test_col):
    le = LabelEncoder()
    # Fit on union to avoid unseen categories at test/predict time
    all_vals = pd.concat([train_col, test_col], axis=0).astype(str).fillna('NA')
    le.fit(all_vals)
    return le, le.transform(train_col.astype(str).fillna('NA'))

def label_encode_apply(le, s):
    return le.transform(s.astype(str).fillna('NA'))

# -------- base feature builder ----------
def build_base_frame(trans, iden):
    # Fix column name inconsistencies between train and test identity files
    # Train has id_01, id_02, etc. while test has id-01, id-02, etc.
    id_cols = [col for col in iden.columns if col.startswith('id-')]
    for col in id_cols:
        new_col = col.replace('-', '_')
        iden = iden.rename(columns={col: new_col})
    
    df = trans.merge(iden, on='TransactionID', how='left')
    # TransactionDT is seconds from a reference; derive time features
    df['DT_D'] = (df['TransactionDT'] // (24*60*60)).astype('int32')   # day index
    df['DT_W'] = (df['DT_D'] // 7).astype('int32')                     # week index
    df['DT_M'] = (df['DT_D'] // 30).astype('int32')                    # month-ish block

    # Amount transforms commonly useful
    df['TransactionAmt_log1p'] = np.log1p(df['TransactionAmt'])
    df['amt_cents'] = (df['TransactionAmt'] - np.floor(df['TransactionAmt'])).round(2)

    # Email domain splits
    for col in ['P_emaildomain', 'R_emaildomain']:
        df[col+'_prov'] = df[col].str.split('.', expand=True)[0]
        df[col+'_tld']  = df[col].str.split('.', expand=True).iloc[:, -1]

    # DeviceInfo splits
    df['DeviceName'] = df['DeviceInfo'].fillna('NA').str.split('/', expand=True)[0]
    df['DeviceVersion'] = df['DeviceInfo'].fillna('NA').str.extract(r'/(\S+)$')

    # Simple boolean flags - check if id_01 exists before using it
    if 'id_01' in df.columns:
        df['has_id'] = df['id_01'].notna().astype('int8')
    else:
        df['has_id'] = 0  # Default value if id_01 doesn't exist
    df['is_email_match'] = (df['P_emaildomain'] == df['R_emaildomain']).fillna(False).astype('int8')

    return df

# -------- powerful group stats (key idea from winning solutions) ----------
def add_group_stats(train, test, keys, num_cols, suffix):
    # compute on train+test to get consistent encodings (no label leakage – stats are unsupervised)
    full = pd.concat([train, test], axis=0, ignore_index=True)
    for k in keys:
        for num in num_cols:
            gp = full.groupby(k)[num].agg(['mean','std','median','min','max'])
            gp.columns = [f'{num}_{k}_g{suf}' for suf in ['mean','std','med','min','max']]
            # map back
            for c in gp.columns:
                train[c] = train[k].map(gp[c])
                test[c]  = test[k].map(gp[c])
    return train, test

def add_frequency_encodings(train, test, cat_cols):
    full = pd.concat([train[cat_cols], test[cat_cols]], axis=0)
    for c in cat_cols:
        freq = full[c].value_counts(dropna=False)
        train[c+'_freq'] = train[c].map(freq)
        test[c+'_freq']  = test[c].map(freq)
    return train, test
