import React, { useState } from 'react';
import { Mail } from 'lucide-react';

const Verification = ({ email, onVerify, onSwitchToSignIn }) => {
    const [code, setCode] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setLoading(true);

        try {
            await onVerify(email, code);
            setMessage('Account verified! You can now sign in.');
            setTimeout(() => onSwitchToSignIn(), 2000);
        } catch (error) {
            setMessage(error.message || 'Verification failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form">
            <div className="flex items-center justify-center mb-6">
                <Mail className="w-12 h-12 text-blue-500" />
            </div>
            <h2 className="text-2xl font-bold text-center mb-2 text-white">Verify Email</h2>
            <p className="text-center text-gray-400 mb-6 text-sm">
                A verification code has been sent to {email}
            </p>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <input
                        type="text"
                        placeholder="Verification Code"
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    />
                </div>
                {message && (
                    <div className={`p-3 rounded-lg text-sm ${
                        message.includes('verified')
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
                    {loading ? 'Verifying...' : 'Verify'}
                </button>
            </form>
            <div className="mt-6 text-center">
                <button onClick={onSwitchToSignIn} className="text-blue-500 hover:text-blue-400 text-sm font-semibold">
                    Back to Sign In
                </button>
            </div>
        </div>
    );
};

export default Verification;
