# API Credentials Setup Guide

This guide walks you through obtaining all necessary API credentials for the Twitter bot project. Store all credentials securely and never commit them to git.

## 1. AWS API Credentials

### Prerequisites
- AWS account created and logged in
- Access to AWS Console

### Steps to Create IAM User and Access Keys

#### 1.1 Navigate to IAM
1. Log into AWS Console: https://console.aws.amazon.com
2. Search for "IAM" in the search bar
3. Click on "IAM" (Identity and Access Management)

#### 1.2 Create IAM User
1. Click **"Users"** in the left sidebar
2. Click **"Create user"** button
3. User details:
   - Username: `twitter-bot-dev`
   - ✅ Provide user access to the AWS Management Console (optional)
   - Console password: Custom password or auto-generated
4. Click **"Next"**

#### 1.3 Set Permissions
1. Select **"Attach policies directly"**
2. Search and select:
   - `PowerUserAccess` (temporary - will restrict later)
3. Click **"Next"**
4. Review and click **"Create user"**

#### 1.4 Generate Access Keys
1. Click on the username `twitter-bot-dev`
2. Go to **"Security credentials"** tab
3. Under "Access keys", click **"Create access key"**
4. Select use case: **"Command Line Interface (CLI)"**
5. Check the confirmation box
6. Click **"Next"**
7. Description tag: `Twitter bot CLI access`
8. Click **"Create access key"**

#### 1.5 Save Credentials
**⚠️ CRITICAL: Save these immediately - you won't see the secret again!**

Download the .csv file or copy:
- **Access Key ID**: `AKIA...` (20 characters)
- **Secret Access Key**: `wJal...` (40 characters)
- **Region**: `us-east-1` (or your preferred region)

---

## 2. Gmail API Credentials

### Prerequisites
- Google account
- Access to Google Cloud Console

### Steps to Enable Gmail API

#### 2.1 Create Google Cloud Project
1. Go to https://console.cloud.google.com
2. Click **"Select a project"** dropdown → **"New Project"**
3. Project details:
   - Project name: `twitter-bot-gmail`
   - Organization: Leave as-is
   - Location: Leave as-is
4. Click **"Create"**
5. Wait for project creation (spinner in top right)

#### 2.2 Enable Gmail API
1. Ensure your new project is selected (top dropdown)
2. In search bar, type **"Gmail API"**
3. Click on **"Gmail API"** from results
4. Click **"Enable"** button
5. Wait for API to enable

#### 2.3 Configure OAuth Consent Screen
1. Click **"OAuth consent screen"** in left sidebar
2. User type: Select **"External"**
3. Click **"Create"**
4. App information:
   - App name: `Twitter Bot Email Reader`
   - User support email: Your email
   - Developer contact: Your email
   - Leave other fields blank
5. Click **"Save and Continue"**

#### 2.4 Add Scopes
1. Click **"Add or Remove Scopes"**
2. Search for and select:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/pubsub` (for push notifications)
3. Click **"Update"**
4. Click **"Save and Continue"**

#### 2.5 Add Test Users (if in testing mode)
1. Click **"Add Users"**
2. Add your email address: `t.speekenbrink+xposts@gmail.com`
3. Click **"Save and Continue"**

#### 2.6 Create OAuth 2.0 Client ID
1. Go to **"Credentials"** in left sidebar
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `Twitter Bot Client`
5. Authorized redirect URIs - Add:
   - `http://localhost:8080`
   - `http://localhost:8080/callback`
   - `https://YOUR-API-GATEWAY-URL/callback` (update later)
6. Click **"Create"**

#### 2.7 Download Credentials
1. In the popup, click **"Download JSON"**
2. Save the file as `gmail_credentials.json`
3. Contains:
   - **Client ID**: `123456789-abcdef.apps.googleusercontent.com`
   - **Client Secret**: `GOCSPX-...`

#### 2.8 Set Up Pub/Sub for Push Notifications
1. Search for **"Pub/Sub"** in Google Cloud Console
2. Click **"Create Topic"**
3. Topic ID: `gmail-push-notifications`
4. Click **"Create"**
5. Note the topic name: `projects/PROJECT_ID/topics/gmail-push-notifications`

---

## 3. Twitter/X API Credentials

### Prerequisites
- Twitter/X account
- Phone number verified on account

### Steps to Get Twitter API Access

#### 3.1 Apply for Developer Account
1. Go to https://developer.twitter.com
2. Click **"Sign up"** or **"Apply"**
3. Verify your account details
4. Select account type:
   - **"Hobbyist"** → **"Making a bot"**
5. Describe your use:
   ```
   Personal automation bot that:
   - Receives emails sent to my email address
   - Translates content to Japanese using AI
   - Posts translations to my Twitter account
   - No data collection or analysis
   - Single user, personal use only
   ```
6. Answer additional questions:
   - Government use: No
   - Tweet/Retweet/Like: Yes (posting only)
   - Display tweets outside Twitter: No
   - Aggregate data: No
7. Review and accept terms
8. Submit application
9. Verify email if required

#### 3.2 Create a Project and App
1. Once approved, go to Developer Portal
2. Click **"+ Create Project"**
3. Project details:
   - Name: `Email to Japanese Twitter Bot`
   - Use case: **"Making a bot"**
4. Click **"Next"**
5. Project description: `Automated posting of email content in Japanese`
6. Click **"Next"**
7. Create an App:
   - App name: `tycho-email-bot-2025` (must be globally unique)
   - Click **"Next"**

#### 3.3 Save Your Keys
**⚠️ CRITICAL: Save these immediately!**

You'll see your keys once:
- **API Key** (Consumer Key): 25 characters
- **API Key Secret** (Consumer Secret): 50 characters

Click **"App settings"** to continue.

#### 3.4 Generate Access Token
1. Go to **"Keys and tokens"** tab
2. Under "Authentication Tokens", find **"Access Token and Secret"**
3. Click **"Generate"**
4. Save:
   - **Access Token**: 50+ characters with hyphen
   - **Access Token Secret**: 45 characters

#### 3.5 Configure App Permissions
1. Go to **"Settings"** → **"User authentication settings"**
2. Click **"Set up"**
3. Configure:
   - App permissions: **"Read and write"**
   - Type of App: **"Web App, Automated App or Bot"**
   - App info:
     - Callback URI: `http://localhost:3000/callback`
     - Website URL: `https://example.com` (or your website)
   - Terms of service: `https://example.com/terms` (optional)
   - Privacy policy: `https://example.com/privacy` (optional)
4. Click **"Save"**

---

## 4. AWS Bedrock (Claude) Access

### Prerequisites
- AWS account with billing enabled
- IAM user created (from step 1)

### Steps to Enable Bedrock

#### 4.1 Navigate to Bedrock
1. In AWS Console, search for **"Bedrock"**
2. Click **"Amazon Bedrock"**
3. If first time, click **"Get started"**

#### 4.2 Request Model Access
1. Click **"Model access"** in left sidebar
2. Click **"Manage model access"** button
3. Find in the list:
   - **Claude 3 Opus** (Anthropic)
   - **Claude 3 Sonnet** (Anthropic)
   - **Claude 3 Haiku** (Anthropic)
4. Check the boxes for the models you want
5. Click **"Request model access"**

#### 4.3 Complete Access Request
1. Fill out the form:
   - Use case: `Personal project - automated content translation`
   - Customer data: No
   - Expected requests: Less than 1,000/month
   - Data sensitivity: No PII or sensitive data
2. Click **"Submit"**
3. Wait for approval (usually instant for personal accounts)

#### 4.4 Verify Access
1. Refresh the page
2. Status should show **"Access granted"**
3. Note the model IDs:
   - Claude 3 Opus: `anthropic.claude-3-opus-20240229-v1:0`
   - Claude 3 Sonnet: `anthropic.claude-3-sonnet-20240229-v1:0`

---

## 5. Credentials Checklist

After completing all steps, you should have:

### AWS Credentials
- [ ] Access Key ID: `AKIA...` (20 chars)
- [ ] Secret Access Key: `...` (40 chars)
- [ ] Default Region: `us-east-1`
- [ ] Bedrock Model Access: Granted

### Gmail API Credentials
- [ ] Client ID: `...-....apps.googleusercontent.com`
- [ ] Client Secret: `GOCSPX-...`
- [ ] Redirect URIs configured
- [ ] Pub/Sub topic created
- [ ] Downloaded `gmail_credentials.json`

### Twitter API Credentials
- [ ] API Key: (25 characters)
- [ ] API Key Secret: (50 characters)
- [ ] Access Token: (50+ characters)
- [ ] Access Token Secret: (45 characters)
- [ ] App permissions: Read and Write

---

## 6. Secure Storage

### Local Development (.env file)
Create a `.env` file in your project root:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

# Gmail API
GMAIL_CLIENT_ID=...-....apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-...
GMAIL_REDIRECT_URI=http://localhost:8080
GMAIL_PUBSUB_TOPIC=projects/twitter-bot-gmail/topics/gmail-push-notifications

# Twitter API
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...-...
TWITTER_ACCESS_TOKEN_SECRET=...

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-opus-20240229-v1:0
```

### Important Security Notes
1. **Add `.env` to `.gitignore`** immediately
2. Never commit credentials to version control
3. Use AWS Secrets Manager for production
4. Rotate credentials regularly
5. Use least-privilege IAM policies

---

## 7. Testing Your Credentials

### Test AWS CLI
```bash
aws configure
aws sts get-caller-identity
```

### Test Bedrock Access
```bash
aws bedrock list-foundation-models --region us-east-1
```

### Test Gmail API (requires additional OAuth flow)
```python
# We'll implement this in the code
```

### Test Twitter API
```bash
curl -X GET "https://api.twitter.com/2/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Troubleshooting

### AWS Issues
- "Invalid credentials": Regenerate access keys
- "Access denied": Check IAM permissions
- "Model not found": Ensure Bedrock access is granted

### Gmail Issues
- "Redirect URI mismatch": Update OAuth client settings
- "Scope not authorized": Re-configure consent screen
- "Invalid client": Check client ID format

### Twitter Issues
- "Read-only application": Update app permissions
- "Invalid token": Regenerate tokens
- "Rate limited": Check API limits

---

## Next Steps
1. Configure AWS CLI with credentials
2. Store credentials in `.env` file
3. Test each service individually
4. Move to AWS Secrets Manager for production

---

Last Updated: 2025-08-02