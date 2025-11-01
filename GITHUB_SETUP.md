# GitHub Actions CI/CD Setup Guide

This guide will help you set up automated deployments for Trade Quest using GitHub Actions.

## Prerequisites

- GitHub account
- AWS Account with configured credentials
- Finnhub API key
- Hugging Face API key

## Step 1: Create GitHub Repository

```bash
cd trade-quest
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/trade-quest.git
git push -u origin main
```

## Step 2: Configure GitHub Secrets

Go to your GitHub repository settings → Secrets and variables → Actions

Add the following secrets:

### Required Secrets

1. **AWS_ACCESS_KEY_ID**
   - Your AWS access key ID
   - Used for deploying to AWS

2. **AWS_SECRET_ACCESS_KEY**
   - Your AWS secret access key
   - Used for deploying to AWS

3. **FINNHUB_API_KEY**
   - Your Finnhub API key for market data
   - Get it from: https://finnhub.io/

4. **HUGGINGFACE_API_KEY**
   - Your Hugging Face API key for AI news generation
   - Get it from: https://huggingface.co/settings/tokens

## Step 3: How CI/CD Works

### Automatic Deployment
Every time you push to the `main` branch, GitHub Actions will:

1. ✅ **Package Lambda Functions** - Build all 9 Lambda function ZIP files
2. ✅ **Deploy Infrastructure** - Run Terraform to update AWS resources
3. ✅ **Upload Frontend** - Sync frontend files to S3
4. ✅ **Invalidate Cache** - Clear CloudFront cache for instant updates

### Manual Deployment
You can also trigger deployments manually:
- Go to Actions tab → Deploy Trade Quest → Run workflow

## Step 4: Verify Deployment

After pushing to GitHub:

1. Go to the **Actions** tab in your repository
2. Click on the latest workflow run
3. Watch the deployment progress
4. Once complete, you'll see the frontend URL in the summary

## Step 5: Access Your Application

After successful deployment:

- **Frontend**: https://[cloudfront-domain].cloudfront.net
- **API**: https://cseoi2lxp7.execute-api.eu-west-1.amazonaws.com/prod

The frontend URL will be displayed in the GitHub Actions deployment summary.

## Workflow File

The workflow is defined in `.github/workflows/deploy.yml`

## Troubleshooting

### Deployment Fails

**Check secrets are set correctly:**
```
Settings → Secrets and variables → Actions
```

**Check Terraform state:**
The state is stored in S3: `trade-quest-terraform-state-dev`

### Lambda Package Issues

Lambda functions are packaged during the GitHub Actions run using Ubuntu, so they're always Linux-compatible.

### CloudFront Cache Issues

If you don't see frontend changes:
- The workflow automatically invalidates the CloudFront cache
- Wait 1-2 minutes for invalidation to complete
- Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)

## Cost Considerations

GitHub Actions provides:
- 2,000 free minutes/month for private repos
- Unlimited minutes for public repos

Each deployment takes ~3-5 minutes.

## Security Best Practices

✅ **Done:**
- Terraform state stored in S3 with encryption
- DynamoDB state locking enabled
- Secrets stored in GitHub (not in code)
- CloudFront uses HTTPS only

## Next Steps

1. **Custom Domain**: Add a custom domain to CloudFront
2. **Monitoring**: Set up CloudWatch alarms
3. **Staging Environment**: Create a `dev` branch for testing
4. **Automated Tests**: Add test step to workflow

## Additional Commands

### View Terraform Outputs
```bash
cd terraform
terraform output
```

### Manual Frontend Upload
```bash
aws s3 sync frontend/ s3://trade-quest-frontend-dev/ --delete
```

### Manual Cache Invalidation
```bash
aws cloudfront create-invalidation \
  --distribution-id [YOUR_DISTRIBUTION_ID] \
  --paths "/*"
```

## Support

For issues:
- Check GitHub Actions logs
- Review AWS CloudWatch logs
- Verify all secrets are set correctly
