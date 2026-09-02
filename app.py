import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(
    page_title="Startup & Job Title Explorer",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Startup & Job Explorer Dashboard")

# Define path for local file in repository
DATA_FILE = "StartupTarget Job TitleSalary Estimate (Base + Bo....xlsx"
if not os.path.exists(DATA_FILE):
    # Fallback to simple name if renamed in repo
    DATA_FILE = "data.xlsx"

# Helper function to get source and filename
def get_file_source():
    if os.path.exists(DATA_FILE):
        return DATA_FILE, DATA_FILE
    
    uploaded_file = st.sidebar.file_uploader("Upload dataset", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        return uploaded_file, uploaded_file.name
    
    return None, None

source, filename = get_file_source()

if source is None:
    st.info("👈 Please upload your Excel or CSV file in the sidebar to get started.")
    st.stop()

# Determine sheet options if Excel
selected_sheet = None
if not filename.lower().endswith('.csv'):
    try:
        excel_file = pd.ExcelFile(source)
        sheet_names = excel_file.sheet_names
        
        # Default to 'Main Job Sheet' if present, otherwise second tab, otherwise first tab
        default_index = 0
        if "Main Job Sheet" in sheet_names:
            default_index = sheet_names.index("Main Job Sheet")
        elif len(sheet_names) > 1:
            default_index = 1
            
        selected_sheet = st.sidebar.selectbox(
            "📋 Select Sheet / Tab",
            options=sheet_names,
            index=default_index
        )
    except Exception as e:
        st.error(f"Error reading Excel sheets: {e}")
        st.stop()

# Load data based on file type and selected sheet
@st.cache_data
def load_data(file_source, is_csv, sheet):
    if is_csv:
        return pd.read_csv(file_source)
    else:
        return pd.read_excel(file_source, sheet_name=sheet)

is_csv = filename.lower().endswith('.csv')
df = load_data(source, is_csv, selected_sheet)

# Clean column headers
df.columns = [str(col).strip() for col in df.columns]

# --- Sidebar Filters & Controls ---
st.sidebar.markdown("---")
st.sidebar.header("Filter & Sort Options")

# Keyword Search across all columns
search_query = st.sidebar.text_input("🔍 Search Keyword (Job Title, Startup, Location, etc.)")
if search_query:
    mask = df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
    df = df[mask]

# Category Filters (Location, Setup, Equity, etc.)
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
if categorical_cols:
    filter_col = st.sidebar.selectbox("Filter by Category Column", ["None"] + categorical_cols)
    if filter_col != "None":
        unique_options = sorted([str(val) for val in df[filter_col].dropna().unique()])
        selected_options = st.sidebar.multiselect(
            f"Select values in '{filter_col}'",
            options=unique_options,
            default=unique_options
        )
        if selected_options:
            df = df[df[filter_col].astype(str).isin(selected_options)]

# Sorting Controls
st.sidebar.markdown("---")
st.sidebar.subheader("Sort Settings")
all_cols = df.columns.tolist()

# Find reasonable default sort column
default_sort_idx = 0
for candidate in ['Worth-It (1–10)', 'Salary Estimate (Base + Bonus)', 'Startup']:
    if candidate in all_cols:
        default_sort_idx = all_cols.index(candidate)
        break

sort_col = st.sidebar.selectbox("Sort by Column", all_cols, index=default_sort_idx)
sort_order = st.sidebar.radio("Sort Order", ["Descending", "Ascending"])

df_sorted = df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))

# --- Dashboard View ---
st.markdown(f"Displaying **{len(df_sorted)}** of **{len(df)}** records from sheet: `{selected_sheet if selected_sheet else filename}`")

# Render metrics summary bar
col1, col2, col3 = st.columns(3)
col1.metric("Total Rows Shown", len(df_sorted))

numeric_cols = df_sorted.select_dtypes(include=['number']).columns.tolist()
if len(numeric_cols) > 0:
    col2.metric(f"Avg {numeric_cols[0]}", f"{df_sorted[numeric_cols[0]].mean():,.2f}")
if len(numeric_cols) > 1:
    col3.metric(f"Max {numeric_cols[1]}", f"{df_sorted[numeric_cols[1]].max():,.2f}")

st.markdown("---")

# Data Table Display
st.dataframe(
    df_sorted,
    use_container_width=True,
    height=550
)

# Export Filtered Results
csv_download = df_sorted.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_download,
    file_name="filtered_job_data.csv",
    mime="text/csv"
)
