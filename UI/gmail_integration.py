"""
Gmail Integration Example for WorkEase
This file shows how to integrate Gmail API into your WorkEase application.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText

# Gmail API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

class GmailIntegration:
    """Gmail API Integration for WorkEase"""
    
    def __init__(self, credentials_path='credentials.json', token_path='gmail_token.pickle'):
        """Initialize Gmail integration
        
        Args:
            credentials_path: Path to OAuth credentials JSON file
            token_path: Path to save/load OAuth token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.user_email = None
        
    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0
        
        Returns:
            bool: True if authentication successful
        """
        creds = None
        
        # Load saved credentials if they exist
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Run OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        
        # Get user email
        profile = self.service.users().getProfile(userId='me').execute()
        self.user_email = profile['emailAddress']
        
        return True
    
    def get_messages(self, max_results=10, query='', label_ids=None):
        """Fetch messages from Gmail
        
        Args:
            max_results: Maximum number of messages to fetch
            query: Gmail search query (e.g., 'is:unread', 'from:user@example.com')
            label_ids: List of label IDs to filter by
        
        Returns:
            list: List of parsed message objects
        """
        try:
            # Get message list
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'q': query
            }
            
            if label_ids:
                params['labelIds'] = label_ids
            
            results = self.service.users().messages().list(**params).execute()
            messages = results.get('messages', [])
            
            # Get full message details
            detailed_messages = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Parse message
                parsed = self.parse_message(msg)
                detailed_messages.append(parsed)
            
            return detailed_messages
            
        except HttpError as error:
            print(f'Gmail API error: {error}')
            return []
    
    def get_unread_messages(self, max_results=50):
        """Get unread messages
        
        Args:
            max_results: Maximum number of unread messages
        
        Returns:
            list: List of unread message objects
        """
        return self.get_messages(max_results=max_results, query='is:unread')
    
    def parse_message(self, message):
        """Parse Gmail message to extract useful information
        
        Args:
            message: Raw message object from Gmail API
        
        Returns:
            dict: Parsed message with relevant fields
        """
        headers = message['payload']['headers']
        
        parsed = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'snippet': message.get('snippet', ''),
            'labels': message.get('labelIds', []),
            'date': '',
            'from': '',
            'from_email': '',
            'to': '',
            'subject': '',
            'body': '',
            'is_unread': 'UNREAD' in message.get('labelIds', [])
        }
        
        # Extract headers
        for header in headers:
            name = header['name'].lower()
            value = header['value']
            
            if name == 'date':
                parsed['date'] = value
            elif name == 'from':
                parsed['from'] = value
                # Extract email from "Name <email@example.com>" format
                if '<' in value and '>' in value:
                    parsed['from_email'] = value.split('<')[1].split('>')[0]
                else:
                    parsed['from_email'] = value
            elif name == 'to':
                parsed['to'] = value
            elif name == 'subject':
                parsed['subject'] = value
        
        # Extract body
        parsed['body'] = self._extract_body(message['payload'])
        
        return parsed
    
    def _extract_body(self, payload):
        """Extract email body from payload
        
        Args:
            payload: Message payload
        
        Returns:
            str: Email body text
        """
        body = ''
        
        if 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif 'parts' in part:
                    # Nested parts
                    body = self._extract_body(part)
                    if body:
                        break
        else:
            # Simple message
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def send_message(self, to, subject, body, thread_id=None):
        """Send an email message
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            thread_id: Optional thread ID for replies
        
        Returns:
            dict: Sent message object or None on error
        """
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_params = {
                'userId': 'me',
                'body': {'raw': raw}
            }
            
            if thread_id:
                send_params['body']['threadId'] = thread_id
            
            sent = self.service.users().messages().send(**send_params).execute()
            return sent
            
        except HttpError as error:
            print(f'Error sending message: {error}')
            return None
    
    def mark_as_read(self, message_id):
        """Mark a message as read
        
        Args:
            message_id: Message ID
        
        Returns:
            bool: True if successful
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error marking as read: {error}')
            return False
    
    def mark_as_unread(self, message_id):
        """Mark a message as unread
        
        Args:
            message_id: Message ID
        
        Returns:
            bool: True if successful
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error marking as unread: {error}')
            return False
    
    def delete_message(self, message_id):
        """Delete a message (move to trash)
        
        Args:
            message_id: Message ID
        
        Returns:
            bool: True if successful
        """
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return True
        except HttpError as error:
            print(f'Error deleting message: {error}')
            return False
    
    def test_connection(self):
        """Test Gmail API connection
        
        Returns:
            dict: Connection test results
        """
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'success': True,
                'email': profile['emailAddress'],
                'messages_total': profile['messagesTotal'],
                'threads_total': profile['threadsTotal']
            }
        except HttpError as error:
            return {
                'success': False,
                'error': str(error)
            }


# Example usage
if __name__ == "__main__":
    # Initialize Gmail integration
    gmail = GmailIntegration()
    
    print("🔐 Authenticating with Gmail...")
    if gmail.authenticate():
        print(f"✅ Authenticated as: {gmail.user_email}\n")
        
        # Test connection
        test = gmail.test_connection()
        if test['success']:
            print(f"📊 Account stats:")
            print(f"   Total messages: {test['messages_total']}")
            print(f"   Total threads: {test['threads_total']}\n")
        
        # Fetch unread messages
        print("📬 Fetching unread messages...")
        unread = gmail.get_unread_messages(max_results=5)
        print(f"Found {len(unread)} unread messages\n")
        
        for i, msg in enumerate(unread, 1):
            print(f"--- Message {i} ---")
            print(f"From: {msg['from']}")
            print(f"Subject: {msg['subject']}")
            print(f"Snippet: {msg['snippet'][:100]}...")
            print()
        
        # Example: Send a test email (commented out)
        # gmail.send_message(
        #     to="recipient@example.com",
        #     subject="Test from WorkEase",
        #     body="This is a test email from WorkEase!"
        # )
        
    else:
        print("❌ Authentication failed")
