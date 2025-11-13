import React, { useState, useEffect } from 'react';
import { Menu, LogOut, RefreshCw } from 'lucide-react';
import { useAuth } from './hooks/useAuth';
import { API_BASE_URL } from './config';
import AuthContainer from './components/Auth/AuthContainer';
import MarketPrices from './components/Dashboard/MarketPrices';
import Portfolio from './components/Dashboard/Portfolio';
import News from './components/Dashboard/News';
import Leaderboard from './components/Dashboard/Leaderboard';
import TradeModal from './components/Dashboard/TradeModal';

function App() {
    const { user, loading: authLoading, signIn, signUp, confirmSignUp, signOut } = useAuth();
    const [prices, setPrices] = useState({});
    const [portfolioData, setPortfolioData] = useState(null);
    const [news, setNews] = useState([]);
    const [leaderboard, setLeaderboard] = useState([]);
    const [tradeModal, setTradeModal] = useState({ isOpen: false, asset: null });

    // Auto-refresh intervals
    useEffect(() => {
        if (user) {
            loadUserData();
            const portfolioInterval = setInterval(loadUserData, 1000);
            return () => clearInterval(portfolioInterval);
        }
    }, [user]);

    useEffect(() => {
        refreshPrices();
        refreshNews();
        refreshLeaderboard();

        const pricesInterval = setInterval(refreshPrices, 1000);
        const newsInterval = setInterval(refreshNews, 10000);

        return () => {
            clearInterval(pricesInterval);
            clearInterval(newsInterval);
        };
    }, []);

    const loadUserData = async () => {
        if (!user) return;

        try {
            const response = await fetch(`${API_BASE_URL}/portfolio?user_id=${user.userId}`, {
                headers: {
                    'Authorization': `Bearer ${user.token}`
                }
            });
            const result = await response.json();

            if (result.success) {
                setPortfolioData(result.data);
            }
        } catch (error) {
            console.error('Error loading portfolio:', error);
        }
    };

    const refreshPrices = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/prices`);
            const result = await response.json();

            if (result.success) {
                setPrices(result.data.prices);
            }
        } catch (error) {
            console.error('Error fetching prices:', error);
        }
    };

    const refreshNews = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/news`);
            const result = await response.json();

            if (result.success) {
                setNews(result.data.articles);
            }
        } catch (error) {
            console.error('Error fetching news:', error);
        }
    };

    const refreshLeaderboard = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/leaderboard`);
            const result = await response.json();

            if (result.success) {
                setLeaderboard(result.data.leaderboard);
            }
        } catch (error) {
            console.error('Error fetching leaderboard:', error);
        }
    };

    const handleTrade = (symbol, price) => {
        if (!user) return;
        setTradeModal({ isOpen: true, asset: { symbol, price } });
    };

    const handleExecuteTrade = async (symbol, action, quantity) => {
        if (!user) throw new Error('Please sign in to trade');

        const response = await fetch(`${API_BASE_URL}/trade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${user.token}`
            },
            body: JSON.stringify({
                user_id: user.userId,
                symbol: symbol,
                action: action,
                quantity: quantity
            })
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.message);
        }

        await loadUserData();
        return result;
    };

    if (authLoading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-white text-xl">Loading...</div>
            </div>
        );
    }

    if (!user) {
        return (
            <AuthContainer
                onSignIn={signIn}
                onSignUp={signUp}
                onVerify={confirmSignUp}
            />
        );
    }

    const balance = portfolioData?.balance || 0;
    const portfolioValue = portfolioData?.portfolio_value || 0;
    const totalValue = portfolioData?.total_value || 0;
    const profitLoss = portfolioData?.total_profit_loss || 0;
    const profitLossPercent = portfolioData?.total_profit_loss_percent || 0;

    const holdings = portfolioData?.positions?.find(p => p.symbol === tradeModal.asset?.symbol)?.quantity || 0;

    return (
        <div className="bg-gray-900 text-white min-h-screen font-sans flex flex-col">
            {/* Header */}
            <header className="bg-gray-800 p-4 flex items-center justify-between shadow-lg">
                <div className="flex items-center space-x-6">
                    <span className="text-3xl font-bold text-blue-500">TQ</span>
                    <div className="hidden md:block">
                        <h1 className="text-xl font-bold text-white">Trade Quest</h1>
                        <p className="text-sm text-gray-400">Cloud-Native Trading Simulator</p>
                    </div>
                </div>
                <div className="flex items-center space-x-4">
                    <span className="hidden sm:block text-sm text-gray-300 bg-gray-700 px-4 py-2 rounded-full">
                        {user.email}
                    </span>
                    <button
                        onClick={signOut}
                        className="bg-blue-600 hover:bg-blue-700 rounded-full p-2 transition-colors duration-200"
                        title="Sign Out"
                    >
                        <LogOut className="w-5 h-5" />
                    </button>
                </div>
            </header>

            {/* Balance Display */}
            <div className="bg-gray-800 m-6 rounded-xl shadow-lg p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-all">
                        <div className="text-gray-400 text-sm mb-1">Cash Balance</div>
                        <div className="text-2xl font-bold text-white">${balance.toFixed(2)}</div>
                    </div>
                    <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-all">
                        <div className="text-gray-400 text-sm mb-1">Portfolio Value</div>
                        <div className="text-2xl font-bold text-white">${portfolioValue.toFixed(2)}</div>
                    </div>
                    <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-all">
                        <div className="text-gray-400 text-sm mb-1">Total Value</div>
                        <div className="text-2xl font-bold text-white">${totalValue.toFixed(2)}</div>
                    </div>
                    <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-all">
                        <div className="text-gray-400 text-sm mb-1">P/L</div>
                        <div className={`text-2xl font-bold ${profitLoss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {profitLoss >= 0 ? '+' : ''}${profitLoss.toFixed(2)} ({profitLoss >= 0 ? '+' : ''}
                            {profitLossPercent.toFixed(2)}%)
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-grow px-6 pb-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <MarketPrices prices={prices} onTrade={handleTrade} />
                    <Portfolio portfolioData={portfolioData} />
                </div>

                <div className="grid grid-cols-1 gap-6">
                    <News articles={news} />
                    <Leaderboard leaderboard={leaderboard} />
                </div>
            </main>

            {/* Trade Modal */}
            <TradeModal
                isOpen={tradeModal.isOpen}
                onClose={() => setTradeModal({ isOpen: false, asset: null })}
                asset={tradeModal.asset}
                balance={balance}
                holdings={holdings}
                onExecuteTrade={handleExecuteTrade}
            />
        </div>
    );
}

export default App;
