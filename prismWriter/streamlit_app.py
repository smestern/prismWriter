"""
Streamlit Web Frontend for prismWriter
A simple web interface for creating GraphPad Prism files from CSV/Excel data
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import tempfile
from io import BytesIO

# Lazy import to reduce initial memory footprint
@st.cache_resource
def get_prism_module():
    from prismWriter.prism_writer import PrismFile, load_prism_file
    return PrismFile, load_prism_file

# Page configuration
st.set_page_config(
    page_title="prismWriter - Web Interface",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("prismWriter - Web Interface")
st.markdown("""
Convert your CSV/Excel data into GraphPad Prism format (`.pzfx`) files with customizable grouping.
""")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'prism_file' not in st.session_state:
    st.session_state.prism_file = None

# Sidebar - File Upload
with st.sidebar:
    st.header("Data Input")
    
    # Option 1: Upload file
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your data file to convert to Prism format"
    )
    
    # Option 2: Load existing Prism file
    st.markdown("---")
    st.subheader("Or Load Existing Prism File")
    prism_upload = st.file_uploader(
        "Upload .pzfx file",
        type=['pzfx'],
        help="Load an existing Prism file to view or modify"
    )

# Load data
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            st.session_state.df = pd.read_csv(uploaded_file)
        else:
            # Excel file - check for multiple sheets
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            if len(sheet_names) > 1:
                # Show sheet selector in sidebar
                with st.sidebar:
                    st.markdown("---")
                    selected_sheet = st.selectbox(
                        "Select Excel Sheet",
                        options=sheet_names,
                        key="sheet_selector"
                    )
                st.session_state.df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                st.success(f"Loaded {uploaded_file.name} (Sheet: {selected_sheet}) - {len(st.session_state.df)} rows")
            else:
                st.session_state.df = pd.read_excel(uploaded_file)
                st.success(f"Loaded {uploaded_file.name} - {len(st.session_state.df)} rows")
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")

if prism_upload is not None:
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pzfx') as tmp:
            tmp.write(prism_upload.read())
            tmp_path = tmp.name
        
        PrismFile, load_prism_file = get_prism_module()
        st.session_state.prism_file = load_prism_file(tmp_path, backup=False)
        st.success(f"Loaded Prism file: {prism_upload.name}")
        
        # Clean up temp file
        os.unlink(tmp_path)
    except Exception as e:
        st.error(f"Error loading Prism file: {str(e)}")

# Main content area
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Show data preview
    st.subheader("Data Preview")
    st.dataframe(df.head(20), use_container_width=True)
    
    # Column type detection
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    st.markdown("---")
    st.subheader("Configure Prism Table")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Column Types Detected:**")
        st.write(f"Numeric columns: {len(numeric_cols)}")
        st.write(f"Categorical columns: {len(categorical_cols)}")
    
    with col2:
        table_name = st.text_input(
            "Table Name",
            value="DataTable",
            help="Name for the table in Prism file"
        )
    
    # Grouping configuration
    st.markdown("### Grouping Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Main Group**")
        main_group = st.selectbox(
            "Main grouping column",
            options=["None"] + categorical_cols,
            help="Creates separate Y-columns for each group"
        )
        if main_group == "None":
            main_group = None
    
    with col2:
        st.markdown("**Sub-Groups**")
        sub_group_option = st.radio(
            "Sub-group method",
            ["By column name", "By data columns"],
            help="Creates sub-columns within each Y-column"
        )
        
        if sub_group_option == "By column name":
            subgroupby = st.selectbox(
                "Sub-group column",
                options=["None"] + categorical_cols,
            )
            if subgroupby == "None":
                subgroupby = None
        else:
            subgroupby = st.multiselect(
                "Data columns for sub-groups",
                options=numeric_cols,
            )
    
    with col3:
        st.markdown("**Row Groups**")
        row_group_option = st.radio(
            "Row group method",
            ["By column name", "By data columns"],
            help="Creates row labels on vertical axis"
        )
        
        if row_group_option == "By column name":
            rowgroupby = st.selectbox(
                "Row group column",
                options=["None"] + categorical_cols,
            )
            if rowgroupby == "None":
                rowgroupby = None
        else:
            rowgroupby = st.multiselect(
                "Data columns for row groups",
                options=numeric_cols,
            )
    
    # Data columns
    st.markdown("### Data Columns")
    #grey out if the user selected subgroupby or rowgroupby as data columns
    if (sub_group_option == "By data columns" and len(subgroupby) > 0) or (row_group_option == "By data columns" and len(rowgroupby) > 0):
        st.info("Data columns selection is disabled when using data columns for sub-groups or row groups")
        data_cols = []
    else:
        data_cols = st.multiselect(
            "Select columns to include as data",
            options=numeric_cols,
            default=numeric_cols[0:1] if numeric_cols else [],
            help="Numeric columns that contain the actual data values"
        )
    
    # Preview and Generate
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        preview_btn = st.button("Preview Table", use_container_width=True)
    
    with col2:
        generate_btn = st.button("Generate Prism File", type="primary", use_container_width=True)
    
    # Preview functionality
    if preview_btn:
        if not np.any([data_cols, rowgroupby, subgroupby]):
            st.warning("Please select at least one data column")
        else:
            try:
                with st.spinner("Generating preview..."):
                    # Create temporary PrismFile
                    PrismFile, _ = get_prism_module()
                    temp_prism = PrismFile()
                    
                    # Get unique values for main group
                    if main_group:
                        group_values = df[main_group].unique().tolist()
                    else:
                        group_values = [None]
                    
                    # Create table
                    temp_prism.make_group_table(
                        group_name=f"__{table_name}",
                        group_values=df,
                        groupby=main_group,
                        cols=data_cols if len(data_cols) > 0 else None,
                        subgroupby=subgroupby if len(subgroupby) > 0 else None,
                        rowgroupby=rowgroupby if len(rowgroupby) > 0 else None,
                        append=True
                    )
                    
                    # Convert back to dataframe for preview
                    preview_df = temp_prism.to_dataframe(f"__{table_name}")
                    
                    st.success("Preview generated successfully!")
                    st.dataframe(preview_df, use_container_width=True)
                    
                    st.info(f"Preview dimensions: {preview_df.shape[0]} rows × {preview_df.shape[1]} columns")
                    
            except Exception as e:
                st.error(f"Error generating preview: {str(e)}")
                st.exception(e)
    
    # Generate file
    if generate_btn:
        if not np.any([data_cols, rowgroupby, subgroupby]):
            st.warning("Please select at least one data column")
        else:
            try:
                with st.spinner("Generating Prism file..."):
                    # Create PrismFile
                    PrismFile, _ = get_prism_module()
                    prism_file = PrismFile()
                    
                    # Create table
                    prism_file.make_group_table(
                        group_name=table_name,
                        group_values=df,
                        groupby=main_group,
                        cols=data_cols if len(data_cols) > 0 else None,
                        subgroupby=subgroupby if len(subgroupby) > 0 else None,
                        rowgroupby=rowgroupby if len(rowgroupby) > 0 else None,
                        append=True
                    )
                    
                    # Save to BytesIO
                    output = BytesIO()
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pzfx') as tmp:
                        tmp_path = tmp.name
                    
                    prism_file.save(tmp_path)
                    
                    with open(tmp_path, 'rb') as f:
                        output.write(f.read())
                    
                    os.unlink(tmp_path)
                    output.seek(0)
                    
                    st.success("Prism file generated successfully!")
                    
                    # Download button
                    st.download_button(
                        label="Download Prism File",
                        data=output,
                        file_name=f"{table_name}.pzfx",
                        mime="application/octet-stream",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"Error generating Prism file: {str(e)}")
                st.exception(e)

elif st.session_state.prism_file is not None:
    # Show existing Prism file tables
    st.subheader("Prism File Tables")
    
    prism = st.session_state.prism_file
    table_names = prism.get_table_names()
    
    st.write(f"Found {len(table_names)} table(s) in file")
    
    selected_table = st.selectbox("Select table to view", table_names)
    
    if selected_table:
        try:
            table_df = prism.to_dataframe(selected_table)
            st.dataframe(table_df, use_container_width=True)
            
            st.info(f"Table dimensions: {table_df.shape[0]} rows × {table_df.shape[1]} columns")
        except Exception as e:
            st.error(f"Error loading table: {str(e)}")

else:
    # Welcome screen
    st.info("Upload a CSV/Excel file or an existing Prism file to get started")
    
    st.markdown("""
    ### Quick Start Guide
    
    1. **Upload your data file** (CSV or Excel) using the sidebar
    2. **Configure grouping** options:
       - **Main Group**: Creates separate Y-columns for each category
       - **Sub-Groups**: Creates replicates within each Y-column
       - **Row Groups**: Creates row labels on the vertical axis
    3. **Select data columns** to include in the Prism file
    4. **Preview** the table structure before generating
    5. **Generate and download** your `.pzfx` file
    
    ### Tips
    - Numeric columns are automatically detected for data
    - Categorical columns are used for grouping
    - Use Preview to verify the table structure
    - Generated files can be opened directly in GraphPad Prism
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>prismWriter Web Interface | Built with Streamlit</small>
</div>
""", unsafe_allow_html=True)


def main():
    """Entry point for command-line execution"""
    pass


if __name__ == "__main__":
    main()
