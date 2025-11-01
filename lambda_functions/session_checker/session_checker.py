import json
import os
import boto3
import time

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Checks for active user sessions.
    This function is triggered every 15 minutes by EventBridge.
    It verifies if any users are actively connected before releasing news.
    """
    sessions_table_name = os.environ['SESSIONS_TABLE']
    sessions_table = dynamodb.Table(sessions_table_name)

    current_time = int(time.time())

    try:
        # Scan for active sessions (sessions that haven't expired)
        response = sessions_table.scan(
            FilterExpression='expires_at > :current_time',
            ExpressionAttributeValues={
                ':current_time': current_time
            }
        )

        active_sessions = response.get('Items', [])
        active_count = len(active_sessions)

        print(f"Found {active_count} active sessions")

        if active_count > 0:
            print("Active users detected - news should be visible")
            # In a more sophisticated implementation, you could trigger
            # a notification or update mechanism here
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'active_sessions': active_count,
                    'message': 'Active users detected',
                    'should_show_news': True
                })
            }
        else:
            print("No active users - news release paused")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'active_sessions': 0,
                    'message': 'No active users',
                    'should_show_news': False
                })
            }

    except Exception as e:
        print(f"Error checking sessions: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}',
                'should_show_news': True  # Default to showing news on error
            })
        }
