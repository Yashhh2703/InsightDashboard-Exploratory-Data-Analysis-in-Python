import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Set up the Streamlit app
st.title("Dynamic Data Dashboard with All Chart Options")

# Upload multiple datasetsstrte
uploaded_files = st.file_uploader("Upload CSV or Excel files", accept_multiple_files=True, type=["csv", "xlsx"])

# Function for filtering data
def filter_data(df):
    st.subheader("Filter Data")
    columns = df.columns
    selected_column = st.selectbox("Select Column to Filter", columns)
    
    if df[selected_column].dtype in ["float64", "int64"]:
        min_val, max_val = st.slider(
            "Select Range", min_value=float(df[selected_column].min()), max_value=float(df[selected_column].max()), value=(float(df[selected_column].min()), float(df[selected_column].max()))
        )
        filtered_df = df[(df[selected_column] >= min_val) & (df[selected_column] <= max_val)]
    else:
        unique_values = df[selected_column].unique()
        selected_values = st.multiselect("Select Values", options=unique_values, default=unique_values)
        filtered_df = df[df[selected_column].isin(selected_values)]
    
    st.write("Filtered Data", filtered_df.head())
    return filtered_df

# Function for sorting data
def sort_data(df):
    st.subheader("Sort Data")
    columns = df.columns
    sort_by = st.selectbox("Select Column to Sort By", columns)
    sort_order = st.radio("Select Sort Order", options=["Ascending", "Descending"])
    
    if sort_order == "Ascending":
        sorted_df = df.sort_values(by=sort_by, ascending=True)
    else:
        sorted_df = df.sort_values(by=sort_by, ascending=False)
    
    st.write("Sorted Data", sorted_df.head())
    return sorted_df

# Function for aggregating data
def aggregate_data(df):
    st.subheader("Aggregate Data")
    columns = df.columns
    group_by_column = st.selectbox("Select Column to Group By", columns)
    aggregate_column = st.selectbox("Select Column to Aggregate", df.select_dtypes(include=["float", "int"]).columns)
    aggregation_function = st.selectbox("Select Aggregation Function", ["Sum", "Mean", "Median", "Max", "Min"])
    
    if aggregation_function == "Sum":
        aggregated_df = df.groupby(group_by_column)[aggregate_column].sum().reset_index()
    elif aggregation_function == "Mean":
        aggregated_df = df.groupby(group_by_column)[aggregate_column].mean().reset_index()
    elif aggregation_function == "Median":
        aggregated_df = df.groupby(group_by_column)[aggregate_column].median().reset_index()
    elif aggregation_function == "Max":
        aggregated_df = df.groupby(group_by_column)[aggregate_column].max().reset_index()
    elif aggregation_function == "Min":
        aggregated_df = df.groupby(group_by_column)[aggregate_column].min().reset_index()
    
    st.write("Aggregated Data", aggregated_df.head())
    return aggregated_df

# Function to generate the appropriate plot based on the data characteristics
def generate_plot(df):
    st.subheader("Choose a Chart Type")
    chart_type = st.selectbox("Select Chart Type", options=["Scatter Plot", "Line Chart", "Bar Chart", "Pie Chart", 
                                                            "Histogram", "Box Plot", "Area Chart", "Bubble Chart"])

    numeric_columns = df.select_dtypes(include=["float", "int"]).columns
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns

    # Allow the user to choose axes based on selected chart type
    if chart_type in ["Scatter Plot", "Line Chart", "Box Plot", "Area Chart", "Bubble Chart"]:
        x_axis = st.selectbox("Select X-Axis", options=numeric_columns)
        y_axis = st.selectbox("Select Y-Axis", options=numeric_columns)
        
        if chart_type == "Scatter Plot":
            plot = px.scatter(df, x=x_axis, y=y_axis)
        elif chart_type == "Line Chart":
            plot = px.line(df, x=x_axis, y=y_axis)
        elif chart_type == "Box Plot":
            plot = px.box(df, x=x_axis, y=y_axis)
        elif chart_type == "Area Chart":
            plot = px.area(df, x=x_axis, y=y_axis)
        elif chart_type == "Bubble Chart":
            size_column = st.selectbox("Select Size Column", options=numeric_columns)
            plot = px.scatter(df, x=x_axis, y=y_axis, size=size_column)

    elif chart_type in ["Bar Chart", "Pie Chart"]:
        x_axis = st.selectbox("Select X-Axis (Categorical)", options=categorical_columns)
        y_axis = st.selectbox("Select Y-Axis (Numeric)", options=numeric_columns)
        
        if chart_type == "Bar Chart":
            plot = px.bar(df, x=x_axis, y=y_axis)
        elif chart_type == "Pie Chart":
            plot = px.pie(df, names=x_axis, values=y_axis)
    
    else:  # Histogram
        x_axis = st.selectbox("Select Column for Histogram", options=numeric_columns)
        plot = px.histogram(df, x=x_axis)
    
    st.plotly_chart(plot)

# Process each uploaded file
if uploaded_files:
    for file in uploaded_files:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file, encoding='utf-8-sig')
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        
        # Display the file name and dataset
        st.subheader(f"Dataset: {file.name}")
        st.write("Original Data", df.head())

        # Apply preprocessing
        df = filter_data(df)
        df = sort_data(df)
        df = aggregate_data(df)
        
        # Generate the appropriate plot
        generate_plot(df)

# Function to save the dashboard configuration
def save_configuration(config, file_name="dashboard_config.json"):
    with open(file_name, 'w') as f:
        json.dump(config, f)
    st.success(f"Configuration saved as {file_name}")

# Function to load the dashboard configuration
def load_configuration(file_name="dashboard_config.json"):
    try:
        with open(file_name, 'r') as f:
            config = json.load(f)
        st.success(f"Configuration {file_name} loaded successfully")
        return config
    except FileNotFoundError:
        st.error(f"Configuration file {file_name} not found.")
        return None

# Example save and load functionality
if st.button("Save Dashboard Configuration"):
    config = {
        "files": [file.name for file in uploaded_files],
        "filters": {},  # Add relevant filter settings
        "sort": {},  # Add sort settings
        "aggregate": {}  # Add aggregation settings
    }
    save_configuration(config)

if st.button("Load Dashboard Configuration"):
    config = load_configuration()
    if config:
        st.write(config)
        # Apply loaded configurations to your workflow (e.g., re-load files, apply filters, etc.)
