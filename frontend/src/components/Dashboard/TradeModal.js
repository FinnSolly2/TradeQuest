import React, { useState } from 'react';
import { X } from 'lucide-react';

const TradeModal = ({ isOpen, onClose, asset, balance, holdings, onExecuteTrade }) => {
    const [quantity, setQuantity] = useState(1);
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    if (!isOpen || !asset) return null;

    const handleTrade = async (action) => {
        setMessage('');
        setLoading(true);

        try {
            await onExecuteTrade(asset.symbol, action, quantity);
            setMessage(`${action.toUpperCase()} order executed successfully!`);
            setTimeout(() => {
                onClose();
                setMessage('');
                setQuantity(1);
            }, 1500);
        } catch (error) {
            setMessage(error.message || 'Trade failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-xl shadow-2xl max-w-md w-full p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-white">Execute Trade</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="space-y-4 mb-6">
                    <div className="bg-gray-700 rounded-lg p-4">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="text-gray-400">Asset:</span>
                                <span className="ml-2 text-white font-bold">{asset.symbol}</span>
                            </div>
                            <div>
                                <span className="text-gray-400">Price:</span>
                                <span className="ml-2 text-white font-bold">${asset.price.toFixed(4)}</span>
                            </div>
                            <div>
                                <span className="text-gray-400">Cash:</span>
                                <span className="ml-2 text-white font-bold">${balance.toFixed(2)}</span>
                            </div>
                            <div>
                                <span className="text-gray-400">Holdings:</span>
                                <span className="ml-2 text-white font-bold">{holdings} shares</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label className="block text-gray-400 text-sm font-semibold mb-2">
                            Quantity
                        </label>
                        <input
                            type="number"
                            min="1"
                            value={quantity}
                            onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                            className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    {message && (
                        <div className={`p-3 rounded-lg text-sm font-semibold ${
                            message.includes('successfully')
                                ? 'bg-green-900/50 text-green-300'
                                : 'bg-red-900/50 text-red-300'
                        }`}>
                            {message}
                        </div>
                    )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <button
                        onClick={() => handleTrade('buy')}
                        disabled={loading}
                        className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50"
                    >
                        BUY
                    </button>
                    <button
                        onClick={() => handleTrade('sell')}
                        disabled={loading}
                        className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50"
                    >
                        SELL
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TradeModal;
