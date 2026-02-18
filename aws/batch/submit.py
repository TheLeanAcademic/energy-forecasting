"""Submit jobs to AWS Batch."""
import argparse
import os
from pathlib import Path
import boto3
from bench.utils.io import read_yaml
from bench.runners.suite_expand import expand_suite


def submit_jobs(
    suite_config_path: Path,
    queue_name: str,
    job_definition: str,
    image_tag: str,
):
    """
    Submit jobs to AWS Batch.
    
    Args:
        suite_config_path: Path to suite YAML
        queue_name: AWS Batch queue name
        job_definition: AWS Batch job definition name
        image_tag: Docker image tag
    """
    # Load suite config
    suite_config = read_yaml(suite_config_path)
    
    # Expand to shards
    shards = expand_suite(suite_config)
    
    print(f"Submitting {len(shards)} jobs to AWS Batch")
    print(f"Queue: {queue_name}")
    print(f"Job Definition: {job_definition}")
    
    # Get environment variables for jobs
    data_uri = os.environ.get("BENCH_DATA_URI", "s3://forecast-bench-data")
    artifact_uri = os.environ.get("BENCH_ARTIFACT_URI", "s3://forecast-bench-artifacts")
    mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI", "")
    
    # Create Batch client
    batch = boto3.client("batch")
    
    submitted_jobs = []
    
    for i, shard in enumerate(shards):
        job_name = f"bench_{shard.dataset}_{shard.model}_f{shard.fold}_{i}".replace("_", "-")
        
        # Prepare environment variables
        environment = [
            {"name": "BENCH_DATA_URI", "value": data_uri},
            {"name": "BENCH_ARTIFACT_URI", "value": artifact_uri},
        ]
        
        if mlflow_uri:
            environment.append({"name": "MLFLOW_TRACKING_URI", "value": mlflow_uri})
        
        # Prepare command
        command = ["run-shard", "--shard-json", shard.to_json()]
        
        try:
            response = batch.submit_job(
                jobName=job_name,
                jobQueue=queue_name,
                jobDefinition=job_definition,
                containerOverrides={
                    "command": command,
                    "environment": environment,
                }
            )
            
            job_id = response["jobId"]
            submitted_jobs.append({
                "job_name": job_name,
                "job_id": job_id,
                "shard": shard.to_dict(),
            })
            
            print(f"✓ Submitted: {job_name} (ID: {job_id})")
            
        except Exception as e:
            print(f"✗ Failed to submit {job_name}: {e}")
    
    print(f"\nSubmitted {len(submitted_jobs)}/{len(shards)} jobs successfully")
    
    return submitted_jobs


def main():
    parser = argparse.ArgumentParser(description="Submit jobs to AWS Batch")
    parser.add_argument("--suite", required=True, help="Path to suite config YAML")
    parser.add_argument("--queue", required=True, help="AWS Batch queue name")
    parser.add_argument("--job-definition", required=True, help="AWS Batch job definition name")
    parser.add_argument("--image-tag", default="latest", help="Docker image tag")
    
    args = parser.parse_args()
    
    suite_path = Path(args.suite)
    
    if not suite_path.exists():
        print(f"Error: Suite config not found: {suite_path}")
        return 1
    
    submit_jobs(suite_path, args.queue, args.job_definition, args.image_tag)
    return 0


if __name__ == "__main__":
    exit(main())
