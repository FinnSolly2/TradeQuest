import json
import os
import boto3
import time

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    API endpoint to get AI-generated news articles.
    Only returns articles where publish_at <= current_time (staggered release).
    """
    news_bucket = os.environ['NEWS_BUCKET']
    current_time = int(time.time())

    try:
        # Get latest news
        response = s3_client.get_object(
            Bucket=news_bucket,
            Key='latest_news.json'
        )
        news_data = json.loads(response['Body'].read().decode('utf-8'))

        # Filter articles by publish_at time (only show published articles)
        all_articles = news_data.get('articles', [])
        published_articles = [
            article for article in all_articles
            if article.get('publish_at', 0) <= current_time
        ]

        # Sort by publish_at (most recent first)
        published_articles.sort(key=lambda x: x.get('publish_at', 0), reverse=True)

        # Update response data
        filtered_news_data = {
            'timestamp': news_data.get('timestamp'),
            'datetime': news_data.get('datetime'),
            'articles': published_articles,
            'total_articles': len(all_articles),
            'published_articles': len(published_articles),
            'pending_articles': len(all_articles) - len(published_articles)
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
                'data': filtered_news_data,
                'message': f'{len(published_articles)} news articles available'
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
