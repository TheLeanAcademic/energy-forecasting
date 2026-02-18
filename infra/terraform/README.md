# Terraform Infrastructure

This directory contains Terraform modules for deploying the Forecast Bench infrastructure on AWS.

## Structure

```
infra/terraform/
├── modules/          # Reusable modules
│   ├── s3/          # S3 buckets for data and artifacts
│   ├── ecr/         # ECR repository for Docker images
│   └── iam/         # IAM roles and policies
└── envs/            # Environment-specific configs
    ├── dev/         # Development environment
    └── prod/        # Production environment
```

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Terraform >= 1.0 installed

## Quick Start

### Development Environment

```bash
cd infra/terraform/envs/dev

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the changes
terraform apply
```

### Outputs

After applying, Terraform will output:
- `data_bucket_name`: S3 bucket for datasets
- `artifacts_bucket_name`: S3 bucket for results
- `ecr_repository_url`: ECR repository for Docker images
- `batch_job_role_arn`: IAM role for Batch jobs
- `batch_service_role_arn`: IAM role for Batch service

### Using the Infrastructure

After deploying, set these environment variables:

```bash
export BENCH_DATA_URI=s3://$(terraform output -raw data_bucket_name)
export BENCH_ARTIFACT_URI=s3://$(terraform output -raw artifacts_bucket_name)
```

## Modules

### S3 Module

Creates two S3 buckets:
- Data bucket: For storing datasets
- Artifacts bucket: For storing run results and artifacts

Both buckets have versioning enabled.

### ECR Module

Creates an ECR repository for storing Docker images with:
- Image scanning on push
- Lifecycle policy to keep only the last 10 images

### IAM Module

Creates IAM roles for:
- Batch job execution (with S3 and ECR access)
- Batch service (AWS managed policy)

## Cost Considerations

This minimal setup has low costs:
- S3: Pay per GB stored and data transfer
- ECR: Pay per GB stored
- IAM roles: Free

Note: AWS Batch resources (compute environment, queue, job definition) are not included in these modules to keep costs minimal. They can be created manually or added as additional modules.

## Cleanup

To destroy all resources:

```bash
cd infra/terraform/envs/dev
terraform destroy
```

**Warning:** This will delete all S3 buckets and their contents. Make sure to backup important data first.
