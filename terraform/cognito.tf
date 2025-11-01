# ============================================================================
# COGNITO USER POOL - Authentication
# ============================================================================

resource "aws_cognito_user_pool" "trade_quest" {
  name = "${var.project_name}-users-${var.environment}"

  # Allow users to sign in with email or username
  alias_attributes = ["email", "preferred_username"]
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # User attributes
  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
    mutable             = true

    string_attribute_constraints {
      min_length = 5
      max_length = 256
    }
  }

  # User pool tags
  tags = {
    Name        = "${var.project_name}-user-pool-${var.environment}"
    Environment = var.environment
  }
}

# ============================================================================
# COGNITO USER POOL CLIENT - Frontend App
# ============================================================================

resource "aws_cognito_user_pool_client" "trade_quest_web" {
  name         = "${var.project_name}-web-client-${var.environment}"
  user_pool_id = aws_cognito_user_pool.trade_quest.id

  # OAuth flows
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["implicit", "code"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]

  # Callback URLs (update these with your CloudFront URL)
  callback_urls = [
    "http://localhost:8000",
    "https://${aws_cloudfront_distribution.frontend.domain_name}"
  ]

  logout_urls = [
    "http://localhost:8000",
    "https://${aws_cloudfront_distribution.frontend.domain_name}"
  ]

  # Token validity
  id_token_validity      = 60  # 60 minutes
  access_token_validity  = 60  # 60 minutes
  refresh_token_validity = 30  # 30 days

  token_validity_units {
    id_token      = "minutes"
    access_token  = "minutes"
    refresh_token = "days"
  }

  # Authentication flows
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  # Security
  prevent_user_existence_errors = "ENABLED"

  # Read/Write attributes
  read_attributes = [
    "email",
    "email_verified"
  ]

  write_attributes = [
    "email"
  ]
}

# ============================================================================
# COGNITO USER POOL DOMAIN - Hosted UI
# ============================================================================

resource "aws_cognito_user_pool_domain" "trade_quest" {
  domain       = "${var.project_name}-${var.environment}-${random_string.cognito_domain_suffix.result}"
  user_pool_id = aws_cognito_user_pool.trade_quest.id
}

# Random suffix to ensure unique Cognito domain
resource "random_string" "cognito_domain_suffix" {
  length  = 8
  special = false
  upper   = false
}

# ============================================================================
# COGNITO IDENTITY POOL - For AWS SDK Access
# ============================================================================

resource "aws_cognito_identity_pool" "trade_quest" {
  identity_pool_name               = "${var.project_name}_identity_pool_${var.environment}"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.trade_quest_web.id
    provider_name           = aws_cognito_user_pool.trade_quest.endpoint
    server_side_token_check = false
  }
}

# ============================================================================
# IAM ROLES FOR COGNITO IDENTITY POOL
# ============================================================================

# Authenticated role
resource "aws_iam_role" "cognito_authenticated" {
  name = "${var.project_name}-cognito-authenticated-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = aws_cognito_identity_pool.trade_quest.id
          }
          "ForAnyValue:StringLike" = {
            "cognito-identity.amazonaws.com:amr" = "authenticated"
          }
        }
      }
    ]
  })
}

# Attach policy to authenticated role
resource "aws_iam_role_policy" "cognito_authenticated_policy" {
  name = "${var.project_name}-cognito-authenticated-policy-${var.environment}"
  role = aws_iam_role.cognito_authenticated.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cognito-identity:GetCredentialsForIdentity",
          "cognito-identity:GetId"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach identity pool roles
resource "aws_cognito_identity_pool_roles_attachment" "trade_quest" {
  identity_pool_id = aws_cognito_identity_pool.trade_quest.id

  roles = {
    authenticated = aws_iam_role.cognito_authenticated.arn
  }
}
