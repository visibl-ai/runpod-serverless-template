"""
Google Cloud Storage utilities for RunPod serverless endpoints.
"""

import io
import json

import numpy as np
import requests
from PIL import Image


def upload_to_signed_url(signed_url, data):
    """
    Upload data to a Google Cloud Storage signed URL.

    Args:
        signed_url (str): The GCS signed URL to upload to
        data (dict): The data to upload

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert data to JSON string
        json_data = json.dumps(data)

        # Upload to the signed URL
        response = requests.put(
            signed_url,
            data=json_data,
            headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
        )

        # Check if the upload was successful
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error uploading to signed URL: {str(e)}")
        return False


def upload_image_to_signed_url(signed_url, image_data, image_format="PNG"):
    """
    Upload image data to a Google Cloud Storage signed URL.

    Args:
        signed_url (str): The GCS signed URL to upload to
        image_data: Image data (PIL Image, numpy array, or bytes)
        image_format (str): Image format to save as (PNG, JPEG, etc.)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert image data to bytes
        if isinstance(image_data, np.ndarray):
            # Convert numpy array to PIL Image
            if image_data.max() <= 1.0:
                image_data = (image_data * 255).astype(np.uint8)
            pil_image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            pil_image = image_data
        elif isinstance(image_data, bytes):
            # Already in bytes format
            image_bytes = image_data
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")

        # Convert PIL Image to bytes if needed
        if not isinstance(image_data, bytes):
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format=image_format)
            image_bytes = img_buffer.getvalue()

        # Determine content type
        content_type = f"image/{image_format.lower()}"
        if image_format.upper() == "JPEG":
            content_type = "image/jpeg"

        # Upload to the signed URL
        response = requests.put(
            signed_url,
            data=image_bytes,
            headers={"Content-Type": content_type, "Cache-Control": "no-cache"},
        )

        # Check if the upload was successful
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error uploading image to signed URL: {str(e)}")
        return False
