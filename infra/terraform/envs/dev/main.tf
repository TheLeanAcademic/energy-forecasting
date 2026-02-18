terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 buckets
module "s3" {
  source = "../../modules/s3"

  data_bucket_name      = "forecast-bench-data-${var.environment}"
  artifacts_bucket_name = "forecast-bench-artifacts-${var.environment}"
  environment           = var.environment
}

# ECR repository
module "ecr" {
  source = "../../modules/ecr"

  repository_name = "forecast-bench"
  environment     = var.environment
}

# IAM roles
module "iam" {
  source = "../../modules/iam"

  environment          = var.environment
  data_bucket_arn      = module.s3.data_bucket_arn
  artifacts_bucket_arn = module.s3.artifacts_bucket_arn
}

# Outputs
output "data_bucket_name" {
  value       = module.s3.data_bucket_name
  description = "Name of the S3 bucket for data"
}

output "artifacts_bucket_name" {
  value       = module.s3.artifacts_bucket_name
  description = "Name of the S3 bucket for artifacts"
}

output "ecr_repository_url" {
  value       = module.ecr.repository_url
  description = "URL of the ECR repository"
}

output "batch_job_role_arn" {
  value       = module.iam.batch_job_role_arn
  description = "ARN of the IAM role for Batch jobs"
}

output "batch_service_role_arn" {
  value       = module.iam.batch_service_role_arn
  description = "ARN of the IAM role for Batch service"
}
