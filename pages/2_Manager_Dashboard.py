import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_engine import load_all_applications
import sqlite3

st.set_page_config(page_title="Manager Dashboard", page_icon="💼", layout="wide")

st.title("💼 Loan Underwriter Dashboard")
st.markdown("### Real-time Risk Analysis")

# --- 1. Load Data ---
df = load_all_applications()

if df.empty:
    st.info("Waiting for applications... Go to 'User Application' and submit one!")
else:
    # --- 2. Top-Level Metrics ---
    total_apps = len(df)
    approved = len(df[df['status'] == 'Approved'])
    rejected = len(df[df['status'] == 'Rejected'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applications", total_apps)
    col2.metric("Approved Loans", approved, delta=f"{approved/total_apps:.0%}")
    col3.metric("Rejected Loans", rejected, delta_color="inverse")

    st.markdown("---")

st.markdown("---")

 # --- NEW: CLEAR DATABASE BUTTON ---
 col_btn1, col_btn2 = st.columns([8, 2])
 with col_btn2:
     if st.button("🗑️ Clear All Applications"):
         # Connect to SQLite and wipe the table
         conn = sqlite3.connect('data/applications.db')
         cursor = conn.cursor()
         cursor.execute("DELETE FROM applications")
         conn.commit()
         conn.close()
         st.success("Database wiped! Refreshing...")
         st.rerun() # Reloads the page instantly

 # --- THE TABS ---
 tab1, tab2 = st.tabs(["📈 Live Application Trends", "🔬 Model Training Data"])

 with tab1:
     c1, c2 = st.columns(2)
     with c1:
         st.subheader("Risk Distribution")
         fig_pie = px.pie(df, names='status', title='Approval Rate', 
                          color='status', hole=0.4,
                          color_discrete_map={'Approved':'green', 'Rejected':'red'})
         st.plotly_chart(fig_pie, width="stretch")

     with c2:
         st.subheader("Income vs. Loan Amount")
         fig_scatter = px.scatter(df, x="income", y="loan_amount", 
                                  color="status", size="risk_score",
                                  hover_data=["name"], title="Applicant Financial Spread")
         st.plotly_chart(fig_scatter, width="stretch")

     st.subheader("Recent Applications Log")
     # Ensure this is the ONLY st.dataframe(df) in this file!
     st.dataframe(df.sort_values(by="timestamp", ascending=False), width="stretch")

 with tab2:
     st.markdown("### 🤖 Artificial Intelligence Training Dataset")
     try:
         train_df = pd.read_csv('data/training_data.csv')

         st.subheader("Feature Correlation Heatmap")
         corr = train_df.corr()
         fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
         st.plotly_chart(fig_corr, width="stretch")

         st.subheader("Raw Data Sample")
         st.dataframe(train_df.head(100), width="stretch")
     except FileNotFoundError:
         st.warning("Training data not found.")
