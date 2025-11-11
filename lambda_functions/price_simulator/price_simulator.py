import json
import os
import boto3
import random
import math
from datetime import datetime, timedelta
import time

s3_client = boto3.client('s3')

def calculate_statistics(candles):
    """
    Calculate statistical properties from historical candle data.
    Returns mean return, volatility, and trend.
    """
    if len(candles) < 2:
        return 0, 0.02, 0

    # Calculate returns between consecutive candles
    returns = []
    for i in range(1, len(candles)):
        ret = (candles[i]['close'] - candles[i-1]['close']) / candles[i-1]['close']
        returns.append(ret)

    # Mean return per second
    mean_return = sum(returns) / len(returns) if returns else 0

    # Volatility (standard deviation of returns)
    if len(returns) > 1:
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        volatility = math.sqrt(variance)
    else:
        volatility = 0.02

    # Trend: difference between last and first close
    trend = (candles[-1]['close'] - candles[0]['close']) / candles[0]['close']

    return mean_return, volatility, trend


def generate_second_prices(start_price, mean_return, volatility, trend, num_seconds=600):
    """
    Generate simulated prices for the next 10 minutes using GBM with historical statistics.
    Returns list of 600 prices (one per second).
    """
    prices = []
    current_price = start_price

    # Adjust drift to include trend component
    drift = mean_return + (trend / num_seconds)  # Distribute trend over the 10-minute period

    for second in range(num_seconds):
        # Geometric Brownian Motion
        # dS = μ * S * dt + σ * S * dW
        dt = 1 / (24 * 60 * 60)  # 1 second in terms of days
        dW = random.gauss(0, math.sqrt(dt))

        price_change = drift * current_price + volatility * current_price * dW
        new_price = current_price + price_change

        # Ensure price stays reasonable (max 5% change per second)
        max_change = current_price * 0.05
        new_price = max(new_price, current_price - max_change)
        new_price = min(new_price, current_price + max_change)

        # Ensure price doesn't go negative
        new_price = max(new_price, start_price * 0.5)

        prices.append(round(new_price, 4))
        current_price = new_price

    return prices


def lambda_handler(event, context):
    """
    Generates 600 simulated prices (1 per second) for the NEXT 10 minutes
    based on statistical distribution from the PAST 60 minutes collected price data.
    """
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']

    timestamp = int(time.time())
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    time_str = datetime.utcnow().strftime('%H-%M-%S')

    # Get the collected price history (past hour - 60 minutes of data)
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='collected_prices/rolling_history_60min.json'
        )
        history_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded price history for {len(history_data['assets'])} assets")

        # Check if we have enough data
        if not history_data.get('stats', {}).get('ready_for_simulation', False):
            print(f"⚠️  Warning: Only {history_data['stats']['assets_with_full_hour']} assets have full 60min data")
    except Exception as e:
        print(f"Error loading price history: {str(e)}")
        raise

    # Start time for the simulated 10-minute period (current time, rounded to the second)
    current_dt = datetime.utcnow()
    start_timestamp = int(current_dt.replace(microsecond=0).timestamp())

    simulated_data = {
        'timestamp': timestamp,
        'datetime': current_dt.isoformat(),
        'start_timestamp': start_timestamp,
        'end_timestamp': start_timestamp + 600,
        'resolution': '1sec',
        'assets': {}
    }

    for symbol, asset_history in history_data['assets'].items():
        if asset_history is None or not asset_history.get('data_points'):
            print(f"Skipping {symbol} - no price data available")
            simulated_data['assets'][symbol] = None
            continue

        try:
            data_points = asset_history['data_points']

            # Convert collected prices to candle format for calculate_statistics
            candles = []
            for point in data_points:
                candles.append({
                    'close': point['price'],
                    'timestamp': point['timestamp']
                })

            last_price = data_points[-1]['price']  # Most recent price

            # Calculate statistics from historical data
            mean_return, volatility, trend = calculate_statistics(candles)

            print(f"📊 {symbol}: mean_return={mean_return:.6f}, volatility={volatility:.4f}, trend={trend:+.2%}")

            # Generate 600 simulated prices for next 10 minutes
            random.seed(int(timestamp) + hash(symbol) % 10000)
            simulated_prices = generate_second_prices(
                start_price=last_price,
                mean_return=mean_return,
                volatility=volatility * 2,  # Amplify for more interesting simulation
                trend=trend,
                num_seconds=600
            )

            # Create timestamped price data
            second_data = []
            for i, price in enumerate(simulated_prices):
                second_timestamp = start_timestamp + i
                second_data.append({
                    'second': i,
                    'timestamp': second_timestamp,
                    'datetime': datetime.fromtimestamp(second_timestamp).isoformat(),
                    'price': price
                })

            # Calculate summary statistics for the simulated 10-minute period
            simulated_data['assets'][symbol] = {
                'seconds': second_data,
                'count': len(second_data),
                'start_price': simulated_prices[0],
                'end_price': simulated_prices[-1],
                'period_high': max(simulated_prices),
                'period_low': min(simulated_prices),
                'period_change': simulated_prices[-1] - simulated_prices[0],
                'period_change_percent': ((simulated_prices[-1] - simulated_prices[0]) / simulated_prices[0] * 100),
                'based_on': {
                    'historical_mean_return': mean_return,
                    'historical_volatility': volatility,
                    'historical_trend': trend,
                    'historical_last_price': last_price
                }
            }

            change_pct = simulated_data['assets'][symbol]['period_change_percent']
            print(f"✓ {symbol}: Generated 600 prices, ${simulated_prices[0]:.2f} → ${simulated_prices[-1]:.2f} ({change_pct:+.2f}%)")

        except Exception as e:
            print(f"Error simulating {symbol}: {str(e)}")
            simulated_data['assets'][symbol] = None

    # Store simulated data in S3
    s3_key = f"simulated_data/{date_str}/{time_str}_simulated_1sec.json"

    try:
        s3_client.put_object(
            Bucket=market_data_bucket,
            Key=s3_key,
            Body=json.dumps(simulated_data, indent=2),
            ContentType='application/json'
        )
        print(f"Simulated data saved to s3://{market_data_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving simulated data to S3: {str(e)}")
        raise

    # Update latest simulated data
    latest_key = "simulated_data/latest_simulated_1sec.json"
    try:
        s3_client.put_object(
            Bucket=market_data_bucket,
            Key=latest_key,
            Body=json.dumps(simulated_data, indent=2),
            ContentType='application/json'
        )
        print(f"Latest simulated data updated at s3://{market_data_bucket}/{latest_key}")
    except Exception as e:
        print(f"Error updating latest simulated data: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Price simulation completed successfully',
            's3_key': s3_key,
            'assets_simulated': len([a for a in simulated_data['assets'].values() if a is not None]),
            'timestamp': timestamp,
            'simulation_period': f"{datetime.fromtimestamp(start_timestamp).strftime('%H:%M')} - {datetime.fromtimestamp(start_timestamp + 600).strftime('%H:%M')}"
        })
    }
