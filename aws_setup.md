# AWS Setup Guide - Terminal Commands

This guide contains all AWS CLI commands needed to set up the Twitter bot infrastructure. Run these commands in order after completing each prerequisite step.

## Prerequisites Check

```bash
# Check if AWS CLI is installed
aws --version

# If not installed on macOS:
brew install awscli

# Check if you're in the right directory
pwd  # Should show: /Users/tycho/personal/twitter_bot
```

## Step 1: Configure AWS CLI

```bash
# Configure AWS credentials
aws configure

# When prompted, enter:
# AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
# AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
# Default region name [None]: us-east-1
# Default output format [None]: json

# Verify configuration
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/twitter-bot-dev"
}
```

## Step 2: Check Bedrock Access

```bash
# List available Bedrock models
aws bedrock list-foundation-models \
    --by-provider Anthropic \
    --region us-east-1 \
    --query 'modelSummaries[?modelId==`anthropic.claude-3-opus-20240229-v1:0`]'

# If empty, you need to request access via AWS Console
```

## Step 3: Create DynamoDB Tables

### Table 1: Processed Emails

```bash
# Create table for tracking processed emails
aws dynamodb create-table \
    --table-name twitter-bot-processed-emails \
    --attribute-definitions \
        AttributeName=email_id,AttributeType=S \
    --key-schema \
        AttributeName=email_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --tags \
        Key=Project,Value=twitter-bot \
        Key=Environment,Value=production

# Wait for table to be active
aws dynamodb wait table-exists \
    --table-name twitter-bot-processed-emails

# Verify table creation
aws dynamodb describe-table \
    --table-name twitter-bot-processed-emails \
    --query 'Table.TableStatus'
```

### Table 2: Application State

```bash
# Create table for storing tokens and state
aws dynamodb create-table \
    --table-name twitter-bot-app-state \
    --attribute-definitions \
        AttributeName=key,AttributeType=S \
    --key-schema \
        AttributeName=key,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --tags \
        Key=Project,Value=twitter-bot \
        Key=Environment,Value=production

# Verify
aws dynamodb describe-table \
    --table-name twitter-bot-app-state \
    --query 'Table.TableStatus'
```

## Step 4: Create S3 Bucket (Optional - for attachments)

```bash
# Create unique bucket name (must be globally unique)
BUCKET_NAME="twitter-bot-tycho-$(date +%Y%m%d)"
echo "Bucket name: $BUCKET_NAME"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Enable versioning for safety
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Add lifecycle policy to delete old attachments after 30 days
cat > /tmp/lifecycle.json << 'EOF'
{
    "Rules": [{
        "ID": "DeleteOldAttachments",
        "Status": "Enabled",
        "Expiration": {
            "Days": 30
        }
    }]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket $BUCKET_NAME \
    --lifecycle-configuration file:///tmp/lifecycle.json
```

## Step 5: Create Secrets in Secrets Manager

```bash
# Store Gmail API credentials
aws secretsmanager create-secret \
    --name twitter-bot/gmail-api \
    --description "Gmail API credentials for Twitter bot" \
    --secret-string '{
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "refresh_token": "YOUR_REFRESH_TOKEN"
    }' \
    --tags \
        Key=Project,Value=twitter-bot

# Store Twitter API credentials
aws secretsmanager create-secret \
    --name twitter-bot/twitter-api \
    --description "Twitter API credentials" \
    --secret-string '{
        "api_key": "YOUR_API_KEY",
        "api_secret": "YOUR_API_SECRET",
        "access_token": "YOUR_ACCESS_TOKEN",
        "access_token_secret": "YOUR_TOKEN_SECRET"
    }' \
    --tags \
        Key=Project,Value=twitter-bot

# Verify secrets were created
aws secretsmanager list-secrets \
    --filters Key=name,Values=twitter-bot/ \
    --query 'SecretList[*].Name'
```

## Step 6: Create SQS Queue

```bash
# Create standard SQS queue for email processing
aws sqs create-queue \
    --queue-name twitter-bot-email-queue \
    --attributes '{
        "MessageRetentionPeriod": "1209600",
        "VisibilityTimeout": "300"
    }' \
    --tags \
        Project=twitter-bot \
        Environment=production

# Get queue URL
aws sqs get-queue-url \
    --queue-name twitter-bot-email-queue
```

## Step 7: Create IAM Role for Lambda

```bash
# Create trust policy for Lambda
cat > /tmp/lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create IAM role
aws iam create-role \
    --role-name twitter-bot-lambda-role \
    --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
    --description "Role for Twitter bot Lambda functions"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name twitter-bot-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy for our services
cat > /tmp/twitter-bot-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/twitter-bot-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "arn:aws:secretsmanager:*:*:secret:twitter-bot/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": [
                "arn:aws:sqs:*:*:twitter-bot-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-opus-20240229-v1:0"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::twitter-bot-*/*"
            ]
        }
    ]
}
EOF

# Create and attach the policy
aws iam create-policy \
    --policy-name twitter-bot-lambda-policy \
    --policy-document file:///tmp/twitter-bot-policy.json

# Get your account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Attach the custom policy
aws iam attach-role-policy \
    --role-name twitter-bot-lambda-role \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/twitter-bot-lambda-policy
```

## Step 8: Create Lambda Functions

### Email Receiver Function

```bash
# Create deployment package directory
mkdir -p /tmp/email-receiver
cd /tmp/email-receiver

# Create basic Lambda function code
cat > lambda_function.py << 'EOF'
import json
import boto3
import os

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    # TODO: Implement Gmail webhook processing
    
    return {
        'statusCode': 200,
        'body': json.dumps('Email received')
    }
EOF

# Zip the function
zip function.zip lambda_function.py

# Create Lambda function
aws lambda create-function \
    --function-name twitter-bot-email-receiver \
    --runtime python3.11 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/twitter-bot-lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 60 \
    --memory-size 256 \
    --environment Variables={
        SQS_QUEUE_NAME=twitter-bot-email-queue,
        DYNAMODB_TABLE=twitter-bot-processed-emails
    } \
    --tags \
        Project=twitter-bot \
        Environment=production
```

### Content Processor Function

```bash
# Create deployment package
mkdir -p /tmp/content-processor
cd /tmp/content-processor

# Create basic Lambda function code
cat > lambda_function.py << 'EOF'
import json
import boto3
import os

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    print(f"Processing content: {json.dumps(event)}")
    
    # TODO: Implement Bedrock content generation
    
    return {
        'statusCode': 200,
        'body': json.dumps('Content processed')
    }
EOF

# Zip and create function
zip function.zip lambda_function.py

aws lambda create-function \
    --function-name twitter-bot-content-processor \
    --runtime python3.11 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/twitter-bot-lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 120 \
    --memory-size 512 \
    --environment Variables={
        BEDROCK_MODEL_ID=anthropic.claude-3-opus-20240229-v1:0
    } \
    --tags \
        Project=twitter-bot \
        Environment=production
```

### Twitter Poster Function

```bash
# Create deployment package
mkdir -p /tmp/twitter-poster
cd /tmp/twitter-poster

# Create basic Lambda function code
cat > lambda_function.py << 'EOF'
import json
import boto3
import os

def lambda_handler(event, context):
    print(f"Posting to Twitter: {json.dumps(event)}")
    
    # TODO: Implement Twitter posting
    
    return {
        'statusCode': 200,
        'body': json.dumps('Posted to Twitter')
    }
EOF

# Zip and create function
zip function.zip lambda_function.py

aws lambda create-function \
    --function-name twitter-bot-twitter-poster \
    --runtime python3.11 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/twitter-bot-lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 30 \
    --memory-size 256 \
    --environment Variables={
        TWITTER_SECRETS_NAME=twitter-bot/twitter-api
    } \
    --tags \
        Project=twitter-bot \
        Environment=production

# Return to project directory
cd ~/personal/twitter_bot
```

## Step 9: Create API Gateway

```bash
# Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name twitter-bot-api \
    --description "API for Twitter bot Gmail webhook" \
    --endpoint-configuration types=REGIONAL \
    --tags Project=twitter-bot,Environment=production \
    --query 'id' \
    --output text)

echo "API ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[0].id' \
    --output text)

# Create /webhook resource
RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part webhook \
    --query 'id' \
    --output text)

# Create POST method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE

# Create Lambda integration
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:${ACCOUNT_ID}:function:twitter-bot-email-receiver/invocations

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --stage-description "Production stage"

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
    --function-name twitter-bot-email-receiver \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:${ACCOUNT_ID}:${API_ID}/*/*"

# Get the invoke URL
echo "Webhook URL: https://${API_ID}.execute-api.us-east-1.amazonaws.com/prod/webhook"
```

## Step 10: Testing Commands

### Test DynamoDB

```bash
# Put test item in DynamoDB
aws dynamodb put-item \
    --table-name twitter-bot-processed-emails \
    --item '{
        "email_id": {"S": "test-email-001"},
        "processed_at": {"S": "2025-01-01T00:00:00Z"},
        "status": {"S": "processed"}
    }'

# Get the item back
aws dynamodb get-item \
    --table-name twitter-bot-processed-emails \
    --key '{"email_id": {"S": "test-email-001"}}'
```

### Test Lambda Functions

```bash
# Test email receiver
aws lambda invoke \
    --function-name twitter-bot-email-receiver \
    --payload '{"test": "data"}' \
    /tmp/response.json

cat /tmp/response.json

# Check Lambda logs
aws logs tail /aws/lambda/twitter-bot-email-receiver --follow
```

### Test Bedrock Access

```bash
# Test Bedrock invocation
aws bedrock-runtime invoke-model \
    --model-id anthropic.claude-3-opus-20240229-v1:0 \
    --content-type application/json \
    --accept application/json \
    --body '{
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [{
            "role": "user",
            "content": "Say hello in Japanese"
        }]
    }' \
    /tmp/bedrock-response.json

# View response
cat /tmp/bedrock-response.json | jq -r '.content[0].text'
```

## Useful Debugging Commands

```bash
# List all resources with twitter-bot tag
aws resourcegroupstaggingapi get-resources \
    --tag-filters Key=Project,Values=twitter-bot \
    --query 'ResourceTagMappingList[*].ResourceARN'

# Check Lambda function configuration
aws lambda get-function \
    --function-name twitter-bot-email-receiver

# View CloudWatch logs
aws logs describe-log-groups \
    --log-group-name-prefix /aws/lambda/twitter-bot

# Check API Gateway endpoint
aws apigateway get-rest-apis \
    --query 'items[?name==`twitter-bot-api`]'

# Monitor costs
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE
```

## Cleanup Commands (if needed)

```bash
# Delete Lambda functions
aws lambda delete-function --function-name twitter-bot-email-receiver
aws lambda delete-function --function-name twitter-bot-content-processor
aws lambda delete-function --function-name twitter-bot-twitter-poster

# Delete DynamoDB tables
aws dynamodb delete-table --table-name twitter-bot-processed-emails
aws dynamodb delete-table --table-name twitter-bot-app-state

# Delete secrets
aws secretsmanager delete-secret --secret-id twitter-bot/gmail-api --force-delete-without-recovery
aws secretsmanager delete-secret --secret-id twitter-bot/twitter-api --force-delete-without-recovery

# Delete SQS queue
aws sqs delete-queue --queue-url $(aws sqs get-queue-url --queue-name twitter-bot-email-queue --query QueueUrl --output text)

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id $API_ID
```

## Next Steps

1. Update Lambda functions with actual implementation code
2. Configure Gmail push notifications to API Gateway URL
3. Add Twitter API credentials to Secrets Manager
4. Test end-to-end flow
5. Set up monitoring and alerts

---

Remember to replace placeholder values (YOUR_ACCESS_KEY_ID, etc.) with actual values when running these commands!