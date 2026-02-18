"""Evaluation metrics for forecasting."""
import numpy as np
import pandas as pd
from typing import Dict, Optional


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return np.mean(np.abs(y_true - y_pred))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Symmetric Mean Absolute Percentage Error."""
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    # Avoid division by zero
    mask = denominator != 0
    if not mask.any():
        return 0.0
    return 100 * np.mean(np.abs(y_true[mask] - y_pred[mask]) / denominator[mask])


def mase(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, seasonal_period: int = 1) -> float:
    """Mean Absolute Scaled Error."""
    # Calculate naive forecast error on training set
    if len(y_train) <= seasonal_period:
        seasonal_period = 1
    
    naive_errors = np.abs(y_train[seasonal_period:] - y_train[:-seasonal_period])
    mae_naive = np.mean(naive_errors)
    
    if mae_naive == 0:
        return 0.0
    
    mae_forecast = mae(y_true, y_pred)
    return mae_forecast / mae_naive


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error."""
    mask = y_true != 0
    if not mask.any():
        return 0.0
    return 100 * np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]))


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, quantile: float) -> float:
    """Pinball loss for quantile forecasts."""
    errors = y_true - y_pred
    return np.mean(np.maximum(quantile * errors, (quantile - 1) * errors))


def coverage(y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    """Coverage of prediction intervals."""
    in_interval = (y_true >= lower) & (y_true <= upper)
    return np.mean(in_interval)


def compute_point_metrics(
    y_true: pd.Series,
    y_pred: pd.Series,
    y_train: Optional[pd.Series] = None,
    seasonal_period: int = 1
) -> Dict[str, float]:
    """Compute all point forecast metrics."""
    y_true_arr = y_true.values
    y_pred_arr = y_pred.values
    
    metrics = {
        "mae": mae(y_true_arr, y_pred_arr),
        "rmse": rmse(y_true_arr, y_pred_arr),
        "smape": smape(y_true_arr, y_pred_arr),
        "mape": mape(y_true_arr, y_pred_arr),
    }
    
    if y_train is not None:
        metrics["mase"] = mase(y_true_arr, y_pred_arr, y_train.values, seasonal_period)
    
    return metrics


def compute_probabilistic_metrics(
    y_true: pd.Series,
    quantiles: pd.DataFrame,
    nominal_coverage: float = 0.8
) -> Dict[str, float]:
    """Compute probabilistic forecast metrics."""
    metrics = {}
    
    # Pinball losses for different quantiles
    if "q10" in quantiles.columns:
        metrics["pinball_10"] = pinball_loss(y_true.values, quantiles["q10"].values, 0.1)
    if "q50" in quantiles.columns:
        metrics["pinball_50"] = pinball_loss(y_true.values, quantiles["q50"].values, 0.5)
    if "q90" in quantiles.columns:
        metrics["pinball_90"] = pinball_loss(y_true.values, quantiles["q90"].values, 0.9)
    
    # Coverage
    if "q10" in quantiles.columns and "q90" in quantiles.columns:
        metrics["coverage_80"] = coverage(
            y_true.values,
            quantiles["q10"].values,
            quantiles["q90"].values
        )
    
    return metrics


def aggregate_metrics(metrics_list: list[Dict[str, float]]) -> Dict[str, float]:
    """Aggregate metrics across multiple series/folds."""
    if not metrics_list:
        return {}
    
    aggregated = {}
    keys = metrics_list[0].keys()
    
    for key in keys:
        values = [m[key] for m in metrics_list if key in m and not np.isnan(m[key])]
        if values:
            aggregated[key] = np.mean(values)
            aggregated[f"{key}_std"] = np.std(values)
    
    return aggregated
