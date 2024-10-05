from __future__ import print_function
import secrets
from googleapiclient.discovery import build 
from google.oauth2 import service_account
import base64, json, os


SCOPES = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]

try:
    secret_json = os.getenv('GOOGLE_CREDS')

    if secret_json==None: raiseError()

    base64_bytes = secret_json.encode("ascii")

    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")

    creds = json.loads(sample_string)
except:
    with open("../credentials.json") as f:
        creds = json.load(f)

credentials = service_account.Credentials.from_service_account_info(creds, scopes=SCOPES)
spreadsheet_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)