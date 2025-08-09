import json
import boto3
import os
import logging
import base64
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
secrets_manager = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

# Environment variables
GMAIL_SECRET_NAME = os.environ.get('GMAIL_SECRET_NAME', 'twitter-bot/gmail-api')
STATE_TABLE = os.environ.get('STATE_TABLE', 'twitter-bot-app-state')
EMAIL_QUEUE_URL = os.environ.get('EMAIL_QUEUE_URL')
PROCESSED_TABLE = os.environ.get('PROCESSED_TABLE', 'twitter-bot-processed-emails')

def get_gmail_service():
    """Initialize Gmail API service with credentials from Secrets Manager"""
    secret = secrets_manager.get_secret_value(SecretId=GMAIL_SECRET_NAME)
    creds_data = json.loads(secret['SecretString'])
    
    creds = Credentials(
        token=None,
        refresh_token=creds_data['refresh_token'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        token_uri='https://oauth2.googleapis.com/token'
    )
    
    return build('gmail', 'v1', credentials=creds)

def get_last_check_time():
    """Get the last time we checked Gmail from DynamoDB"""
    table = dynamodb.Table(STATE_TABLE)
    try:
        response = table.get_item(Key={'key': 'gmail_last_check'})
        if 'Item' in response:
            return response['Item'].get('timestamp')
    except Exception as e:
        logger.warning(f"Could not get last check time: {e}")
    
    # Default to 1 hour ago if no record exists
    return (datetime.utcnow() - timedelta(hours=1)).isoformat()

def save_last_check_time(timestamp):
    """Save the last check time to DynamoDB"""
    table = dynamodb.Table(STATE_TABLE)
    table.put_item(Item={
        'key': 'gmail_last_check',
        'timestamp': timestamp
    })

def lambda_handler(event, context):
    """
    Poll Gmail for new messages and queue them for processing.
    This function should be triggered by CloudWatch Events every 5 minutes.
    """
    logger.info("Starting Gmail poll")
    
    try:
        # Initialize Gmail service
        service = get_gmail_service()
        
        # Get the last check time
        last_check = get_last_check_time()
        last_check_timestamp = int(datetime.fromisoformat(last_check.replace('Z', '')).timestamp())
        
        # Query for messages received after last check
        # Gmail expects timestamp in seconds since epoch
        query = f'after:{last_check_timestamp} to:t.speekenbrink+xposts@gmail.com'
        
        logger.info(f"Searching for messages with query: {query}")
        
        # List messages
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        logger.info(f"Found {len(messages)} new messages")
        
        processed_count = 0
        
        for msg in messages:
            msg_id = msg['id']
            
            # Check if already processed
            processed_table = dynamodb.Table(PROCESSED_TABLE)
            existing = processed_table.get_item(Key={'email_id': msg_id})
            
            if 'Item' in existing:
                logger.info(f"Message {msg_id} already processed, skipping")
                continue
            
            # Get the full message
            message = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract basic info for logging
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            logger.info(f"Processing message: {subject} from {from_addr}")
            
            # Extract email content
            def get_body(payload):
                body = ''
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data', '')
                            if data:
                                body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif payload['body'].get('data'):
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                return body
            
            body = get_body(message['payload'])
            
            # Queue for processing
            if EMAIL_QUEUE_URL:
                message_data = {
                    'email_id': msg_id,
                    'subject': subject,
                    'body': body[:1000],  # Limit body size
                    'from': from_addr,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                sqs.send_message(
                    QueueUrl=EMAIL_QUEUE_URL,
                    MessageBody=json.dumps(message_data)
                )
                
                logger.info(f"Queued message {msg_id} for processing")
                processed_count += 1
            
            # Mark as being processed to avoid duplicates
            processed_table.put_item(Item={
                'email_id': msg_id,
                'status': 'queued',
                'queued_at': datetime.utcnow().isoformat(),
                'subject': subject
            })
        
        # Save the current time as last check
        save_last_check_time(datetime.utcnow().isoformat())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'messages_found': len(messages),
                'messages_processed': processed_count
            })
        }
        
    except Exception as e:
        logger.error(f"Error polling Gmail: {str(e)}")
        raise