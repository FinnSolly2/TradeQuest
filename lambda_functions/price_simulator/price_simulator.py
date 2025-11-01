import json
import os
import boto3
import random
import math
from datetime import datetime
import time

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Generates simulated price movements based on real market data.
    Uses statistical models (Geometric Brownian Motion) to create realistic price paths.
    """
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']

    timestamp = int(time.time())
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    time_str = datetime.utcnow().strftime('%H-%M-%S')

    # Get the latest real market data
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='raw_data/latest_market_data.json'
        )
        real_data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Loaded real market data with {len(real_data['prices'])} assets")
    except Exception as e:
        print(f"Error loading real market data: {str(e)}")
        raise

    # Get historical simulated data to maintain continuity
    try:
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='simulated_data/latest_simulated_prices.json'
        )
        previous_simulated = json.loads(response['Body'].read().decode('utf-8'))
        print("Loaded previous simulated data for continuity")
    except s3_client.exceptions.NoSuchKey:
        print("No previous simulated data found, using real prices as base")
        previous_simulated = None
    except Exception as e:
        print(f"Error loading previous simulated data: {str(e)}")
        previous_simulated = None

    simulated_data = {
        'timestamp': timestamp,
        'datetime': datetime.utcnow().isoformat(),
        'prices': {}
    }

    for symbol, real_price_data in real_data['prices'].items():
        if real_price_data is None:
            print(f"Skipping {symbol} - no real data available")
            simulated_data['prices'][symbol] = None
            continue

        try:
            # Get the current real price
            current_real_price = real_price_data['current']

            # Calculate volatility from real data (using daily change percentage as proxy)
            real_volatility = abs(real_price_data['change_percent']) / 100 if real_price_data['change_percent'] != 0 else 0.02

            # Get previous simulated price or use current real price as starting point
            if previous_simulated and symbol in previous_simulated['prices'] and previous_simulated['prices'][symbol]:
                previous_price = previous_simulated['prices'][symbol]['current']
            else:
                previous_price = current_real_price

            # Simulate price using Geometric Brownian Motion (GBM)
            # dS = μ * S * dt + σ * S * dW
            # where μ is drift, σ is volatility, dW is Wiener process

            # Parameters
            dt = 1/24  # Time step (1 hour = 1/24 of a day)
            mu = real_price_data['change_percent'] / 100  # Drift from real market
            sigma = real_volatility * 2  # Amplified volatility for more interesting simulation

            # Generate random walk
            random.seed(int(timestamp) + hash(symbol) % 10000)  # Seed for reproducibility
            dW = random.gauss(0, math.sqrt(dt))  # Normal distribution: mean=0, std=sqrt(dt)

            # Calculate new simulated price
            price_change = mu * previous_price * dt + sigma * previous_price * dW
            new_price = previous_price + price_change

            # Ensure price doesn't go negative or change too dramatically
            new_price = max(new_price, previous_price * 0.8)  # Max 20% drop
            new_price = min(new_price, previous_price * 1.2)  # Max 20% gain

            # Calculate metrics
            open_price = previous_price
            high_price = max(new_price, previous_price * (1 + abs(sigma * dW) / 2))
            low_price = min(new_price, previous_price * (1 - abs(sigma * dW) / 2))

            simulated_data['prices'][symbol] = {
                'current': round(new_price, 2),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'previous_close': round(previous_price, 2),
                'change': round(new_price - previous_price, 2),
                'change_percent': round(((new_price - previous_price) / previous_price * 100), 2),
                'real_price_reference': round(current_real_price, 2),
                'volatility': round(sigma, 4)
            }

            print(f"✓ {symbol}: ${previous_price:.2f} → ${new_price:.2f} ({simulated_data['prices'][symbol]['change_percent']:+.2f}%)")

        except Exception as e:
            print(f"Error simulating {symbol}: {str(e)}")
            simulated_data['prices'][symbol] = None

    # Store simulated data in S3
    s3_key = f"simulated_data/{date_str}/{time_str}_simulated_prices.json"

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
    latest_key = "simulated_data/latest_simulated_prices.json"
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
            'assets_simulated': len([p for p in simulated_data['prices'].values() if p is not None]),
            'timestamp': timestamp
        })
    }
