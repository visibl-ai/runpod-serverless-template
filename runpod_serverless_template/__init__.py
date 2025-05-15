"""
RunPod Serverless Template Package

This package provides utilities and base classes for creating serverless endpoints on RunPod.
"""

__version__ = "0.1.0"

from runpod_serverless_template.core.handler import BaseHandler
from runpod_serverless_template.core.model import BaseModel
from runpod_serverless_template.utils import upload_to_signed_url

__all__ = ["BaseHandler", "BaseModel", "upload_to_signed_url"]
