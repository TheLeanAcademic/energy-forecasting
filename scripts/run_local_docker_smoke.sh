#!/bin/bash
set -e

echo "=========================================="
echo "Forecast Bench - Docker Local Smoke Test"
echo "=========================================="

# Ensure we're in the repo root
cd "$(dirname "$0")/.."

# Build image
echo ""
echo "Building Docker image..."
docker build -t forecast-bench:local -f docker/Dockerfile .

# Create directories
mkdir -p data results

echo ""
echo "Step 1: Creating smoke dataset (in container)..."
docker run --rm \
  -e BENCH_DATA_URI=/app/data \
  -e BENCH_ARTIFACT_URI=/app/results \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/results:/app/results" \
  forecast-bench:local \
  make-smoke

echo ""
echo "Step 2: Running smoke suite (in container)..."
docker run --rm \
  -e BENCH_DATA_URI=/app/data \
  -e BENCH_ARTIFACT_URI=/app/results \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/results:/app/results" \
  forecast-bench:local \
  suite --config /app/configs/runs/suite_smoke.yaml

echo ""
echo "=========================================="
echo "Docker smoke test complete!"
echo "Results saved to: ./results/runs/"
echo "=========================================="
