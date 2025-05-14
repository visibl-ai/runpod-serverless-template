#!/usr/bin/env python3
"""
This script provides a simple way to test your RunPod serverless handler locally
before deploying it to RunPod.
"""

import json
from runpod_endpoint.handler import handler

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

if __name__ == "__main__":
    print("Starting local test of RunPod serverless handler...")
    
    # Run test cases
    test_image_url()
    test_text()
    test_empty_input()
    test_with_callback()
    
    print("\nLocal testing completed!") 