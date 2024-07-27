import base64
import os.path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import io
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly", 
          "https://www.googleapis.com/auth/gmail.modify",
         ]

with open('.env') as env:
    file_lines = env.read().split("\n")

client_secret = file_lines[0]
person_name = file_lines[1]
cuka_no = file_lines[2]
receiver = file_lines[3]

def get_services():
  creds = None

  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES )
      creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
  with open("token.json", "w") as token:
    token.write(creds.to_json())

  service_drive = build("drive", "v3", credentials=creds)
  service_gmail = build("gmail", "v1", credentials=creds)

  tup = (service_drive, service_gmail)

  return tup
  
def read_saved_date():
  filename = 'latest_email.txt'
  if not os.path.exists(filename):
      return None
  
  with open(filename, 'r') as f:
      lines = f.readlines()
      if lines:
          return lines[0].strip().split("Date: ")[1]
      
  return None

def save_email_data(email_date, email_body):
    filename = 'latest_email.txt'
    with open(filename, 'w') as f:
        f.write(f"Date: {email_date}\n")
        f.write("Body:\n")
        f.write(email_body)

def get_latest_email(service, query):
    results = service.users().messages().list(userId='me', q=query, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    if not messages:
        return None
    latest_msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=latest_msg_id).execute()
    return msg

def download_file(service_drive):
  results = (
            service_drive.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
  
  items = results.get("files", [])
  if not items:
      print("No files found.")
      return
  
  user_inp = input("Enter the file name: ")
  for item in items:
  
      if item['name'] == user_inp:
          print(f"{item['name']} ({item['id']})")
          break

  file_id = item["id"]
  request = service_drive.files().get_media(fileId=file_id)
  file = io.BytesIO()

  downloader = MediaIoBaseDownload(file, request)
  done = False

  while not done :
      status, done = downloader.next_chunk()
      print(f"Download {int(status.progress() * 100)}.")

  file.seek(0)
  with open(item['name'], 'wb') as f:
      f.write(file.read())

def send_mail(service_gmail):
  message = EmailMessage()
  contents_of_email = f"FULL NAME: {person_name}\nCUKA NUMBER: {cuka_no}\nTIME: 3:30PM TO 1:30AM 20TH OF JULY 2024\nSTATION: SPADINA\n\nRegards."
  message.set_content(contents_of_email)
  
  #innocentyakubu01@gmail.com
  message["To"] = receiver
  
  message["From"] = "me"
  message["Subject"] = "SELECTION OF SHIFTS"
  
  # encoded message
  encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
  
  create_message = {"raw": encoded_message}
  send_message = (
    service_gmail.users()
    .messages()
    .send(userId="me", body=create_message)
    .execute()
    )

def check_email(service_gmail):
  last_date = read_saved_date()
  query = 'subject:SELECTION OF SHIFTS'
  if last_date:
      query += f' after:{last_date}'
  
  email = get_latest_email(service_gmail, query)
  if email:
      headers = email['payload']['headers']
      for header in headers:
          if header['name'] == 'Date':
              email_date = header['value']
              break
      email_body = base64.urlsafe_b64decode(email['payload']['body']['data']).decode('utf-8')
      save_email_data(email_date, email_body)
      print(f"Email saved with date: {email_date}")

def sheet_examine():
   pass # go through shared file

def main():  
  try:
    if True:
       
      service_drive, service_gmail = get_services()
      check_email(service_gmail = service_gmail)
      if True:
         download_file(service_drive = service_drive)
         sheet_examine()
         
         if True:
            send_mail(service_gmail = service_gmail)

         else:
            pass # No shift suit
         
      else:
         pass #Email doesn't match

    else:
       pass # if time interval is too small

  except HttpError as error:
    print(f"An error occurred: {error}")

if __name__ == "__main__":
  main()