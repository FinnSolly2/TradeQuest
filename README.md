# Trade Quest - Cloud-Native Trading Simulator

A serverless trading simulator built on AWS that simulates real market dynamics using Finnhub API data, AI-generated news, and cloud-native architecture.

## Architecture Overview

```
┌─────────────┐
│   Finnhub   │
│     API     │
└──────┬──────┘
       │
       v
┌─────────────────────────────────────────────────────────┐
│                    AWS CLOUD                            │
│                                                         │
│  ┌─────────────┐    ┌──────────────┐                  │
│  │ EventBridge │───>│Step Functions│                  │
│  │  (Hourly)   │    │  Workflow    │                  │
│  └─────────────┘    └──────┬───────┘                  │
│                             │                           │
│                     ┌───────┴───────┐                  │
│                     │                │                  │
│              ┌──────v──────┐ ┌──────v────────┐        │
│              │  Finnhub    │ │    Price      │        │
│              │   Fetcher   │ │  Simulator    │        │
│              │   Lambda    │ │   Lambda      │        │
│              └──────┬──────┘ └───────┬───────┘        │
│                     │                 │                 │
│                     v                 v                 │
│              ┌─────────────────────────┐               │
│              │      S3 Buckets         │               │
│              │ (Market Data & News)    │               │
│              └──────────┬──────────────┘               │
│                         │                               │
│                         v                               │
│              ┌──────────────────┐                      │
│              │   News Generator │                      │
│              │  Lambda (AI)     │                      │
│              └──────────────────┘                      │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │           API Gateway (HTTP)                 │     │
│  └──────────┬───────────────────────────────────┘     │
│             │                                           │
│      ┌──────┴──────────┬────────┬──────────┐          │
│      v                  v        v          v          │
│  ┌────────┐      ┌──────────┐ ┌──────┐ ┌─────────┐   │
│  │Get     │      │Execute   │ │Get   │ │Get      │   │
│  │Prices  │      │Trade     │ │News  │ │Portfolio│   │
│  │Lambda  │      │Lambda    │ │Lambda│ │Lambda   │   │
│  └────────┘      └──────────┘ └──────┘ └─────────┘   │
│      │                 │          │          │         │
│      └────────┬────────┴──────────┴──────────┘         │
│               v                                         │
│      ┌────────────────┐      ┌─────────────┐          │
│      │   DynamoDB     │      │   Cognito   │          │
│      │   Tables       │      │   (Auth)    │          │
│      └────────────────┘      └─────────────┘          │
└─────────────────────────────────────────────────────────┘
                          │
                          v
                 ┌─────────────────┐
                 │  Frontend HTML  │
                 │   (Browser)     │
                 └─────────────────┘
```

## Features

- **Real-Time Market Data**: Fetches live prices from Finnhub API every hour
- **Price Simulation**: Uses Geometric Brownian Motion to generate realistic price movements
- **AI-Generated News**: Creates contextual market news using Hugging Face API
- **Trading Engine**: Buy/sell assets with portfolio tracking and P/L calculation
- **Leaderboard**: Compete with other users based on trading performance
- **Serverless Architecture**: Fully managed AWS services with auto-scaling
- **Event-Driven**: Automated workflows using EventBridge and Step Functions

## Prerequisites

Before deployment, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Terraform** (v1.6.0 or higher)
4. **Python 3.11** or higher
5. **Finnhub API Key** (free tier available)
6. **Hugging Face API Key** (optional, falls back to templates)

## Project Structure

```
trade-quest/
├── terraform/
│   ├── main.tf              # Main infrastructure
│   ├── variables.tf         # Variable definitions
│   ├── outputs.tf          # Output values
│   ├── providers.tf        # Provider configuration
│   ├── versions.tf         # Version constraints
│   └── terraform.tfvars    # Your configuration values
├── lambda_functions/
│   ├── finnhub_fetcher/    # Fetches real market data
│   ├── price_simulator/    # Simulates price movements
│   ├── news_generator/     # Generates AI news
│   ├── api_get_prices/     # API: Get current prices
│   ├── api_get_news/       # API: Get latest news
│   ├── api_execute_trade/  # API: Execute trades
│   ├── api_get_portfolio/  # API: Get user portfolio
│   ├── api_get_leaderboard/# API: Get leaderboard
│   └── session_checker/    # Check active sessions
├── frontend/
│   ├── index.html          # Main webpage
│   ├── style.css           # Styling
│   └── app.js              # JavaScript logic
├── deploy.sh               # Deployment script (Linux/Mac)
├── deploy.bat              # Deployment script (Windows)
└── README.md               # This file
```

## Quick Start

### Step 1: Configure Your API Keys

Edit `terraform/terraform.tfvars`:

```hcl
finnhub_api_key = "YOUR_FINNHUB_API_KEY"
huggingface_api_key = "YOUR_HUGGINGFACE_API_KEY"  # or "demo" for fallback
```

### Step 2: Deploy Infrastructure

**On Windows:**
```batch
deploy.bat
```

**On Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Package all Lambda functions with dependencies
2. Initialize Terraform
3. Create an execution plan
4. Deploy all AWS resources

### Step 3: Update Frontend

After deployment completes, copy the API Gateway URL from the output and update `frontend/app.js`:

```javascript
const API_BASE_URL = 'https://YOUR_API_GATEWAY_URL/prod';
```

### Step 4: Access the Application

Open `frontend/index.html` in your web browser.

### Step 5: Trigger First Data Fetch (Optional)

The system fetches data every hour automatically. To trigger immediately:

```bash
aws stepfunctions start-execution \
  --state-machine-arn $(terraform output -raw simulation_state_machine_arn) \
  --region eu-west-1
```

## Configuration

### Assets to Track

Edit `terraform/terraform.tfvars` to change tracked assets:

```hcl
assets_to_track = [
  "AAPL",
  "GOOGL",
  "MSFT",
  # Add more symbols...
]
```

### Schedule Configuration

Modify schedules in `terraform/terraform.tfvars`:

```hcl
# Fetch data every hour
data_fetch_schedule = "cron(0 * * * ? *)"

# Release news every 15 minutes
news_release_schedule = "rate(15 minutes)"
```

## AWS Resources Created

The deployment creates the following AWS resources:

### Storage
- **3 S3 Buckets**: Market data, news, Lambda artifacts
- **4 DynamoDB Tables**: Users, sessions, trades, leaderboard

### Compute
- **9 Lambda Functions**: Data processing and API endpoints
- **1 Step Functions State Machine**: Orchestration workflow

### API & Auth
- **1 API Gateway**: HTTP API with CORS enabled
- **1 Cognito User Pool**: User authentication (optional)

### Scheduling
- **2 EventBridge Rules**: Hourly data fetch, 15-min news release

### IAM
- **3 IAM Roles**: Lambda, Step Functions, EventBridge
- **3 IAM Policies**: Fine-grained permissions

## Cost Estimation

Estimated monthly costs (based on moderate usage):

| Service | Estimated Cost |
|---------|---------------|
| Lambda (9 functions) | ~$5-10 |
| DynamoDB (on-demand) | ~$2-5 |
| S3 Storage & Requests | ~$1-2 |
| API Gateway | ~$3-5 |
| Step Functions | ~$0.50 |
| **Total** | **~$12-23/month** |

*Note: Costs vary based on usage. AWS Free Tier covers most services initially.*

## Development

### Test Lambda Locally

```bash
cd lambda_functions/finnhub_fetcher
python3 finnhub_fetcher.py
```

### View Logs

```bash
aws logs tail /aws/lambda/trade-quest-finnhub-fetcher-dev --follow
```

### Manual Lambda Invocation

```bash
aws lambda invoke \
  --function-name trade-quest-finnhub-fetcher-dev \
  --payload '{}' \
  response.json
```

## Troubleshooting

### Lambda Package Too Large

If you get "Unzipped size must be smaller than 262144000 bytes":
- Remove unnecessary dependencies
- Use Lambda Layers for shared libraries

### CORS Errors

Ensure API Gateway has CORS enabled:
```hcl
cors_configuration {
  allow_origins = ["*"]
  allow_methods = ["GET", "POST", "OPTIONS"]
}
```

### No Data Showing

1. Check if Step Function has run: AWS Console → Step Functions
2. Verify S3 buckets have data
3. Check Lambda logs for errors
4. Ensure Finnhub API key is valid

### Terraform Errors

```bash
cd terraform
terraform destroy  # Clean up
terraform init     # Reinitialize
terraform apply    # Redeploy
```

## Cleanup

To destroy all resources and avoid charges:

```bash
cd terraform
terraform destroy
```

Then manually delete:
- S3 buckets (if versioning enabled)
- CloudWatch Logs

## Security Considerations

1. **API Keys**: Stored as environment variables in Lambda, never committed to git
2. **IAM Roles**: Least privilege access for each service
3. **S3 Buckets**: Private by default
4. **DynamoDB**: Encrypted at rest
5. **API Gateway**: Can add Cognito authorizer for production

## Future Enhancements

- [ ] Add real-time WebSocket updates
- [ ] Implement user authentication with Cognito
- [ ] Add more sophisticated trading strategies
- [ ] Create mobile-responsive design
- [ ] Add historical chart visualization
- [ ] Implement stop-loss/take-profit orders
- [ ] Add email notifications for large P/L changes
- [ ] Create admin dashboard

## License

This project is for educational purposes.

## Support

For issues or questions:
1. Check CloudWatch Logs
2. Review Terraform plan output
3. Verify AWS service quotas
4. Check Finnhub API rate limits

## Credits

- Market data: Finnhub API
- AI text generation: Hugging Face
- Cloud infrastructure: AWS
- Infrastructure as Code: Terraform
