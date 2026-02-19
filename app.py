import streamlit as st

st.set_page_config(
    page_title="Enterprise Credit AI",
    page_icon="🏦",
    layout="wide"
)

st.title("Welcome to the Enterprise Credit Evaluation System 🏦")
st.markdown("""
### AI-Powered Financial Risk Assessment

Welcome to the internal portal. Please select a module from the sidebar to the left:

* **User Application:** Submit new business loan applications, run the ML Risk Model, and generate Llama 3 Audit Reports.
* **Manager Dashboard:** View live portfolio metrics, risk distributions, and synthetic training data.
""")
