// API Configuration
export const API_BASE_URL = 'https://cseoi2lxp7.execute-api.eu-west-1.amazonaws.com/prod';

// AWS Cognito Configuration
export const AWS_CONFIG = {
    region: 'eu-west-1',
    userPoolId: 'eu-west-1_mg32ltx41',
    userPoolWebClientId: '3s9jdapqe6b2ov2jcsvmhf14ut',
    identityPoolId: 'eu-west-1:d1eaa64c-d9c3-4e40-98f7-9f0ef9d48ba0',
    oauth: {
        domain: 'trade-quest-dev-uhmdl40t.auth.eu-west-1.amazoncognito.com',
        scope: ['email', 'openid', 'profile'],
        redirectSignIn: typeof window !== 'undefined' ? window.location.origin : '',
        redirectSignOut: typeof window !== 'undefined' ? window.location.origin : '',
        responseType: 'code'
    }
};
