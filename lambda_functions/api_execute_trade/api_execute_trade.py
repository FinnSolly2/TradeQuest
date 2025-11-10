import json
import os
import boto3
from decimal import Decimal
import time
import uuid
import base64

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to execute buy/sell trades.
    """
    users_table_name = os.environ['USERS_TABLE']
    trades_table_name = os.environ['TRADES_TABLE']
    market_data_bucket = os.environ['MARKET_DATA_BUCKET']

    users_table = dynamodb.Table(users_table_name)
    trades_table = dynamodb.Table(trades_table_name)

    try:
        # Extract username from JWT token
        username = None
        auth_header = event.get('headers', {}).get('Authorization', '') or event.get('headers', {}).get('authorization', '')
        if auth_header:
            try:
                token = auth_header.replace('Bearer ', '')
                # JWT tokens are base64 encoded, split into 3 parts
                payload = token.split('.')[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload)
                token_data = json.loads(decoded)

                # Try multiple possible username fields
                username = (
                    token_data.get('preferred_username') or
                    token_data.get('cognito:username') or
                    token_data.get('email') or
                    token_data.get('name')
                )

                # Debug: log available fields
                print(f"JWT token fields: {list(token_data.keys())}")
                print(f"Extracted username: {username}")
            except Exception as e:
                print(f"Warning: Could not extract username from token: {str(e)}")

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        symbol = body.get('symbol')
        action = body.get('action')  # 'buy' or 'sell'
        quantity = int(body.get('quantity', 0))

        # Validate input
        if not all([user_id, symbol, action, quantity]):
            return error_response(400, 'Missing required fields: user_id, symbol, action, quantity')

        if action not in ['buy', 'sell']:
            return error_response(400, 'Action must be either "buy" or "sell"')

        if quantity <= 0:
            return error_response(400, 'Quantity must be positive')

        # Get current price
        try:
            response = s3_client.get_object(
                Bucket=market_data_bucket,
                Key='simulated_data/latest_simulated_1sec.json'
            )
            simulated_data = json.loads(response['Body'].read().decode('utf-8'))

            # Calculate current second within the hour (0-3599)
            from datetime import datetime
            current_time = datetime.utcnow()
            current_second = (current_time.minute * 60) + current_time.second  # 0-3599

            if symbol not in simulated_data['assets'] or simulated_data['assets'][symbol] is None:
                return error_response(404, f'Symbol {symbol} not found or unavailable')

            asset_data = simulated_data['assets'][symbol]

            # Get the price for the current second
            if 'seconds' in asset_data and current_second < len(asset_data['seconds']):
                current_price = Decimal(str(asset_data['seconds'][current_second]['price']))
            else:
                # Fallback to last available price
                current_price = Decimal(str(asset_data['seconds'][-1]['price']))
        except Exception as e:
            return error_response(500, f'Error fetching price data: {str(e)}')

        # Get user data
        try:
            user_response = users_table.get_item(Key={'user_id': user_id})

            if 'Item' not in user_response:
                # Create new user with initial balance
                user_data = {
                    'user_id': user_id,
                    'username': username if username else user_id[:8],  # Use extracted username or truncated ID
                    'balance': Decimal('100000'),  # Initial balance
                    'portfolio': {},
                    'total_trades': 0,
                    'total_profit_loss': Decimal('0')
                }
                users_table.put_item(Item=user_data)
            else:
                user_data = user_response['Item']
                # Update username if not set and we have one from token
                if username and 'username' not in user_data:
                    user_data['username'] = username

        except Exception as e:
            return error_response(500, f'Error fetching user data: {str(e)}')

        # Calculate trade value
        trade_value = current_price * Decimal(str(quantity))

        # Execute trade logic
        if action == 'buy':
            # Check if user has enough balance
            if user_data['balance'] < trade_value:
                return error_response(400, f'Insufficient balance. Required: ${float(trade_value):.2f}, Available: ${float(user_data["balance"]):.2f}')

            # Deduct balance
            user_data['balance'] -= trade_value

            # Add to portfolio
            portfolio = user_data.get('portfolio', {})
            if symbol in portfolio:
                portfolio[symbol] = {
                    'quantity': int(portfolio[symbol].get('quantity', 0)) + quantity,
                    'avg_price': ((Decimal(str(portfolio[symbol].get('avg_price', 0))) * Decimal(str(portfolio[symbol].get('quantity', 0))) + trade_value) /
                                  (Decimal(str(portfolio[symbol].get('quantity', 0))) + Decimal(str(quantity))))
                }
            else:
                portfolio[symbol] = {
                    'quantity': quantity,
                    'avg_price': current_price
                }
            user_data['portfolio'] = portfolio

        elif action == 'sell':
            # Check if user has enough shares
            portfolio = user_data.get('portfolio', {})
            if symbol not in portfolio or portfolio[symbol]['quantity'] < quantity:
                available = portfolio.get(symbol, {}).get('quantity', 0)
                return error_response(400, f'Insufficient shares. Required: {quantity}, Available: {available}')

            # Add to balance
            user_data['balance'] += trade_value

            # Remove from portfolio
            portfolio[symbol]['quantity'] -= quantity
            if portfolio[symbol]['quantity'] == 0:
                del portfolio[symbol]

            user_data['portfolio'] = portfolio

        # Update trade count
        user_data['total_trades'] = int(user_data.get('total_trades', 0)) + 1

        # Save updated user data
        try:
            users_table.put_item(Item=user_data)
        except Exception as e:
            return error_response(500, f'Error updating user data: {str(e)}')

        # Record trade in trades table
        trade_record = {
            'trade_id': str(uuid.uuid4()),
            'user_id': user_id,
            'timestamp': int(time.time()),
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': current_price,
            'total_value': trade_value
        }

        try:
            trades_table.put_item(Item=trade_record)
        except Exception as e:
            print(f"Warning: Failed to record trade: {str(e)}")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'message': f'Trade executed successfully: {action.upper()} {quantity} shares of {symbol}',
                'trade': {
                    'trade_id': trade_record['trade_id'],
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': float(current_price),
                    'total_value': float(trade_value),
                    'new_balance': float(user_data['balance'])
                }
            }, default=decimal_default)
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


def decimal_default(obj):
    """Helper function to serialize Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
