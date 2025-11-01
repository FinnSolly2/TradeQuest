// Authentication Manager using Amazon Cognito
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.userPool = null;
        this.jwtToken = null;
    }

    // Initialize Cognito User Pool
    initialize() {
        const poolData = {
            UserPoolId: AWS_CONFIG.userPoolId,
            ClientId: AWS_CONFIG.userPoolWebClientId
        };
        this.userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

        // Check if user is already signed in
        this.checkAuthState();
    }

    // Check current authentication state
    checkAuthState() {
        const cognitoUser = this.userPool.getCurrentUser();

        if (cognitoUser) {
            cognitoUser.getSession((err, session) => {
                if (err) {
                    console.error('Session error:', err);
                    this.showAuthUI();
                    return;
                }

                if (session.isValid()) {
                    this.jwtToken = session.getIdToken().getJwtToken();
                    cognitoUser.getUserAttributes((err, attributes) => {
                        if (err) {
                            console.error('Error getting user attributes:', err);
                            return;
                        }

                        const email = attributes.find(attr => attr.Name === 'email')?.Value;
                        const userId = attributes.find(attr => attr.Name === 'sub')?.Value;

                        this.currentUser = {
                            cognitoUser,
                            userId,
                            email,
                            session
                        };

                        this.onSignInSuccess();
                    });
                } else {
                    this.showAuthUI();
                }
            });
        } else {
            this.showAuthUI();
        }
    }

    // Sign up new user
    signUp(email, password) {
        const attributeList = [];

        const dataEmail = {
            Name: 'email',
            Value: email
        };

        attributeList.push(new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail));

        return new Promise((resolve, reject) => {
            this.userPool.signUp(email, password, attributeList, null, (err, result) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(result);
            });
        });
    }

    // Confirm sign up with verification code
    confirmSignUp(email, code) {
        const userData = {
            Username: email,
            Pool: this.userPool
        };

        const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

        return new Promise((resolve, reject) => {
            cognitoUser.confirmRegistration(code, true, (err, result) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(result);
            });
        });
    }

    // Sign in user
    signIn(email, password) {
        const authenticationData = {
            Username: email,
            Password: password
        };

        const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);

        const userData = {
            Username: email,
            Pool: this.userPool
        };

        const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

        return new Promise((resolve, reject) => {
            cognitoUser.authenticateUser(authenticationDetails, {
                onSuccess: (session) => {
                    this.jwtToken = session.getIdToken().getJwtToken();

                    cognitoUser.getUserAttributes((err, attributes) => {
                        if (err) {
                            reject(err);
                            return;
                        }

                        const email = attributes.find(attr => attr.Name === 'email')?.Value;
                        const userId = attributes.find(attr => attr.Name === 'sub')?.Value;

                        this.currentUser = {
                            cognitoUser,
                            userId,
                            email,
                            session
                        };

                        resolve(session);
                        this.onSignInSuccess();
                    });
                },
                onFailure: (err) => {
                    reject(err);
                },
                newPasswordRequired: (userAttributes, requiredAttributes) => {
                    reject(new Error('New password required'));
                }
            });
        });
    }

    // Sign out user
    signOut() {
        if (this.currentUser && this.currentUser.cognitoUser) {
            this.currentUser.cognitoUser.signOut();
        }
        this.currentUser = null;
        this.jwtToken = null;
        this.showAuthUI();
    }

    // Get current JWT token
    getJwtToken() {
        return this.jwtToken;
    }

    // Get current user ID
    getUserId() {
        return this.currentUser ? this.currentUser.userId : null;
    }

    // Get current user email
    getUserEmail() {
        return this.currentUser ? this.currentUser.email : null;
    }

    // Check if user is authenticated
    isAuthenticated() {
        return this.currentUser !== null && this.jwtToken !== null;
    }

    // Show authentication UI
    showAuthUI() {
        document.getElementById('auth-container').style.display = 'flex';
        document.getElementById('app-container').style.display = 'none';
    }

    // Hide authentication UI and show app
    hideAuthUI() {
        document.getElementById('auth-container').style.display = 'none';
        document.getElementById('app-container').style.display = 'block';
    }

    // Handle successful sign in
    onSignInSuccess() {
        this.hideAuthUI();

        // Update user info display
        if (this.currentUser) {
            document.getElementById('user-email-display').textContent = this.currentUser.email;
        }

        // Load user data and refresh all data
        if (window.loadUserData) {
            window.loadUserData();
        }
        if (window.refreshPrices) {
            window.refreshPrices();
        }
        if (window.refreshNews) {
            window.refreshNews();
        }
        if (window.refreshLeaderboard) {
            window.refreshLeaderboard();
        }
    }

    // Resend verification code
    resendConfirmationCode(email) {
        const userData = {
            Username: email,
            Pool: this.userPool
        };

        const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

        return new Promise((resolve, reject) => {
            cognitoUser.resendConfirmationCode((err, result) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(result);
            });
        });
    }

    // Forgot password - initiate reset
    forgotPassword(email) {
        const userData = {
            Username: email,
            Pool: this.userPool
        };

        const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

        return new Promise((resolve, reject) => {
            cognitoUser.forgotPassword({
                onSuccess: (result) => {
                    resolve(result);
                },
                onFailure: (err) => {
                    reject(err);
                }
            });
        });
    }

    // Confirm password reset
    confirmPassword(email, verificationCode, newPassword) {
        const userData = {
            Username: email,
            Pool: this.userPool
        };

        const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

        return new Promise((resolve, reject) => {
            cognitoUser.confirmPassword(verificationCode, newPassword, {
                onSuccess: () => {
                    resolve();
                },
                onFailure: (err) => {
                    reject(err);
                }
            });
        });
    }
}

// Global auth manager instance
const authManager = new AuthManager();
