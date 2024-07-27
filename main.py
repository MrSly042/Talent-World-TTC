
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
          "https://www.googleapis.com/auth/gmail.compose", 
          "https://www.googleapis.com/auth/gmail.labels",
         ]

with open('.env') as env:
    file_lines = env.read().split("\n")

client_secret = file_lines[0]

def main():

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
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

  try:
    service_drive = build("drive", "v3", credentials=creds)
    service_gmail = build("gmail", "v1", credentials=creds)

    # Call the APIs
    #check inbox block
    if True: #set condition for email being present
        
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

        #check for shift prefers...
        if True: #if match
           #send email
           message = EmailMessage()
           contents_of_email = "FULL NAME: INNOCENT ITOPA YAKUBU\nCUKA NUMBER: C010622\nTIME: 3:30PM TO 1:30AM 20TH OF JULY 2024\nSTATION: SPADINA\n\nRegards."
           message.set_content(contents_of_email)
           
           rec = input("Enter talent world email: ")
           fro = input("Enter your email: ") #innocentyakubu01@gmail.com
           message["To"] = rec
           
           message["From"] = fro
           message["Subject"] = "SELECTION OF SHIFTS"
           
           # encoded message
           encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
           
           create_message = {"raw": encoded_message}
           # pylint: disable=E1101
           send_message = (
              service_gmail.users()
              .messages()
              .send(userId="me", body=create_message)
              .execute()
              )

        else:
           pass
           
    
    else:
    #    time.sleep(2)
       pass

  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")

if __name__ == "__main__":
  main()