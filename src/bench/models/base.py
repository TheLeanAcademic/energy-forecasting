"""Base model interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np


@dataclass
class ForecastResult:
    """Result from a forecast."""
    predictions: pd.DataFrame  # series_id, ds, yhat columns
    quantiles: Optional[pd.DataFrame] = None  # series_id, ds, q10, q50, q90 etc
    metadata: Dict[str, Any] = None  # Additional metadata (train_time, etc.)
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseModel(ABC):
    """Base class for forecasting models."""
    
    def __init__(self, config: dict):
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.mode = config.get("mode", "zero_shot")
        self._is_fitted = False
    
    @abstractmethod
    def fit(self, train: pd.DataFrame) -> None:
        """
        Fit the model on training data.
        
        Args:
            train: DataFrame with series_id, ds, y columns
        """
        pass
    
    @abstractmethod
    def predict(
        self,
        train: pd.DataFrame,
        horizon: int,
        quantiles: Optional[list[float]] = None
    ) -> ForecastResult:
        """
        Generate forecasts.
        
        Args:
            train: DataFrame with series_id, ds, y columns (history)
            horizon: Number of steps to forecast
            quantiles: Optional list of quantiles to predict (e.g., [0.1, 0.5, 0.9])
        
        Returns:
            ForecastResult with predictions
        """
        pass
    
    def supports_mode(self, mode: str) -> bool:
        """Check if model supports a given mode."""
        return mode in self.get_supported_modes()
    
    @abstractmethod
    def get_supported_modes(self) -> list[str]:
        """Return list of supported modes."""
        pass
    
    def requires_fitting(self) -> bool:
        """Check if model requires fitting (vs zero-shot)."""
        return self.mode not in ["zero_shot"]
    
    def is_fitted(self) -> bool:
        """Check if model is fitted."""
        return self._is_fitted


class NotSupportedError(Exception):
    """Raised when a model doesn't support a requested mode/operation."""
    pass
