#!/usr/bin/env python3
"""
Test script for RunPod endpoint with GCS signed URL functionality.
This script:
1. Takes a GCS signed URL as input
2. Sends a request to the RunPod endpoint with the signed URL
3. Checks if the results were uploaded to GCS
"""

import os
import sys
import json
import time
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test RunPod endpoint with GCS signed URL")
    
    # RunPod connection settings
    parser.add_argument("--api-key", type=str, help="RunPod API key")
    parser.add_argument("--endpoint-id", type=str, help="RunPod endpoint ID")
    
    # Input options
    parser.add_argument("--text", type=str, help="Text input for the model")
    parser.add_argument("--image-url", type=str, help="Image URL input for the model")
    parser.add_argument("--json-input", type=str, help="Path to JSON file containing input data")
    
    # GCS settings
    parser.add_argument("--signed-url", type=str, required=True, help="GCS signed URL to upload results to")
    
    return parser.parse_args()

def get_input_data(args):
    """Get the input data from arguments or environment variables."""
    # If JSON input file is provided, use that
    if args.json_input:
        try:
            with open(args.json_input, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON input: {str(e)}")
            sys.exit(1)
    
    # Otherwise build input from arguments
    input_data = {}
    
    # Use text input if provided
    if args.text:
        input_data["text"] = args.text
    elif os.environ.get("DEFAULT_TEST_TEXT"):
        input_data["text"] = os.environ.get("DEFAULT_TEST_TEXT")
    
    # Use image URL if provided
    if args.image_url:
        input_data["image_url"] = args.image_url
    elif os.environ.get("DEFAULT_TEST_IMAGE_URL") and not input_data:
        # Only use default image if no text was specified
        input_data["image_url"] = os.environ.get("DEFAULT_TEST_IMAGE_URL")
    
    # If no input was provided, use a default text
    if not input_data:
        input_data["text"] = "This is a test for RunPod serverless with GCS signed URL."
    
    return input_data

def run_test(args):
    """Run the test with the provided arguments."""
    # Get API key and endpoint ID (from args or environment)
    api_key = args.api_key or os.environ.get("RUNPOD_API_KEY")
    if not api_key:
        print("Error: RunPod API key is required. Provide it with --api-key or set RUNPOD_API_KEY environment variable.")
        sys.exit(1)
    
    endpoint_id = args.endpoint_id or os.environ.get("RUNPOD_ENDPOINT_ID")
    if not endpoint_id:
        print("Error: RunPod endpoint ID is required. Provide it with --endpoint-id or set RUNPOD_ENDPOINT_ID environment variable.")
        sys.exit(1)
    
    # Get the input data
    input_data = get_input_data(args)
    print(f"Using input data: {json.dumps(input_data, indent=2)}")
    
    # Use the provided signed URL
    signed_url = args.signed_url
    print(f"Using provided signed URL for uploading results")
    
    # Build the request payload
    payload = {
        "input": input_data,
        "gcs_signed_url": signed_url
    }
    
    # Send the request to RunPod
    print(f"Sending request to RunPod endpoint {endpoint_id}...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        
        print(f"Response status code: {response.status_code}")
        print(f"Response data: {json.dumps(response_data, indent=2)}")
        
        # If it's an async job, get the status
        if "id" in response_data:
            job_id = response_data["id"]
            print(f"Job ID: {job_id}")
            print("This is an asynchronous job. You'll need to check the status separately.")
        
        # Wait a moment to allow upload to complete
        print("Request sent successfully. If the endpoint is functioning correctly,")
        print("it should upload the results to the provided GCS signed URL.")
        print("You can check the uploaded content through the Google Cloud Console or other GCS tools.")
    
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_args()
    run_test(args) 