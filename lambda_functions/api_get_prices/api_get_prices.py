import json
import os
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to get current simulated prices for all assets.
    """
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']

    try:
        # Get latest simulated prices
        response = s3_client.get_object(
            Bucket=market_data_bucket,
            Key='simulated_data/latest_simulated_prices.json'
        )
        price_data = json.loads(response['Body'].read().decode('utf-8'))

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
                'data': price_data,
                'message': 'Prices fetched successfully'
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
