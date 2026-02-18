variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "forecast-bench"
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}
