"""Registry for datasets and models."""
from typing import Dict, Type
from bench.data.base import BaseDataLoader
from bench.models.base import BaseModel


class Registry:
    """Registry for datasets and models."""
    
    def __init__(self):
        self._datasets: Dict[str, Type[BaseDataLoader]] = {}
        self._models: Dict[str, Type[BaseModel]] = {}
    
    def register_dataset(self, name: str, loader_class: Type[BaseDataLoader]):
        """Register a dataset loader."""
        self._datasets[name] = loader_class
    
    def register_model(self, name: str, model_class: Type[BaseModel]):
        """Register a model."""
        self._models[name] = model_class
    
    def get_dataset_loader(self, name: str) -> Type[BaseDataLoader]:
        """Get a dataset loader by name."""
        if name not in self._datasets:
            raise ValueError(f"Unknown dataset: {name}. Available: {list(self._datasets.keys())}")
        return self._datasets[name]
    
    def get_model(self, name: str) -> Type[BaseModel]:
        """Get a model by name."""
        if name not in self._models:
            raise ValueError(f"Unknown model: {name}. Available: {list(self._models.keys())}")
        return self._models[name]
    
    def list_datasets(self) -> list[str]:
        """List all registered datasets."""
        return list(self._datasets.keys())
    
    def list_models(self) -> list[str]:
        """List all registered models."""
        return list(self._models.keys())


# Global registry instance
_registry = Registry()

# Register datasets
from bench.data.loaders.smoke import SmokeDataLoader
_registry.register_dataset("smoke", SmokeDataLoader)

# Register models
from bench.models.adapters.seasonal_naive import SeasonalNaiveModel
_registry.register_model("seasonal_naive", SeasonalNaiveModel)


def get_registry() -> Registry:
    """Get the global registry."""
    return _registry
