# Fraud Detection App

A modern web application for detecting fraudulent transactions using machine learning.

#Images
<img width="1890" height="990" alt="Screenshot 2025-09-05 172204" src="https://github.com/user-attachments/assets/13d8b1ed-d36f-4c7a-918e-07c7b502790d" />
<img width="1895" height="982" alt="Screenshot 2025-09-05 172243" src="https://github.com/user-attachments/assets/0191e33a-6f41-4bfd-8a13-a1b57ac4d145" />
<img width="1891" height="983" alt="Screenshot 2025-09-05 172257" src="https://github.com/user-attachments/assets/baa5b37c-09cd-45ce-8e52-c2f1e29e868d" />


## Features

- **Real-time Fraud Detection**: Upload CSV files and get instant fraud analysis
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- **AI-Powered**: Uses LightGBM models trained on IEEE-CIS fraud detection dataset
- **Detailed Results**: View transaction amounts, fraud probabilities, and risk assessments

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

