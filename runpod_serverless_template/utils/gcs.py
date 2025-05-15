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
