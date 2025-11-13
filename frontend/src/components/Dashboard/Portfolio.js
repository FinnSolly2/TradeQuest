import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const Portfolio = ({ portfolioData }) => {
    if (!portfolioData || !portfolioData.positions) {
        return (
            <div className="bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-6 text-blue-400">My Portfolio</h2>
                <p className="text-gray-400">No positions yet</p>
            </div>
        );
    }

    const { positions } = portfolioData;

    if (positions.length === 0) {
        return (
            <div className="bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-6 text-blue-400">My Portfolio</h2>
                <p className="text-gray-400">No positions yet</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6 text-blue-400">My Portfolio</h2>
            <div className="space-y-3">
                {positions.map((position) => {
                    const isProfit = position.profit_loss >= 0;

                    return (
                        <div
                            key={position.symbol}
                            className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-all duration-200"
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className="font-bold text-xl text-blue-400">{position.symbol}</div>
                                <div className={`flex items-center font-bold ${
                                    isProfit ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {isProfit ? (
                                        <TrendingUp className="w-5 h-5 mr-1" />
                                    ) : (
                                        <TrendingDown className="w-5 h-5 mr-1" />
                                    )}
                                    {isProfit ? '+' : ''}${position.profit_loss.toFixed(2)} (
                                    {isProfit ? '+' : ''}
                                    {position.profit_loss_percent.toFixed(2)}%)
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-3 text-sm text-gray-300">
                                <div>
                                    <span className="text-gray-400">Quantity:</span>
                                    <span className="ml-2 font-semibold">{position.quantity}</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Avg Price:</span>
                                    <span className="ml-2 font-semibold">${position.avg_price.toFixed(4)}</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Current:</span>
                                    <span className="ml-2 font-semibold">${position.current_price.toFixed(4)}</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Value:</span>
                                    <span className="ml-2 font-semibold">${position.market_value.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Portfolio;
