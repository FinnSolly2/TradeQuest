// AWS Cognito Configuration
// IMPORTANT: Update these values after deploying Terraform infrastructure
// Run: cd terraform && terraform output
// to get these values

const AWS_CONFIG = {
    region: 'eu-west-1',
    userPoolId: 'eu-west-1_9xwU22S9A',  // From terraform output: cognito_user_pool_id
    userPoolWebClientId: '4927evlbod672h6m0h2boja5ns',  // From terraform output: cognito_user_pool_client_id
    identityPoolId: 'eu-west-1:d1eaa64c-d9c3-4e40-98f7-9f0ef9d48ba0',  // From terraform output: cognito_identity_pool_id
    oauth: {
        domain: 'trade-quest-dev-uhmdl40t.auth.eu-west-1.amazoncognito.com',  // From terraform output: cognito_domain
        scope: ['email', 'openid', 'profile'],
        redirectSignIn: window.location.origin,
        redirectSignOut: window.location.origin,
        responseType: 'code'
    }
};

// API Configuration
const API_BASE_URL = 'https://cseoi2lxp7.execute-api.eu-west-1.amazonaws.com/prod';
