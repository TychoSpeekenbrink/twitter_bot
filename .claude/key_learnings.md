# Key Learnings - Twitter Bot Project

## AWS Fundamentals

### Q: What is IAM in AWS?
A: Identity and Access Management - controls who can access what in AWS. Key concepts:
- Users: Individual logins
- Groups: Collections of users
- Roles: Temporary permissions for services
- Policies: Documents defining permissions

### Q: What's the difference between root account and IAM user?
A: 
- Root account: Has unlimited access, should be protected with MFA
- IAM user: Limited permissions based on policies, used for daily work

### Q: What is AWS Bedrock?
A: AWS service that provides access to foundation models (like Claude) via API. No infrastructure to manage.

### Q: What is the AWS CLI command to verify your identity?
A: `aws sts get-caller-identity`

## AWS Services for Serverless

### Q: What is AWS Lambda?
A: Serverless compute service that runs code without managing servers. You pay only when code runs.

### Q: What is DynamoDB?
A: AWS's NoSQL database service. Key features:
- Serverless (no connections to manage)
- Key-value and document database
- Single-digit millisecond performance
- 25GB free tier forever

### Q: DynamoDB vs S3 - when to use which?
A: 
- DynamoDB: Structured data (user info, settings, records)
- S3: Files (images, documents, backups)

### Q: What is API Gateway?
A: Service to create REST APIs that can trigger Lambda functions. Handles HTTP requests from the internet.

## OAuth and Authentication

### Q: What is OAuth 2.0?
A: A protocol that lets apps access user data without getting their password. Key concepts:
- Client ID: Your app's public identifier
- Client Secret: Your app's password (keep secret!)
- Redirect URI: Where users go after authorizing
- Access Token: Short-lived key to access APIs
- Refresh Token: Long-lived key to get new access tokens

### Q: What's the difference between "Web application" and "Desktop application" OAuth types?
A: 
- Web application: For apps with a backend server, uses redirect URIs
- Desktop application: For local apps, uses different flow with localhost redirects

### Q: What is a redirect URI mismatch error?
A: OAuth security feature - the redirect URI in your code must exactly match one configured in the OAuth client (including trailing slashes!)

## Gmail API

### Q: What does the Gmail readonly scope allow?
A: `https://www.googleapis.com/auth/gmail.readonly` - Read email messages and settings, but cannot modify/delete/send

### Q: What's the difference between access token and refresh token?
A: 
- Access token: Works for ~1 hour, used for API calls
- Refresh token: Works forever (until revoked), used to get new access tokens

### Q: What is Google Cloud Platform's "test mode" for OAuth apps?
A: Allows only specific test users to access your app. Perfect for personal projects - no need for app verification.

## Python Virtual Environments

### Q: Why use Python virtual environments?
A: 
- Isolates project dependencies from system Python
- Prevents version conflicts between projects
- Makes project portable
- Standard practice for Python development

### Q: How to create and activate a virtual environment?
A: 
```bash
python3 -m venv venv        # Create
source venv/bin/activate    # Activate (macOS/Linux)
```

### Q: How to check if virtual environment is active?
A: Look for `(venv)` in terminal prompt or run `which python`

## Security Best Practices

### Q: What should NEVER be committed to git?
A: 
- API keys and secrets
- Access tokens
- .env files
- AWS credentials
- Any file with passwords

### Q: What happens if you accidentally expose AWS credentials?
A: 
1. Immediately deactivate the credentials in AWS Console
2. Delete them
3. Create new credentials
4. Anyone with credentials can access your AWS account and incur charges

### Q: What is .gitignore?
A: File that tells git which files to never track/commit. Essential for keeping secrets out of version control.

## AWS Costs

### Q: What AWS services have free tiers?
A: 
- Lambda: 1M requests/month free
- DynamoDB: 25GB storage free forever
- API Gateway: 1M API calls free (12 months)
- S3: 5GB storage free (12 months)

### Q: How to monitor AWS costs?
A: 
- Set up billing alerts
- Use AWS Cost Explorer
- Tag resources for cost tracking
- Check AWS Free Tier dashboard

## Gmail to AWS Integration

### Q: What are the two approaches for Gmail to trigger AWS?
A: 
1. Push notifications: Gmail sends webhook when email arrives (real-time)
2. Polling: Lambda checks Gmail periodically (simpler but delayed)

### Q: What is Pub/Sub in Google Cloud?
A: Messaging service that Gmail uses to send notifications about new emails. Connects to AWS via webhooks.

## Error Messages and Troubleshooting

### Q: "ModuleNotFoundError: No module named 'google'" - what's wrong?
A: Python is not using the virtual environment. Either:
- Activate venv: `source venv/bin/activate`
- Use venv Python directly: `./venv/bin/python script.py`

### Q: "The security token included in the request is expired" - AWS error
A: Your AWS session expired. Run `aws sso login --profile profilename` or get new credentials.

### Q: Gmail "redirect_uri_mismatch" error - how to fix?
A: The redirect URI in your code doesn't match Google Cloud Console. Check for:
- Exact match including protocol (http vs https)
- Trailing slashes (localhost:8080 vs localhost:8080/)
- Port numbers

## Architecture Patterns

### Q: What is serverless architecture?
A: Building applications without managing servers. Key benefits:
- No server maintenance
- Automatic scaling
- Pay per use
- Focus on code, not infrastructure

### Q: What's the flow of the email-to-Twitter bot?
A: 
1. Email arrives at Gmail
2. Gmail sends webhook to API Gateway
3. API Gateway triggers Lambda
4. Lambda reads email via Gmail API
5. Lambda sends to Bedrock for Japanese translation
6. Lambda posts to Twitter
7. DynamoDB tracks processed emails

## Claude/Bedrock Specifics

### Q: What's the difference between Claude 3 and Claude 4?
A: Claude 4 (Opus/Sonnet) is newer with improved reasoning and capabilities. Model IDs:
- Claude 3 Opus: `anthropic.claude-3-opus-20240229-v1:0`
- Claude 4 Opus: `anthropic.claude-opus-4-20250514-v1:0`

### Q: How does Bedrock pricing work?
A: Pay per token (piece of text). Typically:
- Input tokens: What you send to Claude
- Output tokens: What Claude generates
- Different prices for different models

## Development Tools

### Q: What is requirements.txt?
A: File listing all Python packages needed for a project. Install with: `pip install -r requirements.txt`

### Q: What is .env file?
A: Local file storing environment variables (like API keys). Never commit to git. Load with python-dotenv.

### Q: Virtual environment Python vs system Python issue?
A: If `python` command uses system Python despite activated venv, it might be aliased. Use `python3` or full path `./venv/bin/python`

---

## Flash Card Tips
- Review error messages and their solutions
- Practice AWS CLI commands
- Memorize the OAuth flow
- Understand when to use each AWS service
- Know security best practices by heart