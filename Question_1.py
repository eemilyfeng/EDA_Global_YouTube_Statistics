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


# Filter Function
def filter_data(selected_countries, selected_categories):
    if selected_countries and selected_categories:
        filtered_df = df[df['Country'].isin(selected_countries) & df['Category'].isin(selected_categories)]
    elif selected_countries:
        filtered_df = df[df['Country'].isin(selected_countries)]
    elif selected_categories:
        filtered_df = df[df['Category'].isin(selected_categories)]
    else:
        filtered_df = df
    return filtered_df

# Plotting Function for Subscribers with Updated Descriptive Caption
def plot_top_subscribers(data, filter_description):
    fig = px.bar(
        data_frame=data,
        x='Youtuber',
        y='Subscribers',
        title='Top 10 YouTuber in terms of no. of Subscribers',
        labels={'Subscribers': 'Subscribers (in millions)'},
        color='Subscribers'
    )
    fig.update_layout(xaxis_title='YouTuber', yaxis_title='Subscribers (M)')
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"This bar chart displays the top 10 YouTubers ranked by their number of subscribers, **{filter_description}**")

# Plotting Function for Views with Updated Descriptive Caption
def plot_top_views(data, filter_description):
    fig = px.bar(
        data_frame=data,
        x='Youtuber',
        y='Video Views',
        title='Top 10 YouTubers in terms of Views (in billions)',
        labels={'Video Views': 'Video Views (in billions)'},
        color='Video Views'
    )
    fig.update_layout(xaxis_title='YouTuber', yaxis_title='Video Views (B)')
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"This bar chart illustrates the top 10 YouTubers based on their video views, **{filter_description}**")

# Streamlit Interface for User Input
st.markdown("# Q1: Who are the Top 10 YouTubers in Terms of Subscribers and the Top 10 YouTubers with the Highest Views?")
st.markdown("### Explore the most popular YouTubers based on subscribers and video views.")

selected_countries = st.sidebar.multiselect('Select Countries', df['Country'].unique(), default=None)
selected_categories = st.sidebar.multiselect('Select Categories', df['Category'].unique(), default=None)

filtered_df = filter_data(selected_countries, selected_categories)

# Filter Description
# Update the filter description to be more coherent
selected_countries_text = ', '.join(selected_countries) if selected_countries else 'All countries'
selected_categories_text = ', '.join(selected_categories) if selected_categories else 'All categories'
filter_description = f"highlighting the most followed personalities within the categories of **{selected_categories_text}**, specifically in **{selected_countries_text}**."

# Top 10 Subscribers and Views
top_subscribers = filtered_df.sort_values(by='Subscribers', ascending=False).head(10)
top_views = filtered_df.sort_values(by='Video Views', ascending=False).head(10)

# Displaying the plots with enhanced descriptions
plot_top_subscribers(top_subscribers, filter_description)
plot_top_views(top_views, filter_description)