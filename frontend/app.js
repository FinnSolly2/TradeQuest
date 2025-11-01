// Configuration - Updated with deployed API Gateway URL
const API_BASE_URL = 'https://cseoi2lxp7.execute-api.eu-west-1.amazonaws.com/prod';

// Global state
let currentUser = 'user123';
let currentPrices = {};
let currentPortfolio = {};
let selectedAsset = null;

// Initialize on page load
window.onload = function() {
    loadUserData();
    refreshPrices();
    refreshNews();
    refreshLeaderboard();

    // Auto-refresh every minute (prices change minute-by-minute)
    setInterval(refreshPrices, 60000);
    setInterval(refreshNews, 60000);
};

// Load user data and portfolio
async function loadUserData() {
    const userId = document.getElementById('user-id').value || 'user123';
    currentUser = userId;

    try {
        const response = await fetch(`${API_BASE_URL}/portfolio?user_id=${userId}`);
        const result = await response.json();

        if (result.success) {
            const data = result.data;
            currentPortfolio = data;

            // Update balance display
            document.getElementById('balance').textContent = `$${data.balance.toFixed(2)}`;
            document.getElementById('portfolio-value').textContent = `$${data.portfolio_value.toFixed(2)}`;
            document.getElementById('total-value').textContent = `$${data.total_value.toFixed(2)}`;

            const plElement = document.getElementById('profit-loss');
            const pl = data.total_profit_loss;
            const plPercent = data.total_profit_loss_percent;
            plElement.textContent = `$${pl.toFixed(2)} (${plPercent >= 0 ? '+' : ''}${plPercent.toFixed(2)}%)`;
            plElement.style.color = pl >= 0 ? '#10b981' : '#ef4444';

            // Display portfolio positions
            displayPortfolio(data.positions);
        } else {
            console.error('Error loading portfolio:', result.message);
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        // Set default values
        document.getElementById('balance').textContent = '$100,000.00';
        document.getElementById('portfolio-value').textContent = '$0.00';
        document.getElementById('total-value').textContent = '$100,000.00';
        document.getElementById('profit-loss').textContent = '$0.00 (0.00%)';
    }
}

// Refresh market prices
async function refreshPrices() {
    try {
        const response = await fetch(`${API_BASE_URL}/prices`);
        const result = await response.json();

        if (result.success) {
            currentPrices = result.data.prices;
            displayPrices(result.data.prices);
        } else {
            document.getElementById('prices-container').innerHTML =
                `<p style="color: #ef4444;">Error: ${result.message}</p>`;
        }
    } catch (error) {
        console.error('Error fetching prices:', error);
        document.getElementById('prices-container').innerHTML =
            '<p style="color: #ef4444;">Failed to load prices. Please check API configuration.</p>';
    }
}

// Display market prices
function displayPrices(prices) {
    const container = document.getElementById('prices-container');

    if (!prices || Object.keys(prices).length === 0) {
        container.innerHTML = '<p>No price data available</p>';
        return;
    }

    let html = '';

    for (const [symbol, data] of Object.entries(prices)) {
        if (!data || !data.current) continue;

        // Calculate change from hour start to current price
        const change = data.current - data.hour_start;
        const changePercent = (change / data.hour_start) * 100;

        const changeClass = changePercent >= 0 ? 'positive' : 'negative';
        const changeSign = changePercent >= 0 ? '+' : '';

        html += `
            <div class="price-card ${changeClass}">
                <div class="price-symbol">${symbol}</div>
                <div class="price-info">
                    <div class="price-current">$${data.current.toFixed(2)}</div>
                    <div class="price-change ${changeClass}">
                        ${changeSign}${change.toFixed(2)} (${changeSign}${changePercent.toFixed(2)}%)
                    </div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                        Hour: ${data.hour_projected_change_percent >= 0 ? '📈' : '📉'} ${data.hour_projected_change_percent >= 0 ? '+' : ''}${data.hour_projected_change_percent.toFixed(1)}% projected
                    </div>
                </div>
                <div class="price-actions">
                    <button class="buy-btn" onclick="openTradeModal('${symbol}', ${data.current})">BUY</button>
                    <button class="sell-btn" onclick="openTradeModal('${symbol}', ${data.current})">SELL</button>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

// Display portfolio
function displayPortfolio(positions) {
    const container = document.getElementById('portfolio-container');

    if (!positions || positions.length === 0) {
        container.innerHTML = '<p>No positions yet</p>';
        return;
    }

    let html = '';

    positions.forEach(position => {
        const plClass = position.profit_loss >= 0 ? 'positive' : 'negative';
        const plSign = position.profit_loss >= 0 ? '+' : '';

        html += `
            <div class="portfolio-card">
                <div class="portfolio-symbol">${position.symbol}</div>
                <div class="portfolio-details">
                    <div><strong>Quantity:</strong> ${position.quantity}</div>
                    <div><strong>Avg Price:</strong> $${position.avg_price.toFixed(2)}</div>
                    <div><strong>Current:</strong> $${position.current_price.toFixed(2)}</div>
                    <div><strong>Value:</strong> $${position.market_value.toFixed(2)}</div>
                    <div style="color: ${position.profit_loss >= 0 ? '#10b981' : '#ef4444'}">
                        <strong>P/L:</strong> ${plSign}$${position.profit_loss.toFixed(2)} (${plSign}${position.profit_loss_percent.toFixed(2)}%)
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Refresh news
async function refreshNews() {
    try {
        const response = await fetch(`${API_BASE_URL}/news`);
        const result = await response.json();

        if (result.success) {
            displayNews(result.data.articles);
        } else {
            document.getElementById('news-container').innerHTML =
                `<p style="color: #ef4444;">Error: ${result.message}</p>`;
        }
    } catch (error) {
        console.error('Error fetching news:', error);
        document.getElementById('news-container').innerHTML =
            '<p style="color: #ef4444;">Failed to load news. Please check API configuration.</p>';
    }
}

// Display news
function displayNews(articles) {
    const container = document.getElementById('news-container');

    if (!articles || articles.length === 0) {
        container.innerHTML = '<p>No news available yet</p>';
        return;
    }

    let html = '';

    articles.forEach(article => {
        const sentimentClass = article.sentiment === 'positive' ? 'positive' : 'negative';
        const changeIcon = article.sentiment === 'positive' ? '📈' : '📉';

        html += `
            <div class="news-card ${sentimentClass}">
                <div class="news-headline">${changeIcon} ${article.headline}</div>
                <div class="news-article">${article.article}</div>
                <div class="news-meta">
                    <span>${article.symbol}</span>
                    <span>${new Date(article.datetime).toLocaleString()}</span>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Refresh leaderboard
async function refreshLeaderboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard`);
        const result = await response.json();

        if (result.success) {
            displayLeaderboard(result.data.leaderboard);
        } else {
            document.getElementById('leaderboard-container').innerHTML =
                `<p style="color: #ef4444;">Error: ${result.message}</p>`;
        }
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        document.getElementById('leaderboard-container').innerHTML =
            '<p style="color: #ef4444;">Failed to load leaderboard. Please check API configuration.</p>';
    }
}

// Display leaderboard
function displayLeaderboard(leaderboard) {
    const container = document.getElementById('leaderboard-container');

    if (!leaderboard || leaderboard.length === 0) {
        container.innerHTML = '<p>No leaderboard data available</p>';
        return;
    }

    let html = `
        <table class="leaderboard-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>User ID</th>
                    <th>Total Value</th>
                    <th>P/L</th>
                    <th>Trades</th>
                </tr>
            </thead>
            <tbody>
    `;

    leaderboard.forEach(entry => {
        const medal = entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : entry.rank === 3 ? '🥉' : '';
        const plColor = entry.profit_loss >= 0 ? '#10b981' : '#ef4444';
        const plSign = entry.profit_loss >= 0 ? '+' : '';

        html += `
            <tr>
                <td><span class="rank-medal">${medal}</span> ${entry.rank}</td>
                <td>${entry.user_id}</td>
                <td>$${entry.total_value.toFixed(2)}</td>
                <td style="color: ${plColor}; font-weight: bold;">
                    ${plSign}$${entry.profit_loss.toFixed(2)} (${plSign}${entry.profit_loss_percent.toFixed(2)}%)
                </td>
                <td>${entry.total_trades}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// Open trade modal
function openTradeModal(symbol, price) {
    selectedAsset = { symbol, price };

    document.getElementById('trade-symbol').textContent = symbol;
    document.getElementById('trade-price').textContent = price.toFixed(2);
    document.getElementById('trade-available-cash').textContent = currentPortfolio.balance ? currentPortfolio.balance.toFixed(2) : '0.00';

    // Find holdings for this symbol
    const position = currentPortfolio.positions ? currentPortfolio.positions.find(p => p.symbol === symbol) : null;
    const holdings = position ? position.quantity : 0;
    document.getElementById('trade-holdings').textContent = holdings;

    document.getElementById('trade-quantity').value = 1;
    document.getElementById('trade-message').textContent = '';
    document.getElementById('trade-message').className = 'trade-message';

    document.getElementById('trade-modal').style.display = 'block';
}

// Close trade modal
function closeTradeModal() {
    document.getElementById('trade-modal').style.display = 'none';
    selectedAsset = null;
}

// Execute trade
async function executeTrade(action) {
    if (!selectedAsset) return;

    const quantity = parseInt(document.getElementById('trade-quantity').value);

    if (!quantity || quantity <= 0) {
        showTradeMessage('Please enter a valid quantity', 'error');
        return;
    }

    const messageElement = document.getElementById('trade-message');
    messageElement.textContent = 'Executing trade...';
    messageElement.className = 'trade-message';

    try {
        const response = await fetch(`${API_BASE_URL}/trade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser,
                symbol: selectedAsset.symbol,
                action: action,
                quantity: quantity
            })
        });

        const result = await response.json();

        if (result.success) {
            showTradeMessage(result.message, 'success');

            // Refresh data after successful trade
            setTimeout(() => {
                loadUserData();
                closeTradeModal();
            }, 1500);
        } else {
            showTradeMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('Error executing trade:', error);
        showTradeMessage('Failed to execute trade. Please try again.', 'error');
    }
}

// Show trade message
function showTradeMessage(message, type) {
    const messageElement = document.getElementById('trade-message');
    messageElement.textContent = message;
    messageElement.className = `trade-message ${type}`;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('trade-modal');
    if (event.target == modal) {
        closeTradeModal();
    }
}
