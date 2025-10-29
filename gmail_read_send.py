from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os

# Gmail API scope (read, send, manage)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Handles authentication and returns Gmail API service client."""
    creds = None
    # Use token.json if already authorized
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service


def read_latest_emails(service, num=5):
    """Read latest Gmail messages."""
    results = service.users().messages().list(userId='me', maxResults=num).execute()
    messages = results.get('messages', [])
    if not messages:
        print("No emails found.")
    else:
        print(f"📬 Last {num} Emails:")
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg_data.get('snippet', '')
            print(f"- {snippet}")


def send_email(service, to, subject, message_text):
    """Send a simple text email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    sent_msg = service.users().messages().send(userId='me', body=body).execute()
    print(f"✅ Email sent to {to} (Message ID: {sent_msg['id']})")


if __name__ == '__main__':
    # Step 1: Authenticate
    service = authenticate_gmail()

    # Step 2: Read latest emails
    read_latest_emails(service)

    # Step 3: Send test email
    send_email(service, "alishbat2012@gmail.com", "Test Automation", "This email was sent by an automated script.")
