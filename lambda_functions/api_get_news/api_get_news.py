import json
import os
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to get latest AI-generated news articles.
    """
    news_bucket = os.environ['NEWS_BUCKET']

    try:
        # Get latest news
        response = s3_client.get_object(
            Bucket=news_bucket,
            Key='latest_news.json'
        )
        news_data = json.loads(response['Body'].read().decode('utf-8'))

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
                'data': news_data,
                'message': 'News fetched successfully'
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
                'message': 'No news available yet. Please wait for the first news generation.'
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
                'message': f'Error fetching news: {str(e)}'
            })
        }
