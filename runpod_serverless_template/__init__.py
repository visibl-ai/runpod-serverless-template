"""
RunPod Serverless Template Package

This package provides utilities and base classes for creating serverless endpoints on RunPod.
"""

__version__ = "0.1.0"

from runpod_serverless_template.core.handler import BaseHandler, BatchBaseHandler
from runpod_serverless_template.core.model import BaseModel
from runpod_serverless_template.utils import (
    upload_image_to_signed_url,
    upload_to_signed_url,
)

__all__ = [
    "BaseHandler",
    "BatchBaseHandler",
    "BaseModel",
    "upload_to_signed_url",
    "upload_image_to_signed_url",
]
