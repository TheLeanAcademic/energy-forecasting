#!/bin/bash
# Login to AWS ECR

set -e

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"

echo "Logging in to ECR..."
echo "Region: $AWS_REGION"
echo "Account: $AWS_ACCOUNT_ID"

aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo "Successfully logged in to ECR"
