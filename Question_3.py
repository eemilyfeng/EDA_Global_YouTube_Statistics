import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np


##Open the data##
# Import csv dataset & convert to pandas dataframe (df)
df = pd.read_csv('data/Global_YouTube_Statistics.csv', encoding='latin-1')
# Set the display.max_columns option to None to display all columns of the df
pd.set_option('display.max_columns', None)


## Clean the data
# Rename columns: replace '_' with ' ' and capitalize each word
df.columns = df.columns.str.replace('_', ' ').str.title()

# Drop the 'Rank' column as it's not required
df = df.drop(columns='Rank')

# Remove duplicate rows
df = df.drop_duplicates()

# Handle missing values
# Replace missing values in categorical columns with 'Unknown'
categorical_columns = df.select_dtypes(include=['object']).columns
df[categorical_columns] = df[categorical_columns].fillna('Unknown')

# Replace missing values in numerical columns with 0
numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns
df[numerical_columns] = df[numerical_columns].fillna(0)

# Remove and replace unwanted characters in 'Youtuber' and 'Title'
import re
pattern = r'[^a-zA-Z0-9\s.,!?&\'-]'
df['Youtuber'] = df['Youtuber'].str.replace(pattern, '', regex=True)
df['Title'] = df['Title'].str.replace(pattern, '', regex=True)

# Trim leading/trailing whitespace
df['Youtuber'] = df['Youtuber'].str.strip()
df['Title'] = df['Title'].str.strip()

# Remove rows with 0 video views, blank Youtuber names, and 'Created Year' as 0
df = df[df['Video Views'] != 0]
df = df[df['Youtuber'] != '']
df = df[df['Created Year'] != 0]

# Convert certain float columns to integers
float_to_int_columns = [
    'Video Views', 'Video Views Rank', 'Country Rank', 'Channel Type Rank',
    'Video Views For The Last 30 Days', 'Subscribers For Last 30 Days',
    'Created Year', 'Population', 'Urban Population'
]
df[float_to_int_columns] = df[float_to_int_columns].astype(int)

# Sort by 'Subscribers' and reset index
df = df.sort_values(by='Subscribers', ascending=False)
df = df.reset_index(drop=True)

# Filter Function for Category and Year of Channel Creation
def filter_data_by_category_and_year(selected_categories, selected_years):
    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    if selected_years:
        filtered_df = filtered_df[filtered_df['Created Year'].isin(selected_years)]
    return filtered_df

# Grouped Bar Chart for Subscriber Count across Countries
def plot_subscriber_count_by_country(data, selected_categories, selected_years):
    grouped_data = data.groupby(['Country', 'Category'])['Subscribers'].mean().reset_index()
    fig = px.bar(
        grouped_data,
        x='Country',
        y='Subscribers',
        color='Category',
        barmode='group',
        title='Average Subscriber Count Across Different Countries by Category'
    )
    fig.update_layout(xaxis_title='Country', yaxis_title='Average Subscribers')
    st.plotly_chart(fig)

    # Forming descriptive caption with bold selections
    categories_text = ', '.join(selected_categories) if selected_categories else 'all categories'
    years_text = ', '.join(map(str, selected_years)) if selected_years else 'all years'
    st.caption(
        f"This chart illustrates the average subscriber count across various countries for **{categories_text}**, considering channels created in **{years_text}**. It highlights how audience preferences and channel popularity vary geographically and categorically.")

# Streamlit Interface for User Input with Sorted Year Filter
st.title("Q3: How Does Subscriber Count Vary Across Different Countries?")
selected_categories = st.sidebar.multiselect('Select Categories', df['Category'].unique(), default=None)

# Sorting the years before presenting them in the multiselect widget
sorted_years = sorted(df['Created Year'].unique())
selected_years = st.sidebar.multiselect('Select Year of Channel Creation', sorted_years, default=None)

filtered_df = filter_data_by_category_and_year(selected_categories, selected_years)





# Displaying the Grouped Bar Chart
plot_subscriber_count_by_country(filtered_df, selected_categories, selected_years)