#!/bin/bash
# Submit AWS Batch jobs for a suite

set -e

cd "$(dirname "$0")/.."

if [ $# -lt 1 ]; then
    echo "Usage: $0 <suite_config_path>"
    echo "Example: $0 configs/runs/suite_smoke.yaml"
    exit 1
fi

SUITE_CONFIG="$1"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
BATCH_QUEUE="${BATCH_QUEUE:-forecast-bench-queue}"
BATCH_JOB_DEF="${BATCH_JOB_DEF:-forecast-bench-job}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ECR_REPO="${ECR_REPO:-forecast-bench}"

echo "Submitting AWS Batch jobs for suite: $SUITE_CONFIG"
echo "Queue: $BATCH_QUEUE"
echo "Job Definition: $BATCH_JOB_DEF"
echo "Image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG"

# Call Python script to render and submit jobs
python aws/batch/submit.py \
    --suite "$SUITE_CONFIG" \
    --queue "$BATCH_QUEUE" \
    --job-definition "$BATCH_JOB_DEF" \
    --image-tag "$IMAGE_TAG"

echo "Jobs submitted successfully"
