# Frontend Authentication Setup

After deploying the Terraform infrastructure, you need to update the Cognito configuration in the frontend.

## Steps:

### 1. Get Cognito Configuration Values

Run the following command in the `terraform` directory:

```bash
cd terraform
terraform output
```

You will see outputs like:
```
cognito_user_pool_id = "eu-west-1_XXXXXXXXX"
cognito_user_pool_client_id = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
cognito_identity_pool_id = "eu-west-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
cognito_domain = "trade-quest-dev-XXXXXXXX"
cognito_region = "eu-west-1"
```

### 2. Update `frontend/config.js`

Open `frontend/config.js` and update the following values:

```javascript
const AWS_CONFIG = {
    region: 'eu-west-1',  // From cognito_region
    userPoolId: 'YOUR_USER_POOL_ID',  // From cognito_user_pool_id
    userPoolWebClientId: 'YOUR_CLIENT_ID',  // From cognito_user_pool_client_id
    identityPoolId: 'YOUR_IDENTITY_POOL_ID',  // From cognito_identity_pool_id
    oauth: {
        domain: 'YOUR_COGNITO_DOMAIN.auth.eu-west-1.amazoncognito.com',  // From cognito_domain + region
        // ... rest stays the same
    }
};
```

### 3. Deploy Frontend

After updating the config, deploy the frontend to S3:

```bash
# Upload to S3
aws s3 sync frontend/ s3://YOUR_FRONTEND_BUCKET/ --exclude "*.md"

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

Or the deployment will happen automatically via GitHub Actions.

## Features

- Sign Up with email verification
- Sign In with email and password
- Password reset flow
- JWT-based authentication for protected API routes
- Automatic session management
- Sign out functionality

## Protected Routes

The following API endpoints require authentication:
- `POST /trade` - Execute trades
- `GET /portfolio` - Get user portfolio

## Public Routes

The following API endpoints are public:
- `GET /prices` - Get market prices
- `GET /news` - Get market news
- `GET /leaderboard` - Get leaderboard

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
