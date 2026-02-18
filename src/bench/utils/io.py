"""IO utilities for reading/writing data."""
from pathlib import Path
from typing import Union
import pandas as pd
import yaml


def read_parquet(path: Union[str, Path]) -> pd.DataFrame:
    """Read parquet file from local or S3."""
    return pd.read_parquet(path)


def write_parquet(df: pd.DataFrame, path: Union[str, Path]) -> None:
    """Write parquet file to local or S3."""
    # For S3, pandas with s3fs will handle it automatically
    df.to_parquet(path, index=False)


def read_yaml(path: Union[str, Path]) -> dict:
    """Read YAML config file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def write_yaml(data: dict, path: Union[str, Path]) -> None:
    """Write YAML config file."""
    import json
    
    # Convert data to JSON-serializable format (handles numpy types)
    json_str = json.dumps(data, default=str)
    data_clean = json.loads(json_str)
    
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(data_clean, f, default_flow_style=False, sort_keys=False)


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, creating if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
