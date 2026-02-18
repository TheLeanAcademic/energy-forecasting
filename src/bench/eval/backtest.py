"""Backtesting framework."""
import time
from typing import Dict, List, Optional
import pandas as pd
from bench.models.base import BaseModel, ForecastResult
from bench.data.splits import Split
from bench.eval.metrics import compute_point_metrics, compute_probabilistic_metrics
from bench.utils.logging import get_logger

logger = get_logger(__name__)


def backtest_model(
    model: BaseModel,
    splits: List[Split],
    horizon: int,
    quantiles: Optional[List[float]] = None,
    seasonal_period: int = 1
) -> Dict:
    """
    Run backtesting for a model across multiple splits.
    
    Args:
        model: Model to evaluate
        splits: List of train/test splits
        horizon: Forecast horizon
        quantiles: Optional quantiles for probabilistic forecasts
        seasonal_period: Seasonal period for MASE calculation
    
    Returns:
        Dictionary with results including metrics and timings
    """
    results = {
        "model": model.name,
        "mode": model.mode,
        "n_folds": len(splits),
        "horizon": horizon,
        "fold_results": [],
        "aggregated_metrics": {},
        "total_train_time": 0.0,
        "total_predict_time": 0.0,
    }
    
    for split in splits:
        logger.info(f"Processing fold {split.fold}")
        
        # Fit model
        train_start = time.time()
        if model.requires_fitting():
            model.fit(split.train)
        train_time = time.time() - train_start
        
        # Generate predictions
        predict_start = time.time()
        forecast = model.predict(split.train, horizon, quantiles)
        predict_time = time.time() - predict_start
        
        # Merge predictions with actuals
        test_with_pred = split.test.merge(
            forecast.predictions,
            on=["series_id", "ds"],
            how="left"
        )
        
        # Compute metrics per series
        series_metrics = []
        for series_id in test_with_pred["series_id"].unique():
            series_data = test_with_pred[test_with_pred["series_id"] == series_id]
            series_train = split.train[split.train["series_id"] == series_id]
            
            # Skip if no predictions
            if series_data["yhat"].isna().all():
                continue
            
            # Point metrics
            point_metrics = compute_point_metrics(
                series_data["y"],
                series_data["yhat"],
                series_train["y"],
                seasonal_period
            )
            point_metrics["series_id"] = series_id
            
            # Probabilistic metrics
            if forecast.quantiles is not None:
                series_quantiles = forecast.quantiles[
                    forecast.quantiles["series_id"] == series_id
                ]
                if not series_quantiles.empty:
                    prob_metrics = compute_probabilistic_metrics(
                        series_data["y"],
                        series_quantiles
                    )
                    point_metrics.update(prob_metrics)
            
            series_metrics.append(point_metrics)
        
        # Aggregate metrics across series for this fold
        fold_metrics = {}
        if series_metrics:
            metric_keys = [k for k in series_metrics[0].keys() if k != "series_id"]
            for key in metric_keys:
                values = [m[key] for m in series_metrics if key in m]
                if values:
                    fold_metrics[key] = sum(values) / len(values)
        
        fold_result = {
            "fold": split.fold,
            "metrics": fold_metrics,
            "train_time": train_time,
            "predict_time": predict_time,
            "n_series": len(series_metrics),
        }
        results["fold_results"].append(fold_result)
        results["total_train_time"] += train_time
        results["total_predict_time"] += predict_time
        
        logger.info(f"Fold {split.fold} metrics: {fold_metrics}")
    
    # Aggregate across folds
    if results["fold_results"]:
        all_fold_metrics = [fr["metrics"] for fr in results["fold_results"]]
        metric_keys = all_fold_metrics[0].keys()
        
        for key in metric_keys:
            values = [m[key] for m in all_fold_metrics if key in m]
            if values:
                results["aggregated_metrics"][key] = sum(values) / len(values)
                results["aggregated_metrics"][f"{key}_std"] = (
                    sum((v - results["aggregated_metrics"][key]) ** 2 for v in values) / len(values)
                ) ** 0.5
    
    return results
