import json
import boto3
import os
import logging
import tweepy
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
secrets_manager = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')

# Environment variables
TWITTER_SECRET_NAME = os.environ.get('TWITTER_SECRET_NAME', 'twitter-bot/twitter-api')
PROCESSED_TABLE = os.environ.get('PROCESSED_TABLE', 'twitter-bot-processed-emails')

def get_twitter_client():
    """Initialize Twitter client with credentials from Secrets Manager"""
    try:
        # Get credentials from Secrets Manager
        secret = secrets_manager.get_secret_value(SecretId=TWITTER_SECRET_NAME)
        creds = json.loads(secret['SecretString'])
        
        # Initialize Tweepy client
        client = tweepy.Client(
            consumer_key=creds['api_key'],
            consumer_secret=creds['api_secret'],
            access_token=creds['access_token'],
            access_token_secret=creds['access_token_secret']
        )
        
        return client
        
    except Exception as e:
        logger.error(f"Error initializing Twitter client: {str(e)}")
        raise

def post_tweet(client, tweet_text):
    """Post tweet to Twitter"""
    try:
        response = client.create_tweet(text=tweet_text)
        
        if response.data:
            tweet_id = response.data['id']
            logger.info(f"Successfully posted tweet: {tweet_id}")
            return tweet_id
        else:
            raise Exception("No data in Twitter response")
            
    except tweepy.TooManyRequests:
        logger.error("Twitter rate limit exceeded")
        raise
    except tweepy.Forbidden as e:
        logger.error(f"Twitter forbidden error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error posting tweet: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    Post tweets to Twitter from SQS queue
    """
    logger.info(f"Processing event: {json.dumps(event)}")
    
    try:
        # Initialize Twitter client
        twitter_client = get_twitter_client()
        
        # Get DynamoDB table
        table = dynamodb.Table(PROCESSED_TABLE)
        
        # Process each SQS message
        for record in event.get('Records', []):
            message_body = json.loads(record['body'])
            
            tweet_text = message_body.get('tweet_text')
            email_id = message_body.get('email_id')
            
            if not tweet_text:
                logger.error("No tweet text in message")
                continue
            
            try:
                # Post the tweet
                tweet_id = post_tweet(twitter_client, tweet_text)
                
                # Update DynamoDB with success
                table.update_item(
                    Key={'email_id': email_id},
                    UpdateExpression='SET #status = :status, tweet_id = :tweet_id, posted_at = :posted_at',
                    ExpressionAttributeNames={
                        '#status': 'status'
                    },
                    ExpressionAttributeValues={
                        ':status': 'posted',
                        ':tweet_id': tweet_id,
                        ':posted_at': datetime.utcnow().isoformat()
                    }
                )
                
                logger.info(f"Successfully posted tweet for email {email_id}")
                
            except tweepy.TooManyRequests:
                # Don't delete message from queue, let it retry later
                logger.warning("Rate limited, will retry later")
                raise
                
            except Exception as e:
                # Update DynamoDB with failure
                table.update_item(
                    Key={'email_id': email_id},
                    UpdateExpression='SET #status = :status, error = :error',
                    ExpressionAttributeNames={
                        '#status': 'status'
                    },
                    ExpressionAttributeValues={
                        ':status': 'failed',
                        ':error': str(e)
                    }
                )
                logger.error(f"Failed to post tweet for email {email_id}: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Tweets processed')
        }
        
    except Exception as e:
        logger.error(f"Error in Twitter poster: {str(e)}")
        raise