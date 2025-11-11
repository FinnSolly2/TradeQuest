import json
import os
import boto3
from datetime import datetime
import time
import random
from huggingface_hub import InferenceClient

s3_client = boto3.client('s3')

def generate_ai_news_with_huggingface(api_key, prompt):
    """
    Generate AI news using Hugging Face InferenceClient.
    Uses Llama 3.2 1B Instruct model for fast, quality text generation.
    """
    try:
        # Initialize client with API key (same as your working local code)
        client = InferenceClient(token=api_key)

        # Create chat messages - system prompt + user prompt for better quality
        messages = [
            {"role": "user", "content": f"Write a brief, neutral financial news article (2-3 sentences) about: {prompt}. Do not include specific numbers or percentages."}
        ]

        # Generate text using chat completion
        response = client.chat_completion(
            messages=messages,
            model="meta-llama/Llama-3.2-1B-Instruct",
            max_tokens=100,
            temperature=0.7
        )

        generated_text = response.choices[0].message.content.strip()

        # Clean up - ensure it's concise (2-3 sentences)
        sentences = generated_text.split('.')[:3]
        clean_text = '. '.join(s.strip() for s in sentences if s.strip())
        if clean_text and not clean_text.endswith('.'):
            clean_text += '.'

        return clean_text if clean_text else None

    except Exception as e:
        print(f"Error calling Hugging Face API: {str(e)}")
        return None


def generate_market_wide_news(movements, timestamp, api_key):
    """
    Generate market-wide news using Hugging Face AI.
    """
    topics = [
        "central bank monetary policy and its impact on currency markets",
        "global economic growth trends affecting forex trading",
        "international trade developments and currency valuations",
        "inflation concerns and their effect on major currencies"
    ]

    topic = random.choice(topics)
    prompt = f"Write a brief financial news update about {topic}."

    article = generate_ai_news_with_huggingface(api_key, prompt)

    if not article:
        # Fallback to template if API fails
        article = "Currency markets continue responding to evolving economic conditions. Traders are monitoring central bank policies and economic indicators for guidance on future exchange rate movements."

    # Generate headline using AI
    headline_prompt = f"Write a short, neutral news headline (max 10 words) about: {topic}"
    headline = generate_ai_news_with_huggingface(api_key, headline_prompt)

    if not headline or len(headline) > 100:
        headline = "Currency Markets React to Economic Developments"

    return {
        'headline': headline.strip(),
        'article': article.strip(),
        'category': 'market_wide',
        'sentiment': 'neutral'
    }


def generate_sector_news(movements, timestamp, api_key):
    """
    Generate forex sector news using Hugging Face AI.
    """
    topics = [
        "major currency pair trading activity in forex markets",
        "emerging market currencies and their recent movements",
        "safe haven currencies in current market conditions",
        "commodity-linked currencies and resource prices"
    ]

    topic = random.choice(topics)
    prompt = f"Write a brief forex market update about {topic}."

    article = generate_ai_news_with_huggingface(api_key, prompt)

    if not article:
        article = "Currency pairs showed varying activity as traders assessed economic data. Major currencies continue responding to shifts in monetary policy expectations."

    headline_prompt = f"Write a short, neutral forex news headline about: {topic}"
    headline = generate_ai_news_with_huggingface(api_key, headline_prompt)

    if not headline or len(headline) > 100:
        headline = "Forex Markets Show Mixed Trading Patterns"

    return {
        'headline': headline.strip(),
        'article': article.strip(),
        'category': 'sector',
        'sentiment': 'neutral'
    }


def generate_geopolitical_news(timestamp, api_key):
    """
    Generate geopolitical news using Hugging Face AI.
    """
    topics = [
        "international trade relations and currency impacts",
        "geopolitical developments affecting global markets",
        "central bank cooperation and policy coordination",
        "economic sanctions and their market implications"
    ]

    topic = random.choice(topics)
    prompt = f"Write a brief neutral financial news update about {topic}."

    article = generate_ai_news_with_huggingface(api_key, prompt)

    if not article:
        article = "Global markets continue monitoring geopolitical developments. Traders are evaluating how international events may influence currency valuations and trading strategies."

    headline_prompt = f"Write a short, neutral news headline about: {topic}"
    headline = generate_ai_news_with_huggingface(api_key, headline_prompt)

    if not headline or len(headline) > 100:
        headline = "Global Events Shape Market Outlook"

    return {
        'headline': headline.strip(),
        'article': article.strip(),
        'category': 'geopolitical',
        'sentiment': 'neutral'
    }


def generate_economic_data_news(timestamp, api_key):
    """
    Generate economic data news using Hugging Face AI.
    """
    topics = [
        "employment data and labor market conditions",
        "inflation indicators and price stability",
        "manufacturing activity and industrial production",
        "consumer spending patterns and retail trends"
    ]

    topic = random.choice(topics)
    prompt = f"Write a brief neutral economic news update about {topic}."

    article = generate_ai_news_with_huggingface(api_key, prompt)

    if not article:
        article = "Economic indicators continue drawing attention from market participants. Analysts are evaluating recent data releases for insights into future economic trends."

    headline_prompt = f"Write a short, neutral news headline about: {topic}"
    headline = generate_ai_news_with_huggingface(api_key, headline_prompt)

    if not headline or len(headline) > 100:
        headline = "Economic Data Continues to Guide Markets"

    return {
        'headline': headline.strip(),
        'article': article.strip(),
        'category': 'economic',
        'sentiment': 'neutral'
    }


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

    # Generate 2-3 diverse AI-powered news articles
    news_articles = []

    # Randomly select article types to generate variety
    article_types = ['market', 'sector', 'geopolitical', 'economic']
    selected_types = random.sample(article_types, k=random.randint(2, 3))

    print(f"Generating {len(selected_types)} AI news articles using Hugging Face...")

    for article_type in selected_types:
        if article_type == 'market':
            news_articles.append(generate_market_wide_news(movements, timestamp, huggingface_api_key))
        elif article_type == 'sector':
            news_articles.append(generate_sector_news(movements, timestamp, huggingface_api_key))
        elif article_type == 'geopolitical':
            news_articles.append(generate_geopolitical_news(timestamp, huggingface_api_key))
        elif article_type == 'economic':
            news_articles.append(generate_economic_data_news(timestamp, huggingface_api_key))

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
