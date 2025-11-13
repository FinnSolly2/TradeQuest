import React, { useState } from 'react';
import { UserPlus } from 'lucide-react';

const SignUp = ({ onSignUp, onSwitchToSignIn }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');

        if (password !== confirmPassword) {
            setMessage('Passwords do not match');
            return;
        }

        if (password.length < 8) {
            setMessage('Password must be at least 8 characters');
            return;
        }

        setLoading(true);

        try {
            await onSignUp(username, email, password);
            setMessage('Verification code sent to your email!');
        } catch (error) {
            setMessage(error.message || 'Sign up failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form">
            <div className="flex items-center justify-center mb-6">
                <UserPlus className="w-12 h-12 text-blue-500" />
            </div>
            <h2 className="text-2xl font-bold text-center mb-2 text-white">Sign Up</h2>
            <p className="text-center text-gray-400 mb-6 text-sm">Start with $100,000 to trade!</p>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <input
                        type="text"
                        placeholder="Username (3-20 chars)"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        minLength={3}
                        maxLength={20}
                        required
                    />
                </div>
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
                        placeholder="Password (min 8 chars)"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        minLength={8}
                        required
                    />
                </div>
                <div>
                    <input
                        type="password"
                        placeholder="Confirm Password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    />
                </div>
                {message && (
                    <div className={`p-3 rounded-lg text-sm ${
                        message.includes('sent')
                            ? 'bg-green-900/50 text-green-300'
                            : 'bg-red-900/50 text-red-300'
                    }`}>
                        {message}
                    </div>
                )}
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50"
                >
                    {loading ? 'Signing Up...' : 'Sign Up'}
                </button>
            </form>
            <div className="mt-6 text-center">
                <p className="text-gray-400 text-sm">
                    Already have an account?{' '}
                    <button onClick={onSwitchToSignIn} className="text-blue-500 hover:text-blue-400 font-semibold">
                        Sign In
                    </button>
                </p>
            </div>
        </div>
    );
};

export default SignUp;
