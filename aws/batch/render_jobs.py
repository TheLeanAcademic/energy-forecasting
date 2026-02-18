"""Render AWS Batch job specifications from suite config."""
import json
import argparse
from pathlib import Path
from bench.utils.io import read_yaml, write_yaml, ensure_dir
from bench.runners.suite_expand import expand_suite


def render_jobs(suite_config_path: Path, output_dir: Path) -> list[dict]:
    """
    Render job specifications from suite config.
    
    Args:
        suite_config_path: Path to suite YAML
        output_dir: Directory to save job specs
    
    Returns:
        List of job specifications
    """
    # Load suite config
    suite_config = read_yaml(suite_config_path)
    
    # Expand to shards
    shards = expand_suite(suite_config)
    
    # Create job specs
    job_specs = []
    for i, shard in enumerate(shards):
        job_spec = {
            "job_name": f"bench_{shard.dataset}_{shard.model}_f{shard.fold}_{i}",
            "shard": shard.to_dict(),
            "shard_json": shard.to_json(),
        }
        job_specs.append(job_spec)
    
    # Save job specs
    ensure_dir(output_dir)
    output_file = output_dir / "job_specs.json"
    
    with open(output_file, "w") as f:
        json.dump(job_specs, f, indent=2)
    
    print(f"Rendered {len(job_specs)} job specifications")
    print(f"Saved to: {output_file}")
    
    return job_specs


def main():
    parser = argparse.ArgumentParser(description="Render AWS Batch job specs from suite config")
    parser.add_argument("--suite", required=True, help="Path to suite config YAML")
    parser.add_argument("--output-dir", default="./aws/batch/jobs", help="Output directory for job specs")
    
    args = parser.parse_args()
    
    suite_path = Path(args.suite)
    output_dir = Path(args.output_dir)
    
    if not suite_path.exists():
        print(f"Error: Suite config not found: {suite_path}")
        return 1
    
    render_jobs(suite_path, output_dir)
    return 0


if __name__ == "__main__":
    exit(main())
