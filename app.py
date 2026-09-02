import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Startup & Job Title Explorer", layout="wide")

st.title("💼 Startup & Job Explorer Dashboard")

# Function to read uploaded file object or file path
def load_data(source):
    # Check if 'source' is a string path (e.g. "data.xlsx") or an UploadedFile object
    if isinstance(source, str):
        filename = source
    else:
        filename = source.name

    if filename.lower().endswith('.csv'):
        return pd.read_csv(source)
    else:
        return pd.read_excel(source)

data_file = "data.xlsx"

# Determine whether to read from local repository file or file uploader
if os.path.exists(data_file):
    df = load_data(data_file)
    st.success(f"Loaded dataset: `{data_file}`")
else:
    uploaded_file = st.sidebar.file_uploader("Upload dataset", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        st.info("👈 Please upload your `data.xlsx` or `.csv` file in the sidebar.")
        st.stop()

# Clean column headers
df.columns = [str(col).strip() for col in df.columns]

# Sidebar controls
st.sidebar.header("Filter & Sort")

# Text search
search = st.sidebar.text_input("🔍 Search keyword")
if search:
    df = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)]

# Sorting selector
all_cols = df.columns.tolist()
sort_col = st.sidebar.selectbox("Sort by column", all_cols)
sort_order = st.sidebar.radio("Order", ["Ascending", "Descending"])

df_sorted = df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))

# Data Table Display
st.metric("Total Records", len(df_sorted))
st.dataframe(df_sorted, use_container_width=True, height=500)
