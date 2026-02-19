import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

st.set_page_config(page_title="Manager Dashboard", page_icon="📊", layout="wide")
st.title("📊 Manager Dashboard")

# Connect to SQLite Database
conn = sqlite3.connect('data/applications.db')
try:
    df = pd.read_sql_query("SELECT * FROM applications", conn)
except Exception as e:
    df = pd.DataFrame(columns=["id", "name", "income", "loan_amount", "risk_score", "status", "timestamp"])
conn.close()

if df.empty:
    st.info("No applications processed yet. Run some tests in the User Application first!")
else:
    # Key Metrics
    st.subheader("Enterprise Portfolio Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applications", len(df))
    col2.metric("Total Loan Volume (₹)", f"₹{df['loan_amount'].sum():,.2f}")
    approval_rate = (len(df[df['status'] == 'Approved']) / len(df)) * 100
    col3.metric("Approval Rate", f"{approval_rate:.1f}%")

    st.markdown("---")
    
    # --- NEW: CLEAR DATABASE BUTTON ---
    col_btn1, col_btn2 = st.columns([8, 2])
    with col_btn2:
        if st.button("🗑️ Clear All Applications"):
            conn = sqlite3.connect('data/applications.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM applications")
            conn.commit()
            conn.close()
            st.success("Database wiped! Refreshing...")
            st.rerun()

    # --- THE TABS ---
    tab1, tab2 = st.tabs(["📈 Live Application Trends", "🔬 Model Training Data"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Risk Distribution")
            fig_pie = px.pie(df, names='status', title='Approval Rate', 
                             color='status', hole=0.4,
                             color_discrete_map={'Approved':'green', 'Rejected':'red'})
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.subheader("Income vs. Loan Amount")
            fig_scatter = px.scatter(df, x="income", y="loan_amount", 
                                     color="status", size="risk_score",
                                     hover_data=["name"], title="Applicant Financial Spread")
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.subheader("Recent Applications Log")
        st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)

    with tab2:
        st.markdown("### 🤖 Artificial Intelligence Training Dataset")
        try:
            train_df = pd.read_csv('data/training_data.csv')
            
            st.subheader("Feature Correlation Heatmap")
            numeric_df = train_df.select_dtypes(include='number')
            corr = numeric_df.corr()
            fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
            st.plotly_chart(fig_corr, use_container_width=True)
            
            st.subheader("Raw Data Sample")
            st.dataframe(train_df.head(100), use_container_width=True)
        except FileNotFoundError:
            st.warning("Training data not found.")
