import React, { useState } from 'react';
import { LogIn } from 'lucide-react';

const SignIn = ({ onSignIn, onSwitchToSignUp, onSwitchToForgotPassword }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setLoading(true);

        try {
            await onSignIn(email, password);
        } catch (error) {
            setMessage(error.message || 'Sign in failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form">
            <div className="flex items-center justify-center mb-6">
                <LogIn className="w-12 h-12 text-blue-500" />
            </div>
            <h2 className="text-2xl font-bold text-center mb-6 text-white">Sign In</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    />
                </div>
                <div>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    />
                </div>
                {message && (
                    <div className="p-3 bg-red-900/50 text-red-300 rounded-lg text-sm">
                        {message}
                    </div>
                )}
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50"
                >
                    {loading ? 'Signing In...' : 'Sign In'}
                </button>
            </form>
            <div className="mt-6 text-center space-y-2">
                <p className="text-gray-400 text-sm">
                    Don't have an account?{' '}
                    <button onClick={onSwitchToSignUp} className="text-blue-500 hover:text-blue-400 font-semibold">
                        Sign Up
                    </button>
                </p>
                <button onClick={onSwitchToForgotPassword} className="text-blue-500 hover:text-blue-400 text-sm font-semibold">
                    Forgot Password?
                </button>
            </div>
        </div>
    );
};

export default SignIn;
