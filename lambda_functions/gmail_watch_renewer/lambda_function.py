import json
import boto3
import os
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger()
logger.setLevel(logging.INFO)

secrets_manager = boto3.client('secretsmanager')

def lambda_handler(event, context):
    """
    Automatically renew Gmail watch subscription.
    Run this every 6 days via CloudWatch Events/EventBridge.
    """
    
    try:
        # Get Gmail credentials from Secrets Manager
        secret = secrets_manager.get_secret_value(SecretId='twitter-bot/gmail-api')
        creds_data = json.loads(secret['SecretString'])
        
        # Create credentials
        creds = Credentials(
            token=None,
            refresh_token=creds_data['refresh_token'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            token_uri='https://oauth2.googleapis.com/token'
        )
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Set up watch
        watch_request = {
            'labelIds': ['INBOX'],
            'topicName': 'projects/twitter-bot-gmail/topics/gmail-notifications'
        }
        
        response = service.users().watch(userId='me', body=watch_request).execute()
        
        logger.info(f"Successfully renewed Gmail watch. Expires: {response.get('expiration')}")
        
        # Convert expiration to readable format
        exp_timestamp = int(response.get('expiration')) / 1000
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Gmail watch renewed',
                'expires': exp_datetime.isoformat(),
                'historyId': response.get('historyId')
            })
        }
        
    except Exception as e:
        logger.error(f"Failed to renew Gmail watch: {str(e)}")
        raise