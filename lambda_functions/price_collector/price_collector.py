import json
import os
import boto3
import requests
from datetime import datetime
import time

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Collects current prices using Yahoo Finance query API every minute.
    Maintains a rolling 60-minute (1 hour) history for each asset.
    This data is used by price_simulator to generate 3600 simulated prices (1 per second).
    """
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']
    assets_to_track = json.loads(os.environ['ASSETS_TO_TRACK'])

    current_timestamp = int(time.time())
    current_datetime = datetime.utcnow()

    # Try to load existing history
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='collected_prices/rolling_history_60min.json'
        )
        history_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded existing history with {len(history_data.get('assets', {}))} assets")
    except s3_client.exceptions.NoSuchKey:
        print("No existing history found, creating new")
        history_data = {
            'created_at': current_datetime.isoformat(),
            'assets': {}
        }

    # Fetch current prices using Yahoo Finance query API (lightweight, no library needed)
    newly_fetched = 0
    for symbol in assets_to_track:
        try:
            # Yahoo Finance query API - free, no authentication needed
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract price data from response
            if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
                result = data['chart']['result'][0]
                meta = result.get('meta', {})

                current_price = meta.get('regularMarketPrice')

                if current_price and current_price > 0:
                    # Get additional price info
                    high = meta.get('regularMarketDayHigh', current_price)
                    low = meta.get('regularMarketDayLow', current_price)
                    open_price = meta.get('regularMarketOpen', current_price)
                    previous_close = meta.get('previousClose', current_price)

                    # Initialize asset history if not exists
                    if symbol not in history_data['assets']:
                        history_data['assets'][symbol] = {
                            'symbol': symbol,
                            'data_points': []
                        }

                    # Add new data point
                    data_point = {
                        'timestamp': current_timestamp,
                        'datetime': current_datetime.isoformat(),
                        'price': float(current_price),
                        'high': float(high),
                        'low': float(low),
                        'open': float(open_price),
                        'previous_close': float(previous_close)
                    }

                    history_data['assets'][symbol]['data_points'].append(data_point)

                    # Keep only last 60 data points (60 minutes = 1 hour)
                    if len(history_data['assets'][symbol]['data_points']) > 60:
                        history_data['assets'][symbol]['data_points'] = \
                            history_data['assets'][symbol]['data_points'][-60:]

                    count = len(history_data['assets'][symbol]['data_points'])
                    print(f"✓ {symbol}: ${current_price:.2f} (collected {count}/60 data points)")
                    newly_fetched += 1
                else:
                    print(f"✗ {symbol}: No valid price data")
            else:
                print(f"✗ {symbol}: Invalid response structure")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {symbol}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error for {symbol}: {str(e)}")

    # Update metadata
    history_data['last_updated'] = current_datetime.isoformat()
    history_data['last_updated_timestamp'] = current_timestamp

    # Calculate completeness stats
    assets_with_full_hour = 0
    for symbol, asset_data in history_data['assets'].items():
        if len(asset_data['data_points']) >= 60:
            assets_with_full_hour += 1

    history_data['stats'] = {
        'total_assets': len(history_data['assets']),
        'assets_with_full_hour': assets_with_full_hour,
        'ready_for_simulation': assets_with_full_hour >= len(assets_to_track) * 0.8  # 80% threshold
    }

    # Save updated history
    s3_key = 'collected_prices/rolling_history_60min.json'
    try:
        s3_client.put_object(
            Bucket=market_data_bucket,
            Key=s3_key,
            Body=json.dumps(history_data, indent=2),
            ContentType='application/json'
        )
        print(f"\n✅ History saved: {assets_with_full_hour}/{len(assets_to_track)} assets have full 60min data")
        print(f"   Ready for simulation: {history_data['stats']['ready_for_simulation']}")
    except Exception as e:
        print(f"Error saving history to S3: {str(e)}")
        raise

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Collected prices for {newly_fetched} assets',
            'assets_with_full_hour': assets_with_full_hour,
            'total_assets': len(assets_to_track),
            'ready_for_simulation': history_data['stats']['ready_for_simulation'],
            'timestamp': current_timestamp
        })
    }
