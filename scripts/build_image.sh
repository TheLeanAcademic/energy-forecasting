#!/bin/bash
# Build Docker image with git SHA tag

set -e

cd "$(dirname "$0")/.."

GIT_SHA=$(git rev-parse --short HEAD)
IMAGE_NAME="forecast-bench"
IMAGE_TAG="${IMAGE_TAG:-$GIT_SHA}"

echo "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"

docker build -t "$IMAGE_NAME:$IMAGE_TAG" -f docker/Dockerfile .
docker tag "$IMAGE_NAME:$IMAGE_TAG" "$IMAGE_NAME:latest"

echo "Built: $IMAGE_NAME:$IMAGE_TAG"
echo "Tagged as: $IMAGE_NAME:latest"
