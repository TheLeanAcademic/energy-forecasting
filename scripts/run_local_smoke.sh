#!/bin/bash
set -e

echo "=========================================="
echo "Forecast Bench - Local Smoke Test"
echo "=========================================="

# Ensure we're in the repo root
cd "$(dirname "$0")/.."

# Set environment variables
export BENCH_DATA_URI="./data"
export BENCH_ARTIFACT_URI="./results"
export BENCH_TRACKING="none"

echo ""
echo "Step 1: Creating smoke dataset..."
python -m bench.cli make-smoke

echo ""
echo "Step 2: Running smoke suite..."
python -m bench.cli suite --config configs/runs/suite_smoke.yaml

echo ""
echo "=========================================="
echo "Smoke test complete!"
echo "Results saved to: ./results/runs/"
echo "=========================================="
