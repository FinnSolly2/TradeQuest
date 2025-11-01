import json
import os
import boto3
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to get current minute's simulated prices for all assets.
    Returns the appropriate price from the pre-generated 60-price batch
    based on the current minute within the hour.
    """
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']

    try:
        # Get latest simulated data (60 prices per asset)
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='simulated_data/latest_simulated_1min.json'
        )
        simulated_data = json.loads(response['Body'].read().decode('utf-8'))

        # Calculate current minute within the hour (0-59)
        current_time = datetime.utcnow()
        current_minute = current_time.minute  # 0-59

        # Build response with current minute's prices for all assets
        prices = {}

        for symbol, asset_data in simulated_data['assets'].items():
            if asset_data is None or 'minutes' not in asset_data:
                prices[symbol] = {
                    'error': 'No data available',
                    'current': None
                }
                continue

            # Get the price for the current minute
            if current_minute < len(asset_data['minutes']):
                minute_data = asset_data['minutes'][current_minute]
                prices[symbol] = {
                    'current': minute_data['price'],
                    'timestamp': minute_data['timestamp'],
                    'datetime': minute_data['datetime'],
                    'minute': minute_data['minute'],
                    'hour_high': asset_data['hour_high'],
                    'hour_low': asset_data['hour_low'],
                    'hour_start': asset_data['start_price'],
                    'hour_projected_end': asset_data['end_price'],
                    'hour_projected_change_percent': asset_data['hour_change_percent']
                }
            else:
                # Fallback to last available price if current minute is out of range
                minute_data = asset_data['minutes'][-1]
                prices[symbol] = {
                    'current': minute_data['price'],
                    'timestamp': minute_data['timestamp'],
                    'datetime': minute_data['datetime'],
                    'minute': minute_data['minute'],
                    'hour_high': asset_data['hour_high'],
                    'hour_low': asset_data['hour_low'],
                    'hour_start': asset_data['start_price'],
                    'hour_projected_end': asset_data['end_price'],
                    'hour_projected_change_percent': asset_data['hour_change_percent'],
                    'note': 'Using last available minute (simulation may be outdated)'
                }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'data': {
                    'prices': prices,
                    'current_minute': current_minute,
                    'current_time': current_time.isoformat(),
                    'simulation_timestamp': simulated_data['timestamp'],
                    'simulation_datetime': simulated_data['datetime'],
                    'simulation_start': simulated_data['start_timestamp'],
                    'simulation_end': simulated_data['end_timestamp'],
                    'resolution': simulated_data['resolution']
                },
                'message': f'Prices for minute {current_minute} fetched successfully'
            })
        }

    except s3_client.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'message': 'No price data available yet. Please wait for the first simulation run.'
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'message': f'Error fetching prices: {str(e)}'
            })
        }
