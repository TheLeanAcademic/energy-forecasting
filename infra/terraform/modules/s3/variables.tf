variable "data_bucket_name" {
  description = "Name of the S3 bucket for data"
  type        = string
}

variable "artifacts_bucket_name" {
  description = "Name of the S3 bucket for artifacts"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}
