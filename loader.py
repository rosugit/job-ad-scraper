import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

def gsheets_upload(dataframe):
    ### google sheets authorization
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    gcp_json = './auth/gs-auth.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gcp_json, scope)
    client = gspread.authorize(credentials)
    
    ### data upload
    worksheet = client.open('scraped-data').worksheet('main')
    worksheet.clear()
    set_with_dataframe(worksheet, dataframe)
    
    print(' >> Data uploaded to Google Sheets')