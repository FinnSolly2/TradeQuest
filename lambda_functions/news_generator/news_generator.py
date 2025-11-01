import json
import os
import boto3
import requests
from datetime import datetime
import time
import random

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Generates AI-powered "fake news" articles based on simulated price movements.
    Uses Hugging Face Inference API to create contextual market news.
    """
    huggingface_api_key = os.environ['HUGGINGFACE_API_KEY']
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']
    news_bucket = os.environ['NEWS_BUCKET']

    timestamp = int(time.time())
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    time_str = datetime.utcnow().strftime('%H-%M-%S')

    # Get the latest simulated price data
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='simulated_data/latest_simulated_prices.json'
        )
        simulated_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded simulated price data for {len(simulated_data['prices'])} assets")
    except Exception as e:
        print(f"Error loading simulated data: {str(e)}")
        raise

    # Analyze price movements to find interesting stories
    price_changes = []
    for symbol, price_data in simulated_data['prices'].items():
        if price_data and price_data['change_percent'] != 0:
            price_changes.append({
                'symbol': symbol,
                'change_percent': price_data['change_percent'],
                'current_price': price_data['current'],
                'change': price_data['change']
            })

    # Sort by absolute change percentage to find most significant movements
    price_changes.sort(key=lambda x: abs(x['change_percent']), reverse=True)

    # Generate news for top 3 movers
    news_articles = []
    assets_to_cover = min(3, len(price_changes))

    for i in range(assets_to_cover):
        asset = price_changes[i]
        symbol = asset['symbol']
        change_pct = asset['change_percent']
        current_price = asset['current_price']

        # Determine sentiment and create prompt
        if change_pct > 0:
            sentiment = "surged" if change_pct > 3 else "rose" if change_pct > 1 else "edged up"
            context = "positive"
        else:
            sentiment = "plummeted" if change_pct < -3 else "fell" if change_pct < -1 else "dipped"
            context = "negative"

        # Create a prompt for the AI model
        prompt = f"""Write a short financial news headline and brief article (2-3 sentences) about {symbol} stock.
The stock {sentiment} by {abs(change_pct):.2f}% to ${current_price:.2f}.
Make it sound professional and include a plausible reason for the {context} movement.
Format: HEADLINE: [headline]
ARTICLE: [article]"""

        try:
            # Call Hugging Face API
            if huggingface_api_key and huggingface_api_key != "demo":
                article_text = generate_news_with_huggingface(prompt, huggingface_api_key)
            else:
                # Fallback to template-based news for demo
                article_text = generate_template_news(symbol, change_pct, current_price, sentiment)

            # Parse the response
            if "HEADLINE:" in article_text and "ARTICLE:" in article_text:
                parts = article_text.split("ARTICLE:")
                headline = parts[0].replace("HEADLINE:", "").strip()
                article = parts[1].strip()
            else:
                # If parsing fails, use the entire text as article
                headline = f"{symbol} {sentiment.capitalize()} {abs(change_pct):.2f}%"
                article = article_text

            news_item = {
                'id': f"news_{timestamp}_{i}",
                'timestamp': timestamp,
                'datetime': datetime.utcnow().isoformat(),
                'symbol': symbol,
                'headline': headline,
                'article': article,
                'sentiment': context,
                'price_change': change_pct,
                'current_price': current_price
            }

            news_articles.append(news_item)
            print(f"✓ Generated news for {symbol}: {headline[:50]}...")

        except Exception as e:
            print(f"Error generating news for {symbol}: {str(e)}")
            # Create a simple fallback news item
            news_item = {
                'id': f"news_{timestamp}_{i}",
                'timestamp': timestamp,
                'datetime': datetime.utcnow().isoformat(),
                'symbol': symbol,
                'headline': f"{symbol} {sentiment.capitalize()} {abs(change_pct):.2f}%",
                'article': f"Trading activity today saw {symbol} {sentiment} by {abs(change_pct):.2f}% to ${current_price:.2f}. Market analysts are monitoring the situation closely.",
                'sentiment': context,
                'price_change': change_pct,
                'current_price': current_price
            }
            news_articles.append(news_item)

    # Store news in S3
    news_data = {
        'timestamp': timestamp,
        'datetime': datetime.utcnow().isoformat(),
        'articles': news_articles
    }

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
            'message': 'News generation completed successfully',
            's3_key': s3_key,
            'articles_generated': len(news_articles),
            'timestamp': timestamp
        })
    }


def generate_news_with_huggingface(prompt, api_key):
    """
    Generate news using Hugging Face Inference API.
    Uses a free text generation model.
    """
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {api_key}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    result = response.json()

    if isinstance(result, list) and len(result) > 0:
        return result[0].get('generated_text', '').replace(prompt, '').strip()
    return result.get('generated_text', '').replace(prompt, '').strip()


def generate_template_news(symbol, change_pct, current_price, sentiment):
    """
    Generate template-based news as fallback when HuggingFace API is not available.
    """
    reasons_positive = [
        "strong quarterly earnings report",
        "positive analyst upgrades",
        "bullish market sentiment",
        "strong sector performance",
        "favorable economic indicators",
        "successful product launch announcement",
        "better than expected revenue growth"
    ]

    reasons_negative = [
        "disappointing earnings results",
        "analyst downgrades",
        "bearish market sentiment",
        "sector-wide concerns",
        "macroeconomic headwinds",
        "regulatory concerns",
        "weaker than expected guidance"
    ]

    if change_pct > 0:
        reason = random.choice(reasons_positive)
        additional = "Investors remain optimistic about future growth prospects."
    else:
        reason = random.choice(reasons_negative)
        additional = "Market participants are closely watching for further developments."

    headline = f"{symbol} {sentiment.capitalize()} {abs(change_pct):.2f}% on {reason.capitalize()}"
    article = f"Shares of {symbol} {sentiment} {abs(change_pct):.2f}% to ${current_price:.2f} following {reason}. {additional} Trading volume increased as market makers adjusted their positions."

    return f"HEADLINE: {headline}\nARTICLE: {article}"
