# IAM role for Batch job execution
resource "aws_iam_role" "batch_job_role" {
  name = "${var.environment}-forecast-bench-batch-job-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "Forecast Bench Batch Job Role"
    Environment = var.environment
  }
}

# Policy for S3 access
resource "aws_iam_role_policy" "batch_s3_access" {
  name = "s3-access"
  role = aws_iam_role.batch_job_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ]
      Resource = [
        var.data_bucket_arn,
        "${var.data_bucket_arn}/*",
        var.artifacts_bucket_arn,
        "${var.artifacts_bucket_arn}/*"
      ]
    }]
  })
}

# Policy for ECR access
resource "aws_iam_role_policy" "batch_ecr_access" {
  name = "ecr-access"
  role = aws_iam_role.batch_job_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ]
      Resource = "*"
    }]
  })
}

# IAM role for Batch service
resource "aws_iam_role" "batch_service_role" {
  name = "${var.environment}-forecast-bench-batch-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "batch.amazonaws.com"
      }
    }]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
  ]

  tags = {
    Name        = "Forecast Bench Batch Service Role"
    Environment = var.environment
  }
}

# Outputs
output "batch_job_role_arn" {
  value = aws_iam_role.batch_job_role.arn
}

output "batch_service_role_arn" {
  value = aws_iam_role.batch_service_role.arn
}
