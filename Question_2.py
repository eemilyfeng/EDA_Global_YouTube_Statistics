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


# Updated Filter Function
def filter_data_by_year_and_country(selected_countries, selected_years):
    filter_conditions = []
    if selected_countries:
        filter_conditions.append(df['Country'].isin(selected_countries))
    if selected_years:
        filter_conditions.append(df['Created Year'].isin(selected_years))

    if filter_conditions:
        filtered_df = df[filter_conditions[0]]
        for condition in filter_conditions[1:]:
            filtered_df = filtered_df[condition]
    else:
        filtered_df = df

    return filtered_df

# Function to get most popular categories from filtered data
def get_most_popular_categories(data, column='Subscribers'):
    return data.groupby('Category').sum()[column].sort_values(ascending=False).index[0]

# Pie Chart for Category Popularity by Subscribers with Updated Caption
def plot_category_by_subscribers(data, selected_countries, selected_years):
    fig = px.pie(
        data_frame=data,
        names='Category',
        values='Subscribers',
        title='Distribution of Subscribers Across Categories'
    )
    st.plotly_chart(fig)
    most_popular_category = get_most_popular_categories(data, 'Subscribers')
    countries_text = ', '.join(selected_countries) if selected_countries else 'All countries'
    years_text = ', '.join(map(str, selected_years)) if selected_years else 'all creation years'
    st.caption(f"The most popular category by subscribers, considering the selected countries of **{countries_text}**, across **{years_text}**, is '{most_popular_category}'.")

# Pie Chart for Category Popularity by Video Views with Updated Caption
def plot_category_by_views(data, selected_countries, selected_years):
    fig = px.pie(
        data_frame=data,
        names='Category',
        values='Video Views',
        title='Distribution of Video Views Across Categories'
    )
    st.plotly_chart(fig)
    most_popular_category = get_most_popular_categories(data, 'Video Views')
    countries_text = ', '.join(selected_countries) if selected_countries else 'All countries'
    years_text = ', '.join(map(str, selected_years)) if selected_years else 'all creation years'
    st.caption(f"The most popular category by video views, considering the selected countries of **{countries_text}**, across **{years_text}**, is '{most_popular_category}'.")

# Streamlit Interface for User Input
st.title("Q2: Which YouTube Categories are Most Popular by Subscriber Count and Video Views?")
selected_countries = st.sidebar.multiselect('Select Countries', df['Country'].unique(), default=None)
selected_years = st.sidebar.multiselect('Select Created Year', df['Created Year'].unique(), default=None)

filtered_df = filter_data_by_year_and_country(selected_countries, selected_years)

# Displaying the Pie Charts
plot_category_by_subscribers(filtered_df, selected_countries, selected_years)
plot_category_by_views(filtered_df, selected_countries, selected_years)