#!/usr/bin/env python3
"""
This script provides a simple way to test your RunPod serverless handler locally
before deploying it to RunPod.
"""

import json
import argparse
import sys
import os

# Add the parent directory to sys.path to make src module importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handler import handler

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test RunPod handler locally')
    parser.add_argument('--signed-url', type=str, help='GCS signed URL for testing', default="")
    return parser.parse_args()

def test_image_url():
    """Test the handler with an image URL input."""
    test_event = {
        "input": {
            "image_url": "https://github.com/runpod-workers/worker-template/raw/main/test-image.jpg"
        }
    }
    
    print("\n==== Testing with image URL ====")
    print(f"Input: {json.dumps(test_event, indent=2)}")
    
    # Call the handler
    result = handler(test_event)
    
    print(f"Output: {json.dumps(result, indent=2)}")
    
def test_text():
    """Test the handler with text input."""
    test_event = {
        "input": {
            "text": "This is a sample text for testing."
        }
    }
    
    print("\n==== Testing with text input ====")
    print(f"Input: {json.dumps(test_event, indent=2)}")
    
    # Call the handler
    result = handler(test_event)
    
    print(f"Output: {json.dumps(result, indent=2)}")

def test_empty_input():
    """Test the handler with empty input."""
    test_event = {
        "input": {}
    }
    
    print("\n==== Testing with empty input ====")
    print(f"Input: {json.dumps(test_event, indent=2)}")
    
    # Call the handler
    result = handler(test_event)
    
    print(f"Output: {json.dumps(result, indent=2)}")

def test_with_callback():
    """Test the handler with a callback URL."""
    test_event = {
        "input": {
            "text": "This is a test with callback URL."
        },
        "callback_url": "https://example.com/callback",
        "id": "test-job-123"
    }
    
    print("\n==== Testing with callback URL ====")
    print(f"Input: {json.dumps(test_event, indent=2)}")
    print("NOTE: The callback URL won't actually be called in local testing.")
    
    # Call the handler
    result = handler(test_event)
    
    print(f"Output: {json.dumps(result, indent=2)}")

def test_with_gcs_signed_url(signed_url=None):
    """Test the handler with a GCS signed URL."""
    # Use provided signed URL or fall back to example URL
    actual_signed_url = signed_url or "https://storage.googleapis.com/example-bucket/results.json?X-Goog-Signature=example"
    
    test_event = {
        "input": {
            "text": "This is a test with GCS signed URL."
        },
        "gcs_signed_url": actual_signed_url,
        "id": "test-job-456"
    }
    
    print("\n==== Testing with GCS signed URL ====")
    # Don't print the full signed URL for security reasons
    redacted_event = {**test_event}
    redacted_event["gcs_signed_url"] = "(real signed url)" if signed_url else actual_signed_url
    print(f"Input: {json.dumps(redacted_event, indent=2)}")
    
    if not signed_url:
        print("NOTE: Using example signed URL that won't work in real testing.")
    else:
        print("NOTE: Using provided signed URL for testing.")
    
    # Call the handler
    result = handler(test_event)
    
    print(f"Output: {json.dumps(result, indent=2)}")

def test_with_callback_and_gcs(signed_url=None):
    """Test the handler with both callback URL and GCS signed URL."""
    # Use provided signed URL or fall back to example URL
    actual_signed_url = signed_url or "https://storage.googleapis.com/example-bucket/results.json?X-Goog-Signature=example"
    
    test_event = {
        "input": {
            "text": "This is a test with both callback and GCS signed URL."
        },
        "callback_url": "https://example.com/callback",
        "gcs_signed_url": actual_signed_url,
        "id": "test-job-789"
    }
    
    print("\n==== Testing with both callback URL and GCS signed URL ====")
    # Don't print the full signed URL for security reasons
    redacted_event = {**test_event}
    redacted_event["gcs_signed_url"] = "(real signed url)" if signed_url else actual_signed_url
    print(f"Input: {json.dumps(redacted_event, indent=2)}")
    
    if not signed_url:
        print("NOTE: Using example signed URL that won't work in real testing.")
    else:
        print("NOTE: Using provided signed URL for testing.")
    print("NOTE: The callback URL won't actually be used in local testing.")
    
    # Call the handler
    result = handler(test_event)
    
    print(f"Output: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    print("Starting local test of RunPod serverless handler...")
    
    # Parse command line arguments
    args = parse_args()
    
    # Run test cases
    test_image_url()
    test_text()
    test_empty_input()
    test_with_callback()
    test_with_gcs_signed_url(args.signed_url)
    test_with_callback_and_gcs(args.signed_url)
    
    print("\nLocal testing completed!") 