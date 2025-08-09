# Deployment Guide & Code Walkthrough

## 🎯 Project Overview

This project implements an automated pipeline that:
1. Monitors a Gmail inbox for new emails
2. Translates email content to Japanese using AI
3. Posts the translation as a tweet

The entire system is serverless, using AWS managed services for reliability and scalability.

## 🏗️ Infrastructure Setup Walkthrough

### Step 1: DynamoDB Tables

We created two tables for state management:

```bash
# Table for tracking processed emails
aws dynamodb create-table \
    --table-name twitter-bot-processed-emails \
    --attribute-definitions AttributeName=email_id,AttributeType=S \
    --key-schema AttributeName=email_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Table for application state (last check time)
aws dynamodb create-table \
    --table-name twitter-bot-app-state \
    --attribute-definitions AttributeName=key,AttributeType=S \
    --key-schema AttributeName=key,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

**Why DynamoDB?**
- Serverless, no management overhead
- Pay-per-request pricing perfect for sporadic workload
- Built-in encryption and backups

### Step 2: SQS Queues

Created two queues for decoupling components:

```bash
# Queue from Gmail poller to content processor
aws sqs create-queue \
    --queue-name twitter-bot-email-queue \
    --attributes MessageRetentionPeriod=1209600,VisibilityTimeout=300

# Queue from content processor to Twitter poster  
aws sqs create-queue \
    --queue-name twitter-bot-twitter-queue \
    --attributes MessageRetentionPeriod=1209600,VisibilityTimeout=300
```

**Why SQS?**
- Reliable message delivery with retries
- Decouples components for independent scaling
- Handles failures gracefully

### Step 3: IAM Role

Created a role for Lambda functions:

```bash
aws iam create-role \
    --role-name twitter-bot-lambda-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attached policies for:
# - CloudWatch Logs
# - DynamoDB access
# - SQS operations
# - Secrets Manager
# - Bedrock invocation
```

### Step 4: Secrets Manager

Stored API credentials securely:

```bash
# Gmail OAuth credentials
aws secretsmanager create-secret \
    --name twitter-bot/gmail-api \
    --secret-string '{
        "client_id": "...",
        "client_secret": "...",
        "refresh_token": "..."
    }'

# Twitter API keys
aws secretsmanager create-secret \
    --name twitter-bot/twitter-api \
    --secret-string '{
        "api_key": "...",
        "api_secret": "...",
        "access_token": "...",
        "access_token_secret": "..."
    }'
```

## 📝 Lambda Functions Deep Dive

### Gmail Poller (`gmail_poller/lambda_function.py`)

**Key Components:**

```python
def lambda_handler(event, context):
    # 1. Get Gmail service using OAuth
    service = get_gmail_service()
    
    # 2. Check last polling time from DynamoDB
    last_check = get_last_check_time()
    
    # 3. Query Gmail for new messages
    query = f'after:{last_check_timestamp} to:t.speekenbrink+xposts@gmail.com'
    messages = service.users().messages().list(userId='me', q=query)
    
    # 4. For each new message:
    for msg in messages:
        # Extract content
        email_content = extract_email_body(msg)
        
        # Queue for processing
        sqs.send_message(
            QueueUrl=EMAIL_QUEUE_URL,
            MessageBody=json.dumps(email_content)
        )
        
    # 5. Update last check time
    save_last_check_time(datetime.utcnow())
```

**Deployment:**
```bash
cd lambda_functions/gmail_poller
zip -r lambda_function.zip lambda_function.py
aws lambda create-function \
    --function-name twitter-bot-gmail-poller \
    --runtime python3.11 \
    --handler lambda_function.lambda_handler \
    --role arn:aws:iam::706213173358:role/twitter-bot-lambda-role \
    --layers arn:aws:lambda:us-east-1:706213173358:layer:twitter-bot-dependencies:2
```

### Content Processor (`content_processor/lambda_function.py`)

**Key Components:**

```python
def generate_japanese_tweet(email_content):
    prompt = f'''あなたは英語のメールを日本語のツイートに変換する専門家です。
    
    以下のメールの内容を、魅力的で簡潔な日本語のツイート（280文字以内）に変換してください：
    
    件名: {email_content['subject']}
    本文: {email_content['body']}
    
    要件：
    - 自然な日本語で書く
    - 重要な情報を保持する
    - ツイッターに適したカジュアルなトーン
    - 適切な絵文字を1-2個含める
    - ハッシュタグを1-2個提案する
    '''
    
    # Call Bedrock with Claude Opus 4
    response = bedrock.invoke_model(
        modelId="us.anthropic.claude-opus-4-20250514-v1:0",
        body=json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        })
    )
    
    return parse_response(response)
```

**Why Claude Opus 4?**
- Superior Japanese language understanding
- Creative and engaging translations
- Maintains context and nuance

### Twitter Poster (`twitter_poster/lambda_function.py`)

**Key Components:**

```python
def lambda_handler(event, context):
    # 1. Get Twitter client
    client = get_twitter_client()
    
    # 2. Process each message from queue
    for record in event['Records']:
        tweet_data = json.loads(record['body'])
        
        # 3. Post tweet
        response = client.create_tweet(text=tweet_data['tweet_text'])
        
        # 4. Update DynamoDB with result
        table.update_item(
            Key={'email_id': tweet_data['email_id']},
            UpdateExpression='SET status = :status, tweet_id = :id',
            ExpressionAttributeValues={
                ':status': 'posted',
                ':id': response.data['id']
            }
        )
```

## 🔧 Lambda Layer Creation

The layer contains shared dependencies:

```bash
# Create layer structure
mkdir -p layer/python
pip install -r requirements.txt -t layer/python/

# Requirements include:
# - tweepy (Twitter API)
# - google-auth (Gmail OAuth)
# - google-api-python-client (Gmail API)
# - requests (HTTP client)

# Package and publish
cd layer
zip -r ../python_dependencies_layer.zip python/
aws lambda publish-layer-version \
    --layer-name twitter-bot-dependencies \
    --zip-file fileb://../python_dependencies_layer.zip
```

## ⏰ EventBridge Scheduling

Set up automatic polling every 5 minutes:

```bash
# Create schedule rule
aws events put-rule \
    --name twitter-bot-gmail-poll-schedule \
    --schedule-expression "rate(5 minutes)"

# Add Lambda permission
aws lambda add-permission \
    --function-name twitter-bot-gmail-poller \
    --statement-id allow-eventbridge \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com

# Connect rule to Lambda
aws events put-targets \
    --rule twitter-bot-gmail-poll-schedule \
    --targets "Id=1,Arn=arn:aws:lambda:us-east-1:706213173358:function:twitter-bot-gmail-poller"
```

## 🔗 SQS Triggers

Connected queues to Lambda functions:

```bash
# Email queue → Content processor
aws lambda create-event-source-mapping \
    --function-name twitter-bot-content-processor \
    --event-source-arn arn:aws:sqs:us-east-1:706213173358:twitter-bot-email-queue \
    --batch-size 10

# Twitter queue → Twitter poster
aws lambda create-event-source-mapping \
    --function-name twitter-bot-twitter-poster \
    --event-source-arn arn:aws:sqs:us-east-1:706213173358:twitter-bot-twitter-queue \
    --batch-size 1
```

## 🔑 Key Design Decisions

### Why Polling Instead of Pub/Sub?

Initially considered Gmail Pub/Sub for real-time notifications, but chose polling because:
- No Google Cloud setup required
- No 7-day renewal needed
- Simpler architecture
- 5-minute delay acceptable for this use case

### Why Multiple Lambda Functions?

Separated concerns for:
- Independent scaling
- Isolated failures
- Easier debugging
- Single responsibility principle

### Why SQS Between Functions?

- Automatic retries on failure
- Decouples processing stages
- Handles rate limiting gracefully
- Provides durability

## 🚀 Testing the System

1. **Send test email** to `t.speekenbrink+xposts@gmail.com`
2. **Wait 5 minutes** for poller to run
3. **Check CloudWatch Logs** for processing
4. **Verify tweet** appears on Twitter

## 📊 Monitoring

Key metrics to watch:
- Lambda invocation count and errors
- SQS message age
- DynamoDB consumed capacity
- Bedrock invocation latency

## 🛠️ Troubleshooting

Common issues and solutions:

1. **Email not processed**
   - Check Gmail query in poller logs
   - Verify email address matches filter
   - Check last_check timestamp in DynamoDB

2. **Translation fails**
   - Verify Bedrock model access
   - Check inference profile ID
   - Review prompt for special characters

3. **Tweet not posted**
   - Verify Twitter API credentials
   - Check rate limit errors
   - Ensure tweet length < 280 chars

## 💡 Lessons Learned

1. **Inference Profiles**: Bedrock models may require inference profile IDs instead of direct model IDs
2. **JSON Escaping**: Special characters in messages need proper escaping
3. **Lambda Layers**: Directory structure must be exact (`python/` at root)
4. **OAuth Tokens**: Gmail refresh tokens work indefinitely with proper setup
5. **SQS Retries**: Built-in retry mechanism handles transient failures well

## 🔄 Future Improvements

- Add CloudFormation/CDK for infrastructure as code
- Implement DLQ for failed messages
- Add CloudWatch dashboard
- Support image attachments
- Create approval workflow
- Add A/B testing for translations