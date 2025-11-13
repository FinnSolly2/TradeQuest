import { useState, useEffect } from 'react';
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';
import { AWS_CONFIG } from '../config';

const userPool = new CognitoUserPool({
    UserPoolId: AWS_CONFIG.userPoolId,
    ClientId: AWS_CONFIG.userPoolWebClientId
});

export const useAuth = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = () => {
        const cognitoUser = userPool.getCurrentUser();
        if (cognitoUser) {
            cognitoUser.getSession((err, session) => {
                if (err || !session.isValid()) {
                    setUser(null);
                    setLoading(false);
                    return;
                }
                setUser({
                    email: cognitoUser.getUsername(),
                    userId: session.getIdToken().payload.sub,
                    token: session.getIdToken().getJwtToken()
                });
                setLoading(false);
            });
        } else {
            setLoading(false);
        }
    };

    const signIn = (email, password) => {
        return new Promise((resolve, reject) => {
            const authenticationDetails = new AuthenticationDetails({
                Username: email,
                Password: password
            });

            const cognitoUser = new CognitoUser({
                Username: email,
                Pool: userPool
            });

            cognitoUser.authenticateUser(authenticationDetails, {
                onSuccess: (session) => {
                    setUser({
                        email: cognitoUser.getUsername(),
                        userId: session.getIdToken().payload.sub,
                        token: session.getIdToken().getJwtToken()
                    });
                    resolve(session);
                },
                onFailure: (err) => {
                    reject(err);
                }
            });
        });
    };

    const signUp = (username, email, password) => {
        return new Promise((resolve, reject) => {
            userPool.signUp(email, password, [
                { Name: 'email', Value: email },
                { Name: 'preferred_username', Value: username }
            ], null, (err, result) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(result);
            });
        });
    };

    const confirmSignUp = (email, code) => {
        return new Promise((resolve, reject) => {
            const cognitoUser = new CognitoUser({
                Username: email,
                Pool: userPool
            });

            cognitoUser.confirmRegistration(code, true, (err, result) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(result);
            });
        });
    };

    const signOut = () => {
        const cognitoUser = userPool.getCurrentUser();
        if (cognitoUser) {
            cognitoUser.signOut();
        }
        setUser(null);
    };

    const forgotPassword = (email) => {
        return new Promise((resolve, reject) => {
            const cognitoUser = new CognitoUser({
                Username: email,
                Pool: userPool
            });

            cognitoUser.forgotPassword({
                onSuccess: () => resolve(),
                onFailure: (err) => reject(err)
            });
        });
    };

    const confirmPassword = (email, code, newPassword) => {
        return new Promise((resolve, reject) => {
            const cognitoUser = new CognitoUser({
                Username: email,
                Pool: userPool
            });

            cognitoUser.confirmPassword(code, newPassword, {
                onSuccess: () => resolve(),
                onFailure: (err) => reject(err)
            });
        });
    };

    return {
        user,
        loading,
        signIn,
        signUp,
        confirmSignUp,
        signOut,
        forgotPassword,
        confirmPassword
    };
};
