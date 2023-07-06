import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import matplotlib.pyplot as plt

#google sheet connection
SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials= None

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1AE4wMKDPV0VLS-qV9U4d5DvhSP560HrGW8q3yYnhJsQ'

service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="A1:h336219").execute()
values = result.get('values', [])



# Convert the array of arrays to a pandas DataFrame
df = pd.DataFrame(values, columns=['Date','Outlet','Category','Items','Price','State','Quantity','Revenue'])
# Branch selection
branch_select = df['Outlet'].unique()
store = st.sidebar.selectbox("Pick the branch", branch_select)

#convert start and end dates to variable dates for overview
st.sidebar.write('''Pick Main Dates''')
sd = pd.to_datetime(st.sidebar.date_input('Start Date'))
ed = pd.to_datetime(st.sidebar.date_input('End Date'))


# Convert the 'Date' column to datetime data type
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = pd.to_datetime(df['Date'])



# Filter rows based on dates using .query() method
fil_df = df[(df['Date'] >= sd) & (df['Date'] <= ed) & (df['Outlet'].isin([store]))]

# comparison date section
st.sidebar.write('''Pick Comparison Dates''')
sd_c = pd.to_datetime(st.sidebar.date_input('Start comparison Date'))
ed_c = pd.to_datetime(st.sidebar.date_input('End comparison Date'))

#Filter the datafrane based on the comparison
fil_df_c = df[(df['Date'] >= sd_c) & (df['Date'] <= ed_c) & (df['Outlet'].isin([store]))]
#page contents
st.title(f"{store} Analysis")
# Display the value in the subheader using Markdown formatting
st.write(f" This is a deep dive in {store} for the dates between {sd} and {ed}.")

# Revenue metric
# Convert the 'Price' column to numeric data type
fil_df['Revenue'] = pd.to_numeric(fil_df['Revenue'])

# Sum the numbers in the 'Price' column
total_price = fil_df['Revenue'].sum()

# Format the revenue metric
formatted_revenue = "{:.1f}".format(total_price)
if total_price >= 1000:
    formatted_revenue = "{:,.1f}k".format(total_price)

# Transaction metric
# Convert the 'Price' column to numeric data type
fil_df['Revenue'] = pd.to_numeric(fil_df['Revenue'])

# Sum the numbers in the 'Price' column
total_tcs = fil_df['Revenue'].count()
formatted_tc = total_tcs

# Format the tcs metric
if total_tcs >= 1000:
    formatted_tc = "{:,.1f}k".format(total_tcs)

# the comparison metrics are here boi
# Comparison Revenue metric
# Convert the 'Price' column to numeric data type
fil_df_c['Revenue'] = pd.to_numeric(fil_df_c['Revenue'])

# Sum the numbers in the 'Price' column
total_price_c = fil_df_c['Revenue'].sum()

revenue_c = total_price - total_price_c
# Comparison Transaction metric
# Convert the 'Price' column to numeric data type
fil_df_c['Revenue'] = pd.to_numeric(fil_df_c['Revenue'])

# Sum the numbers in the 'Price' column
total_tc_c = fil_df_c['Revenue'].count()

tc_c = total_tcs - total_tc_c
# Use columns layout manager
col1, col2 = st.columns(2)

# Display the metrics in separate columns
col1.metric(label="Revenue",value= formatted_revenue, delta= "{:,.1f}".format(revenue_c))
col2.metric(label="Transactions", value=formatted_tc, delta= "{:,.1f}".format(tc_c))
col1.metric(label="Average order value", value="{:,.1f}".format(total_price/ total_tcs), delta= "{:,.1f}".format(revenue_c/tc_c))

# Calculate the total sales for each item
Sales_mix= fil_df.groupby('Items')['Revenue'].sum()

# Plot the bar chart
st.write('''
Sales by items
''')
st.bar_chart(Sales_mix)

# Diagnostic section
st.write('''
## Diagnostic Section
''')
# Calculate the total sales for each item
Sales_mix_c= fil_df_c.groupby('Items')['Revenue'].sum()

# Merge the DataFrames based on the 'ID' column
merged_Salesmix = pd.merge(Sales_mix, Sales_mix_c, on='Items', how='outer')

# Replace None values in 'ColumnA' with zero
merged_Salesmix['Revenue_x'].fillna(0, inplace=True)
merged_Salesmix['Revenue_y'].fillna(0, inplace=True)

#Calculate variance
merged_Salesmix['Variance'] = merged_Salesmix['Revenue_x'] - merged_Salesmix['Revenue_y']

#Display the diagnostic Dataframe
st.write('''
Overview
''')
st.dataframe(merged_Salesmix)

# Create a new DataFrame with only positive variance items
negative_variance_df = merged_Salesmix[merged_Salesmix['Variance'] < 0]

st.write('''
This store's sales dropped in the following items
''')
st.dataframe(negative_variance_df)

# Create a new DataFrame with only negative revenue stores
positive_variance_df = merged_Salesmix[merged_Salesmix['Variance'] >= 0]

st.write('''
This store's sales increased or remained stable in the following items
''')
st.dataframe(positive_variance_df)

