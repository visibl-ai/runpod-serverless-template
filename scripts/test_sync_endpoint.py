#!/usr/bin/env python3
"""
Test script for making synchronous requests to the RunPod endpoint.
This script sends a request and waits for the response.
"""

import os
import sys
import json
import time
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Default test values
DEFAULT_TEXT = "This is a default test input."
DEFAULT_IMAGE_URL = "https://images.unsplash.com/photo-1579353977828-2a4eab540b9a"

def test_endpoint(endpoint_id, api_key, input_data):
    """
    Test the RunPod endpoint with the provided input data.
    
    Args:
        endpoint_id (str): The RunPod endpoint ID
        api_key (str): The RunPod API key
        input_data (dict): The input data for the model
    
    Returns:
        dict: The response from the endpoint
    """
    # Construct the endpoint URL
    endpoint_url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    # Create the headers with authentication
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Create the payload
    payload = {
        "input": input_data
    }
    
    print(f"Sending request to {endpoint_url}")
    print(f"Input data: {json.dumps(input_data, indent=2)}")
    
    try:
        # Make the request
        start_time = time.time()
        response = requests.post(endpoint_url, headers=headers, json=payload, timeout=30)
        end_time = time.time()
        
        # Calculate the request duration
        duration = end_time - start_time
        
        # Check if the response is valid
        if response.status_code != 200:
            print(f"\nError: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        try:
            # Try to parse the JSON response
            result = response.json()
            
            print(f"\nResponse received in {duration:.2f} seconds:")
            print(json.dumps(result, indent=2))
            
            return result
        except json.JSONDecodeError:
            print(f"Error: Could not parse response as JSON")
            print(f"Raw response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the endpoint.")
        print("Please check:")
        print("  1. Your endpoint ID is correct")
        print("  2. Your API key is valid")
        print("  3. The endpoint is running and accessible")
        print("\nIf testing locally without a real endpoint, this is expected.")
        return None
    
    except requests.exceptions.Timeout:
        print("\nError: Request timed out after 30 seconds.")
        print("This could indicate a slow endpoint or a processing-intensive request.")
        return None
        
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return None

def main():
    """
    Main function to parse command line arguments and run the test.
    """
    parser = argparse.ArgumentParser(description="Test the RunPod serverless endpoint")
    
    # Add arguments
    parser.add_argument("--endpoint-id", help="The RunPod endpoint ID (or set RUNPOD_ENDPOINT_ID env var)")
    parser.add_argument("--api-key", help="The RunPod API key (or set RUNPOD_API_KEY env var)")
    parser.add_argument("--text", help=f"Text input for the model (or set DEFAULT_TEST_TEXT env var)")
    parser.add_argument("--image-url", help="URL of an image for the model (or set DEFAULT_TEST_IMAGE_URL env var)")
    parser.add_argument("--json-input", help="Path to a JSON file containing the input data")
    
    args = parser.parse_args()
    
    # Get endpoint ID and API key from args or environment variables
    endpoint_id = args.endpoint_id or os.environ.get("RUNPOD_ENDPOINT_ID", "your_endpoint_id_here")
    api_key = args.api_key or os.environ.get("RUNPOD_API_KEY", "your_api_key_here")
    
    # Skip credential warnings for development environment
    dev_mode = endpoint_id == "your_endpoint_id_here" or api_key == "your_api_key_here"
    
    # Warn about placeholder credentials if not in dev mode
    if not dev_mode and endpoint_id == "your_endpoint_id_here":
        print("Warning: Using placeholder endpoint ID. Set --endpoint-id or RUNPOD_ENDPOINT_ID environment variable.")
        
    if not dev_mode and api_key == "your_api_key_here":
        print("Warning: Using placeholder API key. Set --api-key or RUNPOD_API_KEY environment variable.")
    
    # Determine the input data
    if args.json_input:
        # Load input data from JSON file
        try:
            with open(args.json_input, 'r') as f:
                input_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON input file: {str(e)}")
            sys.exit(1)
    elif args.text:
        # Use text input from args
        input_data = {"text": args.text}
    elif args.image_url:
        # Use image URL input from args
        input_data = {"image_url": args.image_url}
    elif os.environ.get("DEFAULT_TEST_TEXT"):
        # Use text input from environment
        input_data = {"text": os.environ.get("DEFAULT_TEST_TEXT")}
    elif os.environ.get("DEFAULT_TEST_IMAGE_URL"):
        # Use image URL input from environment
        input_data = {"image_url": os.environ.get("DEFAULT_TEST_IMAGE_URL")}
    else:
        # Use default text input
        print("No input specified. Using default text input.")
        input_data = {"text": DEFAULT_TEXT}
    
    # Call the test function
    test_endpoint(endpoint_id, api_key, input_data)

if __name__ == "__main__":
    main() 