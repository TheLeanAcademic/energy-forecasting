"""Tests for metrics."""
import pytest
import numpy as np
import pandas as pd
from bench.eval.metrics import mae, rmse, smape, mase, compute_point_metrics


def test_mae():
    """Test MAE calculation."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    
    result = mae(y_true, y_pred)
    expected = np.mean([0.1, 0.1, 0.1, 0.2, 0.2])
    
    assert abs(result - expected) < 1e-10


def test_rmse():
    """Test RMSE calculation."""
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0, 3.0])
    
    result = rmse(y_true, y_pred)
    assert result == 0.0


def test_smape():
    """Test sMAPE calculation."""
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 180.0, 300.0])
    
    result = smape(y_true, y_pred)
    # sMAPE should be > 0 for imperfect predictions
    assert result > 0
    assert result < 100  # Maximum is 100%


def test_compute_point_metrics():
    """Test computation of all point metrics."""
    y_true = pd.Series([100.0, 200.0, 300.0, 400.0])
    y_pred = pd.Series([105.0, 195.0, 310.0, 390.0])
    y_train = pd.Series([50.0, 150.0, 250.0])
    
    metrics = compute_point_metrics(y_true, y_pred, y_train, seasonal_period=1)
    
    # Check that all expected metrics are present
    assert "mae" in metrics
    assert "rmse" in metrics
    assert "smape" in metrics
    assert "mape" in metrics
    assert "mase" in metrics
    
    # Check that values are reasonable
    assert metrics["mae"] > 0
    assert metrics["rmse"] > 0
    assert metrics["smape"] >= 0
