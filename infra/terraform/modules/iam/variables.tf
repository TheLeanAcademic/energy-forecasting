variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "data_bucket_arn" {
  description = "ARN of the data S3 bucket"
  type        = string
}

variable "artifacts_bucket_arn" {
  description = "ARN of the artifacts S3 bucket"
  type        = string
}
