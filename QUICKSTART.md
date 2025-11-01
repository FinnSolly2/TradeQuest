# Trade Quest - Quick Start Guide

Get your trading simulator up and running in 5 minutes!

## Prerequisites Check

Run these commands to verify you have everything installed:

```bash
# Check Python
python --version
# Should show: Python 3.11.x or higher

# Check AWS CLI
aws --version
# Should show: aws-cli/2.x.x

# Check Terraform
terraform --version
# Should show: Terraform v1.6.x or higher

# Check AWS credentials
aws sts get-caller-identity
# Should show your AWS account info
```

If any of these fail, refer to the installation instructions in the main README.

## Step-by-Step Deployment

### 1. Get Your API Keys

**Finnhub API Key** (Required):
1. Go to https://finnhub.io/register
2. Sign up for a free account
3. Copy your API key (looks like: `csjfk1hr01qvuv6vvgq0...`)

**Hugging Face API Key** (Optional):
1. Go to https://huggingface.co/settings/tokens
2. Create a new token
3. Copy it (or use "demo" for fallback mode)

### 2. Configure the Project

Open `terraform/terraform.tfvars` and update:

```hcl
finnhub_api_key = "YOUR_FINNHUB_API_KEY_HERE"
huggingface_api_key = "demo"  # or your HuggingFace key
```

### 3. Deploy to AWS

**On Windows:**
```cmd
deploy.bat
```

**On Mac/Linux:**
```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Package all Lambda functions (~2 minutes)
- Initialize Terraform
- Show you what will be created
- Ask for confirmation
- Deploy everything to AWS (~5-10 minutes)

### 4. Get Your API URL

After deployment, you'll see output like:

```
API Gateway URL: https://abc123xyz.execute-api.eu-west-1.amazonaws.com/prod
```

**Copy this URL!**

### 5. Update Frontend

Open `frontend/app.js` and replace line 2:

```javascript
// Change this:
const API_BASE_URL = 'https://YOUR_API_GATEWAY_URL/prod';

// To this (use your actual URL):
const API_BASE_URL = 'https://abc123xyz.execute-api.eu-west-1.amazonaws.com/prod';
```

### 6. Launch the App

Simply open `frontend/index.html` in your web browser!

### 7. Trigger First Data Fetch

The system automatically fetches data every hour. To get data immediately:

```bash
# Get the state machine ARN
cd terraform
terraform output simulation_state_machine_arn

# Trigger it manually
aws stepfunctions start-execution \
  --state-machine-arn "YOUR_ARN_HERE" \
  --region eu-west-1
```

Or just wait up to 1 hour for the automatic fetch.

## Verify Everything Works

### Check Lambda Functions

```bash
# List all functions
aws lambda list-functions --query "Functions[?contains(FunctionName, 'trade-quest')].FunctionName"

# Test the Finnhub fetcher
aws lambda invoke \
  --function-name trade-quest-finnhub-fetcher-dev \
  --payload '{}' \
  response.json

cat response.json
```

### Check S3 Buckets

```bash
# List buckets
aws s3 ls | grep trade-quest

# Check if data exists
aws s3 ls s3://trade-quest-market-data-dev/raw_data/
```

### Check DynamoDB Tables

```bash
# List tables
aws dynamodb list-tables --query "TableNames[?contains(@, 'trade-quest')]"
```

### View Logs

```bash
# Finnhub fetcher logs
aws logs tail /aws/lambda/trade-quest-finnhub-fetcher-dev --follow

# Price simulator logs
aws logs tail /aws/lambda/trade-quest-price-simulator-dev --follow
```

## Testing the Application

1. **Open the frontend** in your browser
2. **Enter a User ID** (any string, e.g., "user123")
3. **Click "Load Account"** - you'll start with $100,000
4. **Wait for prices to load** (may take a few seconds)
5. **Click BUY on any asset**
6. **Enter quantity** and click BUY button
7. **Refresh your portfolio** to see your purchase

## Troubleshooting

### "No price data available"

**Cause**: Data hasn't been fetched yet

**Solution**:
```bash
# Manually trigger the Step Function
aws stepfunctions start-execution \
  --state-machine-arn $(cd terraform && terraform output -raw simulation_state_machine_arn) \
  --region eu-west-1
```

Wait 2-3 minutes and refresh.

### "Failed to load prices. Please check API configuration"

**Cause**: Frontend can't reach API Gateway

**Solution**:
1. Check you updated `frontend/app.js` with correct API URL
2. Open browser console (F12) to see exact error
3. Verify API Gateway is deployed: `aws apigatewayv2 get-apis`

### "ERROR: Terraform init failed"

**Cause**: Terraform configuration issue

**Solution**:
```bash
cd terraform
rm -rf .terraform
terraform init
```

### Lambda package size error

**Cause**: Dependencies are too large for Lambda

**Solution**: Use Lambda Layers (advanced) or optimize dependencies

### CORS errors in browser

**Cause**: API Gateway CORS not configured

**Solution**: Already configured in Terraform. If still occurring, check browser console for specific error.

### Rate limiting from Finnhub

**Cause**: Free tier allows 60 calls/minute

**Solution**: The fetcher includes 1.1 second delay between calls. Should not be an issue.

## Cost Management

To check your AWS costs:
```bash
# View current month costs
aws ce get-cost-and-usage \
  --time-period Start=2025-11-01,End=2025-11-30 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## Cleanup

When you're done testing, destroy everything to avoid charges:

```bash
cd terraform
terraform destroy
```

Type `yes` when prompted.

**Note**: You may need to manually empty and delete S3 buckets if versioning is enabled.

## Next Steps

Now that everything is running:

1. **Invite friends** - Share the frontend HTML file
2. **Compete** - Check the leaderboard
3. **Customize** - Modify assets in `terraform/terraform.tfvars`
4. **Extend** - Add more Lambda functions for custom features

## Common Workflows

### Change Tracked Assets

1. Edit `terraform/terraform.tfvars`:
   ```hcl
   assets_to_track = [
     "AAPL",
     "TSLA",
     "BTC-USD"
   ]
   ```

2. Redeploy:
   ```bash
   cd terraform
   terraform apply
   ```

### Update Lambda Function Code

1. Edit the Python file in `lambda_functions/<function_name>/`
2. Re-run deployment script:
   ```bash
   deploy.bat  # or ./deploy.sh
   ```

### View Real-Time Logs

```bash
# Terminal 1 - Finnhub fetcher
aws logs tail /aws/lambda/trade-quest-finnhub-fetcher-dev --follow

# Terminal 2 - Price simulator
aws logs tail /aws/lambda/trade-quest-price-simulator-dev --follow

# Terminal 3 - News generator
aws logs tail /aws/lambda/trade-quest-news-generator-dev --follow
```

## Getting Help

If you encounter issues:

1. **Check CloudWatch Logs** for error messages
2. **Review Terraform output** for deployment errors
3. **Verify API keys** are correct in terraform.tfvars
4. **Check AWS service quotas** (Lambda concurrent executions, etc.)

## Architecture Diagram

```
User Browser
     ↓
  Frontend (HTML/JS)
     ↓
  API Gateway
     ↓
  Lambda Functions
     ↓
  DynamoDB + S3
     ↑
  Step Functions
     ↑
  EventBridge (Scheduler)
     ↑
  Finnhub API
```

Happy Trading! 🚀📈
