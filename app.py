import streamlit as st
from utils.db_engine import init_db

st.set_page_config(page_title="Smart Credit AI", page_icon="🏦", layout="wide")
init_db()

st.title("🏦 Smart Credit Evaluation System (Enterprise Edition)")
st.markdown("---")
st.info("👈 Select 'User Application' from the sidebar to start.")
