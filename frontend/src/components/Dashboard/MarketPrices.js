import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const MarketPrices = ({ prices, onTrade }) => {
    if (!prices || Object.keys(prices).length === 0) {
        return (
            <div className="bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-6 text-blue-400">Market Prices</h2>
                <p className="text-gray-400">Loading prices...</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6 text-blue-400">Market Prices</h2>
            <div className="space-y-3">
                {Object.entries(prices).map(([symbol, data]) => {
                    const change = data.current - data.hour_start;
                    const changePercent = (change / data.hour_start) * 100;
                    const isPositive = changePercent >= 0;

                    return (
                        <div
                            key={symbol}
                            className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-all duration-200 cursor-pointer transform hover:scale-[1.02]"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <div className="font-bold text-lg text-white mb-1">{symbol}</div>
                                    <div className="text-2xl font-bold text-white">
                                        ${data.current.toFixed(4)}
                                    </div>
                                    <div className={`flex items-center text-sm mt-1 ${
                                        isPositive ? 'text-green-400' : 'text-red-400'
                                    }`}>
                                        {isPositive ? (
                                            <TrendingUp className="w-4 h-4 mr-1" />
                                        ) : (
                                            <TrendingDown className="w-4 h-4 mr-1" />
                                        )}
                                        {isPositive ? '+' : ''}{change.toFixed(4)} ({isPositive ? '+' : ''}
                                        {changePercent.toFixed(2)}%)
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => onTrade(symbol, data.current)}
                                        className="bg-green-600 hover:bg-green-700 text-white font-semibold px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
                                    >
                                        BUY
                                    </button>
                                    <button
                                        onClick={() => onTrade(symbol, data.current)}
                                        className="bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105"
                                    >
                                        SELL
                                    </button>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default MarketPrices;
