import time
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from services.email_monitor_service import PhishingCoordinator, EmailAnalyzer
from services.ml_integration_service import MLIntegrationService
from models.db_models import ScanModel
from utils.db import DatabaseService

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailMonitor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.ml_service = MLIntegrationService()
        self.creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def _get_credentials(self):
        # In a real app, these tokens would be stored in the DB per user
        token_path = f'tokens/user_{self.user_id}_token.json'
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def start_monitoring(self):
        print(f"Starting PhishGuard Gmail Monitor for User: {self.user_id}")
        last_history_id = None
        
        while True:
            try:
                # Poll for new messages (In production, use Gmail Webhooks/Watch)
                results = self.service.users().messages().list(userId='me', q='is:unread').execute()
                messages = results.get('messages', [])

                for msg in messages:
                    self._process_message(msg['id'])
                    
                time.sleep(30) # Poll every 30 seconds
            except Exception as e:
                print(f"Monitor Error: {e}")
                time.sleep(60)

    def _process_message(self, msg_id):
        # Fetch full message
        message = self.service.users().messages().get(userId='me', id=msg_id).execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        
        # Extract body
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body = base64.urlsafe_b64decode(data).decode()
        else:
            data = payload['body'].get('data', '')
            body = base64.urlsafe_b64decode(data).decode()

        # Coordinate Analysis
        report = PhishingCoordinator.analyze_email_full(sender, subject, body, self.ml_service)
        
        # Save to MongoDB
        ScanModel.log_scan(self.user_id, 'email_monitor', sender, report)
        
        if report['analysis']['is_phishing']:
            print(f"ALERT: Phishing detected in email from {sender}!")
            # Trigger further notification logic (Push/Email)

        # Mark as read/processed so we don't re-scan
        self.service.users().messages().batchModify(
            userId='me',
            body={'ids': [msg_id], 'removeLabelIds': ['UNREAD']}
        ).execute()
