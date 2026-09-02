import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Startup & Job Title Explorer", layout="wide")

st.title("💼 Startup & Job Explorer Dashboard")

# Load file directly from repo or via sidebar upload
@st.cache_data
def load_data(file_path):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)

data_file = "data.xlsx"

if os.path.exists(data_file):
    df = load_data(data_file)
    st.success(f"Loaded dataset: `{data_file}`")
else:
    uploaded_file = st.sidebar.file_uploader("Upload dataset", type=["xlsx", "csv"])
    if uploaded_file:
        df = load_data(uploaded_file)
    else:
        st.warning("Please upload a file or place `data.xlsx` in the repository root.")
        st.stop()

# Clean column names
df.columns = [str(col).strip() for col in df.columns]

# Sidebar filters
st.sidebar.header("Filter & Sort Options")

# Search keyword
search = st.sidebar.text_input("🔍 Search keyword")
if search:
    df = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)]

# Sort options
sort_col = st.sidebar.selectbox("Sort by column", df.columns.tolist())
sort_order = st.sidebar.radio("Order", ["Ascending", "Descending"])

df_sorted = df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))

# Display
st.metric("Total Matches", len(df_sorted))
st.dataframe(df_sorted, use_container_width=True, height=500)
