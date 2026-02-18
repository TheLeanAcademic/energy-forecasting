"""Seasonal naive baseline model."""
import pandas as pd
import numpy as np
from typing import Optional
from bench.models.base import BaseModel, ForecastResult


class SeasonalNaiveModel(BaseModel):
    """Seasonal naive forecasting model."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.season_length = config.get("season_length", 24)  # Default to daily seasonality
    
    def fit(self, train: pd.DataFrame) -> None:
        """Seasonal naive doesn't require fitting."""
        self._is_fitted = True
    
    def predict(
        self,
        train: pd.DataFrame,
        horizon: int,
        quantiles: Optional[list[float]] = None
    ) -> ForecastResult:
        """Generate forecasts using seasonal naive method."""
        if not self._is_fitted:
            self.fit(train)
        
        predictions = []
        
        for series_id in train["series_id"].unique():
            series_data = train[train["series_id"] == series_id].sort_values("ds")
            
            if len(series_data) < self.season_length:
                # Not enough data, use simple naive
                last_value = series_data["y"].iloc[-1]
                forecast_values = np.full(horizon, last_value)
            else:
                # Use seasonal naive
                last_season = series_data["y"].iloc[-self.season_length:].values
                # Repeat the last season to cover the horizon
                n_repeats = (horizon // self.season_length) + 1
                forecast_values = np.tile(last_season, n_repeats)[:horizon]
            
            # Generate future dates
            last_date = series_data["ds"].max()
            
            # Try to infer frequency
            freq_str = pd.infer_freq(series_data["ds"])
            
            if freq_str:
                # Use inferred frequency for date_range
                future_dates = pd.date_range(
                    start=last_date,
                    periods=horizon + 1,
                    freq=freq_str
                )[1:]  # Skip first date (which is last_date)
            else:
                # Fallback: compute median time difference
                time_diffs = series_data["ds"].diff()
                median_diff = time_diffs.median()
                
                future_dates = []
                current_date = last_date
                for _ in range(horizon):
                    current_date = current_date + median_diff
                    future_dates.append(current_date)
                future_dates = pd.DatetimeIndex(future_dates)
            
            pred_df = pd.DataFrame({
                "series_id": series_id,
                "ds": future_dates,
                "yhat": forecast_values
            })
            predictions.append(pred_df)
        
        predictions_df = pd.concat(predictions, ignore_index=True)
        
        # Generate quantiles if requested (simple approach: add noise)
        quantiles_df = None
        if quantiles:
            quantiles_df = self._generate_quantiles(train, predictions_df, quantiles)
        
        return ForecastResult(
            predictions=predictions_df,
            quantiles=quantiles_df,
            metadata={"model": "seasonal_naive", "season_length": self.season_length}
        )
    
    def _generate_quantiles(
        self,
        train: pd.DataFrame,
        predictions: pd.DataFrame,
        quantiles: list[float]
    ) -> pd.DataFrame:
        """Generate quantile forecasts based on historical residuals."""
        from scipy.stats import norm
        
        quantile_dfs = []
        
        for series_id in predictions["series_id"].unique():
            # Estimate residual std from training data
            series_train = train[train["series_id"] == series_id]
            residual_std = series_train["y"].std()
            
            series_pred = predictions[predictions["series_id"] == series_id].copy()
            
            for q in quantiles:
                # Use proper z-score from normal distribution
                z_score = norm.ppf(q)
                col_name = f"q{int(q*100):02d}"
                series_pred[col_name] = series_pred["yhat"] + z_score * residual_std
            
            quantile_dfs.append(series_pred)
        
        return pd.concat(quantile_dfs, ignore_index=True)
    
    def get_supported_modes(self) -> list[str]:
        """Seasonal naive only supports zero-shot."""
        return ["zero_shot"]
