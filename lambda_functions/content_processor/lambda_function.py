import json
import boto3
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

# Environment variables
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-sonnet-4-20250514-v1:0')
PROCESSED_TABLE = os.environ.get('PROCESSED_TABLE', 'twitter-bot-processed-emails')
TWITTER_QUEUE_URL = os.environ.get('TWITTER_QUEUE_URL')

def generate_japanese_tweet(email_content):
    """Use Bedrock to generate Japanese tweet from email content"""
    
    prompt = f"""あなたは英語のメールを日本語のツイートに変換する専門家です。

以下のメールの内容を、魅力的で簡潔な日本語のツイート（280文字以内）に変換してください：

件名: {email_content['subject']}
本文: {email_content['body']}

要件：
- 自然な日本語で書く
- 重要な情報を保持する
- ツイッターに適したカジュアルなトーンを使う
- 絵文字は使用しない
- ハッシュタグを1-2個提案する

ツイート："""

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        tweet_text = response_body['content'][0]['text'].strip()
        
        # Ensure it's within Twitter's character limit
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
            
        return tweet_text
        
    except Exception as e:
        logger.error(f"Error generating tweet with Bedrock: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    Process emails from SQS queue and generate Japanese tweets.
    Only processes messages from the Gmail poller (no webhook support).
    """
    logger.info(f"Processing {len(event.get('Records', []))} messages")
    
    try:
        # Process each SQS message
        for record in event.get('Records', []):
            message_body = json.loads(record['body'])
            
            # Process message from gmail_poller
            email_id = message_body.get('email_id')
            
            if not email_id:
                logger.warning(f"Message missing email_id: {message_body}")
                continue
            
            # Check if already processed/posted
            table = dynamodb.Table(PROCESSED_TABLE)
            existing = table.get_item(Key={'email_id': email_id})
            
            if 'Item' in existing and existing['Item'].get('status') in ['queued_for_posting', 'posted']:
                logger.info(f"Email {email_id} already processed/posted, skipping")
                continue
            
            # Use the email content from the poller
            email_content = {
                'subject': message_body.get('subject', ''),
                'body': message_body.get('body', ''),
                'id': email_id
            }
            
            logger.info(f"Processing email: {email_content['subject']}")
            
            # Generate Japanese tweet
            tweet_text = generate_japanese_tweet(email_content)
            
            # Queue for Twitter posting
            if TWITTER_QUEUE_URL:
                sqs.send_message(
                    QueueUrl=TWITTER_QUEUE_URL,
                    MessageBody=json.dumps({
                        'tweet_text': tweet_text,
                        'email_id': email_id,
                        'original_subject': email_content['subject']
                    })
                )
            
            # Mark as processed
            table = dynamodb.Table(PROCESSED_TABLE)
            table.put_item(Item={
                'email_id': email_id,
                'processed_at': datetime.utcnow().isoformat(),
                'tweet_text': tweet_text,
                'status': 'queued_for_posting'
            })
            
            logger.info(f"Successfully processed email {email_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Processing complete')
        }
        
    except Exception as e:
        logger.error(f"Error processing messages: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }