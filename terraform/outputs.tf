# S3 Outputs
output "market_data_bucket" {
  description = "S3 bucket for market data"
  value       = aws_s3_bucket.market_data.id
}

output "news_bucket" {
  description = "S3 bucket for AI-generated news"
  value       = aws_s3_bucket.news_data.id
}

# DynamoDB Outputs
output "users_table" {
  description = "DynamoDB table for user data"
  value       = aws_dynamodb_table.users.id
}

output "sessions_table" {
  description = "DynamoDB table for active sessions"
  value       = aws_dynamodb_table.sessions.id
}

output "trades_table" {
  description = "DynamoDB table for trade history"
  value       = aws_dynamodb_table.trades.id
}

output "leaderboard_table" {
  description = "DynamoDB table for leaderboard"
  value       = aws_dynamodb_table.leaderboard.id
}

# Cognito Outputs
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.trade_quest.id
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.trade_quest_web.id
}

output "cognito_user_pool_endpoint" {
  description = "Cognito User Pool Endpoint"
  value       = aws_cognito_user_pool.trade_quest.endpoint
}

output "cognito_identity_pool_id" {
  description = "Cognito Identity Pool ID"
  value       = aws_cognito_identity_pool.trade_quest.id
}

output "cognito_domain" {
  description = "Cognito Hosted UI Domain"
  value       = aws_cognito_user_pool_domain.trade_quest.domain
}

output "cognito_region" {
  description = "AWS Region for Cognito"
  value       = var.aws_region
}

# API Gateway Outputs
output "api_gateway_url" {
  description = "API Gateway invoke URL"
  value       = aws_apigatewayv2_stage.prod.invoke_url
}

# Lambda Outputs
output "finnhub_fetcher_function_name" {
  description = "Finnhub data fetcher Lambda function name"
  value       = aws_lambda_function.finnhub_fetcher.function_name
}

output "price_simulator_function_name" {
  description = "Price simulator Lambda function name"
  value       = aws_lambda_function.price_simulator.function_name
}

output "news_generator_function_name" {
  description = "News generator Lambda function name"
  value       = aws_lambda_function.news_generator.function_name
}

# Step Functions Outputs
output "simulation_state_machine_arn" {
  description = "Step Functions state machine ARN"
  value       = aws_sfn_state_machine.simulation_pipeline.arn
}

# Frontend Hosting Outputs
output "frontend_bucket" {
  description = "S3 bucket for frontend hosting"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_url" {
  description = "CloudFront distribution URL for frontend"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for cache invalidation)"
  value       = aws_cloudfront_distribution.frontend.id
}
