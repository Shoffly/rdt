import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

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
                            range="A1:h300052").execute()
values = result.get('values', [])



# Convert the array of arrays to a pandas DataFrame
df = pd.DataFrame(values, columns=['Transaction Date','Branch','Item Category','Item','Unit Price','Transaction Month','Quantity','Revenue'])
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
df['Revenue'] = pd.to_numeric(df['Revenue'])

dfn = df
#page contents
st.title("Data Chat")



OPENAI_API_KEY = "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"

llm = OpenAI(api_token=OPENAI_API_KEY)

pandas_ai = PandasAI(llm, verbose=True, conversational=True)

question = st.text_input('What would you like to know?')

if question:
    result = pandas_ai.run(dfn, prompt=question)
    print(result)
else:
    result = "Query your data"

st.info(f"{result}")

