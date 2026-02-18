"""Suite expansion and shard generation."""
from dataclasses import dataclass
from typing import List, Dict, Any
import json


@dataclass
class Shard:
    """A single shard of work (dataset, model, horizon, fold)."""
    dataset: str
    model: str
    horizon: int
    fold: int
    mode: str = "zero_shot"
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "dataset": self.dataset,
            "model": self.model,
            "horizon": self.horizon,
            "fold": self.fold,
            "mode": self.mode,
            "config": self.config,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: dict) -> "Shard":
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Shard":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


def expand_suite(suite_config: dict) -> List[Shard]:
    """
    Expand a suite configuration into individual shards.
    
    Args:
        suite_config: Suite configuration dictionary
    
    Returns:
        List of Shard objects
    """
    shards = []
    
    # Extract suite-level defaults
    default_mode = suite_config.get("default_mode", "zero_shot")
    default_horizon = suite_config.get("default_horizon", 24)
    default_n_folds = suite_config.get("n_folds", 2)
    
    datasets = suite_config.get("datasets", [])
    models = suite_config.get("models", [])
    
    # Normalize datasets
    if isinstance(datasets, str):
        datasets = [datasets]
    if isinstance(datasets, list) and datasets and isinstance(datasets[0], str):
        datasets = [{"name": d} for d in datasets]
    
    # Normalize models
    if isinstance(models, str):
        models = [models]
    if isinstance(models, list) and models and isinstance(models[0], str):
        models = [{"name": m} for m in models]
    
    # Generate shards
    for dataset_spec in datasets:
        dataset_name = dataset_spec if isinstance(dataset_spec, str) else dataset_spec.get("name")
        dataset_horizon = dataset_spec.get("horizon", default_horizon) if isinstance(dataset_spec, dict) else default_horizon
        dataset_n_folds = dataset_spec.get("n_folds", default_n_folds) if isinstance(dataset_spec, dict) else default_n_folds
        
        for model_spec in models:
            model_name = model_spec if isinstance(model_spec, str) else model_spec.get("name")
            model_mode = model_spec.get("mode", default_mode) if isinstance(model_spec, dict) else default_mode
            model_config = model_spec.get("config", {}) if isinstance(model_spec, dict) else {}
            
            for fold in range(dataset_n_folds):
                shard = Shard(
                    dataset=dataset_name,
                    model=model_name,
                    horizon=dataset_horizon,
                    fold=fold,
                    mode=model_mode,
                    config=model_config,
                )
                shards.append(shard)
    
    return shards
