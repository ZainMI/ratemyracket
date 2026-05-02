from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


def r2_is_configured() -> bool:
    return bool(
        settings.r2_endpoint_url
        and settings.r2_access_key_id
        and settings.r2_secret_access_key
        and settings.r2_bucket
    )


def get_r2_client():
    if not r2_is_configured():
        return None

    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


def download_r2_prefix(
    local_dir: str | Path,
    prefix: str | None = None,
) -> dict:
    """
    Downloads all files from an R2 prefix into local_dir.

    Example:
      R2 bucket:
        inference_state.pkl
        matches_cleaned.csv

      local_dir="ml/data"

      Result:
        ml/data/inference_state.pkl
        ml/data/matches_cleaned.csv
    """
    if not r2_is_configured():
        return {
            "status": "skipped",
            "reason": "R2 is not configured.",
            "downloaded": 0,
        }

    client = get_r2_client()
    bucket = settings.r2_bucket
    prefix = settings.r2_prefix if prefix is None else prefix
    prefix = prefix.strip("/")

    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0

    try:
        paginator = client.get_paginator("list_objects_v2")

        paginate_kwargs = {"Bucket": bucket}
        if prefix:
            paginate_kwargs["Prefix"] = prefix + "/"

        for page in paginator.paginate(**paginate_kwargs):
            for obj in page.get("Contents", []):
                key = obj["Key"]

                if key.endswith("/"):
                    continue

                if prefix:
                    relative_key = key.removeprefix(prefix + "/")
                else:
                    relative_key = key

                if not relative_key:
                    continue

                target = local_dir / relative_key
                target.parent.mkdir(parents=True, exist_ok=True)

                print(f"Downloading R2 file: {key} -> {target}")
                client.download_file(bucket, key, str(target))
                downloaded += 1

        return {
            "status": "ok",
            "bucket": bucket,
            "prefix": prefix,
            "local_dir": str(local_dir),
            "downloaded": downloaded,
        }

    except (BotoCoreError, ClientError) as e:
        print(f"R2 download failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "downloaded": downloaded,
        }


def upload_file_to_r2(
    local_file: str | Path,
    key: str | None = None,
) -> dict:
    """
    Uploads one file to R2.
    Useful later for pipeline output.
    """
    if not r2_is_configured():
        return {
            "status": "skipped",
            "reason": "R2 is not configured.",
        }

    local_file = Path(local_file)

    if not local_file.exists():
        return {
            "status": "error",
            "error": f"File does not exist: {local_file}",
        }

    client = get_r2_client()
    bucket = settings.r2_bucket

    if key is None:
        key = local_file.name

    try:
        print(f"Uploading R2 file: {local_file} -> {key}")
        client.upload_file(str(local_file), bucket, key)

        return {
            "status": "ok",
            "bucket": bucket,
            "key": key,
        }

    except (BotoCoreError, ClientError) as e:
        print(f"R2 upload failed: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def upload_directory_to_r2(
    local_dir: str | Path,
    prefix: str | None = None,
) -> dict:
    """
    Uploads all files in a directory to R2.
    Useful later for pipeline outputs.
    """
    if not r2_is_configured():
        return {
            "status": "skipped",
            "reason": "R2 is not configured.",
            "uploaded": 0,
        }

    local_dir = Path(local_dir)

    if not local_dir.exists():
        return {
            "status": "error",
            "error": f"Directory does not exist: {local_dir}",
            "uploaded": 0,
        }

    prefix = settings.r2_prefix if prefix is None else prefix
    prefix = prefix.strip("/")

    uploaded = 0

    for path in local_dir.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(local_dir).as_posix()
        key = f"{prefix}/{relative}" if prefix else relative

        result = upload_file_to_r2(path, key=key)

        if result["status"] == "ok":
            uploaded += 1

    return {
        "status": "ok",
        "local_dir": str(local_dir),
        "prefix": prefix,
        "uploaded": uploaded,
    }
