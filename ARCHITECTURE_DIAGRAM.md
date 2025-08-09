# Twitter Bot Architecture Diagram (Simplified)

## Visual Architecture Overview

```mermaid
graph TB
    subgraph "External Services"
        Gmail[Gmail API<br/>📧]
        Twitter[Twitter/X API<br/>🐦]
        Bedrock[AWS Bedrock<br/>Claude 3.5 Sonnet<br/>🤖]
    end
    
    subgraph "AWS Infrastructure"
        subgraph "Trigger"
            EventBridge[EventBridge Schedule<br/>⏰ Every 5 minutes]
        end
        
        subgraph "Lambda Functions (3)"
            GmailPoller[Lambda: Gmail Poller<br/>256MB / 60s<br/>📥]
            ContentProcessor[Lambda: Content Processor<br/>512MB / 120s<br/>🔄]
            TwitterPoster[Lambda: Twitter Poster<br/>256MB / 60s<br/>📤]
        end
        
        subgraph "Message Queues"
            EmailQueue[SQS: Email Queue<br/>14 day retention<br/>📨]
            TwitterQueue[SQS: Twitter Queue<br/>14 day retention<br/>💬]
        end
        
        subgraph "Storage"
            ProcessedEmails[(DynamoDB<br/>processed-emails<br/>📊)]
            AppState[(DynamoDB<br/>app-state<br/>💾)]
            Secrets[Secrets Manager<br/>API Credentials<br/>🔐]
        end
        
        subgraph "Monitoring"
            CloudWatch[CloudWatch Logs<br/>📝]
        end
    end
    
    %% Connections
    EventBridge -->|Trigger| GmailPoller
    Gmail -->|Pull emails| GmailPoller
    GmailPoller -->|Check state| AppState
    GmailPoller -->|Send message| EmailQueue
    GmailPoller -->|Update timestamp| AppState
    
    EmailQueue -->|SQS Trigger<br/>Batch: 10| ContentProcessor
    ContentProcessor -->|Check duplicate| ProcessedEmails
    ContentProcessor -->|Call AI| Bedrock
    ContentProcessor -->|Mark processed| ProcessedEmails
    ContentProcessor -->|Queue tweet| TwitterQueue
    
    TwitterQueue -->|SQS Trigger<br/>Batch: 1| TwitterPoster
    TwitterPoster -->|Post tweet| Twitter
    TwitterPoster -->|Update status| ProcessedEmails
    
    Secrets -.->|Credentials| GmailPoller
    Secrets -.->|Credentials| TwitterPoster
    
    GmailPoller -->|Logs| CloudWatch
    ContentProcessor -->|Logs| CloudWatch
    TwitterPoster -->|Logs| CloudWatch
    
    style Gmail fill:#EA4335
    style Twitter fill:#1DA1F2
    style Bedrock fill:#FF9900
    style EventBridge fill:#FF9900
    style EmailQueue fill:#FF9900
    style TwitterQueue fill:#FF9900
    style ProcessedEmails fill:#3949AB
    style AppState fill:#3949AB
    style Secrets fill:#D13212
    style CloudWatch fill:#759C3E
```

## Data Flow Sequence (Simplified)

```mermaid
sequenceDiagram
    participant EB as EventBridge
    participant GP as Gmail Poller
    participant GM as Gmail API
    participant EQ as Email Queue
    participant CP as Content Processor
    participant AI as Bedrock AI
    participant TQ as Twitter Queue
    participant TP as Twitter Poster
    participant TW as Twitter API
    participant DB as DynamoDB
    
    EB->>GP: Trigger (every 5 min)
    GP->>DB: Get last check timestamp
    GP->>GM: Fetch new emails
    GM-->>GP: Email data
    GP->>DB: Check if already processed
    GP->>EQ: Queue new email
    GP->>DB: Update timestamp
    
    EQ->>CP: Trigger with email
    CP->>DB: Check if processed
    alt Not processed
        CP->>AI: Generate Japanese tweet
        AI-->>CP: Japanese text (280 chars)
        CP->>DB: Mark as processed
        CP->>TQ: Queue tweet
    else Already processed
        CP->>CP: Skip
    end
    
    TQ->>TP: Trigger with tweet
    TP->>TW: Post tweet
    TW-->>TP: Tweet ID
    TP->>DB: Update with tweet ID
```

## Component Details (Simplified)

### 🔵 **Trigger Layer**
- **EventBridge**: Scheduled trigger every 5 minutes (polling only)

### 🟢 **Processing Layer (3 Lambdas)**
- **Gmail Poller**: Fetches new emails from Gmail
- **Content Processor**: Translates to Japanese using AI (512MB/120s)
- **Twitter Poster**: Posts to Twitter API

### 🟡 **Queue Layer**
- **Email Queue**: Decouples email fetching from processing
- **Twitter Queue**: Decouples AI processing from Twitter posting

### 🔴 **Storage Layer**
- **DynamoDB Tables**: Track state and prevent duplicates
- **Secrets Manager**: Secure credential storage

### ⚫ **Monitoring Layer**
- **CloudWatch Logs**: Centralized logging for all Lambda functions

## Key Design Patterns

1. **Pull-Based Architecture**: System polls Gmail (no webhooks needed)
2. **Event-Driven Processing**: SQS triggers automate the flow
3. **Queue-Based Decoupling**: SQS ensures resilience and retry capability
4. **Serverless Computing**: No servers to manage, automatic scaling
5. **Idempotency**: DynamoDB tracking prevents duplicate processing

## Simplified Benefits

- **No API Gateway**: No public endpoints to secure
- **No Webhooks**: No tokens to refresh or endpoints to maintain
- **Single Path**: One clear flow from Gmail to Twitter
- **3 Lambdas Only**: Minimal components to manage
- **Pull Model**: System controls when to check for emails

## Resilience Features

- **Automatic Retries**: SQS handles failed messages with exponential backoff
- **14-Day Message Retention**: Long retention period prevents data loss
- **State Tracking**: DynamoDB ensures consistency across restarts
- **Error Isolation**: Queue decoupling prevents cascading failures