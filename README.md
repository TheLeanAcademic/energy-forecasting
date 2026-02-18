# Forecast Bench

A comprehensive benchmarking framework for forecasting models that supports local and cloud (AWS) execution.

## Overview

Forecast Bench enables you to:
- Benchmark multiple forecasting methods (baselines, deep learning, foundation models)
- Run consistent rolling backtests across multiple datasets
- Execute locally (Python or Docker) or at scale on AWS Batch
- Track experiments with MLflow
- Generate reproducible results with declarative configs

**Key Design Principle:** "One command, multiple environments"
- Same CLI (`bench ...`)
- Environment differences controlled by configs + env vars
- Data/artifacts stored locally or on S3

## Quick Start

### Local Python Workflow

1. **Install dependencies:**
```bash
pip install -e .
```

2. **Run smoke test:**
```bash
./scripts/run_local_smoke.sh
```

This will:
- Generate a synthetic smoke dataset
- Run a simple baseline model (seasonal naive)
- Save results to `./results/runs/`

### Local Docker Workflow

Test the full Docker setup locally:

```bash
./scripts/run_local_docker_smoke.sh
```

This builds the Docker image and runs the same smoke test in a container.

## Project Structure

```
forecast-bench/
├── configs/              # Configuration files
│   ├── datasets/        # Dataset configs (smoke.yaml, etc.)
│   ├── models/          # Model configs (seasonal_naive.yaml, etc.)
│   └── runs/            # Suite configs (suite_smoke.yaml, etc.)
├── src/bench/           # Core library
│   ├── data/           # Data loaders and processing
│   ├── models/         # Model adapters
│   ├── eval/           # Metrics and backtesting
│   ├── runners/        # Execution logic
│   └── utils/          # Utilities (logging, I/O, S3, etc.)
├── docker/              # Docker configuration
├── aws/                 # AWS Batch scripts
├── scripts/             # Execution scripts
└── tests/               # Tests
```

## CLI Commands

### Data Preparation

**Generate smoke dataset:**
```bash
bench make-smoke
```

**Prepare a named dataset:**
```bash
bench prepare --dataset <name>
```

### Running Experiments

**Run a suite:**
```bash
bench suite --config configs/runs/suite_smoke.yaml
```

**Run a single shard (used by AWS Batch):**
```bash
bench run-shard --shard-json '{"dataset":"smoke","model":"seasonal_naive",...}'
```

**Generate a report:**
```bash
bench report --run-id <run_id> --out report.md
```

**List available datasets/models:**
```bash
bench list-datasets
bench list-models
```

## Environment Variables

Control execution environment with these variables:

- `BENCH_DATA_URI`: Data location (default: `./data`)
  - Local: `./data`
  - S3: `s3://forecast-bench-data-dev`
  
- `BENCH_ARTIFACT_URI`: Results location (default: `./results`)
  - Local: `./results`
  - S3: `s3://forecast-bench-artifacts-dev`

- `MLFLOW_TRACKING_URI`: MLflow server (default: `./mlruns`)

- `BENCH_TRACKING`: Tracking backend (`mlflow`, `wandb`, or `none`)

- `HF_TOKEN`: HuggingFace token (for foundation models)

- `TIMEGPT_API_KEY`: TimeGPT API key (if using TimeGPT)

## AWS Deployment

### Prerequisites

1. AWS account with permissions for:
   - ECR (Elastic Container Registry)
   - S3 (Simple Storage Service)
   - Batch (AWS Batch)
   - IAM (roles and policies)

2. Set AWS credentials:
```bash
export AWS_ACCOUNT_ID=<your-account-id>
export AWS_REGION=us-east-1
```

### Step 1: Build and Push Docker Image

```bash
# Build image
./scripts/build_image.sh

# Login to ECR
./scripts/ecr_login.sh

# Push to ECR
./scripts/push_ecr.sh
```

### Step 2: Set Up Infrastructure (Optional)

Use Terraform to create required AWS resources:

```bash
cd infra/terraform/envs/dev
terraform init
terraform plan
terraform apply
```

This creates:
- S3 buckets for data and artifacts
- ECR repository
- AWS Batch compute environment, queue, and job definition
- IAM roles and policies

### Step 3: Submit Jobs

```bash
# Set environment variables for cloud execution
export BENCH_DATA_URI=s3://forecast-bench-data-dev
export BENCH_ARTIFACT_URI=s3://forecast-bench-artifacts-dev
export BATCH_QUEUE=forecast-bench-queue
export BATCH_JOB_DEF=forecast-bench-job

# Submit jobs
./scripts/run_aws_batch_suite.sh configs/runs/suite_smoke.yaml
```

## Configuration

### Suite Configuration

A suite config (e.g., `configs/runs/suite_smoke.yaml`) defines:

```yaml
name: suite_smoke
description: "Smoke test suite"

datasets:
  - name: smoke
    horizon: 24
    n_folds: 2

models:
  - name: seasonal_naive
    mode: zero_shot

default_horizon: 24
n_folds: 2
initial_train_frac: 0.7
limit_series: 10  # Limit for faster testing
tracking: none
```

### Dataset Schema

All datasets are normalized to this schema:
- `series_id` (string): Identifier for the time series
- `ds` (datetime): Timestamp (timezone-naive UTC)
- `y` (float): Target value
- Optional: Covariates/features

### Backtesting Protocol

- **Rolling origin evaluation**: Fixed initial training window, then rolling forward
- **Parameters**:
  - `horizon`: Forecast horizon (steps ahead)
  - `n_folds`: Number of evaluation windows
  - `initial_train_frac`: Fraction of data for initial training (e.g., 0.7)
  - `step_size`: Steps between folds (defaults to horizon)

## Models

### Implemented Models

Currently implemented:
- **seasonal_naive**: Seasonal naive baseline (repeats last season)

### Adding New Models

1. Create adapter in `src/bench/models/adapters/`
2. Inherit from `BaseModel`
3. Implement `fit()`, `predict()`, and `get_supported_modes()`
4. Register in `src/bench/registry.py`
5. Add config in `configs/models/`

## Metrics

### Point Forecasts
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- sMAPE (Symmetric Mean Absolute Percentage Error)
- MASE (Mean Absolute Scaled Error)

### Probabilistic Forecasts
- Pinball loss (quantiles 10%, 50%, 90%)
- Coverage (percentage of actuals within prediction interval)

### Runtime
- Training time
- Inference time

## Troubleshooting

### "Module not found" errors

Make sure you've installed the package:
```bash
pip install -e .
```

### Docker build fails

Check that you have sufficient disk space and Docker is running:
```bash
docker info
```

### AWS Batch jobs fail

1. Check CloudWatch logs for the job
2. Verify S3 bucket permissions
3. Ensure ECR image was pushed successfully
4. Check IAM role has necessary permissions

### MLflow tracking not working

Set the tracking URI explicitly:
```bash
export MLFLOW_TRACKING_URI=./mlruns
# or for remote server:
export MLFLOW_TRACKING_URI=http://mlflow-server:5000
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black src/

# Lint
ruff check src/
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
