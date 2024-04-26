#!/usr/bin/env python
# coding: utf-8

# In[847]:


import os
import pandas as pd
import pandas as pd
import re


# In[848]:


#Import raw MMA Judge Data
filtered_df = pd.read_csv(r"/Users/danielbrown/Desktop/fight_scores_1.csv")


# In[849]:


# Define a function to find the mode within each group
def find_mode(x):
    return x.mode().iloc[0]

# Apply the mode function to 'Fighter 1 Score' within each group
filtered_df['mode'] = filtered_df.groupby(['Fight ID', 'Round'])['Fighter 1 Score'].transform(find_mode)

# Check if any judge's score differs from the mode for each group
filtered_df['In Minority'] = (filtered_df['Fighter 1 Score'] != filtered_df['mode']).astype(int)

# Finally, drop the 'mode' column since we no longer need it
filtered_df = filtered_df.drop(columns=['mode'])

filtered_df_sorted = filtered_df.sort_values(by='Event Date')
filtered_df.reset_index(drop=True, inplace=True)

# Convert to datetime
filtered_df['Event Date'] = pd.to_datetime(filtered_df['Event Date'])


# In[850]:


# Get the data types of each column in the DataFrame
column_datatypes = filtered_df.dtypes

# Print the data types
print(column_datatypes)


# In[851]:


#filtered_df


# In[852]:


# Group by 'Judge Name' and count occurrences
filtered_df['Rounds_Judged'] = filtered_df.groupby('Judge Name')['Judge Name'].transform('count')

# Group by 'Judge Name' and 'Year' and count occurrences
# Extract year from 'Event Date'
filtered_df['Year'] = filtered_df['Event Date'].dt.year
filtered_df['Judge Year Count'] = filtered_df.groupby(['Judge Name', 'Year'])['Judge Name'].transform('count')

#filtered_df.to_csv('/Users/danielbrown/Desktop/fight_scores_2.csv', index=False)

# Display the updated dataframe
#print(filtered_df)


# In[853]:


# Convert 'Event Date' to datetime
filtered_df['Event Date'] = pd.to_datetime(filtered_df['Event Date'])

# Sort the dataframe by 'Event Date'
filtered_df = filtered_df.sort_values(by='Event Date')

# Group by 'Judge Name'
grouped_by_judge = filtered_df.groupby('Judge Name')

# Calculate the cumulative count of rounds judged for each judge
filtered_df['Rounds_Judged_SoFar'] = grouped_by_judge.cumcount() + 1

filtered_df.to_csv('/Users/danielbrown/Desktop/fight_scores_2.csv', index=False)

# Display the dataframe with the new column
filtered_df


# In[854]:


#Finds the average of "In Minority" decisions year over year

# Convert 'Event Date' to datetime
filtered_df['Event Date'] = pd.to_datetime(filtered_df['Event Date'])

# Extract year from 'Event Date'
filtered_df['Year'] = filtered_df['Event Date'].dt.year

# Group by 'Year' and calculate the ratio of "In Minority" 1s for each year
field_ratio = filtered_df.groupby('Year')['In Minority'].mean().reset_index()

print(field_ratio)


# In[855]:


#Find the year by year "In Minority" decisions for each judge
# Convert 'Event Date' column to datetime type
filtered_df['Event Date'] = pd.to_datetime(filtered_df['Event Date'])

# Extract the year from the 'Event Date' column
filtered_df['Year'] = filtered_df['Event Date'].dt.year

# Group by 'Judge Name' and 'Year', then calculate the ratio of "In Minority" 1s
judge_year_ratio = filtered_df.groupby(['Judge Name', 'Year'])['In Minority'].mean().reset_index()

# Rename the column to 'In Minority Ratio'
judge_year_ratio.rename(columns={'In Minority': 'In Minority Ratio'}, inplace=True)

# Display the resulting DataFrame
print(judge_year_ratio)


# In[856]:


import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display

# Convert 'Event Date' to datetime
filtered_df['Event Date'] = pd.to_datetime(filtered_df['Event Date'])

# Extract year from 'Event Date'
filtered_df['Year'] = filtered_df['Event Date'].dt.year

# Group by 'Judge Name' and 'Year' and calculate the ratio of "In Minority" 1s for each judge
judge_year_ratio = filtered_df.groupby(['Judge Name', 'Year'])['In Minority'].mean().reset_index()

# Calculate the overall 'In Minority' ratio for each year
overall_year_ratio = filtered_df.groupby('Year')['In Minority'].mean().reset_index()
overall_year_ratio.rename(columns={'In Minority': 'Overall In Minority'}, inplace=True)

# Create a function to update the plot when a judge is selected
def update_plot(change):
    judge = change.new
    
    # Filter data for the selected judge
    judge_data = judge_year_ratio[judge_year_ratio['Judge Name'] == judge]
    
    # Clear previous traces from the figure
    fig.data = []
    
    # Create the line plot for the selected judge
    fig.add_trace(go.Scatter(x=judge_data['Year'], y=judge_data['In Minority'], mode='lines', name=judge))
    
    # Add the overall 'In Minority' ratio for each year to the same plot
    overall_ratio = overall_year_ratio.loc[overall_year_ratio['Year'].isin(judge_data['Year']), 'Overall In Minority']
    fig.add_trace(go.Scatter(x=judge_data['Year'], y=overall_ratio, mode='lines', name='Overall Judges'))
    
    # Update layout
    fig.update_layout(title=f'In Minority Ratio Over Years for {judge}',
                      xaxis_title='Year',
                      yaxis_title='In Minority Ratio')

# Create a dropdown widget for judges
judge_dropdown = widgets.Dropdown(options=sorted(judge_year_ratio['Judge Name'].unique()), description='Judge:')

# Bind the update_plot function to the dropdown widget
judge_dropdown.observe(update_plot, names='value')

# Initialize an empty figure object
fig = go.FigureWidget()

# Display the dropdown widget and an empty graph
display(judge_dropdown)
display(fig)


# In[857]:


# Assuming df is your dataframe
# Group by year
grouped_by_year = judge_year_ratio.groupby('Year')

# Create an empty dictionary to store dataframes for each year
yearly_dataframes = {}

# Iterate over each group (year)
for year, group_df in grouped_by_year:
    # Sort the dataframe by "In Minority Ratio" in descending order
    sorted_df = group_df.sort_values(by='In Minority', ascending=False)
    # Add the sorted dataframe to the dictionary with the year as the key
    yearly_dataframes[year] = sorted_df

# Now you have a dictionary where each key is a year and the corresponding value is the sorted dataframe for that year
# You can access each dataframe using the year as the key, for example:
print("Top 5 years with highest 'In Minority Ratio':")
for year, sorted_df in yearly_dataframes.items():
    print(f"Year: {year}")
    print(sorted_df.head())
    print()


# In[ ]:





# In[ ]:





# In[858]:


#Find ratio of times judges were "In the Minority". This is for all judges, no matter if they judged 1 round 

# Group by 'Judge Name'
judge_group = df.groupby('Judge Name')

# Calculate the total number of rounds judged by each judge
rounds_judged = judge_group['Round'].count()

# Calculate the number of rounds judged where 'In Minority' is 1 for each judge
minority_1_count = judge_group['In Minority'].sum()

# Calculate the ratio of "In Minority" 1s over the total number of rounds judged by each judge
ratio_minority_1 = minority_1_count / rounds_judged

# Create a DataFrame to store the results
judge_ratio_df = pd.DataFrame({
    'Judge Name': ratio_minority_1.index,
    'In Minority Ratio': ratio_minority_1.values,
    'Total Rounds Judged': rounds_judged.values,
    'In Minority Count': minority_1_count.values
})


print(len(judge_ratio_df))
print(judge_ratio_df)


# In[859]:


#Filter judge_ratio_df for judges that have judged more than 50 rounds

# Assuming judge_ratio_df is your DataFrame
filtered_df = judge_ratio_df[judge_ratio_df['Total Rounds Judged'] > 50]

# Sort the judge ratio DataFrame by the ratio of "In Minority" 1s
judge_ratio_df_sorted = filtered_df.sort_values(by='In Minority Ratio', ascending=False)

print(len(judge_ratio_df_sorted))
print(judge_ratio_df_sorted)


# In[860]:


# Sort the judge ratio DataFrame by the number of rounds judged and then by the ratio of "In Minority" 1s
judge_ratio_df_sorted = judge_ratio_df_sorted.sort_values(by=['In Minority Ratio'], ascending=[False])
# Reset the index
judge_ratio_df_sorted.reset_index(drop=True, inplace=True)
judge_ratio_df_sorted.to_csv('/Users/danielbrown/Desktop/fight_scores_judge_career_ratio.csv', index=False)

print(judge_ratio_df_sorted)


# In[861]:


#Check to see if any of the judges who have judged over 50 rounds have judged statistically significant than the 
#other judges


# In[862]:


import pandas as pd
from scipy import stats

# Assuming your DataFrame is named df
# Step 1: Convert "In Minority" column to numeric type
df['In Minority'] = pd.to_numeric(df['In Minority'], errors='coerce')

# Step 2: Drop rows with missing values in "In Minority" column
df.dropna(subset=['In Minority'], inplace=True)

# Step 3: Group data by judge and calculate the mean of "In Minority"
judge_ratios = df.groupby('Judge Name')['In Minority'].mean()

# Step 4: Perform Mann-Whitney U test for each judge against the field
results = []
for judge in judge_ratios.index:
    p_value = stats.mannwhitneyu(judge_ratios, judge_ratios.loc[judge], alternative='two-sided').pvalue
    if p_value < 0.05:
        results.append((judge, p_value, "Significant"))
    else:
        results.append((judge, p_value, "Not Significant"))

# Display results
for result in results:
    print(f"Judge: {result[0]}, p-value: {result[1]:.4f}, Test result: {result[2]}")


# In[ ]:





# In[863]:


from scipy import stats
from itertools import combinations

def test_judges(judge1, data):
    # Extract "In Minority" ratios for the two judges
    ratio_judge1 = data[data['Judge Name'] == judge1]['In Minority Ratio']
    ratio_other_judges = data[data['Judge Name'] != judge1]['In Minority Ratio']
    
    # Perform Mann-Whitney U test
    p_value = stats.mannwhitneyu(ratio_judge1, ratio_other_judges, alternative='two-sided').pvalue
    if p_value < 0.05:
        return p_value, "Significant"
    else:
        return p_value, "Not significant"

# Get the list of all judges
all_judges = judge_ratio_df_sorted['Judge Name'].unique()

# Test each judge against the rest of the judges
results = []
for judge in all_judges:
    p_value, test_type = test_judges(judge, judge_ratio_df_sorted)
    results.append((judge, p_value, test_type))
    print(f"Testing {judge} against the field: p-value = {p_value:.4f} ({test_type})")


# In[ ]:





# In[864]:


filtered_df_overtime = pd.read_csv(r"/Users/danielbrown/Desktop/fight_scores_2.csv")
filtered_df_overtime = filtered_df_overtime[filtered_df_overtime['Rounds_Judged'] > 50]
filtered_df_overtime


# In[865]:


#Find the year by year "In Minority" decisions for each judge
# Convert 'Event Date' column to datetime type
filtered_df_overtime['Event Date'] = pd.to_datetime(filtered_df_overtime['Event Date'])

# Extract the year from the 'Event Date' column
filtered_df_overtime['Year'] = filtered_df_overtime['Event Date'].dt.year

# Group by 'Judge Name' and 'Year', then calculate the ratio of "In Minority" 1s
judge_year_ratio = filtered_df_overtime.groupby(['Judge Name', 'Year'])['In Minority'].mean().reset_index()

# Rename the column to 'In Minority Ratio'
judge_year_ratio.rename(columns={'In Minority': 'In Minority Ratio'}, inplace=True)

# Display the resulting DataFrame
print(judge_year_ratio)

filtered_df = filtered_df_overtime


# In[866]:


import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display

# Convert 'Event Date' to datetime
filtered_df['Event Date'] = pd.to_datetime(filtered_df['Event Date'])

# Extract year from 'Event Date'
filtered_df['Year'] = filtered_df['Event Date'].dt.year

# Group by 'Judge Name' and 'Year' and calculate the ratio of "In Minority" 1s for each judge
judge_year_ratio = filtered_df.groupby(['Judge Name', 'Year'])['In Minority'].mean().reset_index()

# Calculate the overall 'In Minority' ratio for each year
overall_year_ratio = filtered_df.groupby('Year')['In Minority'].mean().reset_index()
overall_year_ratio.rename(columns={'In Minority': 'Overall In Minority'}, inplace=True)

# Create a function to update the plot when a judge is selected
def update_plot(change):
    judge = change.new
    
    # Filter data for the selected judge
    judge_data = judge_year_ratio[judge_year_ratio['Judge Name'] == judge]
    
    # Clear previous traces from the figure
    fig.data = []
    
    # Create the line plot for the selected judge
    fig.add_trace(go.Scatter(x=judge_data['Year'], y=judge_data['In Minority'], mode='lines', name=judge))
    
    # Add the overall 'In Minority' ratio for each year to the same plot
    overall_ratio = overall_year_ratio.loc[overall_year_ratio['Year'].isin(judge_data['Year']), 'Overall In Minority']
    fig.add_trace(go.Scatter(x=judge_data['Year'], y=overall_ratio, mode='lines', name='Overall Judges'))
    
    # Update layout
    fig.update_layout(title=f'In Minority Ratio Over Years for {judge}',
                      xaxis_title='Year',
                      yaxis_title='In Minority Ratio')

# Create a dropdown widget for judges
judge_dropdown = widgets.Dropdown(options=sorted(judge_year_ratio['Judge Name'].unique()), description='Judge:')

# Bind the update_plot function to the dropdown widget
judge_dropdown.observe(update_plot, names='value')

# Initialize an empty figure object
fig = go.FigureWidget()

# Display the dropdown widget and an empty graph
display(judge_dropdown)
display(fig)


# In[867]:


# Assuming df is your dataframe
# Group by year
grouped_by_year = judge_year_ratio.groupby('Year')

# Create an empty dictionary to store dataframes for each year
yearly_dataframes = {}

# Iterate over each group (year)
for year, group_df in grouped_by_year:
    # Sort the dataframe by "In Minority Ratio" in descending order
    sorted_df = group_df.sort_values(by='In Minority', ascending=False)
    # Add the sorted dataframe to the dictionary with the year as the key
    yearly_dataframes[year] = sorted_df

# Now you have a dictionary where each key is a year and the corresponding value is the sorted dataframe for that year
# You can access each dataframe using the year as the key, for example:
print("Top 5 years with highest 'In Minority Ratio':")
for year, sorted_df in yearly_dataframes.items():
    print(f"Year: {year}")
    print(sorted_df.head())
    print()


# In[ ]:





# In[868]:


filtered_df_yearyear = pd.read_csv(r"/Users/danielbrown/Desktop/fight_scores_2.csv")

#filtered_df_judgedata = filtered_df_yearyear[filtered_df_yearyear['Judge Name'] == 'Cecil Peoples']
#filtered_df_filtered.to_csv('/Users/danielbrown/Desktop/fight_scores_judge.csv', index=False)

# Filter the dataframe to keep only rows where Judge Year Count is greater than 30
filtered_df_filtered = filtered_df_yearyear[filtered_df_yearyear['Judge Year Count'] > 30]
filtered_df_filtered.to_csv('/Users/danielbrown/Desktop/fight_scores_judge_year.csv', index=False)
filtered_df_filtered


# In[869]:


filtered_df_overtime = filtered_df_filtered

#Find the year by year "In Minority" decisions for each judge
# Convert 'Event Date' column to datetime type
filtered_df_overtime['Event Date'] = pd.to_datetime(filtered_df_overtime['Event Date'])

# Extract the year from the 'Event Date' column
filtered_df_overtime['Year'] = filtered_df_overtime['Event Date'].dt.year

# Group by 'Judge Name' and 'Year', then calculate the ratio of "In Minority" 1s
judge_year_ratio = filtered_df_overtime.groupby(['Judge Name', 'Year'])['In Minority'].mean().reset_index()

# Rename the column to 'In Minority Ratio'
judge_year_ratio.rename(columns={'In Minority': 'In Minority Ratio'}, inplace=True)

# Display the resulting DataFrame
print(judge_year_ratio)
judge_year_ratio = judge_year_ratio.sort_values(by=['In Minority Ratio'], ascending=[False])
judge_year_ratio.to_csv('/Users/danielbrown/Desktop/fight_scores_judge_year_ratio.csv', index=False)


filtered_df = filtered_df_overtime


# In[872]:


import pandas as pd

# Assuming your dataframe is already loaded and named df

# Define a function to get top 10 judges with highest 'In Minority Ratio' for each year
def top_10_in_minority(df):
    return df.nlargest(10, 'In Minority Ratio')

# Apply the function to each group by year
top_10_in_minority_per_year = judge_year_ratio.groupby('Year').apply(top_10_in_minority)

# Reset the index
top_10_in_minority_per_year.reset_index(drop=True, inplace=True)

# Order the result by Year and 'In Minority Ratio' in descending order
top_10_in_minority_per_year_sorted = top_10_in_minority_per_year.sort_values(by=['Year', 'In Minority Ratio'], ascending=[True, False])

dfs = []
# Print the result
for year, group in top_10_in_minority_per_year_sorted.groupby('Year'):
    print(f"Year: {year}")
    print(group)
    print()
    group['Year'] = year  # Add Year column to each group
    dfs.append(group)


# In[875]:


top_10_in_minority_per_year_sorted.to_csv('/Users/danielbrown/Desktop/top_10_in_minority_per_year_sorted.csv', index=False)


# In[ ]:




