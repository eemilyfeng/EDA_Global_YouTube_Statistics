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

st.dataframe(df)