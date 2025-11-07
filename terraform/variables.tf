# General Configuration
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "trade-quest"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# API Keys
variable "finnhub_api_key" {
  description = "Finnhub API key for market data"
  type        = string
  sensitive   = true
}

variable "huggingface_api_key" {
  description = "Hugging Face API key for AI news generation"
  type        = string
  sensitive   = true
}

# Trading Configuration
variable "assets_to_track" {
  description = "List of asset symbols to track"
  type        = list(string)
  default = [
    "AAPL",
    "GOOGL",
    "MSFT",
    "TSLA",
    "AMZN",
    "ASML.AS",
    "MC.PA",
    "SAP",
    "OR.PA",
    "SIE.DE"
  ]
}

variable "initial_balance" {
  description = "Initial balance for new users"
  type        = number
  default     = 100000
}

variable "data_fetch_schedule" {
  description = "Cron expression for data fetching (default: every hour)"
  type        = string
  default     = "cron(0 * * * ? *)"
}

variable "news_release_schedule" {
  description = "Rate expression for news release (default: every 15 minutes)"
  type        = string
  default     = "rate(15 minutes)"
}
