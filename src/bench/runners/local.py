"""Local runner for executing suites sequentially."""
import time
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
from bench.utils.logging import get_logger, setup_logger
from bench.utils.io import read_yaml, write_yaml, ensure_dir
from bench.utils.env import get_data_uri, get_artifact_uri
from bench.registry import get_registry
from bench.data.splits import create_rolling_splits
from bench.eval.backtest import backtest_model
from bench.runners.suite_expand import expand_suite, Shard

logger = get_logger(__name__)


def run_shard(
    shard: Shard,
    data_uri: str,
    artifact_uri: str,
    suite_config: dict,
) -> Dict:
    """
    Run a single shard.
    
    Args:
        shard: Shard specification
        data_uri: Data URI (local or S3)
        artifact_uri: Artifact URI (local or S3)
        suite_config: Suite configuration for additional parameters
    
    Returns:
        Results dictionary
    """
    logger.info(f"Running shard: {shard.to_dict()}")
    
    registry = get_registry()
    
    # Load dataset
    dataset_path = f"{data_uri}/processed/{shard.dataset}.parquet"
    logger.info(f"Loading dataset from {dataset_path}")
    df = pd.read_parquet(dataset_path)
    
    # Apply limit_series if specified
    limit_series = suite_config.get("limit_series")
    if limit_series:
        unique_series = df["series_id"].unique()[:limit_series]
        df = df[df["series_id"].isin(unique_series)]
        logger.info(f"Limited to {limit_series} series")
    
    # Create splits
    initial_train_frac = suite_config.get("initial_train_frac", 0.7)
    n_folds = suite_config.get("n_folds", 2)
    
    # For single fold shard, we need to create all splits first, then select the one we need
    logger.info(f"Creating {n_folds} rolling splits")
    all_splits = create_rolling_splits(
        df,
        horizon=shard.horizon,
        n_folds=n_folds,
        initial_train_frac=initial_train_frac,
    )
    
    if shard.fold >= len(all_splits):
        logger.warning(f"Fold {shard.fold} not available (only {len(all_splits)} folds)")
        return {"error": "Fold not available", "shard": shard.to_dict()}
    
    # Select the specific fold for this shard
    split = all_splits[shard.fold]
    
    # Load and configure model
    model_class = registry.get_model(shard.model)
    model_config = {
        "name": shard.model,
        "mode": shard.mode,
        **shard.config,
    }
    model = model_class(model_config)
    
    # Run backtest
    logger.info(f"Running backtest for fold {shard.fold}")
    start_time = time.time()
    
    results = backtest_model(
        model,
        [split],  # Single fold
        horizon=shard.horizon,
        quantiles=[0.1, 0.5, 0.9],
    )
    
    results["elapsed_time"] = time.time() - start_time
    results["shard"] = shard.to_dict()
    
    return results


def run_suite_local(suite_config_path: Path) -> None:
    """
    Run a suite locally (sequentially).
    
    Args:
        suite_config_path: Path to suite configuration YAML
    """
    setup_logger(level="INFO")
    logger.info(f"Running suite: {suite_config_path}")
    
    # Load suite config
    suite_config = read_yaml(suite_config_path)
    suite_name = suite_config.get("name", suite_config_path.stem)
    
    # Get URIs
    data_uri = get_data_uri()
    artifact_uri = get_artifact_uri()
    
    logger.info(f"Data URI: {data_uri}")
    logger.info(f"Artifact URI: {artifact_uri}")
    
    # Expand suite to shards
    shards = expand_suite(suite_config)
    logger.info(f"Expanded to {len(shards)} shards")
    
    # Create run directory
    run_id = f"{suite_name}_{int(time.time())}"
    run_dir = Path(artifact_uri) / "runs" / run_id
    ensure_dir(run_dir)
    
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Results will be saved to: {run_dir}")
    
    # Save suite config and shards
    write_yaml(suite_config, run_dir / "suite_config.yaml")
    write_yaml(
        [s.to_dict() for s in shards],
        run_dir / "shards.yaml"
    )
    
    # Run shards
    all_results = []
    for i, shard in enumerate(shards):
        logger.info(f"\n{'='*60}")
        logger.info(f"Shard {i+1}/{len(shards)}")
        logger.info(f"{'='*60}")
        
        try:
            result = run_shard(shard, data_uri, artifact_uri, suite_config)
            result["status"] = "success"
        except Exception as e:
            logger.error(f"Shard failed: {e}", exc_info=True)
            result = {
                "shard": shard.to_dict(),
                "status": "failed",
                "error": str(e),
            }
        
        all_results.append(result)
        
        # Save individual shard result
        shard_file = run_dir / f"shard_{i:04d}.yaml"
        write_yaml(result, shard_file)
    
    # Aggregate and save final results
    summary = {
        "run_id": run_id,
        "suite_name": suite_name,
        "n_shards": len(shards),
        "n_success": sum(1 for r in all_results if r.get("status") == "success"),
        "n_failed": sum(1 for r in all_results if r.get("status") == "failed"),
        "results": all_results,
    }
    
    write_yaml(summary, run_dir / "summary.yaml")
    
    logger.info(f"\n{'='*60}")
    logger.info("Suite complete!")
    logger.info(f"Success: {summary['n_success']}/{summary['n_shards']}")
    logger.info(f"Results saved to: {run_dir}")
    logger.info(f"{'='*60}\n")
