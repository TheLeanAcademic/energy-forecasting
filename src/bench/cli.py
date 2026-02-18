"""Command-line interface for forecast-bench."""
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from bench.utils.logging import setup_logger, get_logger
from bench.utils.io import read_yaml, write_parquet
from bench.utils.env import get_data_uri, get_artifact_uri
from bench.registry import get_registry
from bench.runners.local import run_suite_local, run_shard
from bench.runners.suite_expand import Shard

app = typer.Typer(help="Forecast Bench - Benchmarking framework for forecasting models")
console = Console()


@app.command()
def make_smoke(
    out: str = typer.Option(
        None,
        help="Output path for parquet file (defaults to <DATA_URI>/processed/smoke.parquet)"
    ),
    n_series: int = typer.Option(10, help="Number of series to generate"),
    n_timesteps: int = typer.Option(1000, help="Number of timesteps per series"),
    frequency: str = typer.Option("H", help="Frequency (H=hourly, D=daily)"),
    seed: int = typer.Option(42, help="Random seed"),
):
    """Generate synthetic smoke test dataset."""
    setup_logger(level="INFO")
    logger = get_logger(__name__)
    
    # Determine output path
    if out is None:
        data_uri = get_data_uri()
        out = f"{data_uri}/processed/smoke.parquet"
    
    logger.info(f"Generating smoke dataset: {n_series} series, {n_timesteps} timesteps")
    
    # Generate data
    from bench.data.loaders.smoke import SmokeDataLoader
    loader = SmokeDataLoader({
        "name": "smoke",
        "n_series": n_series,
        "n_timesteps": n_timesteps,
        "frequency": frequency,
        "seed": seed,
    })
    
    df = loader.load()
    logger.info(f"Generated dataset with shape: {df.shape}")
    
    # Save
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    write_parquet(df, out)
    logger.info(f"Saved to: {out}")
    
    console.print(f"[green]✓[/green] Smoke dataset created: {out}")


@app.command()
def prepare(
    dataset: str = typer.Argument(..., help="Dataset name to prepare"),
):
    """Prepare a named dataset (download and process)."""
    setup_logger(level="INFO")
    logger = get_logger(__name__)
    
    console.print(f"[yellow]Note:[/yellow] Generic dataset preparation not yet implemented for {dataset}")
    console.print("Use 'bench make-smoke' for smoke dataset")
    logger.error(f"Dataset preparation not implemented: {dataset}")
    raise typer.Exit(1)


@app.command()
def run(
    dataset: str = typer.Option(..., help="Dataset name"),
    model: str = typer.Option(..., help="Model name"),
    horizon: int = typer.Option(24, help="Forecast horizon"),
    n_folds: int = typer.Option(2, help="Number of folds"),
    mode: str = typer.Option("zero_shot", help="Model mode"),
):
    """Run a single benchmark experiment."""
    setup_logger(level="INFO")
    logger = get_logger(__name__)
    
    console.print("[yellow]Note:[/yellow] Single run command not yet fully implemented")
    console.print("Use 'bench suite' to run a suite of experiments")
    logger.error("Single run not implemented")
    raise typer.Exit(1)


@app.command()
def run_shard_cmd(
    shard_json: str = typer.Option(..., "--shard-json", help="Shard specification as JSON string"),
):
    """Run a single shard (used by AWS Batch)."""
    setup_logger(level="INFO")
    logger = get_logger(__name__)
    
    # Parse shard
    shard = Shard.from_json(shard_json)
    
    # Get URIs
    data_uri = get_data_uri()
    artifact_uri = get_artifact_uri()
    
    logger.info(f"Running shard: {shard.to_dict()}")
    
    # Run shard (minimal suite config)
    suite_config = {
        "n_folds": 10,  # Max, actual fold comes from shard
        "initial_train_frac": 0.7,
    }
    
    result = run_shard(shard, data_uri, artifact_uri, suite_config)
    
    # Save result
    import json
    result_json = json.dumps(result, indent=2, default=str)
    console.print(result_json)
    
    if result.get("status") == "failed":
        raise typer.Exit(1)


@app.command()
def suite(
    config: Path = typer.Option(..., "--config", help="Path to suite configuration YAML"),
):
    """Run a suite of experiments."""
    if not config.exists():
        console.print(f"[red]Error:[/red] Config file not found: {config}")
        raise typer.Exit(1)
    
    run_suite_local(config)


@app.command()
def report(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to generate report for"),
    out: Optional[Path] = typer.Option(None, "--out", help="Output markdown file path"),
):
    """Generate a report for a completed run."""
    setup_logger(level="INFO")
    logger = get_logger(__name__)
    
    artifact_uri = get_artifact_uri()
    run_dir = Path(artifact_uri) / "runs" / run_id
    
    if not run_dir.exists():
        console.print(f"[red]Error:[/red] Run directory not found: {run_dir}")
        raise typer.Exit(1)
    
    # Load summary
    summary_file = run_dir / "summary.yaml"
    if not summary_file.exists():
        console.print(f"[red]Error:[/red] Summary file not found: {summary_file}")
        raise typer.Exit(1)
    
    summary = read_yaml(summary_file)
    
    # Create markdown report
    report_lines = [
        f"# Forecast Benchmark Report",
        f"",
        f"**Run ID:** {run_id}",
        f"**Suite:** {summary.get('suite_name', 'Unknown')}",
        f"**Status:** {summary['n_success']}/{summary['n_shards']} shards successful",
        f"",
        f"## Results Summary",
        f"",
    ]
    
    # Create table of results
    table = Table(title="Shard Results")
    table.add_column("Dataset", style="cyan")
    table.add_column("Model", style="magenta")
    table.add_column("Fold", style="green")
    table.add_column("MAE", style="yellow")
    table.add_column("RMSE", style="yellow")
    table.add_column("sMAPE", style="yellow")
    table.add_column("Status", style="white")
    
    for result in summary.get("results", []):
        shard = result.get("shard", {})
        status = result.get("status", "unknown")
        
        if status == "success" and "aggregated_metrics" in result:
            metrics = result["aggregated_metrics"]
            mae = f"{metrics.get('mae', 0):.3f}"
            rmse = f"{metrics.get('rmse', 0):.3f}"
            smape = f"{metrics.get('smape', 0):.3f}"
        else:
            mae = rmse = smape = "N/A"
        
        table.add_row(
            shard.get("dataset", "?"),
            shard.get("model", "?"),
            str(shard.get("fold", "?")),
            mae,
            rmse,
            smape,
            status,
        )
    
    console.print(table)
    
    # Add to markdown
    report_lines.extend([
        "| Dataset | Model | Fold | MAE | RMSE | sMAPE | Status |",
        "|---------|-------|------|-----|------|-------|--------|",
    ])
    
    for result in summary.get("results", []):
        shard = result.get("shard", {})
        status = result.get("status", "unknown")
        
        if status == "success" and "aggregated_metrics" in result:
            metrics = result["aggregated_metrics"]
            mae = f"{metrics.get('mae', 0):.3f}"
            rmse = f"{metrics.get('rmse', 0):.3f}"
            smape = f"{metrics.get('smape', 0):.3f}"
        else:
            mae = rmse = smape = "N/A"
        
        report_lines.append(
            f"| {shard.get('dataset', '?')} | {shard.get('model', '?')} | "
            f"{shard.get('fold', '?')} | {mae} | {rmse} | {smape} | {status} |"
        )
    
    report_md = "\n".join(report_lines)
    
    # Save if output path provided
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report_md)
        console.print(f"[green]✓[/green] Report saved to: {out}")
    else:
        console.print(report_md)


@app.command()
def list_datasets():
    """List available datasets."""
    registry = get_registry()
    datasets = registry.list_datasets()
    
    console.print("[bold]Available Datasets:[/bold]")
    for dataset in datasets:
        console.print(f"  • {dataset}")


@app.command()
def list_models():
    """List available models."""
    registry = get_registry()
    models = registry.list_models()
    
    console.print("[bold]Available Models:[/bold]")
    for model in models:
        console.print(f"  • {model}")


if __name__ == "__main__":
    app()
