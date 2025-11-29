"""
AutoReturn Gmail Automation

Actions available:

1. List unread messages
2. List all messages
3. Read a message
4. Reply to a message
5. Send new email
6. Delete a message
7. Mark a message as unread
8. Search messages
9. Create Draft
10. Schedule Email
11. Exit
12. View Drafts
13. Send Draft manually

"""

import os
import json
import time
import base64
from email import message_from_bytes
from email.mime.text import MIMEText
import threading
from datetime import datetime

from plyer import notification
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ------------------------- CONFIG -------------------------
TOKEN_PATH = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"
POLL_INTERVAL = 5
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",  # read emails
    "https://www.googleapis.com/auth/gmail.modify",    # mark read/unread, delete
    "https://www.googleapis.com/auth/gmail.send",      # send emails
    "https://www.googleapis.com/auth/gmail.compose"    # create drafts, send
]

# ------------------------- CUSTOM EXCEPTION -------------------------
class GmailServiceError(Exception):
    pass

# ------------------------- MESSAGE PARSER -------------------------
class MessageParser:
    @staticmethod
    def decode_message(payload):
        try:
            data = payload.get("body", {}).get("data")
            if data:
                decoded_bytes = base64.urlsafe_b64decode(data)
                email_msg = message_from_bytes(decoded_bytes)
                return email_msg.get_payload()

            parts = payload.get("parts", [])
            if parts:
                for part in parts:
                    mime_type = part.get("mimeType", "")
                    if mime_type == "text/plain":
                        data = part.get("body", {}).get("data")
                        if data:
                            return base64.urlsafe_b64decode(data).decode("utf-8")
                    elif mime_type.startswith("multipart/"):
                        text = MessageParser.decode_message(part)
                        if text:
                            return text
            return "(No Content)"
        except Exception as e:
            return f"(Failed to parse message: {e})"

    @staticmethod
    def extract_header(headers, name):
        for h in headers:
            if h["name"].lower() == name.lower():
                return h["value"]
        return "Unknown"

# ------------------------- POPUP MANAGER -------------------------
class PopupManager:
    @staticmethod
    def show(title, message):
        try:
            notification.notify(title=title, message=message, timeout=8)
        except Exception:
            pass

# ------------------------- OAUTH MANAGER -------------------------
class OAuthManager:
    def __init__(self):
        self.creds = None

    def load_or_generate_token(self):
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "r") as f:
                data = json.load(f)
                self.creds = Credentials.from_authorized_user_info(data, SCOPES)
                print("[OAuth] Loaded existing token.")
                return True

        if not os.path.exists(CLIENT_SECRET_FILE):
            print(f"[OAuth] ERROR: {CLIENT_SECRET_FILE} not found!")
            print("\n=== Beginner Setup Instructions ===")
            print("1. Open https://console.cloud.google.com/apis/credentials")
            print("2. Click 'Create Credentials' -> 'OAuth Client ID'")
            print("3. Select 'Desktop App', name it, click 'Create'")
            print("4. Download JSON and save as 'client_secret.json'")
            print("5. Run this script again")
            return False

        print("[OAuth] No token found. Running authorization flow...")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            self.creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as f:
                f.write(self.creds.to_json())
            print("[OAuth] Token generated and saved as token.json\n")
            return True
        except Exception as e:
            print(f"[OAuth] Failed to generate token: {e}")
            return False

# ------------------------- GMAIL SERVICE -------------------------
class GmailService:
    def __init__(self, creds):
        self.service = build("gmail", "v1", credentials=creds)

    def list_messages(self, query="", max_results=20):
        try:
            res = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
            return res.get("messages", [])
        except Exception as e:
            print(f"[Error] Failed to list messages: {e}")
            return []

    def read_message(self, msg_id):
        try:
            msg = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            headers = msg["payload"]["headers"]
            body = MessageParser.decode_message(msg["payload"])
            snippet = (body[:100] + "...") if body and len(body) > 100 else (body or "(No Content)")
            return {
                "id": msg_id,
                "from": MessageParser.extract_header(headers, "From") or "(Unknown)",
                "subject": MessageParser.extract_header(headers, "Subject") or "(No Subject)",
                "body": body or "(No Content)",
                "snippet": snippet,
                "threadId": msg.get("threadId")
            }
        except Exception as e:
            print(f"[Warning] Failed to read message {msg_id}: {e}")
            return {
                "id": msg_id,
                "from": "(Error)",
                "subject": "(Error)",
                "body": "(Error reading message)",
                "snippet": "(Error)",
                "threadId": None
            }

    def mark_as_read(self, msg_id):
        try:
            self.service.users().messages().modify(
                userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
        except Exception as e:
            print(f"[Error] Could not mark as read: {e}")

    def mark_as_unread(self, msg_id):
        try:
            self.service.users().messages().modify(
                userId="me", id=msg_id, body={"addLabelIds": ["UNREAD"]}
            ).execute()
        except Exception as e:
            print(f"[Error] Could not mark as unread: {e}")

    def send_email(self, to, subject, message):
        msg = MIMEText(message)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return self.service.users().messages().send(userId="me", body={"raw": raw}).execute()

    def reply(self, thread_id, to, message):
        msg = MIMEText(message)
        msg["to"] = to
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return self.service.users().messages().send(
            userId="me", body={"raw": raw, "threadId": thread_id}
        ).execute()

    def delete_message(self, msg_id):
        try:
            self.service.users().messages().delete(userId="me", id=msg_id).execute()
        except Exception as e:
            print(f"[Error] Could not delete message: {e}")

    # ---------------- Draft feature ----------------
    def create_draft(self, to, subject, message):
        msg = MIMEText(message)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        body = {"message": {"raw": raw}}
        draft = self.service.users().drafts().create(userId="me", body=body).execute()
        print(f"[Info] Draft created with ID: {draft['id']}")
        return draft['id']

    def list_drafts(self):
        try:
            res = self.service.users().drafts().list(userId="me").execute()
            drafts = res.get("drafts", [])
            if not drafts:
                print("[Info] No drafts found.")
                return []
            print("Drafts:")
            for idx, d in enumerate(drafts, 1):
                draft_msg = self.service.users().drafts().get(userId="me", id=d["id"]).execute()
                headers = draft_msg["message"]["payload"]["headers"]
                subject = MessageParser.extract_header(headers, "Subject")
                to = MessageParser.extract_header(headers, "To")
                print(f"{idx}. ID: {d['id']}, To: {to}, Subject: {subject}")
            return drafts
        except Exception as e:
            print(f"[Error] Failed to list drafts: {e}")
            return []

    def send_draft(self, draft_id):
        try:
            sent_msg = self.service.users().drafts().send(userId="me", body={"id": draft_id}).execute()
            print(f"[Info] Draft sent: Message ID {sent_msg['id']}")
            return sent_msg
        except Exception as e:
            print(f"[Error] Failed to send draft: {e}")

    # ---------------- Schedule via draft ----------------
    def schedule_email(self, to, subject, message, send_time: datetime):
        delay = (send_time - datetime.now()).total_seconds()
        if delay <= 0:
            print("[Error] Scheduled time must be in the future.")
            return
        draft_id = self.create_draft(to, subject, message)
        print(f"[Info] Email scheduled to be sent at {send_time} using draft {draft_id}")

        def send_later():
            time.sleep(delay)
            self.send_draft(draft_id)
            print(f"[Info] Scheduled email sent to {to} at {datetime.now()}")

        threading.Thread(target=send_later, daemon=True).start()

# ------------------------- GMAIL LISTENER -------------------------
class GmailListener:
    def __init__(self, gmail_service, popup_manager):
        self.gmail = gmail_service
        self.popup = popup_manager
        self.seen_ids = set()

    def start(self):
        while True:
            messages = self.gmail.list_messages(query="is:unread", max_results=5)
            for msg in messages:
                if msg["id"] not in self.seen_ids:
                    details = self.gmail.read_message(msg["id"])
                    popup_text = f"From: {details['from']}\nSubject: {details['subject']}\n{details['snippet']}"
                    self.popup.show("New Email", popup_text)
                    self.seen_ids.add(msg["id"])
            time.sleep(POLL_INTERVAL)

# ------------------------- MENU SYSTEM -------------------------
def menu(gmail_service):
    message_ids = []

    while True:
        print("\n==== AutoReturn Gmail Menu ====")
        print("1. List unread messages")
        print("2. List all messages")
        print("3. Read a message")
        print("4. Reply to a message")
        print("5. Send new email")
        print("6. Delete a message")
        print("7. Mark a message as unread")
        print("8. Search messages")
        print("9. Create Draft")
        print("10. Schedule Email")
        print("11. Exit")
        print("12. View Drafts")
        print("13. Send Draft manually")
        choice = input("Enter your choice: ").strip()

        if choice in ["1", "2", "8"]:
            query = ""
            if choice == "1":
                query = "is:unread"
            elif choice == "8":
                query = input("Enter search query: ").strip()
            messages = gmail_service.list_messages(query=query, max_results=20)
            if not messages:
                print("No messages found.")
                message_ids = []
            else:
                print("Messages:")
                message_ids = []
                for idx, msg in enumerate(messages, 1):
                    details = gmail_service.read_message(msg["id"])
                    print(f"{idx}. From: {details['from']}, Subject: {details['subject']}")
                    message_ids.append(msg["id"])

        elif choice == "3":
            if not message_ids:
                print("No messages to read. Please list messages first.")
                continue
            num = input(f"Enter message number (1-{len(message_ids)}): ").strip()
            if not num.isdigit() or int(num) < 1 or int(num) > len(message_ids):
                print("Invalid number.")
                continue
            msg_id = message_ids[int(num)-1]
            details = gmail_service.read_message(msg_id)
            print(f"From: {details['from']}\nSubject: {details['subject']}\nBody:\n{details['body']}")

        elif choice == "4":
            if not message_ids:
                print("No messages to reply. Please list messages first.")
                continue
            num = input(f"Enter message number to reply (1-{len(message_ids)}): ").strip()
            if not num.isdigit() or int(num) < 1 or int(num) > len(message_ids):
                print("Invalid number.")
                continue
            msg_id = message_ids[int(num)-1]
            details = gmail_service.read_message(msg_id)
            reply_text = input("Enter reply message: ")
            gmail_service.reply(details["threadId"], details["from"], reply_text)
            print("[Info] Reply sent.")

        elif choice == "5":
            to = input("Recipient email: ")
            subject = input("Subject: ")
            body = input("Message body: ")
            gmail_service.send_email(to, subject, body)
            print("[Info] Email sent.")

        elif choice == "6":
            if not message_ids:
                print("No messages to delete. Please list messages first.")
                continue
            num = input(f"Enter message number to delete (1-{len(message_ids)}): ").strip()
            if not num.isdigit() or int(num) < 1 or int(num) > len(message_ids):
                print("Invalid number.")
                continue
            msg_id = message_ids[int(num)-1]
            gmail_service.delete_message(msg_id)
            print("[Info] Message deleted.")

        elif choice == "7":
            if not message_ids:
                print("No messages to mark as unread. Please list messages first.")
                continue
            num = input(f"Enter message number to mark as unread (1-{len(message_ids)}): ").strip()
            if not num.isdigit() or int(num) < 1 or int(num) > len(message_ids):
                print("Invalid number.")
                continue
            msg_id = message_ids[int(num)-1]
            gmail_service.mark_as_unread(msg_id)
            print("[Info] Message marked as unread.")

        elif choice == "9":
            to = input("Recipient email for draft: ")
            subject = input("Draft subject: ")
            body = input("Draft body: ")
            gmail_service.create_draft(to, subject, body)

        elif choice == "10":
            to = input("Recipient email: ")
            subject = input("Subject: ")
            body = input("Message body: ")
            send_time_str = input("Enter send time (YYYY-MM-DD HH:MM:SS): ")
            try:
                send_time = datetime.strptime(send_time_str, "%Y-%m-%d %H:%M:%S")
                gmail_service.schedule_email(to, subject, body, send_time)
            except Exception as e:
                print(f"[Error] Invalid time format: {e}")

        elif choice == "12":
            gmail_service.list_drafts()

        elif choice == "13":
            draft_id = input("Enter draft ID to send: ").strip()
            gmail_service.send_draft(draft_id)

        elif choice == "11":
            print("Exiting...")
            break

        else:
            print("Invalid choice, try again.")

# ------------------------- MAIN -------------------------
def main():
    print("\n=== AutoReturn Gmail Automation ===\n")
    print("Note: For first-time setup, follow beginner instructions.\n")

    oauth = OAuthManager()
    if not oauth.load_or_generate_token():
        print("OAuth token setup failed. Exiting...")
        return

    gmail = GmailService(oauth.creds)

    # listener = GmailListener(gmail, PopupManager())
    # threading.Thread(target=listener.start, daemon=True).start()

    menu(gmail)

if __name__ == "__main__":
    main()
