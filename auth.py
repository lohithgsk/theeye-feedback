from __future__ import print_function
import secrets
from googleapiclient.discovery import build 
from google.oauth2 import service_account
import base64, json, os


SCOPES = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]

creds = {
  "type": "service_account",
  "project_id": "velvety-rookery-434912-c2",
  "private_key_id": "b3e44bb0ed10c2910fa103499a4a220649f124a0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDlYP7T7BesYny9\n/DkHD1I5EpVkmlgb1c8rIRcJKHVYhqaWgJaoNKqT/OPeEcs0YlJLb+lXqrg7Y2RR\nGy4zNFBXMUwKch87Lo716zl9nDxZxNGHnWS0NgD49XDqVvZ1wqoPb5b0YFu7mb59\nNMMAWkGbOnCq/LzMz+7ERdx8A+bE+6o2Ld/pP17epsLcHqi2IlbY4996bIE0Bo2L\nPcs7nQNlY8b5IsG2ZtrIqhmoGnc/QXmMh0SsC6UfpFS2DGq0f/LoAP23pDNECgAe\nzfB4DrvKMxr6Mw6q2XB8hXUfGMNQYgywTwPdoFSQaRu6/hFdfMYes4saQLvU0bTP\nmhdB8mHXAgMBAAECggEAAUm35OaPOmlIsJjCdr6nrkrPUCcN/FztnermPvz3oUgL\nVSogUtRjJpOsmZATzKOgz9L6qXiZ0vN3Q5u3D4dtDW7fKjBcRNPLAqsOn/I9Nw/I\n8hKc9+ZaPQacVdkRaZ7dDgrrAB9cEz9yReTc4V2i4kw9rZ3p0iVpkpmF3MccUhKH\nv3xx7OgMhftaTrVpH6V7wHsPZHqyNKVV9lYo3xLgiSRXXz2Omia3lv+An3feschd\nsTFFdl68jKTsmTZ3pBbm0iMSRt+dDogpZrXN4Ssg6bKXmugXnaohVifePjvmjmaa\nDqpM6s40UYH7vY4lum3XJx0cw3X3OrN+Cl0uYESZKQKBgQD5vUD3D0qQhcJqRJDL\n1ojFSFDAE+PFgAMbQpCvxttaKrFqp4GPyvXDY9XCvJhpebF6doq4KVHRPJw4nCGm\nPtlC/6IcAM5MYDGmgPXITpozdimzxUvZ9qLkqCjow64Hi5rvu7YLjoln4+vEUWBk\nuVjW12zvBcggZkVsm/SPjZEjuQKBgQDrIRNEYYAVoc/oskSBHwP+wWVGsTBZkRJO\nxEHQzyhAOyvJThIxsWWp0bn0z1MgRXgi1NLPXf8hVtvXQd9QyeZiCK2nnAa1caod\nMiwulBCCwtQ4Ij3uSjKW88pQ/YfvEp331ngLqpFIf3vktYrikFkKv5XrcdTj1gO9\n9W18AJSaDwKBgAW0XfyGu+RLOeKliE0vrFYdTcLlcWl8gBWqUpXBTBdmLEFMbDg1\noaGB8UsOdcjK/9PVS1vjjbviz4q3fklG3D2ciz5qgkvaUqgEABlAOmN8in1Rv2bO\nLHBeqviOJ7aCaNqbBhCDg/38hdEpLrN+TFoz94gKMMUUsPdHJLH2wN75AoGAWHdf\nWnEc0gbJxRGduL9Er4twYYK1YF2296/b24a17ETXGqynJ89JIvXn83Y2HoREyUYt\n8xu4rICTwo/kR+9PIT+GpvOLiqUzjjycZwIKnEhVtLEdgBSmqCkdzA84H/lvOhqV\nnD4W36InqUus78XD2sluzOFNalPRoJ1BDlDhmH0CgYEAirHQc8EcbEJgIngN7LqI\nOsuETtPRd7ELRu7bLLQPF0nNy+chTVavgNK16/+/xo1ND/fEtjA22BMld8eSVrug\nOEQu8HnzG5fysfhmKJulRrmJVAuY52sqLzjFpiUH/b2VeZzcliZxn3e6m2sHwA4Q\n4zMFLAgr7qlx5I7IfQndOPU=\n-----END PRIVATE KEY-----\n",
  "client_email": "tm-website@velvety-rookery-434912-c2.iam.gserviceaccount.com",
  "client_id": "118316650637376697599",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tm-website%40velvety-rookery-434912-c2.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(creds, scopes=SCOPES)
spreadsheet_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
