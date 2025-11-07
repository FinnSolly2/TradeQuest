# ============================================================================
# S3 BUCKETS
# ============================================================================

# Bucket for market data (real and simulated prices)
resource "aws_s3_bucket" "market_data" {
  bucket = "${var.project_name}-market-data-${var.environment}"
}

resource "aws_s3_bucket_versioning" "market_data" {
  bucket = aws_s3_bucket.market_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Bucket for AI-generated news
resource "aws_s3_bucket" "news_data" {
  bucket = "${var.project_name}-news-${var.environment}"
}

resource "aws_s3_bucket_versioning" "news_data" {
  bucket = aws_s3_bucket.news_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Bucket for Lambda deployment packages
resource "aws_s3_bucket" "lambda_artifacts" {
  bucket = "${var.project_name}-lambda-artifacts-${var.environment}"
}

# ============================================================================
# DYNAMODB TABLES
# ============================================================================

# Users table - stores user account information
resource "aws_dynamodb_table" "users" {
  name           = "${var.project_name}-users-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  global_secondary_index {
    name            = "EmailIndex"
    hash_key        = "email"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = false
  }
}

# Sessions table - tracks active user sessions
resource "aws_dynamodb_table" "sessions" {
  name           = "${var.project_name}-sessions-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}

# Trades table - stores trading history
resource "aws_dynamodb_table" "trades" {
  name           = "${var.project_name}-trades-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "trade_id"
  range_key      = "timestamp"

  attribute {
    name = "trade_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
}

# Leaderboard table - stores user rankings
resource "aws_dynamodb_table" "leaderboard" {
  name           = "${var.project_name}-leaderboard-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "period"
  range_key      = "rank"

  attribute {
    name = "period"
    type = "S"
  }

  attribute {
    name = "rank"
    type = "N"
  }

  attribute {
    name = "total_profit"
    type = "N"
  }

  global_secondary_index {
    name            = "ProfitIndex"
    hash_key        = "period"
    range_key       = "total_profit"
    projection_type = "ALL"
  }
}

# ============================================================================
# IAM ROLES AND POLICIES
# ============================================================================

# Lambda execution role
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Lambda policy for S3 and DynamoDB access
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${var.environment}"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.market_data.arn,
          "${aws_s3_bucket.market_data.arn}/*",
          aws_s3_bucket.news_data.arn,
          "${aws_s3_bucket.news_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.users.arn,
          "${aws_dynamodb_table.users.arn}/index/*",
          aws_dynamodb_table.sessions.arn,
          "${aws_dynamodb_table.sessions.arn}/index/*",
          aws_dynamodb_table.trades.arn,
          "${aws_dynamodb_table.trades.arn}/index/*",
          aws_dynamodb_table.leaderboard.arn,
          "${aws_dynamodb_table.leaderboard.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Step Functions execution role
resource "aws_iam_role" "step_functions_role" {
  name = "${var.project_name}-step-functions-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

# Step Functions policy to invoke Lambda functions
resource "aws_iam_role_policy" "step_functions_policy" {
  name = "${var.project_name}-step-functions-policy-${var.environment}"
  role = aws_iam_role.step_functions_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "*"
      }
    ]
  })
}

# EventBridge role
resource "aws_iam_role" "eventbridge_role" {
  name = "${var.project_name}-eventbridge-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
    }]
  })
}

# EventBridge policy to trigger Step Functions
resource "aws_iam_role_policy" "eventbridge_policy" {
  name = "${var.project_name}-eventbridge-policy-${var.environment}"
  role = aws_iam_role.eventbridge_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution"
        ]
        Resource = aws_sfn_state_machine.simulation_pipeline.arn
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "*"
      }
    ]
  })
}

# ============================================================================
# LAMBDA FUNCTIONS
# ============================================================================

# Price collector Lambda - runs every minute to collect real prices
resource "aws_lambda_function" "price_collector" {
  filename         = "${path.module}/../lambda_packages/price_collector.zip"
  function_name    = "${var.project_name}-price-collector-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "price_collector.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/price_collector.zip") ? filebase64sha256("${path.module}/../lambda_packages/price_collector.zip") : null
  runtime         = "python3.11"
  timeout         = 120
  memory_size     = 256

  environment {
    variables = {
      FINNHUB_API_KEY    = var.finnhub_api_key
      MARKET_DATA_BUCKET = aws_s3_bucket.market_data.id
      ASSETS_TO_TRACK    = jsonencode(var.assets_to_track)
    }
  }
}

# Finnhub data fetcher Lambda (DEPRECATED - will be removed)
resource "aws_lambda_function" "finnhub_fetcher" {
  filename         = "${path.module}/../lambda_packages/finnhub_fetcher.zip"
  function_name    = "${var.project_name}-finnhub-fetcher-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "finnhub_fetcher.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/finnhub_fetcher.zip") ? filebase64sha256("${path.module}/../lambda_packages/finnhub_fetcher.zip") : null
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 512

  environment {
    variables = {
      FINNHUB_API_KEY    = var.finnhub_api_key
      MARKET_DATA_BUCKET = aws_s3_bucket.market_data.id
      ASSETS_TO_TRACK    = jsonencode(var.assets_to_track)
    }
  }
}

# Price simulator Lambda
resource "aws_lambda_function" "price_simulator" {
  filename         = "${path.module}/../lambda_packages/price_simulator.zip"
  function_name    = "${var.project_name}-price-simulator-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "price_simulator.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/price_simulator.zip") ? filebase64sha256("${path.module}/../lambda_packages/price_simulator.zip") : null
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 1024

  environment {
    variables = {
      MARKET_DATA_BUCKET = aws_s3_bucket.market_data.id
    }
  }
}

# AI news generator Lambda
resource "aws_lambda_function" "news_generator" {
  filename         = "${path.module}/../lambda_packages/news_generator.zip"
  function_name    = "${var.project_name}-news-generator-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "news_generator.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/news_generator.zip") ? filebase64sha256("${path.module}/../lambda_packages/news_generator.zip") : null
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 512

  environment {
    variables = {
      HUGGINGFACE_API_KEY = var.huggingface_api_key
      MARKET_DATA_BUCKET  = aws_s3_bucket.market_data.id
      NEWS_BUCKET         = aws_s3_bucket.news_data.id
    }
  }
}

# API handler - Get prices
resource "aws_lambda_function" "api_get_prices" {
  filename         = "${path.module}/../lambda_packages/api_get_prices.zip"
  function_name    = "${var.project_name}-api-get-prices-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "api_get_prices.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/api_get_prices.zip") ? filebase64sha256("${path.module}/../lambda_packages/api_get_prices.zip") : null
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      MARKET_DATA_BUCKET = aws_s3_bucket.market_data.id
    }
  }
}

# API handler - Get news
resource "aws_lambda_function" "api_get_news" {
  filename         = "${path.module}/../lambda_packages/api_get_news.zip"
  function_name    = "${var.project_name}-api-get-news-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "api_get_news.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/api_get_news.zip") ? filebase64sha256("${path.module}/../lambda_packages/api_get_news.zip") : null
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      NEWS_BUCKET = aws_s3_bucket.news_data.id
    }
  }
}

# API handler - Execute trade
resource "aws_lambda_function" "api_execute_trade" {
  filename         = "${path.module}/../lambda_packages/api_execute_trade.zip"
  function_name    = "${var.project_name}-api-execute-trade-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "api_execute_trade.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/api_execute_trade.zip") ? filebase64sha256("${path.module}/../lambda_packages/api_execute_trade.zip") : null
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      USERS_TABLE  = aws_dynamodb_table.users.name
      TRADES_TABLE = aws_dynamodb_table.trades.name
      MARKET_DATA_BUCKET = aws_s3_bucket.market_data.id
    }
  }
}

# API handler - Get portfolio
resource "aws_lambda_function" "api_get_portfolio" {
  filename         = "${path.module}/../lambda_packages/api_get_portfolio.zip"
  function_name    = "${var.project_name}-api-get-portfolio-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "api_get_portfolio.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/api_get_portfolio.zip") ? filebase64sha256("${path.module}/../lambda_packages/api_get_portfolio.zip") : null
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      USERS_TABLE  = aws_dynamodb_table.users.name
      TRADES_TABLE = aws_dynamodb_table.trades.name
      MARKET_DATA_BUCKET = aws_s3_bucket.market_data.id
    }
  }
}

# API handler - Get leaderboard
resource "aws_lambda_function" "api_get_leaderboard" {
  filename         = "${path.module}/../lambda_packages/api_get_leaderboard.zip"
  function_name    = "${var.project_name}-api-get-leaderboard-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "api_get_leaderboard.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/api_get_leaderboard.zip") ? filebase64sha256("${path.module}/../lambda_packages/api_get_leaderboard.zip") : null
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      LEADERBOARD_TABLE  = aws_dynamodb_table.leaderboard.name
      USERS_TABLE        = aws_dynamodb_table.users.name
      MARKET_DATA_BUCKET = aws_s3_bucket.market_data.id
    }
  }
}

# Session checker Lambda (for news release)
resource "aws_lambda_function" "session_checker" {
  filename         = "${path.module}/../lambda_packages/session_checker.zip"
  function_name    = "${var.project_name}-session-checker-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "session_checker.lambda_handler"
  source_code_hash = fileexists("${path.module}/../lambda_packages/session_checker.zip") ? filebase64sha256("${path.module}/../lambda_packages/session_checker.zip") : null
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      SESSIONS_TABLE = aws_dynamodb_table.sessions.name
    }
  }
}

# ============================================================================
# STEP FUNCTIONS
# ============================================================================

resource "aws_sfn_state_machine" "simulation_pipeline" {
  name     = "${var.project_name}-simulation-pipeline-${var.environment}"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({
    Comment = "Trade Quest simulation pipeline (uses collected price data)"
    StartAt = "SimulatePrices"
    States = {
      SimulatePrices = {
        Type     = "Task"
        Resource = aws_lambda_function.price_simulator.arn
        Next     = "GenerateNews"
        Retry = [{
          ErrorEquals     = ["States.TaskFailed"]
          IntervalSeconds = 2
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next        = "HandleError"
        }]
      }
      GenerateNews = {
        Type     = "Task"
        Resource = aws_lambda_function.news_generator.arn
        End      = true
        Retry = [{
          ErrorEquals     = ["States.TaskFailed"]
          IntervalSeconds = 2
          MaxAttempts     = 3
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next        = "HandleError"
        }]
      }
      HandleError = {
        Type = "Fail"
        Error = "SimulationPipelineFailed"
        Cause = "One of the simulation steps failed after retries"
      }
    }
  })
}

# ============================================================================
# EVENTBRIDGE RULES
# ============================================================================

# Minute-by-minute rule for price collection
resource "aws_cloudwatch_event_rule" "price_collection" {
  name                = "${var.project_name}-price-collection-${var.environment}"
  description         = "Collect prices from Finnhub every minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "price_collection_target" {
  rule     = aws_cloudwatch_event_rule.price_collection.name
  arn      = aws_lambda_function.price_collector.arn
}

resource "aws_lambda_permission" "allow_eventbridge_price_collection" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.price_collector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.price_collection.arn
}

# Hourly rule for data fetching and simulation
resource "aws_cloudwatch_event_rule" "hourly_simulation" {
  name                = "${var.project_name}-hourly-simulation-${var.environment}"
  description         = "Trigger simulation pipeline every hour"
  schedule_expression = var.data_fetch_schedule
}

resource "aws_cloudwatch_event_target" "hourly_simulation_target" {
  rule     = aws_cloudwatch_event_rule.hourly_simulation.name
  arn      = aws_sfn_state_machine.simulation_pipeline.arn
  role_arn = aws_iam_role.eventbridge_role.arn
}

# 15-minute rule for news release (with session check)
resource "aws_cloudwatch_event_rule" "news_release" {
  name                = "${var.project_name}-news-release-${var.environment}"
  description         = "Check for active sessions and release news every 15 minutes"
  schedule_expression = var.news_release_schedule
}

resource "aws_cloudwatch_event_target" "news_release_target" {
  rule     = aws_cloudwatch_event_rule.news_release.name
  arn      = aws_lambda_function.session_checker.arn
}

resource "aws_lambda_permission" "allow_eventbridge_news" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.session_checker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.news_release.arn
}

# ============================================================================
# API GATEWAY
# ============================================================================

resource "aws_apigatewayv2_api" "trade_quest_api" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["*"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.trade_quest_api.id
  name        = "prod"
  auto_deploy = true
}

# Cognito Authorizer
resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.trade_quest_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "${var.project_name}-cognito-authorizer-${var.environment}"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.trade_quest_web.id]
    issuer   = "https://${aws_cognito_user_pool.trade_quest.endpoint}"
  }
}

# Lambda integrations
resource "aws_apigatewayv2_integration" "get_prices" {
  api_id           = aws_apigatewayv2_api.trade_quest_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_get_prices.invoke_arn
}

resource "aws_apigatewayv2_route" "get_prices" {
  api_id    = aws_apigatewayv2_api.trade_quest_api.id
  route_key = "GET /prices"
  target    = "integrations/${aws_apigatewayv2_integration.get_prices.id}"
}

resource "aws_lambda_permission" "api_get_prices" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_get_prices.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.trade_quest_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "get_news" {
  api_id           = aws_apigatewayv2_api.trade_quest_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_get_news.invoke_arn
}

resource "aws_apigatewayv2_route" "get_news" {
  api_id    = aws_apigatewayv2_api.trade_quest_api.id
  route_key = "GET /news"
  target    = "integrations/${aws_apigatewayv2_integration.get_news.id}"
}

resource "aws_lambda_permission" "api_get_news" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_get_news.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.trade_quest_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "execute_trade" {
  api_id           = aws_apigatewayv2_api.trade_quest_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_execute_trade.invoke_arn
}

resource "aws_apigatewayv2_route" "execute_trade" {
  api_id             = aws_apigatewayv2_api.trade_quest_api.id
  route_key          = "POST /trade"
  target             = "integrations/${aws_apigatewayv2_integration.execute_trade.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_lambda_permission" "api_execute_trade" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_execute_trade.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.trade_quest_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "get_portfolio" {
  api_id           = aws_apigatewayv2_api.trade_quest_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_get_portfolio.invoke_arn
}

resource "aws_apigatewayv2_route" "get_portfolio" {
  api_id             = aws_apigatewayv2_api.trade_quest_api.id
  route_key          = "GET /portfolio"
  target             = "integrations/${aws_apigatewayv2_integration.get_portfolio.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_lambda_permission" "api_get_portfolio" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_get_portfolio.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.trade_quest_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "get_leaderboard" {
  api_id           = aws_apigatewayv2_api.trade_quest_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_get_leaderboard.invoke_arn
}

resource "aws_apigatewayv2_route" "get_leaderboard" {
  api_id    = aws_apigatewayv2_api.trade_quest_api.id
  route_key = "GET /leaderboard"
  target    = "integrations/${aws_apigatewayv2_integration.get_leaderboard.id}"
}

resource "aws_lambda_permission" "api_get_leaderboard" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_get_leaderboard.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.trade_quest_api.execution_arn}/*/*"
}

# ============================================================================
# COGNITO
# ============================================================================

resource "aws_cognito_user_pool" "trade_quest_pool" {
  name = "${var.project_name}-user-pool-${var.environment}"

  username_attributes = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }

  schema {
    name                = "name"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }
}

resource "aws_cognito_user_pool_client" "trade_quest_client" {
  name         = "${var.project_name}-client-${var.environment}"
  user_pool_id = aws_cognito_user_pool.trade_quest_pool.id

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  generate_secret = false
}
