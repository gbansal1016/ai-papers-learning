# FinAgent — Personal Finance AI Agent

A personal finance AI agent built on AWS, implementing the **Externalization in LLM Agents** framework (Zhou et al., 2026). The agent manages a 4-tier memory system, executes trades via Alpaca, delivers daily market briefings, and learns your investing behavior over time through episodic → semantic memory consolidation.

---

## Architecture

```
Browser (chat.html / index.html)
    ↓  Cognito JWT
API Gateway
    ↓
AgentFunction          → POST /chat           (Strands + Claude Sonnet)
ApprovalFunction       → GET/POST /approval   (trade approve/cancel)
BriefingFunction       → EventBridge 7am PST  (daily market email)
ConsolidationFunction  → EventBridge Monday   (episodic → semantic memory)
    ↓
DynamoDB (4-tier memory)   S3 (skill files)   SSM (API keys)
```

**Memory tiers (Zhou et al. §3.1):**
| Tier | Sort key prefix | TTL |
|---|---|---|
| Working | `WORKING#<session_id>` | 24h |
| Episodic | `EPISODIC#<timestamp>` | 90 days |
| Semantic | `SEMANTIC#<topic>` | permanent |
| Personal | `PERSONAL#profile` | permanent |

---

## Prerequisites

- AWS CLI configured (`aws configure`)
- SAM CLI installed (`brew install aws-sam-cli`)
- Python 3.12 + virtualenv
- Accounts: [Alpaca](https://alpaca.markets) (paper trading), [Polygon.io](https://polygon.io) (free tier), [Alpha Vantage](https://alphavantage.co) (free tier)

---

## Deploy

```bash
cd infrastructure
python -m venv .venv && source .venv/bin/activate
pip install aws-sam-cli

sam build
sam deploy --guided   # first time — saves config to samconfig.toml
```

After deploy, note the CloudFormation outputs:
```
AgentApiEndpoint    = https://<id>.execute-api.us-west-2.amazonaws.com/dev
UserPoolId          = us-west-2_<id>
UserPoolClientId    = <client-id>
FrontendUrl         = https://<id>.cloudfront.net
FrontendBucketName  = finagent-frontend-dev-<account-id>
```

---

## Configure API Keys

Store your API keys in SSM Parameter Store (never in code):

```bash
aws ssm put-parameter --name "/finagent/alpaca_api_key"     --value "YOUR_KEY"    --type SecureString
aws ssm put-parameter --name "/finagent/alpaca_secret_key"  --value "YOUR_SECRET" --type SecureString
aws ssm put-parameter --name "/finagent/polygon_api_key"    --value "YOUR_KEY"    --type SecureString
aws ssm put-parameter --name "/finagent/alpha_vantage_key"  --value "YOUR_KEY"    --type SecureString
```

---

## Update Frontend Config

After deploy, update these 3 lines in `frontend/chat.html` and `frontend/index.html`:

```javascript
const COGNITO_USER_POOL_ID = "us-west-2_YOUR_POOL_ID";      // UserPoolId output
const COGNITO_CLIENT_ID    = "YOUR_CLIENT_ID";               // UserPoolClientId output
const API_BASE             = "YOUR_API_GATEWAY_URL";         // AgentApiEndpoint output (without /chat)
```

Then upload to S3:
```bash
aws s3 cp frontend/chat.html  s3://finagent-frontend-dev-<account-id>/chat.html
aws s3 cp frontend/index.html s3://finagent-frontend-dev-<account-id>/index.html
aws s3 cp frontend/favicon.png s3://finagent-frontend-dev-<account-id>/favicon.png
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

---

## Create a User

```bash
aws cognito-idp admin-create-user \
  --user-pool-id YOUR_POOL_ID \
  --username user@example.com \
  --user-attributes Name=email,Value=user@example.com Name=email_verified,Value=true \
  --temporary-password "TempPass@123" \
  --message-action SUPPRESS

aws cognito-idp admin-set-user-password \
  --user-pool-id YOUR_POOL_ID \
  --username user@example.com \
  --password "PermanentPass@123" \
  --permanent
```

Add them to the users table so they get briefings:
```bash
aws dynamodb put-item \
  --table-name finagent-users-dev \
  --item '{
    "user_id":          {"S": "user@example.com"},
    "is_active":        {"BOOL": true},
    "briefing_enabled": {"BOOL": true},
    "timezone":         {"S": "America/Los_Angeles"},
    "notifications":    {"M": {"email": {"S": "user@example.com"}}}
  }'
```

---

## Upload Skills

```bash
aws s3 cp skills/general_finance.md   s3://finagent-skills-dev-<account-id>/
aws s3 cp skills/trade_execution.md   s3://finagent-skills-dev-<account-id>/
aws s3 cp skills/market_briefing.md   s3://finagent-skills-dev-<account-id>/
```

---

## Test

```bash
# Test daily briefing
aws lambda invoke \
  --function-name finagent-briefing-dev \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out response.json && cat response.json

# Run memory consolidation (episodic → semantic via LLM)
aws lambda invoke \
  --function-name finagent-consolidation-dev \
  --payload '{"user_id": "user@example.com"}' \
  --cli-binary-format raw-in-base64-out response.json && cat response.json

# Tail agent logs
aws logs tail /aws/lambda/finagent-agent-dev --follow
```

---

## Project Structure

```
personal-finance-agent/
├── agent/
│   ├── agent_core.py          # Lambda handlers + Strands agent + tools
│   ├── memory/
│   │   └── ddb_memory.py      # 4-tier DynamoDB memory store
│   └── requirements.txt
├── frontend/
│   ├── chat.html              # Chat UI (update Cognito/API config after deploy)
│   ├── index.html             # Trade approval page
│   └── favicon.png
├── infrastructure/
│   └── template.yaml          # SAM / CloudFormation
├── skills/
│   ├── general_finance.md
│   ├── trade_execution.md
│   └── market_briefing.md
└── design/
    ├── AGENT_SPECIFICATION.md
    └── AWS_RESOURCES.md
```

---

## Reference

- [Externalization in LLM Agents — Zhou et al. 2026](https://arxiv.org/abs/2506.09583)
- [AWS Strands SDK](https://strandsagents.com)
- [Alpaca Markets API](https://docs.alpaca.markets)
- [Polygon.io API](https://polygon.io/docs)
