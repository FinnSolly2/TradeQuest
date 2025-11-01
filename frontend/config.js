// AWS Cognito Configuration
// IMPORTANT: Update these values after deploying Terraform infrastructure
// Run: cd terraform && terraform output
// to get these values

const AWS_CONFIG = {
    region: 'eu-west-1',
    userPoolId: 'YOUR_USER_POOL_ID',  // From terraform output: cognito_user_pool_id
    userPoolWebClientId: 'YOUR_CLIENT_ID',  // From terraform output: cognito_user_pool_client_id
    identityPoolId: 'YOUR_IDENTITY_POOL_ID',  // From terraform output: cognito_identity_pool_id
    oauth: {
        domain: 'YOUR_COGNITO_DOMAIN.auth.eu-west-1.amazoncognito.com',  // From terraform output: cognito_domain
        scope: ['email', 'openid', 'profile'],
        redirectSignIn: window.location.origin,
        redirectSignOut: window.location.origin,
        responseType: 'code'
    }
};

// API Configuration
const API_BASE_URL = 'https://cseoi2lxp7.execute-api.eu-west-1.amazonaws.com/prod';
