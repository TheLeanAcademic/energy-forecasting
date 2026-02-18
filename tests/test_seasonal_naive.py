"""Tests for seasonal naive model."""
import pytest
import pandas as pd
import numpy as np
from bench.models.adapters.seasonal_naive import SeasonalNaiveModel


def test_seasonal_naive_basic():
    """Test basic seasonal naive prediction."""
    # Create simple test data
    dates = pd.date_range("2020-01-01", periods=100, freq="h")
    train = pd.DataFrame({
        "series_id": "test_series",
        "ds": dates,
        "y": np.random.randn(100) + 50
    })
    
    model = SeasonalNaiveModel({"season_length": 24})
    model.fit(train)
    
    result = model.predict(train, horizon=24)
    
    # Check predictions
    assert len(result.predictions) == 24
    assert "yhat" in result.predictions.columns
    assert result.predictions["series_id"].iloc[0] == "test_series"


def test_seasonal_naive_multiple_series():
    """Test seasonal naive with multiple series."""
    dates = pd.date_range("2020-01-01", periods=50, freq="h")
    
    train = pd.concat([
        pd.DataFrame({
            "series_id": "series_1",
            "ds": dates,
            "y": np.random.randn(50) + 50
        }),
        pd.DataFrame({
            "series_id": "series_2",
            "ds": dates,
            "y": np.random.randn(50) + 100
        })
    ]).reset_index(drop=True)
    
    model = SeasonalNaiveModel({"season_length": 24})
    model.fit(train)
    
    result = model.predict(train, horizon=12)
    
    # Check predictions for both series
    assert len(result.predictions) == 24  # 12 * 2 series
    assert result.predictions["series_id"].nunique() == 2


def test_seasonal_naive_supported_modes():
    """Test that seasonal naive only supports zero-shot."""
    model = SeasonalNaiveModel({"season_length": 24})
    modes = model.get_supported_modes()
    
    assert modes == ["zero_shot"]
    assert model.supports_mode("zero_shot")
    assert not model.supports_mode("full_finetune")
