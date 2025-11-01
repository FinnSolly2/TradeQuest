import json
import os
import boto3
import requests
from datetime import datetime, timedelta
import time

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Fetches 1-minute candle data for the last hour from Finnhub API.
    Returns 60 data points (1 per minute) for each asset.
    This function is triggered by EventBridge every hour.
    """
    finnhub_api_key = os.environ['FINNHUB_API_KEY']
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']
    assets_to_track = json.loads(os.environ['ASSETS_TO_TRACK'])

    current_time = int(time.time())
    # Get last hour (60 minutes)
    from_time = current_time - (60 * 60)

    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    time_str = datetime.utcnow().strftime('%H-%M-%S')

    market_data = {
        'timestamp': current_time,
        'datetime': datetime.utcnow().isoformat(),
        'from_timestamp': from_time,
        'to_timestamp': current_time,
        'resolution': '1',  # 1-minute bars
        'candles': {}
    }

    print(f"Fetching 1-minute candles for {len(assets_to_track)} assets...")
    print(f"Time range: {datetime.fromtimestamp(from_time).strftime('%H:%M')} - {datetime.fromtimestamp(current_time).strftime('%H:%M')}")

    for symbol in assets_to_track:
        try:
            # Finnhub candle endpoint
            # resolution: 1, 5, 15, 30, 60, D, W, M
            url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=1&from={from_time}&to={current_time}&token={finnhub_api_key}"

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Finnhub candle response: {s: "ok", c: [close], h: [high], l: [low], o: [open], v: [volume], t: [timestamp]}
            if data.get('s') == 'ok' and 't' in data:
                candles = []
                for i in range(len(data['t'])):
                    candle = {
                        'timestamp': data['t'][i],
                        'datetime': datetime.fromtimestamp(data['t'][i]).isoformat(),
                        'open': data['o'][i],
                        'high': data['h'][i],
                        'low': data['l'][i],
                        'close': data['c'][i],
                        'volume': data['v'][i] if i < len(data.get('v', [])) else 0
                    }
                    candles.append(candle)

                # Calculate statistics from the hour
                if candles:
                    closes = [c['close'] for c in candles]
                    first_close = candles[0]['close']
                    last_close = candles[-1]['close']
                    hour_change = last_close - first_close
                    hour_change_pct = (hour_change / first_close * 100) if first_close != 0 else 0

                    market_data['candles'][symbol] = {
                        'data': candles,
                        'count': len(candles),
                        'first_price': first_close,
                        'last_price': last_close,
                        'hour_high': max(c['high'] for c in candles),
                        'hour_low': min(c['low'] for c in candles),
                        'hour_change': hour_change,
                        'hour_change_percent': hour_change_pct,
                        'avg_volume': sum(c['volume'] for c in candles) / len(candles)
                    }

                    print(f"✓ {symbol}: {len(candles)} candles, ${last_close:.2f} ({hour_change_pct:+.2f}%)")
                else:
                    print(f"✗ {symbol}: No candles in response")
                    market_data['candles'][symbol] = None

            elif data.get('s') == 'no_data':
                print(f"✗ {symbol}: No data available (market closed or invalid symbol)")
                market_data['candles'][symbol] = None
            else:
                print(f"✗ {symbol}: Unexpected response: {data.get('s', 'unknown')}")
                market_data['candles'][symbol] = None

            # Rate limiting - Finnhub free tier allows 60 calls/minute
            time.sleep(1.1)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {symbol}: {str(e)}")
            market_data['candles'][symbol] = None
        except Exception as e:
            print(f"Unexpected error for {symbol}: {str(e)}")
            market_data['candles'][symbol] = None

    # Store raw market data in S3
    s3_key = f"raw_data/{date_str}/{time_str}_candles_1min.json"

    try:
        s3_client.put_object(
            Bucket=market_data_bucket,
            Key=s3_key,
            Body=json.dumps(market_data, indent=2),
            ContentType='application/json'
        )
        print(f"Candle data saved to s3://{market_data_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving to S3: {str(e)}")
        raise

    # Also store as "latest" for easy access
    latest_key = "raw_data/latest_candles_1min.json"
    try:
        s3_client.put_object(
            Bucket=market_data_bucket,
            Key=latest_key,
            Body=json.dumps(market_data, indent=2),
            ContentType='application/json'
        )
        print(f"Latest candle data updated at s3://{market_data_bucket}/{latest_key}")
    except Exception as e:
        print(f"Error updating latest data: {str(e)}")

    successful_fetches = len([c for c in market_data['candles'].values() if c is not None])

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Fetched 1-minute candles for {successful_fetches}/{len(assets_to_track)} assets',
            's3_key': s3_key,
            'assets_fetched': successful_fetches,
            'total_assets': len(assets_to_track),
            'time_range': f"{datetime.fromtimestamp(from_time).strftime('%H:%M')} - {datetime.fromtimestamp(current_time).strftime('%H:%M')}"
        })
    }
