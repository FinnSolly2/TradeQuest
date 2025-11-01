import json
import os
import boto3
import requests
from datetime import datetime
import time
import random

s3_client = boto3.client('s3')

def generate_news_with_huggingface(prompt, api_key):
    """
    Generate news using Hugging Face Inference API.
    Falls back to template-based news if API fails.
    """
    try:
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {api_key}"}

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()

        return None
    except Exception as e:
        print(f"Hugging Face API error: {str(e)}")
        return None


def create_template_news(symbol, past_change_pct, future_change_pct, current_price, sentiment):
    """
    Generate template-based news if AI fails.
    """
    past_direction = "rose" if past_change_pct > 0 else "fell"
    future_direction = "expected to rise" if future_change_pct > 0 else "expected to decline"

    reasons = {
        'positive': ['strong earnings report', 'positive market sentiment', 'analyst upgrades', 'sector rotation'],
        'negative': ['disappointing guidance', 'market concerns', 'profit-taking', 'sector weakness']
    }

    past_reason = random.choice(reasons['positive' if past_change_pct > 0 else 'negative'])
    future_outlook = "bullish" if future_change_pct > 0 else "bearish"

    article = (
        f"In the past hour, {symbol} {past_direction} {abs(past_change_pct):.2f}% to ${current_price:.2f} "
        f"following {past_reason}. Technical indicators suggest a {future_outlook} outlook for the next hour, "
        f"with prices {future_direction} by approximately {abs(future_change_pct):.2f}%. "
        f"Traders should watch key support and resistance levels closely."
    )

    return article


def lambda_handler(event, context):
    """
    Generates news based on PAST hour's movements and FUTURE hour's predictions.
    News is actionable for trading the upcoming hour.
    """
    huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY', '')
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']
    news_bucket = os.environ['NEWS_BUCKET']

    timestamp = int(time.time())
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    time_str = datetime.utcnow().strftime('%H-%M-%S')

    # Get historical candle data (what actually happened in past hour)
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='raw_data/latest_candles_1min.json'
        )
        candle_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded candle data for {len(candle_data['candles'])} assets")
    except Exception as e:
        print(f"Error loading candle data: {str(e)}")
        raise

    # Get simulated future data (predictions for next hour)
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='simulated_data/latest_simulated_1min.json'
        )
        simulated_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded simulated data for {len(simulated_data['assets'])} assets")
    except Exception as e:
        print(f"Error loading simulated data: {str(e)}")
        raise

    # Analyze movements: past hour vs future hour predictions
    movements = []
    for symbol in candle_data['candles'].keys():
        candle_info = candle_data['candles'].get(symbol)
        simulated_info = simulated_data['assets'].get(symbol)

        if candle_info and simulated_info:
            past_change_pct = candle_info.get('hour_change_percent', 0)
            future_change_pct = simulated_info.get('hour_change_percent', 0)
            current_price = simulated_info.get('start_price', 0)

            movements.append({
                'symbol': symbol,
                'past_change_percent': past_change_pct,
                'future_change_percent': future_change_pct,
                'current_price': current_price,
                'volatility': abs(past_change_pct) + abs(future_change_pct)
            })

    # Sort by volatility (most interesting stories first)
    movements.sort(key=lambda x: x['volatility'], reverse=True)

    # Generate news for top 3 movers
    news_articles = []
    assets_to_cover = min(3, len(movements))

    for i in range(assets_to_cover):
        asset = movements[i]
        symbol = asset['symbol']
        past_change = asset['past_change_percent']
        future_change = asset['future_change_percent']
        current_price = asset['current_price']

        # Determine overall sentiment
        sentiment = 'positive' if future_change > 0 else 'negative'

        # Create AI prompt
        prompt = (
            f"Write a brief financial news article: {symbol} moved {past_change:+.2f}% in the past hour. "
            f"Analysts predict {future_change:+.2f}% movement in the next hour. "
            f"Current price: ${current_price:.2f}. Keep it under 100 words."
        )

        # Try AI generation first
        ai_article = None
        if huggingface_api_key:
            ai_article = generate_news_with_huggingface(prompt, huggingface_api_key)

        # Use template if AI fails
        article_text = ai_article if ai_article else create_template_news(
            symbol, past_change, future_change, current_price, sentiment
        )

        # Create headline
        if future_change > 0:
            headline = f"{symbol} Expected to Rally {abs(future_change):.1f}% Next Hour After {abs(past_change):.1f}% Move"
        else:
            headline = f"{symbol} May Drop {abs(future_change):.1f}% Next Hour Despite {abs(past_change):.1f}% Past Move"

        news_article = {
            'id': f"news_{timestamp}_{i}",
            'timestamp': timestamp,
            'datetime': datetime.utcnow().isoformat(),
            'symbol': symbol,
            'headline': headline,
            'article': article_text,
            'sentiment': sentiment,
            'past_hour_change': past_change,
            'predicted_next_hour_change': future_change,
            'current_price': current_price,
            'actionable': True,  # This news can be used for trading decisions
            'valid_until': timestamp + 3600  # Valid for next hour
        }

        news_articles.append(news_article)
        print(f"✓ Generated news for {symbol}: past={past_change:+.2f}%, predicted={future_change:+.2f}%")

    news_data = {
        'timestamp': timestamp,
        'datetime': datetime.utcnow().isoformat(),
        'articles': news_articles,
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
            'message': f'Generated {len(news_articles)} actionable news articles',
            's3_key': s3_key,
            'articles_count': len(news_articles),
            'timestamp': timestamp
        })
    }
