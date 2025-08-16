from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import io
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.features import build_base_frame, label_encode_apply, reduce_mem

app = FastAPI(title="IEEE-CIS Fraud Detection API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model
try:
    ART = joblib.load('models/lgbm_pipeline.joblib')
    MODELS = ART['models']
    FEATS = ART['features']
    ENCODERS = ART['encoders']
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    MODELS = None
    FEATS = None
    ENCODERS = None

def score_frame(df: pd.DataFrame) -> pd.Series:
    """Score a dataframe using the loaded model"""
    if MODELS is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        print("Starting score_frame...")
        # build_base_frame expects separate frames; here we fake identity as empty and merge on TransactionID
        df_trans = df.copy()
        df_id = pd.DataFrame({'TransactionID': df_trans['TransactionID']})
        
        print("Calling build_base_frame...")
        try:
            base = build_base_frame(df_trans, df_id)
            print("build_base_frame completed")
        except Exception as e:
            print(f"build_base_frame failed: {e}")
            # Create a minimal base frame with required features
            base = df_trans.copy()
            base['DT_D'] = (base['TransactionDT'] // (24*60*60)).astype('int32')
            base['DT_W'] = (base['DT_D'] // 7).astype('int32')
            base['DT_M'] = (base['DT_D'] // 30).astype('int32')
            base['TransactionAmt_log1p'] = np.log1p(base['TransactionAmt'])
            base['amt_cents'] = (base['TransactionAmt'] - np.floor(base['TransactionAmt'])).round(2)
            base['has_id'] = 0
            base['is_email_match'] = 0

        print("Processing encoders...")
        for c, le in ENCODERS.items():
            if c not in base.columns:
                base[c] = 'NA'
            try:
                base[c] = label_encode_apply(le, base[c])
            except ValueError as e:
                # Handle unseen labels by using a default value
                print(f"Warning: Unseen labels in column {c}, using default encoding")
                base[c] = 0  # Default encoding for unseen labels

        base = reduce_mem(base)
        
        # Ensure all required features are present
        missing_features = [f for f in FEATS if f not in base.columns]
        if missing_features:
            print(f"Warning: Missing features: {missing_features[:10]}...")  # Show first 10
            # Create a dictionary of missing features to avoid DataFrame fragmentation
            missing_features_dict = {f: 0.0 for f in missing_features}
            base = base.assign(**missing_features_dict)
        
        print("Making predictions...")
        proba = sum(m.predict(base[FEATS], num_iteration=m.best_iteration) for m in MODELS) / len(MODELS)
        print("Predictions completed")
        return pd.Series(proba, index=base.index)
    except Exception as e:
        import traceback
        print(f"Error in score_frame: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Model prediction error: {str(e)}")

@app.post("/predict")
async def predict_file(file: UploadFile = File(...)):
    """Handle CSV file upload and return fraud predictions"""
    try:
        # Check if file is CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        print(f"CSV loaded successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head()}")
        
        # Check if required columns exist
        required_columns = ['TransactionID', 'TransactionDT', 'TransactionAmt', 'ProductCD']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Add missing columns with default values if they don't exist
        expected_columns = [
            'DeviceInfo', 'P_emaildomain', 'R_emaildomain', 'addr1', 'addr2', 
            'dist1', 'dist2', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                if col == 'DeviceInfo':
                    df[col] = 'NA'
                elif col in ['P_emaildomain', 'R_emaildomain']:
                    df[col] = 'unknown.com'
                elif col in ['addr1', 'addr2']:
                    df[col] = 0
                elif col in ['dist1', 'dist2']:
                    df[col] = 0.0
                elif col.startswith('card'):
                    df[col] = 0
                else:
                    df[col] = 'NA'
        
        print(f"Added missing columns. DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {list(df.columns)}")
        
        # Add all the C, D, V columns that might be missing (batch operation to avoid fragmentation)
        missing_c_cols = {f'C{i}': 0 for i in range(1, 15) if f'C{i}' not in df.columns}
        missing_d_cols = {f'D{i}': 0.0 for i in range(1, 16) if f'D{i}' not in df.columns}
        missing_v_cols = {f'V{i}': 0.0 for i in range(1, 340) if f'V{i}' not in df.columns}
        missing_m_cols = {f'M{i}': 'NA' for i in range(1, 10) if f'M{i}' not in df.columns}
        
        # Add all missing columns at once
        all_missing_cols = {**missing_c_cols, **missing_d_cols, **missing_v_cols, **missing_m_cols}
        if all_missing_cols:
            df = df.assign(**all_missing_cols)
        
        # Get fraud probabilities
        print("About to call score_frame...")
        fraud_probs = score_frame(df)
        print("score_frame completed successfully")
        
        # Create results
        print("Creating results...")
        results = []
        for idx, (transaction_id, prob) in enumerate(zip(df['TransactionID'], fraud_probs)):
            # Use actual amount from the data
            amount = float(df.iloc[idx]['TransactionAmt'])
            
            results.append({
                "transaction_id": str(transaction_id),
                "amount": amount,
                "fraud_probability": float(prob),
                "is_fraud": prob > 0.1  # Lower threshold for fraud detection (more sensitive)
            })
        
        print(f"Created {len(results)} results")
        return results
        
    except Exception as e:
        import traceback
        error_msg = f"Error processing file: {e}"
        traceback_msg = traceback.format_exc()
        print(error_msg)
        print(f"Full traceback: {traceback_msg}")
        raise HTTPException(status_code=500, detail=f"Processing error: {error_msg}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": MODELS is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
