terraform {
  backend "s3" {
    bucket         = "trade-quest-terraform-state-dev"
    key            = "terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "trade-quest-terraform-lock-dev"
  }
}
