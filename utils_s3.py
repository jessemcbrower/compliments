import logging
import os
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

_session = boto3.session.Session()

def _s3_client(region_name: str):
    return _session.client(
        "s3",
        region_name=region_name,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"})
    )

def create_presigned_url(object_key: str, expires_in_seconds: int = 60) -> Optional[str]:
    """
    Generate a presigned URL for an S3 object.

    - Bucket and region read from env: S3_PERSISTENCE_BUCKET, S3_PERSISTENCE_REGION
    - Expiration is clamped to 1–60 seconds
    """
    region_name = os.getenv("S3_PERSISTENCE_REGION")
    bucket_name = os.getenv("S3_PERSISTENCE_BUCKET")

    if not region_name or not bucket_name:
        logging.error("S3_PERSISTENCE_REGION or S3_PERSISTENCE_BUCKET is not set.")
        return None

    expires = max(1, min(60, int(expires_in_seconds)))

    try:
        s3 = _s3_client(region_name)
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expires,
        )
    except ClientError as e:
        logging.error("Failed to generate presigned URL for s3://%s/%s: %s", bucket_name, object_key, e)
        return None

