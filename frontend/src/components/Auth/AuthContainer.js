import React, { useState } from 'react';
import SignIn from './SignIn';
import SignUp from './SignUp';
import Verification from './Verification';

const AuthContainer = ({ onSignIn, onSignUp, onVerify }) => {
    const [view, setView] = useState('signin'); // signin, signup, verify, forgot
    const [pendingEmail, setPendingEmail] = useState('');

    const handleSignUp = async (username, email, password) => {
        await onSignUp(username, email, password);
        setPendingEmail(email);
        setView('verify');
    };

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
            <div className="max-w-md w-full bg-gray-800 rounded-xl shadow-2xl p-8">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-blue-500 mb-2">Trade Quest</h1>
                    <p className="text-gray-400">Cloud-Native Trading Simulator</p>
                </div>

                {view === 'signin' && (
                    <SignIn
                        onSignIn={onSignIn}
                        onSwitchToSignUp={() => setView('signup')}
                        onSwitchToForgotPassword={() => setView('forgot')}
                    />
                )}

                {view === 'signup' && (
                    <SignUp
                        onSignUp={handleSignUp}
                        onSwitchToSignIn={() => setView('signin')}
                    />
                )}

                {view === 'verify' && (
                    <Verification
                        email={pendingEmail}
                        onVerify={onVerify}
                        onSwitchToSignIn={() => setView('signin')}
                    />
                )}
            </div>
        </div>
    );
};

export default AuthContainer;
