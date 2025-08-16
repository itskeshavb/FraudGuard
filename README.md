# IEEE-CIS Fraud Detection App

A modern web application for detecting fraudulent transactions using machine learning.

## Features

- **Real-time Fraud Detection**: Upload CSV files and get instant fraud analysis
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- **AI-Powered**: Uses LightGBM models trained on IEEE-CIS fraud detection dataset
- **Detailed Results**: View transaction amounts, fraud probabilities, and risk assessments

## Recent Fixes

### ✅ Fixed Issues

1. **Tooltip Provider Error**: Fixed syntax error in `fraud-detection-app.tsx` where `</Tool>` was incorrectly used instead of `</TooltipProvider>`
2. **Backend CSV Processing**: 
   - Fixed import path issues for the `src.features` module
   - Updated API response format to return results array directly
   - Added proper handling for missing columns in CSV files
3. **Frontend-Backend Integration**: 
   - Created Next.js API route at `/api/predict` to proxy requests to FastAPI backend
   - Updated frontend to use correct API endpoint

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

## Running the Application

### 1. Start the FastAPI Backend

In one terminal:
```bash
python api/app.py
```

The backend will start on `http://localhost:8000`

### 2. Start the Next.js Frontend

In another terminal:
```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Test the Application

1. Open your browser and go to `http://localhost:3000`
2. Upload the `proper_test.csv` file (included in the project)
3. Click "Analyze Transactions" to see the fraud detection results

## File Structure

```
ieee-fraud/
├── api/
│   └── app.py                 # FastAPI backend server
├── app/
│   ├── api/
│   │   └── predict/
│   │       └── route.ts       # Next.js API route
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   └── ui/                    # UI components (buttons, cards, etc.)
├── fraud-detection-app.tsx    # Main application component
├── models/
│   └── lgbm_pipeline.joblib   # Trained ML model
├── src/
│   ├── features.py            # Feature engineering functions
│   ├── train.py               # Model training script
│   └── infer.py               # Inference script
└── proper_test.csv            # Sample test data
```

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /predict` - Upload CSV file for fraud detection

## Model Information

The application uses a LightGBM ensemble model trained on the IEEE-CIS fraud detection dataset. The model includes:

- Feature engineering for transaction data
- Label encoding for categorical variables
- Memory optimization for large datasets
- Ensemble predictions from multiple models

## Troubleshooting

### Common Issues

1. **Module not found errors**: Make sure you're running the backend from the project root directory
2. **Port conflicts**: Ensure ports 3000 and 8000 are available
3. **CSV format issues**: The CSV must contain required columns: `TransactionID`, `TransactionDT`, `TransactionAmt`, `ProductCD`

### Backend Issues

If the FastAPI server fails to start:
```bash
# Check if all dependencies are installed
pip install -r requirements.txt

# Run from project root
python api/app.py
```

### Frontend Issues

If the Next.js app fails to start:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Start development server
npm run dev
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

