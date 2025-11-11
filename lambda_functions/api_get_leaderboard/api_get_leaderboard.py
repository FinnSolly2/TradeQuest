import json
import os
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to get leaderboard rankings based on total profit/loss.
    """
    users_table_name = os.environ['USERS_TABLE']
    leaderboard_table_name = os.environ['LEADERBOARD_TABLE']
    market_data_bucket = os.environ.get('MARKET_DATA_BUCKET')

    users_table = dynamodb.Table(users_table_name)
    leaderboard_table = dynamodb.Table(leaderboard_table_name)

    try:
        # Get current prices for portfolio valuation
        try:
            response = s3_client.get_object(
                Bucket=market_data_bucket,
                Key='simulated_data/latest_simulated_1sec.json'
            )
            simulated_data = json.loads(response['Body'].read().decode('utf-8'))

            # Calculate current second within the 10-minute period (0-599)
            from datetime import datetime
            current_time = datetime.utcnow()
            current_second = ((current_time.minute % 10) * 60) + current_time.second  # 0-599
        except Exception:
            # If no price data available, proceed without it
            simulated_data = None
            current_second = 0

        # Scan all users and calculate their total values
        users_response = users_table.scan()
        users = users_response.get('Items', [])

        leaderboard_entries = []
        initial_investment = Decimal('100000')

        for user in users:
            user_id = user['user_id']
            username = user.get('username', user_id[:8])  # Use username or truncated user_id as fallback
            balance = user.get('balance', Decimal('100000'))
            portfolio = user.get('portfolio', {})
            total_trades = user.get('total_trades', 0)

            # Calculate portfolio value
            portfolio_value = Decimal('0')
            if simulated_data:
                for symbol, holding in portfolio.items():
                    if symbol in simulated_data['assets'] and simulated_data['assets'][symbol]:
                        asset_data = simulated_data['assets'][symbol]

                        # Get the price for the current second
                        if 'seconds' in asset_data and current_second < len(asset_data['seconds']):
                            current_price = Decimal(str(asset_data['seconds'][current_second]['price']))
                        else:
                            # Fallback to last available price
                            current_price = Decimal(str(asset_data['seconds'][-1]['price']))

                        quantity = Decimal(str(holding['quantity']))
                        portfolio_value += current_price * quantity

            total_value = balance + portfolio_value
            profit_loss = total_value - initial_investment
            profit_loss_percent = (profit_loss / initial_investment * 100) if initial_investment > 0 else Decimal('0')

            leaderboard_entries.append({
                'user_id': user_id,
                'username': username,
                'total_value': float(total_value),
                'profit_loss': float(profit_loss),
                'profit_loss_percent': float(profit_loss_percent),
                'total_trades': int(total_trades),
                'balance': float(balance),
                'portfolio_value': float(portfolio_value)
            })

        # Sort by profit_loss descending
        leaderboard_entries.sort(key=lambda x: x['profit_loss'], reverse=True)

        # Add rank
        for i, entry in enumerate(leaderboard_entries):
            entry['rank'] = i + 1

        # Limit to top 100
        leaderboard_entries = leaderboard_entries[:100]

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
                    'leaderboard': leaderboard_entries,
                    'total_users': len(users)
                },
                'message': 'Leaderboard fetched successfully'
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
                'message': f'Internal server error: {str(e)}'
            })
        }
