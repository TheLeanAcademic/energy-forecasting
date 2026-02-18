"""Environment configuration and path resolution."""
import os
from pathlib import Path
from typing import Union


def get_data_uri() -> str:
    """Get data URI from environment or default."""
    return os.environ.get("BENCH_DATA_URI", "./data")


def get_artifact_uri() -> str:
    """Get artifact URI from environment or default."""
    return os.environ.get("BENCH_ARTIFACT_URI", "./results")


def get_mlflow_tracking_uri() -> str:
    """Get MLflow tracking URI from environment or default."""
    return os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")


def get_tracking_backend() -> str:
    """Get tracking backend (mlflow, wandb, or none)."""
    return os.environ.get("BENCH_TRACKING", "mlflow")


def resolve_path(path: Union[str, Path], base_uri: str) -> str:
    """Resolve a relative path against a base URI (local or S3)."""
    path_str = str(path)
    
    # If already absolute or S3 URI, return as-is
    if path_str.startswith(("s3://", "/", "~")):
        return path_str
    
    # Otherwise, join with base URI
    if base_uri.startswith("s3://"):
        return f"{base_uri.rstrip('/')}/{path_str}"
    else:
        return str(Path(base_uri) / path_str)


def get_hf_token() -> str:
    """Get HuggingFace token from environment."""
    return os.environ.get("HF_TOKEN", "")


def get_timegpt_api_key() -> str:
    """Get TimeGPT API key from environment."""
    return os.environ.get("TIMEGPT_API_KEY", "")
