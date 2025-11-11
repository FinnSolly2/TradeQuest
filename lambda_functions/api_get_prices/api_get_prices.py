import json
import os
import boto3
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to get current second's simulated prices for all assets.
    Returns the appropriate price from the pre-generated 600-price batch
    based on the current second within the 10-minute period.
    """
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']

    try:
        # Get latest simulated data (600 prices per asset, 10-minute period)
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='simulated_data/latest_simulated_1sec.json'
        )
        simulated_data = json.loads(response['Body'].read().decode('utf-8'))

        # Calculate current second within the 10-minute period (0-599)
        current_time = datetime.utcnow()
        current_second = ((current_time.minute % 10) * 60) + current_time.second  # 0-599

        # Build response with current second's prices for all assets
        prices = {}

        for symbol, asset_data in simulated_data['assets'].items():
            if asset_data is None or 'seconds' not in asset_data:
                prices[symbol] = {
                    'error': 'No data available',
                    'current': None
                }
                continue

            # Get the price for the current second
            if current_second < len(asset_data['seconds']):
                second_data = asset_data['seconds'][current_second]
                prices[symbol] = {
                    'current': second_data['price'],
                    'timestamp': second_data['timestamp'],
                    'datetime': second_data['datetime'],
                    'second': second_data['second'],
                    'period_high': asset_data.get('period_high', asset_data.get('hour_high')),
                    'period_low': asset_data.get('period_low', asset_data.get('hour_low')),
                    'hour_start': asset_data['start_price'],
                    'hour_projected_end': asset_data['end_price'],
                    'period_change_percent': asset_data.get('period_change_percent', asset_data.get('hour_change_percent'))
                }
            else:
                # Fallback to last available price if current second is out of range
                second_data = asset_data['seconds'][-1]
                prices[symbol] = {
                    'current': second_data['price'],
                    'timestamp': second_data['timestamp'],
                    'datetime': second_data['datetime'],
                    'second': second_data['second'],
                    'period_high': asset_data.get('period_high', asset_data.get('hour_high')),
                    'period_low': asset_data.get('period_low', asset_data.get('hour_low')),
                    'hour_start': asset_data['start_price'],
                    'hour_projected_end': asset_data['end_price'],
                    'period_change_percent': asset_data.get('period_change_percent', asset_data.get('hour_change_percent')),
                    'note': 'Using last available second (simulation may be outdated)'
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
                    'current_second': current_second,
                    'current_time': current_time.isoformat(),
                    'simulation_timestamp': simulated_data['timestamp'],
                    'simulation_datetime': simulated_data['datetime'],
                    'simulation_start': simulated_data['start_timestamp'],
                    'simulation_end': simulated_data['end_timestamp'],
                    'resolution': simulated_data['resolution']
                },
                'message': f'Prices for second {current_second} fetched successfully'
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
