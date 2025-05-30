"""
Google Cloud Storage utilities for RunPod serverless endpoints.
"""

import json

import requests


def upload_to_signed_url(signed_url, data):
    """
    Upload data to a Google Cloud Storage signed URL.

    Args:
        signed_url (str): The GCS signed URL to upload to
        data (dict or bytes): The data to upload - can be JSON dict or binary bytes

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Handle binary data (e.g., image bytes) vs JSON data
        if isinstance(data, bytes):
            # For binary data, upload directly with appropriate content type
            # Detect content type based on data signature or assume generic binary
            if data.startswith(b"\x89PNG"):
                content_type = "image/png"
            elif data.startswith(b"\xff\xd8\xff"):
                content_type = "image/jpeg"
            elif data.startswith(b"GIF"):
                content_type = "image/gif"
            elif data.startswith(b"RIFF") and b"WEBP" in data[:12]:
                content_type = "image/webp"
            else:
                content_type = "application/octet-stream"

            upload_data = data
            headers = {"Content-Type": content_type, "Cache-Control": "no-cache"}
        else:
            # For JSON data, convert to JSON string
            upload_data = json.dumps(data)
            headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}

        # Upload to the signed URL
        response = requests.put(
            signed_url,
            data=upload_data,
            headers=headers,
        )

        # Check if the upload was successful
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error uploading to signed URL: {str(e)}")
        return False
