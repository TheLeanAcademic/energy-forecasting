"""Tests for smoke data loader."""
import pytest
import pandas as pd
from bench.data.loaders.smoke import SmokeDataLoader


def test_smoke_loader_basic():
    """Test basic smoke data generation."""
    config = {
        "name": "smoke",
        "n_series": 5,
        "n_timesteps": 100,
        "frequency": "h",
        "seed": 42,
    }
    
    loader = SmokeDataLoader(config)
    df = loader.load()
    
    # Check shape
    assert len(df) == 5 * 100
    assert df["series_id"].nunique() == 5
    
    # Check columns
    assert set(df.columns) == {"series_id", "ds", "y"}
    
    # Check data types
    assert df["series_id"].dtype == "object"
    assert pd.api.types.is_datetime64_any_dtype(df["ds"])
    assert pd.api.types.is_numeric_dtype(df["y"])
    
    # Check no missing values
    assert not df.isna().any().any()


def test_smoke_loader_metadata():
    """Test metadata generation."""
    config = {
        "n_series": 3,
        "n_timesteps": 50,
        "frequency": "d",
        "seed": 123,
    }
    
    loader = SmokeDataLoader(config)
    metadata = loader.get_metadata()
    
    assert metadata.name == "smoke"
    assert metadata.n_series == 3
    assert metadata.n_timesteps == 50
    assert metadata.frequency == "d"
    assert not metadata.has_covariates


def test_smoke_loader_reproducibility():
    """Test that same seed produces same data."""
    config = {
        "n_series": 2,
        "n_timesteps": 20,
        "frequency": "h",
        "seed": 999,
    }
    
    loader1 = SmokeDataLoader(config)
    df1 = loader1.load()
    
    loader2 = SmokeDataLoader(config)
    df2 = loader2.load()
    
    pd.testing.assert_frame_equal(df1, df2)
