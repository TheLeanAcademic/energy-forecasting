# ECR repository for Docker images
resource "aws_ecr_repository" "forecast_bench" {
  name                 = var.repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "Forecast Bench"
    Environment = var.environment
  }
}

# ECR lifecycle policy
resource "aws_ecr_lifecycle_policy" "forecast_bench" {
  repository = aws_ecr_repository.forecast_bench.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}

# Outputs
output "repository_url" {
  value = aws_ecr_repository.forecast_bench.repository_url
}

output "repository_arn" {
  value = aws_ecr_repository.forecast_bench.arn
}

output "repository_name" {
  value = aws_ecr_repository.forecast_bench.name
}
