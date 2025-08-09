# AWS Components Overview - Twitter Bot (Simplified)

## Account Information
- **Account ID**: 706213173358
- **User**: twitter-bot-dev
- **Region**: us-east-1

## Simplified Architecture Flow
```
EventBridge (5min) → Gmail Poller Lambda → SQS Email Queue 
→ Content Processor Lambda → Bedrock AI → SQS Twitter Queue 
→ Twitter Poster Lambda → Twitter API
```

## 1. DynamoDB Tables (2 tables)

### twitter-bot-processed-emails
- **Purpose**: Track processed emails and prevent duplicates
- **Primary Key**: `email_id` (String) - Unique Gmail message ID
- **Item Count**: 7 items currently
- **Billing**: Pay-per-request (on-demand)
- **Sample Fields**: 
  - `status`: queued → queued_for_posting → posted
  - `tweet_text`: Japanese translation (no emojis)
  - `tweet_id`: Twitter's ID after posting
  - `posted_at`: Timestamp when tweeted

### twitter-bot-app-state
- **Purpose**: Store application state (last check timestamps)
- **Primary Key**: `key` (String)
- **Billing**: Pay-per-request
- **Main entry**: `last_check_time` - When Gmail was last polled

## 2. SQS Queues (2 queues)

### twitter-bot-email-queue
- **URL**: https://sqs.us-east-1.amazonaws.com/706213173358/twitter-bot-email-queue
- **Purpose**: Gmail Poller → Content Processor
- **Visibility Timeout**: 300 seconds (5 minutes)
- **Message Retention**: 14 days
- **Current Messages**: 0

### twitter-bot-twitter-queue  
- **URL**: https://sqs.us-east-1.amazonaws.com/706213173358/twitter-bot-twitter-queue
- **Purpose**: Content Processor → Twitter Poster
- **Visibility Timeout**: 300 seconds (5 minutes)
- **Message Retention**: 14 days

## 3. Lambda Functions (3 functions - Simplified from 4)

### twitter-bot-gmail-poller
- **Runtime**: Python 3.11
- **Memory**: 256 MB
- **Timeout**: 60 seconds
- **Trigger**: EventBridge schedule (every 5 minutes)
- **Purpose**: Pull emails from Gmail
- **Environment Variables**:
  - EMAIL_QUEUE_URL
  - STATE_TABLE
  - GMAIL_SECRET_NAME
  - PROCESSED_TABLE

### twitter-bot-content-processor
- **Runtime**: Python 3.11
- **Memory**: 512 MB (highest)
- **Timeout**: 120 seconds (longest)
- **Trigger**: SQS Email Queue (batch size: 10)
- **Purpose**: Translate emails to Japanese using Bedrock Claude
- **Environment Variables**:
  - BEDROCK_MODEL_ID: anthropic.claude-3-5-sonnet-20241022-v2:0
  - PROCESSED_TABLE
  - TWITTER_QUEUE_URL
- **Special Config**: No emoji generation

### twitter-bot-twitter-poster
- **Runtime**: Python 3.11
- **Memory**: 256 MB
- **Timeout**: 60 seconds
- **Trigger**: SQS Twitter Queue (batch size: 1)
- **Purpose**: Post tweets to Twitter API

## 4. EventBridge Schedule

### twitter-bot-gmail-poll-schedule
- **Schedule**: rate(5 minutes)
- **State**: ENABLED
- **Target**: twitter-bot-gmail-poller Lambda
- **Description**: Trigger Gmail polling every 5 minutes

## 5. ~~API Gateway~~ (REMOVED)
- **Status**: DELETED - No longer needed with polling-only approach
- **Previous**: Was used for Gmail webhook endpoint

## 6. IAM Configuration

### twitter-bot-lambda-role
- **ARN**: arn:aws:iam::706213173358:role/twitter-bot-lambda-role
- **Attached Policies**:
  1. AWSLambdaBasicExecutionRole (AWS managed)
  2. twitter-bot-lambda-policy (Custom)
- **Permissions**: DynamoDB, SQS, Secrets Manager, Bedrock, CloudWatch

## 7. Supporting Resources

### Lambda Layer
- **Name**: twitter-bot-dependencies
- **Version**: 2
- **Purpose**: Shared Python dependencies (google-api-python-client, tweepy, etc.)

### CloudWatch Log Groups
- /aws/lambda/twitter-bot-content-processor
- /aws/lambda/twitter-bot-gmail-poller
- /aws/lambda/twitter-bot-twitter-poster

### Secrets Manager
- **twitter-bot/gmail-api**: Gmail OAuth credentials
- **twitter-bot/twitter-api**: Twitter API credentials

## Current System Status
- **Active Emails Processed**: 7
- **Queue Status**: Both queues empty (no backlog)
- **Schedule**: Running every 5 minutes
- **Latest Activity**: Successfully posted tweet at 2025-08-09 09:27:04 UTC

## Simplified Architecture Benefits
1. **No Public Endpoints**: No API Gateway = more secure
2. **Pull-Only Model**: System controls when to check emails
3. **Single Path**: One clear flow from Gmail to Twitter
4. **3 Lambda Functions**: Down from 4 (removed email-receiver)
5. **No Webhooks**: No tokens to refresh or maintain

## Cost Optimization
- Pay-per-request DynamoDB (no idle costs)
- Appropriate Lambda memory (256-512MB)
- 5-minute polling balances cost vs responsiveness
- No API Gateway charges
- Efficient batch processing in SQS

## Quick Stats
- **Components Removed**: 1 Lambda, 1 API Gateway
- **Total AWS Services Used**: 6 (Lambda, DynamoDB, SQS, EventBridge, Secrets Manager, Bedrock)
- **External APIs**: 2 (Gmail, Twitter)
- **Polling Frequency**: Every 5 minutes (288 times/day)