import json
import os
import boto3
import requests
from datetime import datetime
import time
import random

s3_client = boto3.client('s3')

def generate_market_wide_news(movements, timestamp):
    """
    Generate market-wide news based on overall market movements.
    Examples: Fed decisions, interest rate changes, market sentiment shifts
    """
    # Calculate average market movement
    avg_change = sum(m['past_change_percent'] for m in movements) / len(movements) if movements else 0

    market_templates = []

    if avg_change < -1:
        market_templates = [
            {
                'headline': "Markets Decline Amid Rising Interest Rate Concerns",
                'article': f"Major indices fell sharply in the past hour as investors grew increasingly concerned about potential interest rate hikes. The broad sell-off saw average declines of {abs(avg_change):.1f}% across major assets, with traders rotating out of risk assets into safer investments.",
                'category': 'market_wide',
                'sentiment': 'negative'
            },
            {
                'headline': "Risk-Off Sentiment Grips Markets as Economic Data Disappoints",
                'article': f"A wave of selling pressure hit markets following disappointing economic indicators. Average losses of {abs(avg_change):.1f}% reflected growing concerns about economic growth prospects. Analysts suggest investors are positioning defensively ahead of potential volatility.",
                'category': 'market_wide',
                'sentiment': 'negative'
            }
        ]
    elif avg_change > 1:
        market_templates = [
            {
                'headline': "Markets Rally on Optimistic Fed Signals",
                'article': f"Equities surged in the past hour after signals from Federal Reserve officials suggested a more dovish monetary policy stance. The broad rally saw average gains of {avg_change:.1f}% as investors embraced renewed risk appetite.",
                'category': 'market_wide',
                'sentiment': 'positive'
            },
            {
                'headline': "Strong Economic Data Fuels Market Optimism",
                'article': f"Markets pushed higher following better-than-expected economic indicators, with average gains of {avg_change:.1f}%. The positive momentum reflected renewed confidence in economic resilience and corporate earnings potential.",
                'category': 'market_wide',
                'sentiment': 'positive'
            }
        ]
    else:
        market_templates = [
            {
                'headline': "Markets Trade Mixed as Investors Await Key Economic Data",
                'article': "Cautious trading dominated the past hour as investors weighed conflicting signals about economic growth and monetary policy. Major indices showed limited directional conviction ahead of upcoming inflation reports.",
                'category': 'market_wide',
                'sentiment': 'neutral'
            }
        ]

    return random.choice(market_templates)


def generate_sector_news(movements, timestamp):
    """
    Generate sector-specific news.
    Examples: Tech sector rotation, financial sector strength
    """
    # Group by sectors (simplified - assume symbols indicate sectors)
    tech_stocks = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'META']
    tech_movements = [m for m in movements if m['symbol'] in tech_stocks]

    if tech_movements:
        avg_tech_change = sum(m['past_change_percent'] for m in tech_movements) / len(tech_movements)

        if avg_tech_change > 0.5:
            return {
                'headline': "Technology Sector Leads Market Higher on AI Optimism",
                'article': f"Technology stocks outperformed broader markets in the past hour, rising an average of {avg_tech_change:.1f}%. The sector strength came amid renewed enthusiasm for artificial intelligence applications and cloud computing growth prospects.",
                'category': 'sector',
                'sentiment': 'positive'
            }
        elif avg_tech_change < -0.5:
            return {
                'headline': "Tech Stocks Under Pressure as Growth Concerns Mount",
                'article': f"The technology sector underperformed in recent trading, declining {abs(avg_tech_change):.1f}% as investors questioned high valuations. Concerns about regulatory scrutiny and slowing user growth weighed on sentiment.",
                'category': 'sector',
                'sentiment': 'negative'
            }

    return {
        'headline': "Sector Rotation Continues as Investors Rebalance Portfolios",
        'article': "Investors continued rotating between sectors in the past hour, with defensive stocks gaining ground relative to growth-oriented names. The shift reflected ongoing uncertainty about economic growth trajectories.",
        'category': 'sector',
        'sentiment': 'neutral'
    }


def generate_geopolitical_news(timestamp):
    """
    Generate geopolitical and global event news.
    """
    templates = [
        {
            'headline': "Trade Tensions Ease as Negotiators Report Progress",
            'article': "Global markets received a boost from reports of constructive trade negotiations between major economic powers. Diplomats indicated that significant progress had been made on key sticking points, reducing concerns about escalating tariffs.",
            'category': 'geopolitical',
            'sentiment': 'positive'
        },
        {
            'headline': "Geopolitical Risks Weigh on Market Sentiment",
            'article': "Investors remained cautious amid ongoing geopolitical uncertainties. Developments in international relations continued to create headwinds for risk assets, with traders closely monitoring diplomatic channels for signs of resolution.",
            'category': 'geopolitical',
            'sentiment': 'negative'
        },
        {
            'headline': "Central Banks Signal Coordinated Policy Response",
            'article': "Major central banks hinted at coordinated efforts to support economic stability. The collaborative approach eased concerns about fragmented monetary policy responses and provided reassurance to global markets.",
            'category': 'geopolitical',
            'sentiment': 'positive'
        }
    ]

    return random.choice(templates)


def generate_economic_data_news(timestamp):
    """
    Generate economic data and indicator news.
    """
    templates = [
        {
            'headline': "Inflation Data Comes in Below Expectations, Easing Policy Concerns",
            'article': "The latest inflation reading showed prices rising at a slower pace than economists anticipated. The softer-than-expected data reduced pressure on central banks to maintain aggressive tightening policies, supporting risk assets.",
            'category': 'economic',
            'sentiment': 'positive'
        },
        {
            'headline': "Jobs Report Exceeds Forecasts, Signaling Economic Resilience",
            'article': "Employment figures beat analyst estimates, demonstrating continued strength in the labor market. The robust job creation numbers reinforced views of economic resilience despite recent headwinds.",
            'category': 'economic',
            'sentiment': 'positive'
        },
        {
            'headline': "Consumer Confidence Slips as Economic Uncertainty Persists",
            'article': "Consumer sentiment indicators declined in the latest survey, reflecting growing concerns about economic prospects. The weaker confidence numbers raised questions about future spending patterns and corporate revenue growth.",
            'category': 'economic',
            'sentiment': 'negative'
        },
        {
            'headline': "Manufacturing Activity Shows Signs of Stabilization",
            'article': "The latest manufacturing index suggested industrial activity was stabilizing after months of contraction. While still below expansion territory, the less negative reading provided cautious optimism about supply chain improvements.",
            'category': 'economic',
            'sentiment': 'neutral'
        }
    ]

    return random.choice(templates)


def create_asset_specific_news(symbol, past_change_pct, future_change_pct, current_price, sentiment):
    """
    Generate asset-specific news (original functionality, enhanced).
    """
    past_direction = "surged" if past_change_pct > 1.5 else "rose" if past_change_pct > 0 else "fell" if past_change_pct > -1.5 else "plunged"
    future_direction = "rally" if future_change_pct > 0 else "decline"

    # Company-specific reasons
    reasons = {
        'AAPL': {
            'positive': ['strong iPhone sales', 'services revenue growth', 'ecosystem expansion', 'supply chain improvements'],
            'negative': ['supply constraints', 'China market concerns', 'regulatory headwinds', 'margin pressure']
        },
        'GOOGL': {
            'positive': ['advertising revenue strength', 'cloud growth', 'AI initiatives', 'search dominance'],
            'negative': ['ad spending weakness', 'regulatory challenges', 'competition concerns', 'cost pressures']
        },
        'MSFT': {
            'positive': ['Azure cloud growth', 'enterprise demand', 'AI integration', 'productivity suite strength'],
            'negative': ['cloud competition', 'licensing concerns', 'economic headwinds', 'valuation concerns']
        }
    }

    default_reasons = {
        'positive': ['strong earnings', 'analyst upgrades', 'positive guidance', 'market share gains'],
        'negative': ['earnings miss', 'analyst downgrades', 'weak guidance', 'competitive pressure']
    }

    company_reasons = reasons.get(symbol, default_reasons)
    past_reason = random.choice(company_reasons['positive' if past_change_pct > 0 else 'negative'])

    headline = f"{symbol} {past_direction.capitalize()} {abs(past_change_pct):.1f}% on {past_reason.capitalize()}"

    article = (
        f"{symbol} shares {past_direction} {abs(past_change_pct):.2f}% in the past hour following {past_reason}. "
        f"The stock is currently trading at ${current_price:.2f}. Analysts expect the momentum to continue, "
        f"projecting a {abs(future_change_pct):.1f}% {future_direction} in the near term. "
        f"Traders are monitoring key technical levels and upcoming catalysts for further direction."
    )

    return {
        'headline': headline,
        'article': article,
        'category': 'asset_specific',
        'sentiment': sentiment,
        'symbol': symbol
    }


def lambda_handler(event, context):
    """
    Generates 2-3 diverse news articles that are immediately available.
    Runs every 5 minutes to provide fresh, timely news.
    News types: market-wide, sector, geopolitical, economic, asset-specific
    """
    huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY', '')
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']
    news_bucket = os.environ['NEWS_BUCKET']

    timestamp = int(time.time())
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    time_str = datetime.utcnow().strftime('%H-%M-%S')

    # Get collected price history
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='collected_prices/rolling_history_60min.json'
        )
        history_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded price history for {len(history_data['assets'])} assets")
    except Exception as e:
        print(f"Error loading price history: {str(e)}")
        raise

    # Get simulated future data
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='simulated_data/latest_simulated_1sec.json'
        )
        simulated_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded simulated data for {len(simulated_data['assets'])} assets")
    except Exception as e:
        print(f"Error loading simulated data: {str(e)}")
        raise

    # Analyze movements
    movements = []
    for symbol in history_data['assets'].keys():
        asset_history = history_data['assets'].get(symbol)
        simulated_info = simulated_data['assets'].get(symbol)

        if asset_history and asset_history.get('data_points') and simulated_info:
            data_points = asset_history['data_points']
            if len(data_points) >= 2:
                first_price = data_points[0]['price']
                last_price = data_points[-1]['price']
                past_change_pct = ((last_price - first_price) / first_price) * 100
            else:
                past_change_pct = 0

            future_change_pct = simulated_info.get('hour_change_percent', 0)
            current_price = simulated_info.get('start_price', 0)

            movements.append({
                'symbol': symbol,
                'past_change_percent': past_change_pct,
                'future_change_percent': future_change_pct,
                'current_price': current_price,
                'volatility': abs(past_change_pct) + abs(future_change_pct)
            })

    movements.sort(key=lambda x: x['volatility'], reverse=True)

    # Generate 2-3 diverse news articles (runs every 5 minutes, so fewer articles per run)
    news_articles = []

    # Randomly select article types to generate variety
    article_types = ['market', 'sector', 'geopolitical', 'economic', 'asset']
    selected_types = random.sample(article_types, k=random.randint(2, 3))

    for article_type in selected_types:
        if article_type == 'market':
            news_articles.append(generate_market_wide_news(movements, timestamp))
        elif article_type == 'sector':
            news_articles.append(generate_sector_news(movements, timestamp))
        elif article_type == 'geopolitical':
            news_articles.append(generate_geopolitical_news(timestamp))
        elif article_type == 'economic':
            news_articles.append(generate_economic_data_news(timestamp))
        elif article_type == 'asset' and movements:
            # Pick a random top mover
            asset = random.choice(movements[:min(5, len(movements))])
            sentiment = 'positive' if asset['future_change_percent'] > 0 else 'negative'
            news_articles.append(create_asset_specific_news(
                asset['symbol'],
                asset['past_change_percent'],
                asset['future_change_percent'],
                asset['current_price'],
                sentiment
            ))

    # All articles are immediately available (publish_at = current time)
    # This provides instant news every 5 minutes instead of staggered releases

    # Load existing news to append new articles
    existing_articles = []
    try:
        response = s3_client.get_object(
            Bucket=news_bucket,
            Key='latest_news.json'
        )
        existing_data = json.loads(response['Body'].read().decode('utf-8'))
        existing_articles = existing_data.get('articles', [])

        # Remove articles older than 1 hour
        existing_articles = [
            article for article in existing_articles
            if article.get('timestamp', 0) > timestamp - 3600
        ]
        print(f"Loaded {len(existing_articles)} existing articles (filtered to last hour)")
    except s3_client.exceptions.NoSuchKey:
        print("No existing news found, starting fresh")
    except Exception as e:
        print(f"Error loading existing news: {str(e)}")

    # Create new news articles with immediate availability
    new_articles = []
    for i, news in enumerate(news_articles):
        news_article = {
            'id': f"news_{timestamp}_{i}",
            'timestamp': timestamp,
            'datetime': datetime.utcnow().isoformat(),
            'publish_at': timestamp,  # Immediately available
            'publish_at_datetime': datetime.utcnow().isoformat(),
            'headline': news['headline'],
            'article': news['article'],
            'category': news['category'],
            'sentiment': news['sentiment'],
            'symbol': news.get('symbol', 'MARKET'),  # MARKET for non-asset news
            'actionable': True,
            'valid_until': timestamp + 3600
        }
        new_articles.append(news_article)
        print(f"✓ {news['category']} news: '{news['headline'][:50]}...' (immediately available)")

    # Combine existing and new articles, sort by publish_at (newest first)
    all_articles = existing_articles + new_articles
    all_articles.sort(key=lambda x: x.get('publish_at', 0), reverse=True)

    news_data = {
        'timestamp': timestamp,
        'datetime': datetime.utcnow().isoformat(),
        'articles': all_articles,
        'total_articles': len(all_articles),
        'new_articles': len(new_articles),
        'publication_period': '5 minutes',
        'based_on_past_hour': True,
        'predictions_for_next_hour': True
    }

    # Store news in S3
    s3_key = f"{date_str}/{time_str}_news.json"

    try:
        s3_client.put_object(
            Bucket=news_bucket,
            Key=s3_key,
            Body=json.dumps(news_data, indent=2),
            ContentType='application/json'
        )
        print(f"News saved to s3://{news_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving news to S3: {str(e)}")
        raise

    # Update latest news
    latest_key = "latest_news.json"
    try:
        s3_client.put_object(
            Bucket=news_bucket,
            Key=latest_key,
            Body=json.dumps(news_data, indent=2),
            ContentType='application/json'
        )
        print(f"Latest news updated at s3://{news_bucket}/{latest_key}")
    except Exception as e:
        print(f"Error updating latest news: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Generated {len(new_articles)} new articles, {len(all_articles)} total available',
            's3_key': s3_key,
            'new_articles_count': len(new_articles),
            'total_articles_count': len(all_articles),
            'timestamp': timestamp,
            'categories': {
                'market_wide': sum(1 for a in new_articles if a['category'] == 'market_wide'),
                'sector': sum(1 for a in new_articles if a['category'] == 'sector'),
                'geopolitical': sum(1 for a in new_articles if a['category'] == 'geopolitical'),
                'economic': sum(1 for a in new_articles if a['category'] == 'economic'),
                'asset_specific': sum(1 for a in new_articles if a['category'] == 'asset_specific')
            }
        })
    }
