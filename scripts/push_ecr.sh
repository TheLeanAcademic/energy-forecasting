#!/bin/bash
# Push Docker image to ECR

set -e

cd "$(dirname "$0")/.."

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REPO="${ECR_REPO:-forecast-bench}"
GIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${IMAGE_TAG:-$GIT_SHA}"

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"

echo "Pushing to ECR..."
echo "Repository: $ECR_URI"
echo "Tag: $IMAGE_TAG"

# Tag for ECR
docker tag "forecast-bench:$IMAGE_TAG" "$ECR_URI:$IMAGE_TAG"
docker tag "forecast-bench:$IMAGE_TAG" "$ECR_URI:latest"

# Push
docker push "$ECR_URI:$IMAGE_TAG"
docker push "$ECR_URI:latest"

echo "Successfully pushed $ECR_URI:$IMAGE_TAG"
