import streamlit as st
from app.analysis import perform_analysis
from app.sql_query import execute_sql_query
from app.utils import load_stock_data

st.set_page_config(page_title="Stock Market Analysis", layout="wide")

st.title("Stock Market Analysis")

menu = st.sidebar.selectbox("Choose an option", ["Analysis", "SQL Query"])

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

if st.sidebar.button("Fetch Data"):
    data = load_stock_data(start_date, end_date)
    if data is not None:
        st.session_state["data"] = data
    else:
        st.error("Failed to load data.")

if "data" in st.session_state:
    if menu == "Analysis":
        st.subheader("Advanced Analysis")
        perform_analysis(st.session_state["data"])
    elif menu == "SQL Query":
        st.subheader("Execute SQL Query")
        execute_sql_query(st.session_state["data"])
