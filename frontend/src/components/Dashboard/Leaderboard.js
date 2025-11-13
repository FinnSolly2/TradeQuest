import React from 'react';
import { Trophy } from 'lucide-react';

const Leaderboard = ({ leaderboard }) => {
    if (!leaderboard || leaderboard.length === 0) {
        return (
            <div className="bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-6 text-blue-400 flex items-center">
                    <Trophy className="w-6 h-6 mr-2" />
                    Leaderboard
                </h2>
                <p className="text-gray-400">No leaderboard data available</p>
            </div>
        );
    }

    const getMedal = (rank) => {
        switch (rank) {
            case 1:
                return '🥇';
            case 2:
                return '🥈';
            case 3:
                return '🥉';
            default:
                return '';
        }
    };

    return (
        <div className="bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6 text-blue-400 flex items-center">
                <Trophy className="w-6 h-6 mr-2" />
                Leaderboard
            </h2>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="text-left border-b border-gray-700">
                            <th className="pb-3 text-gray-400 font-semibold text-sm">Rank</th>
                            <th className="pb-3 text-gray-400 font-semibold text-sm">Username</th>
                            <th className="pb-3 text-gray-400 font-semibold text-sm">Total Value</th>
                            <th className="pb-3 text-gray-400 font-semibold text-sm">P/L</th>
                            <th className="pb-3 text-gray-400 font-semibold text-sm">Trades</th>
                        </tr>
                    </thead>
                    <tbody>
                        {leaderboard.map((entry) => {
                            const isProfit = entry.profit_loss >= 0;
                            return (
                                <tr
                                    key={entry.user_id}
                                    className="border-b border-gray-700 hover:bg-gray-700 transition-colors duration-200"
                                >
                                    <td className="py-3 text-white">
                                        <span className="text-xl mr-2">{getMedal(entry.rank)}</span>
                                        {entry.rank}
                                    </td>
                                    <td className="py-3 text-white font-medium">
                                        {entry.username || entry.user_id}
                                    </td>
                                    <td className="py-3 text-white font-semibold">
                                        ${entry.total_value.toFixed(2)}
                                    </td>
                                    <td className={`py-3 font-bold ${
                                        isProfit ? 'text-green-400' : 'text-red-400'
                                    }`}>
                                        {isProfit ? '+' : ''}${entry.profit_loss.toFixed(2)} (
                                        {isProfit ? '+' : ''}
                                        {entry.profit_loss_percent.toFixed(2)}%)
                                    </td>
                                    <td className="py-3 text-gray-300">{entry.total_trades}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Leaderboard;
