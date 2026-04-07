import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re


# -----------------------------
# PAGE SETTINGS
# Set up the app title and layout
# -----------------------------
st.set_page_config(page_title="Video Game Sales Dashboard", layout="wide")
st.title("Video Game Sales Web App")
st.write("This app loads, cleans, analyzes, and visualizes video game sales data.")


# -----------------------------
# LOAD DATA
# Load dataset from CSV file
# -----------------------------
csv_path = "vgsales.csv"
df = pd.read_csv(csv_path)


# -----------------------------
# DATA CLEANING
# Prepare the dataset for analysis
# -----------------------------

# Rename columns to make them clearer and easier to use
df = df.rename(columns={
    "Name": "Game_Name",
    "Year": "Release_Year",
    "NA_Sales": "North_America_Sales",
    "EU_Sales": "Europe_Sales",
    "JP_Sales": "Japan_Sales",
    "Other_Sales": "Other_Region_Sales",
    "Global_Sales": "Global_Sales"
})

# Remove duplicate rows to avoid repeated data
df = df.drop_duplicates()

# Fill missing publisher values with "Unknown"
df["Publisher"] = df["Publisher"].fillna("Unknown")

# Fill missing year values using the median year
median_year = int(df["Release_Year"].median())
df["Release_Year"] = df["Release_Year"].fillna(median_year)

# Convert year column to integer format
df["Release_Year"] = df["Release_Year"].astype(int)

# Create a new column combining game name and platform
df["Game_Label"] = df["Game_Name"] + " (" + df["Platform"] + ")"


# -----------------------------
# SIDEBAR FILTERS
# Allow users to filter the dataset
# -----------------------------
st.sidebar.header("Filter Options")

selected_genre = st.sidebar.selectbox(
    "Select Genre",
    ["All"] + sorted(df["Genre"].unique().tolist())
)

selected_platform = st.sidebar.selectbox(
    "Select Platform",
    ["All"] + sorted(df["Platform"].unique().tolist())
)

year_range = st.sidebar.slider(
    "Select Release Year Range",
    min_value=int(df["Release_Year"].min()),
    max_value=int(df["Release_Year"].max()),
    value=(int(df["Release_Year"].min()), int(df["Release_Year"].max()))
)

# Text input for searching game names
name_pattern = st.sidebar.text_input("Search game names", "")


# -----------------------------
# APPLY FILTERS
# Filter dataset based on user selections
# -----------------------------
filtered_df = df.copy()

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df["Genre"] == selected_genre]

if selected_platform != "All":
    filtered_df = filtered_df[filtered_df["Platform"] == selected_platform]

# Filter based on selected year range
filtered_df = filtered_df[
    (filtered_df["Release_Year"] >= year_range[0]) &
    (filtered_df["Release_Year"] <= year_range[1])
]

# Apply search filter if user enters text
if name_pattern.strip() != "":
    pattern = rf"^{re.escape(name_pattern)}"
    filtered_df = filtered_df[
        filtered_df["Game_Name"].str.contains(pattern, case=False, na=False, regex=True)
    ]


# -----------------------------
# SHOW DATA
# Display dataset preview
# -----------------------------
st.header("Dataset Preview")
st.write("Original dataset size:", df.shape)
st.write("Filtered dataset size:", filtered_df.shape)
st.dataframe(filtered_df.head(20))


# -----------------------------
# METRICS
# Display key summary statistics
# -----------------------------
st.header("Important Metrics")

total_games = filtered_df.shape[0]
total_global_sales = filtered_df["Global_Sales"].sum()
average_global_sales = filtered_df["Global_Sales"].mean()

# Find top-selling game
if total_games > 0:
    top_game = filtered_df.loc[filtered_df["Global_Sales"].idxmax(), "Game_Name"]
else:
    top_game = "No data"

# Display metrics in columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Games", total_games)
col2.metric("Total Global Sales", f"{total_global_sales:.2f} million")
col3.metric("Average Global Sales", f"{average_global_sales:.2f} million")
col4.metric("Top Game", top_game)


# -----------------------------
# CHART 1
# Top 10 games by global sales
# -----------------------------
st.header("Top 10 Games by Global Sales")

if total_games > 0:
    top_10_games = filtered_df.nlargest(10, "Global_Sales")[["Game_Name", "Global_Sales"]]

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(top_10_games["Game_Name"], top_10_games["Global_Sales"])
    ax1.set_title("Top 10 Games by Global Sales")
    ax1.set_xlabel("Game Name")
    ax1.set_ylabel("Global Sales (millions)")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig1)


# -----------------------------
# CHART 2
# Total sales by genre
# -----------------------------
st.header("Global Sales by Genre")

if total_games > 0:
    genre_sales = filtered_df.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(genre_sales.index, genre_sales.values)
    ax2.set_title("Global Sales by Genre")
    ax2.set_xlabel("Genre")
    ax2.set_ylabel("Global Sales (millions)")
    plt.xticks(rotation=45)
    st.pyplot(fig2)


# -----------------------------
# CHART 3
# Sales trend over time
# -----------------------------
st.header("Global Sales Trend by Release Year")

if total_games > 0:
    yearly_sales = filtered_df.groupby("Release_Year")["Global_Sales"].sum().sort_index()

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(yearly_sales.index, yearly_sales.values, marker="o")
    ax3.set_title("Global Sales Trend by Release Year")
    ax3.set_xlabel("Release Year")
    ax3.set_ylabel("Global Sales (millions)")
    st.pyplot(fig3)
