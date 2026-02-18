"""S3 utilities."""
import os
from pathlib import Path
from typing import Union
import boto3
from botocore.exceptions import ClientError


def parse_s3_uri(uri: str) -> tuple[str, str]:
    """Parse S3 URI into bucket and key."""
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an S3 URI: {uri}")
    parts = uri[5:].split("/", 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ""
    return bucket, key


def is_s3_uri(path: Union[str, Path]) -> bool:
    """Check if path is an S3 URI."""
    return str(path).startswith("s3://")


def s3_exists(uri: str) -> bool:
    """Check if S3 object exists."""
    bucket, key = parse_s3_uri(uri)
    s3 = boto3.client("s3")
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False


def s3_list(uri: str, suffix: str = "") -> list[str]:
    """List objects in S3 bucket/prefix."""
    bucket, prefix = parse_s3_uri(uri)
    s3 = boto3.client("s3")
    
    objects = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                if not suffix or key.endswith(suffix):
                    objects.append(f"s3://{bucket}/{key}")
    
    return objects


def s3_upload(local_path: Union[str, Path], s3_uri: str) -> None:
    """Upload local file to S3."""
    bucket, key = parse_s3_uri(s3_uri)
    s3 = boto3.client("s3")
    s3.upload_file(str(local_path), bucket, key)


def s3_download(s3_uri: str, local_path: Union[str, Path]) -> None:
    """Download S3 object to local file."""
    bucket, key = parse_s3_uri(s3_uri)
    s3 = boto3.client("s3")
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, str(local_path))
