# Twitter Bot Project - Master Todo List

## 📊 Current Status: ~95% Complete ✅
**Last Updated**: 2025-08-09  
**Latest Checkpoint**: `.claude/checkpoints/checkpoint_20250803_183653.md`  
**Project Status**: **LIVE IN PRODUCTION** 🚀

### ✅ System Overview:
- **Email Address**: t.speekenbrink+xposts@gmail.com
- **Translation Model**: Claude Opus 4 (via Bedrock)
- **Polling Interval**: Every 5 minutes
- **Tweet Account**: @tikoo_ai

### 🔗 Key Resources:
- **Webhook URL**: `https://cccn7als69.execute-api.us-east-1.amazonaws.com/prod/webhook`
- **AWS Account**: 706213173358
- **Region**: us-east-1

---

## Project Overview
Build an automated bot that receives emails at t.speekenbrink+xposts@gmail.com, uses Claude Sonnet 4.0 via AWS Bedrock to create Japanese Twitter posts, and publishes them.

## Phase 1: AWS Account Setup ✅

### Initial Setup
- [x] Secure root account with MFA
- [x] Create billing alerts ($10, $25, $50)
- [x] Create IAM user for development (twitter-bot-dev)
- [x] Install and configure AWS CLI
- [x] Test AWS CLI access

### Enable Required Services
- [x] Enable Bedrock in your region (us-east-1)
- [x] Request access to Claude 3 Opus model (Using Sonnet 4.0)
- [x] Verify Bedrock model access granted
- [ ] Understand AWS Free Tier limits

## Phase 2: External Services Setup 📧

### Gmail API Setup
- [x] Create Google Cloud Project (twitter-bot-gmail)
- [x] Enable Gmail API
- [x] Create OAuth 2.0 credentials (Web application)
- [x] Configure OAuth consent screen (Google Auth Platform)
- [x] Add test user (t.speekenbrink+xposts@gmail.com)
- [x] Set up redirect URIs (localhost:8080)
- [x] Test Gmail API access locally
- [x] Obtain refresh token for Lambda use
- [x] ~~Set up Pub/Sub topic~~ Using polling instead
- [x] Deploy Gmail poller Lambda with 5-minute schedule

### Twitter Developer Account
- [x] Apply for Twitter Developer account
- [x] Create Twitter App
- [x] Generate API keys and tokens
- [x] Understand Twitter API v2 rate limits
- [x] Test posting a simple tweet via API

## Phase 3: AWS Infrastructure 🏗️

### Core Resources
- [x] Create DynamoDB table for processed emails
- [x] Create DynamoDB table for app state/tokens
- [x] Set up Secrets Manager for API keys
- [ ] Create S3 bucket for any attachments (optional)
- [x] Set up SQS queue for email processing (twitter-bot-email-queue)
- [x] Set up second SQS queue for Twitter posting (twitter-bot-twitter-queue)

### Lambda Functions
- [x] Create email_receiver Lambda function
- [x] Write content_processor Lambda function code
- [x] Write twitter_poster Lambda function code
- [x] Deploy content_processor Lambda function
- [x] Deploy twitter_poster Lambda function
- [x] Deploy gmail_poller Lambda function
- [x] Set up Lambda layers for shared dependencies
- [x] Configure environment variables (all functions)
- [x] Set up CloudWatch Events for polling schedule

### API Gateway
- [x] Create REST API for Gmail webhook
- [x] Configure endpoint for email notifications
- [x] Set up authentication/validation
- [x] Test webhook endpoint (switched to polling)

## Phase 4: Development 💻

### Local Development Setup
- [x] Create project directory structure
- [x] Set up Python virtual environment
- [x] Install boto3, tweepy, google-api-python-client
- [x] Create .env file for local testing
- [x] Create .gitignore to protect credentials
- [ ] Set up git repository

### Lambda Function Development
- [x] Implement Gmail webhook receiver
- [x] Implement email content extraction  
- [x] Create Bedrock prompt for Japanese tweets
- [x] Implement Twitter posting logic
- [x] Add error handling and retries
- [x] Implement duplicate email detection

### Testing
- [x] Test Bedrock connection and prompt
- [x] Test Gmail API integration
- [x] Test Twitter API posting
- [x] Test end-to-end flow in AWS
- [x] Test Lambda functions individually
- [x] Successfully processed real email

## Phase 5: Deployment 🚀

### Infrastructure as Code
- [ ] Create SAM template or CloudFormation
- [ ] Define all resources in IaC
- [ ] Set up deployment scripts
- [ ] Configure CI/CD (optional)

### Deploy to AWS
- [x] Deploy email_receiver Lambda function
- [x] Deploy content_processor Lambda function
- [x] Deploy twitter_poster Lambda function
- [x] Deploy gmail_poller Lambda function
- [x] Deploy API Gateway
- [x] Configure SQS triggers for Lambda functions
- [x] Set up EventBridge schedule for polling
- [x] Test complete flow in AWS

## Phase 6: Monitoring & Optimization 📊

### Monitoring Setup
- [ ] Set up CloudWatch dashboards
- [ ] Configure error alerts
- [ ] Set up DLQ for failed messages
- [ ] Create cost monitoring alerts
- [ ] Set up notification for failed posts

### Security Review
- [ ] Review IAM permissions (least privilege)
- [ ] Ensure no hardcoded credentials
- [ ] Validate input sanitization
- [ ] Review API Gateway security
- [ ] Test error scenarios

### Performance Optimization
- [ ] Optimize Lambda memory allocation
- [ ] Review cold start impact
- [ ] Implement caching where appropriate
- [ ] Monitor Bedrock token usage
- [ ] Optimize DynamoDB queries

## Phase 7: Documentation & Maintenance 📝

### Documentation
- [ ] Create README.md with setup instructions
- [ ] Document API endpoints
- [ ] Document environment variables
- [ ] Create troubleshooting guide
- [ ] Document cost estimates

### Operational Tasks
- [ ] Set up log retention policies
- [ ] Plan for credential rotation
- [ ] Create backup strategy
- [ ] Document deployment process
- [ ] Create runbook for common issues

## Stretch Goals 🎯

### Enhanced Features
- [ ] Add image support from emails
- [ ] Implement thread creation for long content
- [ ] Add scheduling based on optimal posting times
- [ ] Create web dashboard for monitoring
- [ ] Add multiple Twitter account support
- [ ] Implement A/B testing for posts

### Advanced Processing
- [ ] Add content moderation
- [ ] Implement custom terminology for translations
- [ ] Add analytics tracking
- [ ] Create approval workflow
- [ ] Add email filtering rules

## Success Criteria ✅

- [x] Successfully receive email via Gmail API
- [x] Generate engaging Japanese tweet using Bedrock
- [x] Post tweet to Twitter automatically
- [x] System handles errors gracefully
- [x] Total cost under $50/month (estimated ~$10-15/month)
- [x] Processing time under 30 seconds per email
- [x] System running reliably with 5-minute polling

## Notes & Resources

### Useful Links
- AWS Bedrock Documentation: https://docs.aws.amazon.com/bedrock/
- Gmail API: https://developers.google.com/gmail/api
- Twitter API v2: https://developer.twitter.com/en/docs/twitter-api
- AWS Lambda: https://docs.aws.amazon.com/lambda/

### Cost Tracking
- Expected monthly cost: $25-45
- Main costs: Bedrock API calls, Lambda execution
- Free tier coverage: API Gateway, DynamoDB, Lambda (partial)

### Key Decisions Made
- Using personal AWS account
- Claude Opus 4.0 for content generation
- Serverless architecture for scalability
- DynamoDB for state management

---

Last Updated: 2025-08-09
Project Status: **PRODUCTION** - System Live and Processing Emails