import streamlit as st
import os
from dotenv import load_dotenv
from utils.db_engine import save_application
from utils.ai_engine import predict_risk, generate_recommendation, extract_text_from_pdf, analyze_with_llama

load_dotenv()

st.set_page_config(page_title="Business Loan Portal", page_icon="🏢")
st.title("🏢 Business Loan Application")
st.markdown("### Enterprise Credit Evaluation System")

with st.form("application_form"):
    st.subheader("1. Company Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Company/Applicant Name", value="RedFlag Logistics Pvt Ltd")
        turnover = st.number_input("Annual Turnover (₹)", min_value=100000.0, step=50000.0)
    with col2:
        loan_amt = st.number_input("Loan Amount Requested (₹)", min_value=10000.0, step=10000.0)
        industry = st.selectbox("Industry Type", ["Manufacturing", "Services", "Trading", "IT/Tech"])

    st.markdown("---")
    st.subheader("2. Compliance & Risk (AI Analysis)")
    
    col3, col4 = st.columns(2)
    with col3:
        st.write("GST Compliance Rating")
        gst_score = st.slider("Based on recent filing history (1-10)", 1, 10, 7)
        c_score = st.number_input("CIBIL/Credit Score", 300, 900, 750)

    with col4:
        st.write("Audit Status")
        audit_status = st.radio("External Audit Report Findings:", 
                                ["Clean Report", "Minor Discrepancies", "Major Flags/Red Risks"])
        
        audit_flag = 1 if audit_status == "Major Flags/Red Risks" else 0
        uploaded_file = st.file_uploader("Upload Audited Financials (PDF)", type=["pdf"])

    # This is the end of the form block
    submitted = st.form_submit_button("Run AI Assessment")

# --- OUTSIDE THE FORM ---
# Notice this is un-indented all the way to the left edge!
if submitted:
    if not name:
        st.error("Please enter a Company Name.")
    else:
        pdf_text = extract_text_from_pdf(uploaded_file) if uploaded_file else ""
        risk_prob = predict_risk(turnover, loan_amt, gst_score, audit_flag, c_score)
        advice = generate_recommendation(turnover, loan_amt, gst_score, audit_flag)

        st.markdown("---")
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            if risk_prob > 0.6: 
                status = "Rejected"
                st.error(f"❌ REJECTED")
                st.metric("Risk Probability", f"{risk_prob:.1%}")
            else:
                status = "Approved"
                st.success(f"✅ APPROVED")
                st.metric("Risk Probability", f"{risk_prob:.1%}")

        with col_res2:
            st.info(f"**AI Recommendation:** {advice}")

        st.markdown("---")
        st.subheader("🤖 GenAI Audit Report (Powered by Llama 3)")
        
        audit_summary = ""
        if uploaded_file:
            with st.spinner("Llama is analyzing the document for fraud/risks..."):
                audit_summary = analyze_with_llama(pdf_text)
                st.markdown(audit_summary)
        else:
            st.warning("⚠️ No document uploaded. Llama cannot perform text analysis.")

        save_application(name, turnover, loan_amt, risk_prob, status)
        st.toast("Application Data & Risk Profile Saved.")

        # --- THE INNOVATION: EXPORT REPORT ---
        st.markdown("---")
        report_content = f"""
        ENTERPRISE CREDIT EVALUATION REPORT
        -----------------------------------
        Company Name: {name}
        Turnover: ₹{turnover}
        Loan Requested: ₹{loan_amt}
        GST Score: {gst_score}/10
        Audit Flag: {'Major Risks' if audit_flag == 1 else 'Clean/Minor'}
        
        AI RISK ASSESSMENT
        -----------------------------------
        Final Status: {status}
        Risk Probability: {risk_prob:.1%}
        Rule Engine Advice: {advice}
        
        LLAMA 3 GEN-AI AUDIT SUMMARY
        -----------------------------------
        {audit_summary if uploaded_file else 'No document provided for GenAI analysis.'}
        """
        
        st.download_button(
            label="📥 Download Official AI Decision Report",
            data=report_content,
            file_name=f"{name.replace(' ', '_')}_Risk_Report.txt",
            mime="text/plain"
        )
