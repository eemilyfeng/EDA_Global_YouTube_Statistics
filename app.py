import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import re

# Open the data
df = pd.read_csv('data/Global_YouTube_Statistics.csv', encoding='latin-1')
pd.set_option('display.max_columns', None)

# Clean the data
df.columns = df.columns.str.replace('_', ' ').str.title()
df = df.drop(columns='Rank')
df = df.drop_duplicates()
categorical_columns = df.select_dtypes(include=['object']).columns
df[categorical_columns] = df[categorical_columns].fillna('Unknown')
numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns
df[numerical_columns] = df[numerical_columns].fillna(0)
pattern = r'[^a-zA-Z0-9\s.,!?&\'-]'
df['Youtuber'] = df['Youtuber'].str.replace(pattern, '', regex=True)
df['Title'] = df['Title'].str.replace(pattern, '', regex=True)
df['Youtuber'] = df['Youtuber'].str.strip()
df['Title'] = df['Title'].str.strip()
df = df[df['Video Views'] != 0]
df = df[df['Youtuber'] != '']
df = df[df['Created Year'] != 0]
float_to_int_columns = ['Video Views', 'Video Views Rank', 'Country Rank', 'Channel Type Rank',
                        'Video Views For The Last 30 Days', 'Subscribers For Last 30 Days',
                        'Created Year', 'Population', 'Urban Population']
df[float_to_int_columns] = df[float_to_int_columns].astype(int)
df = df.sort_values(by='Subscribers', ascending=False)
df = df.reset_index(drop=True)

# Create Interface
st.set_page_config(layout="wide")
st.sidebar.title("Filters")

# Sidebar for selecting visualization
vis = st.sidebar.radio("Select Your Question:", options=["Question 1", "Question 2", "Question 3"])

# Question 1 Code
if vis == "Question 1":
    st.title("Who are the Top 10 YouTubers in Terms of Subscribers and the Top 10 YouTubers with the Highest Views?")
    selected_countries = st.sidebar.multiselect('Select Countries', df['Country'].unique(), default=None)
    selected_categories = st.sidebar.multiselect('Select Categories', df['Category'].unique(), default=None)

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

    filtered_df = filter_data(selected_countries, selected_categories)

    top_subscribers = filtered_df.sort_values(by='Subscribers', ascending=False).head(10)
    top_views = filtered_df.sort_values(by='Video Views', ascending=False).head(10)

    # Plot for Top 10 YouTubers by Subscribers
    fig_subscribers = px.bar(
        top_subscribers,
        x='Youtuber',
        y='Subscribers',
        color='Subscribers',
        title='Top 10 YouTubers in Terms of Number of Subscribers'
    )
    st.plotly_chart(fig_subscribers)

    # Plot for Top 10 YouTubers by Video Views
    fig_views = px.bar(
        top_views,
        x='Youtuber',
        y='Video Views',
        color='Video Views',
        title='Top 10 YouTubers in Terms of Views (in billions)'
    )
    st.plotly_chart(fig_views)


# Question 2 Code
elif vis == "Question 2":
    st.title("Which YouTube Categories are Most Popular by Subscriber Count and Video Views?")

    selected_countries_q2 = st.sidebar.multiselect('Select Countries', df['Country'].unique(), default=None, key='selected_countries_q2')
    selected_years_q2 = st.sidebar.multiselect('Select Created Year', df['Created Year'].unique(), default=None, key='selected_years_q2')

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

    def get_most_popular_categories(data, column='Subscribers'):
        return data.groupby('Category').sum()[column].sort_values(ascending=False).index[0]

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

    filtered_df_q2 = filter_data_by_year_and_country(selected_countries_q2, selected_years_q2)

    plot_category_by_subscribers(filtered_df_q2, selected_countries_q2, selected_years_q2)
    plot_category_by_views(filtered_df_q2, selected_countries_q2, selected_years_q2)

# Question 3 Code
elif vis == "Question 3":
    st.title("How Does Subscriber Count Vary Across Different Countries?")

    selected_categories_q3 = st.sidebar.multiselect('Select Categories', df['Category'].unique(), default=None, key='selected_categories_q3')
    sorted_years = sorted(df['Created Year'].unique())
    selected_years_q3 = st.sidebar.multiselect('Select Year of Channel Creation', sorted_years, default=None, key='selected_years_q3')

    def filter_data_by_category_and_year(selected_categories, selected_years):
        filtered_df = df.copy()
        if selected_categories:
            filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
        if selected_years:
            filtered_df = filtered_df[filtered_df['Created Year'].isin(selected_years)]
        return filtered_df

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

        categories_text = ', '.join(selected_categories) if selected_categories else 'all categories'
        years_text = ', '.join(map(str, selected_years)) if selected_years else 'all years'
        st.caption(f"This chart illustrates the average subscriber count across various countries for **{categories_text}**, considering channels created in **{years_text}**. It highlights how audience preferences and channel popularity vary geographically and categorically.")

    filtered_df_q3 = filter_data_by_category_and_year(selected_categories_q3, selected_years_q3)
    plot_subscriber_count_by_country(filtered_df_q3, selected_categories_q3, selected_years_q3)

