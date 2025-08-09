# Lambda Functions for Twitter Bot

This directory contains the three Lambda functions that power the email-to-Twitter bot.

## Functions

### 1. email_receiver
- Receives Gmail push notifications via API Gateway
- Validates the notification
- Queues email for processing in SQS

### 2. content_processor  
- Triggered by SQS messages
- Fetches email content from Gmail API
- Uses Claude Sonnet 4.0 to generate Japanese tweet
- Queues tweet for posting
- Tracks processed emails in DynamoDB

### 3. twitter_poster
- Triggered by SQS messages
- Posts tweets to Twitter
- Updates DynamoDB with posting status
- Handles rate limiting gracefully

## Deployment

Due to IAM permission limitations, you'll need to:

1. **Switch to an admin user** or use root account
2. **Run the IAM commands** from aws_setup.md to create the Lambda role
3. **Create Lambda functions** using the code in this directory
4. **Create a Lambda layer** with the dependencies from requirements.txt
5. **Set up API Gateway** to trigger the email_receiver function

## Environment Variables

Each function needs specific environment variables:

### email_receiver
- `SQS_QUEUE_URL`: URL of the email processing queue
- `DYNAMODB_TABLE`: Name of processed emails table

### content_processor
- `BEDROCK_MODEL_ID`: Claude Sonnet 4.0 model ID
- `GMAIL_SECRET_NAME`: Secrets Manager key for Gmail creds
- `PROCESSED_TABLE`: DynamoDB table name
- `TWITTER_QUEUE_URL`: SQS queue for Twitter posting

### twitter_poster
- `TWITTER_SECRET_NAME`: Secrets Manager key for Twitter creds
- `PROCESSED_TABLE`: DynamoDB table name

## Testing Locally

You can test the core logic locally, but you'll need:
- AWS credentials configured
- Access to Secrets Manager
- DynamoDB tables created
- SQS queues created