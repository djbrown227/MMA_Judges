#!/usr/bin/env python
# coding: utf-8

# In[1]:


#In this file we are going to combined all the scraped data from 'http://mmadecisions.com'
#Then combine all the scraped data. Then clean the data, this will include some feature engineering


# In[3]:


import os
import pandas as pd
import pandas as pd
import re

# Define the folder path
folder_path = '/Users/danielbrown/Desktop/WebApps/MMA_Judge_Data/MMA_Judge_Data/scraped_mma_data'

# Get a list of all Excel files in the folder
excel_files = [file for file in os.listdir(folder_path) if file.endswith('.xlsx')]

# Initialize an empty list to store DataFrame objects
dfs = []
# Initialize an empty list to store the names of files combined
combined_file_names = []

# Loop through each Excel file and read it into a DataFrame, then append to dfs list
for file in excel_files:
    df = pd.read_excel(os.path.join(folder_path, file))
    dfs.append(df)
    combined_file_names.append(file)

# Concatenate all DataFrames in dfs list into one
combined_df = pd.concat(dfs, ignore_index=True)

# Write the concatenated DataFrame to a new CSV file
combined_file_path = '/Users/danielbrown/Desktop/WebApps/MMA_Judge_Data/MMA_Judge_Data/combined_data.csv'
combined_df.to_csv(combined_file_path, index=False)

# Get the count of files combined
num_files_combined = len(excel_files)

print(f"Concatenation complete. The combined data has been saved as 'combined_data.csv'.")
print(f"Number of files combined: {num_files_combined}")
print("Names of files combined:")
for file_name in combined_file_names:
    print(file_name)


# In[4]:


#Import raw MMA Judge Data
df = pd.read_csv(r"/Users/danielbrown/Desktop/WebApps/MMA_Judge_Data/MMA_Judge_Data/combined_data.csv")


# In[5]:


# Count the unique entries in the "Fighter 1 Name" column
unique_fighter1_count = df['Fighter 1 Name'].nunique()

print(f"Number of unique entries in 'Fighter 1 Name' column: {unique_fighter1_count}")


# In[6]:


filtered_df = df

# Parse the 'Event Date and Location' column to create the 'Date' and 'Location' columns
filtered_df['Date'] = filtered_df['Event Date and Location'].apply(lambda x: x.split('\n')[0].strip())
filtered_df['Location'] = filtered_df['Event Date and Location'].apply(lambda x: x.split('\n')[-1].strip())

#filtered_df.to_csv('/Users/danielbrown/Desktop/fight_scores.csv', index=False)


# In[7]:


# Function to check if the score is numeric (or a numeric range like '30-27')
def is_numeric(score):
    # This regex will match any number or range like '30-27'
    return pd.notnull(score) and bool(re.match(r'^(\d+(-\d+)?)$', str(score)))

# Filter the DataFrame
filtered_df = df[df['Fighter 2 Score'].apply(is_numeric)]

# Further filter to remove rows where 'Fighter 1 Name' is 'TALE OF THE TAPE'
filtered_df = filtered_df[filtered_df['Fighter 1 Name'] != 'TALE OF THE TAPE']


# In[8]:


# Count the unique entries in the "Fighter 1 Name" column
unique_fighter1_count = filtered_df['Fighter 1 Name'].nunique()

print(f"Number of unique entries in 'Fighter 1 Name' column: {unique_fighter1_count}")


# In[9]:


# Use regular expression to find the pattern of the date
def extract_date_and_location(text):
    match = re.search(r'(\w+ \d{1,2}, \d{4})\s+(.*)', text)
    if match:
        return match.group(1), match.group(2)
    else:
        return '', ''  # Return empty strings if the pattern does not match

# Apply the function to the 'Event Date and Location' column
filtered_df[['Event Date', 'Location']] = df.apply(lambda row: extract_date_and_location(row['Event Date and Location']), axis=1, result_type='expand')


# In[10]:


filtered_df = filtered_df[['Event Title', 'Event Date','Location', 'Judge Name', 'Fighter 1 Name', 'Fighter 2 Name', 'Round', 'Fighter 1 Score','Fighter 2 Score']]
filtered_df


# In[11]:


# Group by the fight-defining characteristics and create a group identifier
grouped = filtered_df.groupby(['Event Title', 'Event Date', 'Location', 'Fighter 1 Name', 'Fighter 2 Name'])

# Create a new column 'Fight ID' and assign a unique number to each group
filtered_df['Fight ID'] = grouped.ngroup()

# Display the DataFrame to verify the new 'Fight ID' column
print(filtered_df[['Fight ID']].head())
filtered_df['Fight ID'] = grouped.ngroup() + 1  # To start numbering from 1


# In[12]:


# Assuming your DataFrame is named filtered_df
# Replace "-" with NaN in 'Fighter 1 Score' column
filtered_df['Fighter 1 Score'] = filtered_df['Fighter 1 Score'].replace('-', pd.NA)

# Convert 'Fighter 1 Score' to numeric in case it's stored as a string
filtered_df['Fighter 1 Score'] = pd.to_numeric(filtered_df['Fighter 1 Score'], errors='coerce')

# Drop rows containing NaN values in 'Fighter 1 Score' column
filtered_df = filtered_df.dropna(subset=['Fighter 1 Score'])


# In[13]:


#The below counts the number of rows for each 'Fight ID'
# Create the new column 'Round Count' initialized with zeros
filtered_df['Round Count'] = 0

# Group the DataFrame by 'Fight ID' and 'Round', and count the occurrences
round_counts = filtered_df.groupby(['Fight ID', 'Round']).size().reset_index(name='Count')

# Iterate over each row in the round_counts DataFrame and update the 'Round Count' column in filtered_df
for index, row in round_counts.iterrows():
    fight_id = row['Fight ID']
    round_value = row['Round']
    count = row['Count']
    filtered_df.loc[(filtered_df['Fight ID'] == fight_id) & (filtered_df['Round'] == round_value), 'Round Count'] += count


# In[14]:


# Group by 'Fight ID' and find the minimum 'Round Count' for each group
min_round_counts = filtered_df.groupby('Fight ID')['Round Count'].min().reset_index()

# Merge the minimum round counts back to the original DataFrame
merged_df = pd.merge(filtered_df, min_round_counts, on=['Fight ID'], suffixes=('', '_min'))

# Filter out the rows where 'Round Count' matches the minimum value for each 'Fight ID'
filtered_df = merged_df[merged_df['Round Count'] != merged_df['Round Count_min']]

# Drop the extra column 'Round Count_min' if needed
filtered_df = filtered_df.drop(columns=['Round Count_min'])

# Order by 'Fight ID' and 'Round'
filtered_df = filtered_df.sort_values(by=['Event Date','Fight ID','Judge Name', 'Round'])


# In[15]:


# Assuming 'column_name' is the name of the column you want to convert to datetime
filtered_df['Event Date'] = pd.to_datetime(filtered_df['Event Date'])

# Get the data types of each column in the DataFrame
column_datatypes = filtered_df.dtypes

# Print the data types
print(column_datatypes)


# In[16]:


# Reset the index
filtered_df.reset_index(drop=True, inplace=True)

# Drop duplicates based on all columns
filtered_df.drop_duplicates(inplace=True)


# In[17]:


filtered_df.to_csv('/Users/danielbrown/Desktop/fight_scores_1.csv', index=False)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




