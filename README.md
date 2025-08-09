# Twitter Bot - Email to Japanese Tweet Automation

An AWS serverless bot that automatically translates emails to Japanese and posts them to Twitter using Claude Opus 4.

## 🚀 Features

- **Automatic Email Processing**: Polls Gmail every 5 minutes for new emails
- **AI Translation**: Uses Claude Opus 4 via AWS Bedrock to create engaging Japanese tweets
- **Twitter Integration**: Automatically posts translated content to Twitter
- **Duplicate Prevention**: Tracks processed emails to avoid reposts
- **Serverless Architecture**: Fully managed using AWS Lambda, SQS, and DynamoDB

## 📧 How It Works

1. Send an email to `t.speekenbrink+xposts@gmail.com`
2. Gmail poller Lambda checks for new emails every 5 minutes
3. Content processor translates the email to a Japanese tweet using Claude
4. Twitter poster publishes the tweet to your account
5. System tracks all processed emails in DynamoDB

## 🏗️ Architecture

```
Gmail Inbox
    ↓ (Every 5 minutes via EventBridge)
Gmail Poller Lambda
    ↓ (SQS Queue)
Content Processor Lambda (Claude Opus 4)
    ↓ (SQS Queue)
Twitter Poster Lambda
    ↓
Twitter Account
```

## 📦 AWS Services Used

- **Lambda Functions**: 4 serverless functions for processing
- **SQS**: 2 queues for reliable message passing
- **DynamoDB**: 2 tables for state tracking
- **EventBridge**: Scheduled triggers for polling
- **Secrets Manager**: Secure API credential storage
- **Bedrock**: Claude Opus 4 for translation
- **CloudWatch**: Logging and monitoring

## 🔧 Configuration

### Environment Variables

Each Lambda function uses environment variables for configuration:

- `GMAIL_SECRET_NAME`: Secrets Manager key for Gmail credentials
- `TWITTER_SECRET_NAME`: Secrets Manager key for Twitter credentials
- `BEDROCK_MODEL_ID`: Claude model inference profile ID
- `PROCESSED_TABLE`: DynamoDB table for tracking
- `EMAIL_QUEUE_URL`: SQS queue for email processing
- `TWITTER_QUEUE_URL`: SQS queue for Twitter posting

### Required Secrets

Store in AWS Secrets Manager:
- `twitter-bot/gmail-api`: Gmail OAuth credentials
- `twitter-bot/twitter-api`: Twitter API keys

## 💰 Cost Estimate

- **Lambda**: ~$5/month (with free tier)
- **Bedrock**: ~$5-10/month (depending on email volume)
- **Other Services**: <$1/month
- **Total**: ~$10-15/month

## 🚦 Monitoring

Check CloudWatch Logs for each Lambda:
- `/aws/lambda/twitter-bot-gmail-poller`
- `/aws/lambda/twitter-bot-content-processor`
- `/aws/lambda/twitter-bot-twitter-poster`

## 📝 Maintenance

- Gmail credentials refresh automatically
- Twitter tokens don't expire
- Lambda functions auto-scale
- CloudWatch logs auto-rotate after 30 days

## 🔒 Security

- All credentials stored in Secrets Manager
- IAM roles follow least privilege principle
- No hardcoded secrets in code
- Input validation on all external data

## 📄 License

Private project - not for redistribution