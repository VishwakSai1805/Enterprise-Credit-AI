import joblib
import pandas as pd
import os
import pdfplumber
from groq import Groq


MODEL_PATH = 'data/loan_model.pkl'

# Load Pipeline
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

def extract_text_from_pdf(uploaded_file):
    """
    Extracts raw text from the uploaded PDF.
    """
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        return ""

def generate_recommendation(turnover, loan, gst_score, audit_flag):
    """
    Explains WHY the user was rejected and WHAT they can do.
    """
    reasons = []

    # Check Ratio
    if turnover > 0:
        if (loan / turnover) > 0.4:
            reasons.append(f"⚠️ Loan amount is too high for your turnover. Try requesting ₹{int(turnover * 0.3)}.")

    # Check GST
    if gst_score < 5:
        reasons.append("⚠️ GST Compliance is critical. File returns on time to boost score.")

    # Check Audit
    if audit_flag == 1:
        reasons.append("❌ Audit Risk detected. Clear pending discrepancies in your balance sheet.")

    if not reasons:
        return "✅ Financial health looks strong."

    return " | ".join(reasons)

def predict_risk(turnover, loan, gst_score, audit_flag, credit_score):
    # 1. Prepare input for the Math Model
    # STRICT ORDER: turnover, loan, gst, audit, cibil
    input_data = {
        'annual_turnover': [turnover],
        'loan_amount': [loan],
        'gst_compliance_score': [gst_score],
        'audit_risk_flag': [audit_flag],
        'cibil_score': [credit_score]
    }

    # Convert to DataFrame and ensure order
    input_df = pd.DataFrame(input_data)
    input_df = input_df[['annual_turnover', 'loan_amount', 'gst_compliance_score', 'audit_risk_flag', 'cibil_score']]

    # 2. Get Base Probability from Random Forest
    if model:
        risk_prob = model.predict_proba(input_df)[0][1]
    else:
        risk_prob = 0.5

    # --- THE VETO POWER (The Fix) ---
    # Logic: Even if income is high, a bad audit MUST kill the deal.

    # Rule A: If Audit has "Major Flags" (1), Risk is at least 75%
    if audit_flag == 1:
        risk_prob = max(risk_prob, 0.75)

    # Rule B: If GST is terrible (< 3), Risk is at least 65%
    if gst_score < 3:
        risk_prob = max(risk_prob, 0.65)

    return round(risk_prob, 2)

def analyze_with_llama(pdf_text):
    """
    Uses Llama 3 to read the Audit Report/Bank Statement.
    """
    # If no text, skip
    if len(pdf_text) < 50:
        return "⚠️ No readable text found in document."

    try:
        # Initialize Llama 3 Client
        client = Groq(api_key=os.environ.get("GROQ_API_KEY")) 

        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Senior Bank Auditor. Summarize the financial health based on this text. identifying 3 key risks (e.g., bounced checks, lawsuits, declining revenue) and 1 strength. Keep it brief (bullet points)."
                },
                {
                    "role": "user",
                    "content": pdf_text[:4000] # Send first 4000 chars to save limits
                }
            ],
            model="llama-3.3-70b-versatile", # Using Llama 3 (Fast & Free tier)
        )

        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Llama Analysis Failed: {str(e)}"
