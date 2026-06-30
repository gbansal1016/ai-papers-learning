# FinAgent — AWS Resources Guide
**Personal Finance AI Agent** | AWS Agent Core + Strands SDK + DynamoDB  
Based on: *Externalization in LLM Agents* (Zhou et al., 2026)

> **Tip (VS Code):** Press `Cmd+Shift+V` to open the Markdown preview panel.

---

## Resource Summary

| # | Resource Type | Count | Method | Notes |
|---|---------------|-------|--------|-------|
| 1 | DynamoDB Tables | 4 | SAM deploy | Memory, approvals, OAuth tokens, users |
| 2 | S3 Bucket | 1 | SAM deploy | Skill SKILL.md files (versioned) |
| 3 | Lambda Functions | 3 | SAM deploy | Agent, briefing, approval handler |
| 4 | API Gateway | 1 REST API | SAM deploy | 3 endpoints |
| 5 | Cognito | 1 User Pool + 1 Client | SAM deploy | JWT auth for API Gateway |
| 6 | SNS Topics | 2 | SAM deploy | Trade approvals + daily briefings |
| 7 | EventBridge Scheduler | 1 | SAM deploy | Daily 7am PST briefing trigger |
| 8 | SSM Parameter Store | 8 parameters | Manual / CLI | All external API keys |
| 9 | CloudWatch | 3 log groups + 1 alarm | Auto-created | Lambda logs + error alert |
| 10 | IAM Roles & Policies | 3 execution roles | SAM deploy | Least-privilege per Lambda |
| 11 | Amazon Bedrock | 1 model | **Console — manual** | Claude 3.5 Sonnet v2 |

> ⚠️ All resources follow the naming pattern `finagent-{resource}-{env}` for environment isolation (dev / staging / prod).

---

## 1. DynamoDB Tables

### 1.1 `finagent-memory-{env}` — Primary Memory Store

Stores all 4 memory tiers: WORKING (24h TTL), EPISODIC (90d TTL), SEMANTIC (permanent), PERSONAL (permanent).

| Configuration | Value |
|---------------|-------|
| Billing Mode | PAY_PER_REQUEST (on-demand) |
| Table Class | STANDARD |
| Partition Key | `memory_type` (String) — `WORKING \| EPISODIC \| SEMANTIC \| PERSONAL` |
| Sort Key | `memory_id` (String) — timestamp-based ULID |
| TTL Attribute | `ttl` (Number, Unix epoch seconds) |
| Point-in-Time Recovery | **ENABLED** |
| GSI-1 Name | `userId-createdAt-index` |
| GSI-1 PK | `user_id` (String) |
| GSI-1 SK | `created_at` (String, ISO-8601) |
| GSI-1 Projection | ALL |

> ⚠️ TTL values: `WORKING` = now + 86,400s (24h) | `EPISODIC` = now + 7,776,000s (90d) | `SEMANTIC`/`PERSONAL` = no TTL

---

### 1.2 `finagent-approvals-{env}` — Pending Trade Approvals

Stores pending trade approval records. Records auto-expire after 5 minutes via TTL.

| Configuration | Value |
|---------------|-------|
| Billing Mode | PAY_PER_REQUEST |
| Partition Key | `approval_id` (String) |
| Sort Key | None |
| TTL Attribute | `ttl` (Number) — set to now + 300s (5 min) at creation |

---

### 1.3 `finagent-oauth-tokens-{env}` — External Service OAuth Tokens

Stores per-user OAuth tokens for Experian Connect and Plaid. Encrypted at rest by DynamoDB default KMS.

| Configuration | Value |
|---------------|-------|
| Billing Mode | PAY_PER_REQUEST |
| Partition Key | `userId` (String) |
| Sort Key | `provider` (String) — `"experian"` or `"plaid"` |
| Attributes | `access_token`, `refresh_token`, `expires_at`, `scope` |

---

### 1.4 `finagent-users-{env}` — User Registry

Stores registered users and notification preferences. Read by all Lambdas; written only during onboarding.

| Configuration | Value |
|---------------|-------|
| Billing Mode | PAY_PER_REQUEST |
| Partition Key | `userId` (String) — Cognito sub (UUID) |
| Key attributes | `email`, `is_active`, `briefing_email`, `created_at`, `notification_arn` |

---

## 2. S3 Bucket

### `finagent-skills-{env}-{accountId}` — Skill File Storage

Stores declarative SKILL.md files that the agent loads at runtime (progressive disclosure, paper §4.3).  
Account ID in the name ensures global uniqueness.

| Configuration | Value |
|---------------|-------|
| Versioning | **ENABLED** — allows skill rollback |
| Access | Private — Lambda reads via IAM role only, no public access |
| Encryption | SSE-S3 (default) |
| Lifecycle rule | Optional: expire old skill versions after 30 days |

**Files to upload after creation:**

```
portfolio_analysis.md
trade_execution.md
credit_health.md
market_briefing.md
stock_research.md
budget_analysis.md
```

---

## 3. Lambda Functions

### 3.1 `finagent-agent-{env}` — Main API Handler

Handles all synchronous user messages: memory retrieval → skill selection → Bedrock reasoning → tool calls → memory write.

| Configuration | Value |
|---------------|-------|
| Runtime | Python 3.12 |
| Handler | `agent_core.handler` |
| Memory | 512 MB |
| Timeout | 120 seconds |
| Trigger | API Gateway `POST /chat` (Cognito-authorized) |
| Env Variables | `MEMORY_DDB_TABLE`, `SKILLS_S3_BUCKET`, `APPROVAL_SNS_TOPIC_ARN`, `USERS_TABLE`, `APPROVALS_TABLE`, `OAUTH_TOKENS_TABLE`, `ALPACA_BASE_URL`, `AWS_REGION` |

**IAM Permissions:**
- `dynamodb:GetItem, PutItem, UpdateItem, DeleteItem, Query` → memory, approvals, oauth-tokens tables
- `dynamodb:GetItem, Query` → users table (read-only)
- `s3:GetObject` → skills bucket
- `ssm:GetParameter` → `/finagent/*`
- `sns:Publish` → approvals topic
- `bedrock:InvokeModel` → `anthropic.claude-sonnet-4-6`

---

### 3.2 `finagent-briefing-{env}` — Daily Market Briefing

Triggered at 7am PST daily. Fetches market data, composes briefing for each active user, pushes via SNS.

| Configuration | Value |
|---------------|-------|
| Runtime | Python 3.12 |
| Handler | `agent_core.market_briefing_handler` |
| Memory | 512 MB |
| Timeout | 300 seconds (5 min — iterates across multiple users) |
| Trigger | EventBridge Scheduler `cron(0 15 * * ? *)` |
| Timezone | `America/Los_Angeles` |
| Env Variables | Same as Agent Lambda |

**IAM Permissions:**
- `dynamodb:GetItem, PutItem, UpdateItem, Query` → memory table
- `dynamodb:GetItem, Query` → users table
- `s3:GetObject` → skills bucket
- `ssm:GetParameter` → `/finagent/*`
- `sns:Publish` → briefings topic
- `bedrock:InvokeModel` → Claude 3.5 Sonnet

---

### 3.3 `finagent-approval-{env}` — Trade Approval Callback

Receives CONFIRM or CANCEL decisions from the user (via email link) and writes them to the approvals table.

| Configuration | Value |
|---------------|-------|
| Runtime | Python 3.12 |
| Handler | `agent_core.approval_handler` |
| Memory | 256 MB |
| Timeout | 30 seconds |
| Triggers | `POST /approve/{approvalId}` and `POST /cancel/{approvalId}` |

**IAM Permissions:**
- `dynamodb:PutItem, UpdateItem` → approvals table only

---

## 4. API Gateway

One REST API with three endpoints. The `/chat` endpoint is Cognito-protected; approval endpoints use a token-in-URL pattern.

| Endpoint | Method | Lambda Target | Auth |
|----------|--------|---------------|------|
| `/chat` | POST | `finagent-agent` | Cognito Authorizer (JWT) |
| `/approve/{approvalId}` | POST | `finagent-approval` | None |
| `/cancel/{approvalId}` | POST | `finagent-approval` | None |

> ⚠️ Deploy a stage per environment. Set throttle: 100 req/sec burst, 50 req/sec steady state for dev.

---

## 5. Cognito

Manages user authentication and issues JWT tokens consumed by API Gateway.

| Resource | Configuration |
|----------|---------------|
| User Pool Name | `finagent-users-{env}` |
| Auto-verified attribute | email |
| Password policy | Min 8 chars, uppercase + number + symbol |
| MFA | Optional (recommend TOTP for prod) |
| User Pool Client Name | `finagent-web` |
| Client secret | None (public client, SRP auth flow) |
| Auth flows | `ALLOW_USER_SRP_AUTH`, `ALLOW_REFRESH_TOKEN_AUTH` |
| Token validity | Access token: 1 hour \| Refresh token: 30 days |

---

## 6. SNS Topics

Two email notification channels — one for trade approvals, one for daily briefings.

| Topic | Purpose | Protocol | Endpoint |
|-------|---------|----------|----------|
| `finagent-approvals-{env}` | Trade approval gate | Email | gtmrrental@gmail.com |
| `finagent-briefings-{env}` | Daily market briefing | Email | gtmrrental@gmail.com |

> ⚠️ Both subscriptions require email confirmation after creation. Check inbox and click the confirm link or notifications won't send.

---

## 7. EventBridge Scheduler

Triggers the daily market briefing Lambda at 7am PST every day.

| Configuration | Value |
|---------------|-------|
| Schedule Type | EventBridge **SchedulerV2** (not classic EventBridge Rules) |
| Schedule Expression | `cron(0 15 * * ? *)` |
| Human-readable | Every day at 15:00 UTC = 7:00am PST / 8:00am PDT |
| Timezone | `America/Los_Angeles` (auto-handles DST) |
| Flexible Time Window | OFF (fires exactly on time) |
| Target | `finagent-briefing-{env}` Lambda |
| Retry policy | 2 retries, 60s interval on Lambda error |

---

## 8. SSM Parameter Store

All 8 external API keys stored as **SecureString** (KMS encrypted). Create these manually before running `sam deploy`.

```bash
# Example — repeat for each key below
aws ssm put-parameter \
  --name /finagent/alpaca_api_key \
  --type SecureString \
  --value "YOUR_KEY_HERE"
```

| Parameter | Service | Where to Get It |
|-----------|---------|-----------------|
| `/finagent/alpaca_api_key` | Alpaca Markets | [alpaca.markets](https://alpaca.markets) → Paper Trading → API Keys |
| `/finagent/alpaca_secret_key` | Alpaca Markets | Same (shown once at creation) |
| `/finagent/polygon_api_key` | Polygon.io | [polygon.io/dashboard](https://polygon.io/dashboard) → API Keys (Starter plan for real-time) |
| `/finagent/alpha_vantage_key` | Alpha Vantage | [alphavantage.co](https://alphavantage.co) → Get Free API Key |
| `/finagent/plaid_client_id` | Plaid | [dashboard.plaid.com](https://dashboard.plaid.com) → Team Settings → Keys |
| `/finagent/plaid_secret` | Plaid | Same — use Sandbox secret for dev |
| `/finagent/experian_client_id` | Experian Connect | [connectapi.experian.com](https://connectapi.experian.com) → Developer Portal |
| `/finagent/experian_client_secret` | Experian Connect | Same |

> ⚠️ Never store API keys in Lambda environment variables or source code. SSM SecureString is the correct pattern. IAM scopes Lambda access to `/finagent/*` only.

---

## 9. CloudWatch

Log groups are auto-created on first Lambda invocation. Set retention to avoid unbounded storage costs.

### Log Groups

| Log Group | Lambda | Suggested Retention |
|-----------|--------|---------------------|
| `/aws/lambda/finagent-agent-{env}` | Agent handler | 30d (dev) / 90d (prod) |
| `/aws/lambda/finagent-briefing-{env}` | Market briefing | 30d (dev) / 90d (prod) |
| `/aws/lambda/finagent-approval-{env}` | Approval handler | 30d (dev) / 90d (prod) |

### Alarm — `finagent-errors-{env}`

| Configuration | Value |
|---------------|-------|
| Metric | `Errors` |
| Namespace | `AWS/Lambda` |
| Dimension | `FunctionName = finagent-agent-{env}` |
| Statistic | Sum |
| Period | 300 seconds |
| Threshold | >= 5 errors in one period |
| Action | Publish to `finagent-approvals` SNS topic (sends email) |

---

## 10. IAM Roles & Policies

Each Lambda gets its own execution role. Do not share roles across functions.

| Lambda | Permission | Resource Scope |
|--------|------------|----------------|
| `finagent-agent` | `dynamodb:GetItem, PutItem, UpdateItem, DeleteItem, Query` | memory, approvals, oauth-tokens tables |
| `finagent-agent` | `dynamodb:GetItem, Query` | users table |
| `finagent-agent` | `s3:GetObject` | skills bucket |
| `finagent-agent` | `ssm:GetParameter` | `/finagent/*` |
| `finagent-agent` | `sns:Publish` | approvals topic |
| `finagent-agent` | `bedrock:InvokeModel` | `arn:aws:bedrock:{region}::foundation-model/anthropic.claude-sonnet-4-6` |
| `finagent-briefing` | `dynamodb:GetItem, PutItem, UpdateItem, Query` | memory table |
| `finagent-briefing` | `dynamodb:GetItem, Query` | users table |
| `finagent-briefing` | `s3:GetObject` | skills bucket |
| `finagent-briefing` | `ssm:GetParameter` | `/finagent/*` |
| `finagent-briefing` | `sns:Publish` | briefings topic |
| `finagent-briefing` | `bedrock:InvokeModel` | Claude 3.5 Sonnet |
| `finagent-approval` | `dynamodb:PutItem, UpdateItem` | approvals table only |

---

## 11. Amazon Bedrock

> ⚠️ **Must be enabled manually in the AWS Console BEFORE `sam deploy`.** The Lambda IAM policy references this model ARN — deployment will fail if model access isn't granted first.

| Configuration | Value |
|---------------|-------|
| Model ID | `anthropic.claude-sonnet-4-6` |
| Supported regions | `us-west-2` (primary), `us-east-1` |
| Access type | On-demand (pay per token, no provisioned throughput needed at MVP) |
| How to enable | Console → Amazon Bedrock → Model access → Request access → Claude 3.5 Sonnet v2 |
| Context window | 200K tokens (agent uses ~20K per invocation) |
| Pricing | Input: $3.00/M tokens \| Output: $15.00/M tokens |

---

## Deployment Checklist

Follow this order — some steps block the ones after them.

| Step | Action | Method | Blocker? |
|------|--------|--------|----------|
| 1 | Enable Bedrock model access (Claude 3.5 Sonnet v2) | AWS Console | **YES — do this first** |
| 2 | Create all 8 SSM Parameter Store secrets | AWS CLI | **YES — Lambda fails without these** |
| 3 | Run `sam build && sam deploy --guided` | SAM CLI | Creates all remaining resources |
| 4 | Confirm both SNS email subscriptions (check inbox) | Email | **YES — no notifications until confirmed** |
| 5 | Upload SKILL.md files to S3 skills bucket | AWS CLI / Console | **YES — agent fails if skills missing** |
| 6 | Create a Cognito test user | AWS Console / CLI | Needed to test `/chat` endpoint |
| 7 | Test `/chat` endpoint with Postman or curl | HTTP client | Validates end-to-end flow |
| 8 | Check CloudWatch logs next morning to verify EventBridge briefing | CloudWatch | Confirms scheduled job works |

> ⚠️ Use Alpaca paper trading URL (`https://paper-api.alpaca.markets`) for all dev and staging. Switch `ALPACA_BASE_URL` to `https://api.alpaca.markets` for prod only.

---

## External API Sign-Up

Register for developer accounts at each service before deployment.

| Service | URL | Plan for MVP | Approx. Cost |
|---------|-----|--------------|--------------|
| Alpaca Markets | [alpaca.markets](https://alpaca.markets) | Paper trading | Free |
| Polygon.io | [polygon.io](https://polygon.io) | Starter (real-time data) | $29/month |
| Alpha Vantage | [alphavantage.co](https://alphavantage.co) | Free tier (25 calls/day) | Free |
| Plaid | [dashboard.plaid.com](https://dashboard.plaid.com) | Sandbox (dev) → Development (prod) | Free dev / usage-based prod |
| Experian Connect | [connectapi.experian.com](https://connectapi.experian.com) | Developer Portal | Contact Experian |
