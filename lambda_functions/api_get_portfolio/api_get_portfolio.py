import json
import os
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to get user's portfolio including positions, balance, and P/L.
    """
    users_table_name = os.environ['USERS_TABLE']
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']

    users_table = dynamodb.Table(users_table_name)

    try:
        # Get user_id from query parameters
        user_id = event.get('queryStringParameters', {}).get('user_id')

        if not user_id:
            return error_response(400, 'Missing required parameter: user_id')

        # Get user data
        try:
            user_response = users_table.get_item(Key={'user_id': user_id})

            if 'Item' not in user_response:
                # Return default portfolio for new user
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
                            'user_id': user_id,
                            'balance': 100000.0,
                            'portfolio': {},
                            'portfolio_value': 0.0,
                            'total_value': 100000.0,
                            'total_profit_loss': 0.0,
                            'total_profit_loss_percent': 0.0,
                            'positions': []
                        },
                        'message': 'New user portfolio'
                    })
                }

            user_data = user_response['Item']

        except Exception as e:
            return error_response(500, f'Error fetching user data: {str(e)}')

        # Get current prices for portfolio valuation
        try:
            response = s3_client.get_object(
                Bucket=market_data_bucket,
                Key='simulated_data/latest_simulated_prices.json'
            )
            price_data = json.loads(response['Body'].read().decode('utf-8'))
        except Exception as e:
            return error_response(500, f'Error fetching price data: {str(e)}')

        # Calculate portfolio value and positions
        portfolio = user_data.get('portfolio', {})
        positions = []
        total_portfolio_value = Decimal('0')
        total_cost_basis = Decimal('0')

        for symbol, holding in portfolio.items():
            if symbol in price_data['prices'] and price_data['prices'][symbol]:
                current_price = Decimal(str(price_data['prices'][symbol]['current']))
                quantity = Decimal(str(holding['quantity']))
                avg_price = Decimal(str(holding['avg_price']))

                market_value = current_price * quantity
                cost_basis = avg_price * quantity
                profit_loss = market_value - cost_basis
                profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else Decimal('0')

                positions.append({
                    'symbol': symbol,
                    'quantity': int(quantity),
                    'avg_price': float(avg_price),
                    'current_price': float(current_price),
                    'market_value': float(market_value),
                    'cost_basis': float(cost_basis),
                    'profit_loss': float(profit_loss),
                    'profit_loss_percent': float(profit_loss_percent)
                })

                total_portfolio_value += market_value
                total_cost_basis += cost_basis

        # Calculate total account value
        balance = user_data.get('balance', Decimal('100000'))
        total_value = balance + total_portfolio_value

        # Calculate overall P/L (assuming initial balance was 100000)
        initial_investment = Decimal('100000')
        total_profit_loss = total_value - initial_investment
        total_profit_loss_percent = (total_profit_loss / initial_investment * 100) if initial_investment > 0 else Decimal('0')

        portfolio_data = {
            'user_id': user_id,
            'balance': float(balance),
            'portfolio_value': float(total_portfolio_value),
            'total_value': float(total_value),
            'total_profit_loss': float(total_profit_loss),
            'total_profit_loss_percent': float(total_profit_loss_percent),
            'total_trades': int(user_data.get('total_trades', 0)),
            'positions': sorted(positions, key=lambda x: x['market_value'], reverse=True)
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
                'data': portfolio_data,
                'message': 'Portfolio fetched successfully'
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')


def error_response(status_code, message):
    """Helper function to return error responses"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'message': message
        })
    }
