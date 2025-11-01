import json
import os
import boto3
import requests
from datetime import datetime
import time

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Fetches real-time market data from Finnhub API and stores it in S3.
    This function is triggered by EventBridge every hour.
    """
    finnhub_api_key = os.environ['FINNHUB_API_KEY']
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']
    assets_to_track = json.loads(os.environ['ASSETS_TO_TRACK'])

    timestamp = int(time.time())
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    time_str = datetime.utcnow().strftime('%H-%M-%S')

    market_data = {
        'timestamp': timestamp,
        'datetime': datetime.utcnow().isoformat(),
        'prices': {}
    }

    print(f"Fetching market data for {len(assets_to_track)} assets...")

    for symbol in assets_to_track:
        try:
            # Finnhub uses different endpoints for stocks vs crypto
            if 'USD' in symbol or 'BTC' in symbol or 'ETH' in symbol:
                # Crypto endpoint
                url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={finnhub_api_key}"
            else:
                # Stock endpoint
                url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={finnhub_api_key}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Finnhub returns: c (current), h (high), l (low), o (open), pc (previous close)
            if 'c' in data and data['c'] != 0:
                market_data['prices'][symbol] = {
                    'current': data['c'],
                    'open': data['o'],
                    'high': data['h'],
                    'low': data['l'],
                    'previous_close': data['pc'],
                    'change': data['c'] - data['pc'],
                    'change_percent': ((data['c'] - data['pc']) / data['pc'] * 100) if data['pc'] != 0 else 0
                }
                print(f"✓ {symbol}: ${data['c']:.2f}")
            else:
                print(f"✗ {symbol}: No data available")
                # Use a fallback or skip
                market_data['prices'][symbol] = None

            # Rate limiting - Finnhub free tier allows 60 calls/minute
            time.sleep(1.1)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {symbol}: {str(e)}")
            market_data['prices'][symbol] = None
        except Exception as e:
            print(f"Unexpected error for {symbol}: {str(e)}")
            market_data['prices'][symbol] = None

    # Store raw market data in S3
    s3_key = f"raw_data/{date_str}/{time_str}_market_data.json"

    try:
        s3_client.put_object(
            Bucket=market_data_bucket,
            Key=s3_key,
            Body=json.dumps(market_data, indent=2),
            ContentType='application/json'
        )
        print(f"Market data saved to s3://{market_data_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving to S3: {str(e)}")
        raise

    # Also store as "latest" for easy access
    latest_key = "raw_data/latest_market_data.json"
    try:
        s3_client.put_object(
            Bucket=market_data_bucket,
            Key=latest_key,
            Body=json.dumps(market_data, indent=2),
            ContentType='application/json'
        )
        print(f"Latest data updated at s3://{market_data_bucket}/{latest_key}")
    except Exception as e:
        print(f"Error updating latest data: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Market data fetched successfully',
            's3_key': s3_key,
            'assets_fetched': len([p for p in market_data['prices'].values() if p is not None]),
            'total_assets': len(assets_to_track)
        })
    }
