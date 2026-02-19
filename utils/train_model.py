import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os

# --- 1. GENERATE SYNTHETIC ENTERPRISE DATA ---
print("Generating synthetic enterprise dataset (N=5000)...")
np.random.seed(42)
n = 5000

data = pd.DataFrame({
    'annual_turnover': np.random.normal(5000000, 2000000, n),
    'loan_amount': np.random.normal(1500000, 500000, n),
    'gst_compliance_score': np.random.randint(1, 11, n), # 1-10
    'audit_risk_flag': np.random.choice([0, 1], n, p=[0.85, 0.15]), # 15% have audit issues
    'cibil_score': np.random.randint(300, 900, n)
})

# Define "Default" Logic (The Rules the AI must learn)
# High Loan + Low GST + Bad Audit = High Risk
data['risk_probability'] = (
    (data['loan_amount'] / (data['annual_turnover'] + 1)) * 3 + 
    (10 - data['gst_compliance_score']) * 0.15 + 
    (data['audit_risk_flag'] * 0.5)
)
# Normalize prob to 0-1 range
data['risk_probability'] = (data['risk_probability'] - data['risk_probability'].min()) / \
                           (data['risk_probability'].max() - data['risk_probability'].min())

# Target: 1 = Default (Risk > 0.6), 0 = Repaid
data['default'] = (data['risk_probability'] > 0.55).astype(int)

# --- 2. TRAIN THE PIPELINE ---
print("Training Random Forest Pipeline...")

# Features must match the 5 inputs in your UI exactly
X = data[['annual_turnover', 'loan_amount', 'gst_compliance_score', 'audit_risk_flag', 'cibil_score']]
y = data['default']

# Professional Pipeline: Imputer -> Scaler -> Model
model_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42))
])

model_pipeline.fit(X, y)
accuracy = model_pipeline.score(X, y)
print(f"✅ Model Trained! Accuracy: {accuracy:.2%}")

# --- 3. SAVE ASSETS ---
if not os.path.exists('data'):
    os.makedirs('data')

joblib.dump(model_pipeline, 'data/loan_model.pkl')
data.to_csv('data/training_data.csv', index=False)
print("Files saved: 'data/loan_model.pkl' & 'data/training_data.csv'")
