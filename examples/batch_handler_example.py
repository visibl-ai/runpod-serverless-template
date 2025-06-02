"""
Example of how to use BatchBaseHandler with the runpod-serverless-template package.

This file demonstrates:
1. How to use BatchBaseHandler for batch processing
2. How to handle the input format: { "input": { "batch": [{ ... }] } }
3. How each batch item can have its own gcs_signed_url
4. How image outputs are automatically uploaded as images to GCS
"""

import time

import numpy as np
from PIL import Image

from runpod_serverless_template import BaseModel, BatchBaseHandler


class ExampleModel(BaseModel):
    """
    Example model that can generate different types of outputs (text, images, JSON).
    """

    def _initialize_model(self):
        """Initialize the model."""
        print("Loading ExampleModel...")
        print("Model loaded successfully")

    def preprocess(self, input_data):
        """Preprocess input data."""
        if "image_url" in input_data:
            return super().preprocess(input_data)
        elif "text" in input_data:
            return input_data["text"].strip()
        else:
            return input_data

    def _run_inference(self, processed_input):
        """Run model inference."""
        if isinstance(processed_input, np.ndarray):
            # Input is an image - return a modified version
            noise = np.random.normal(0, 0.05, processed_input.shape)
            modified_image = np.clip(processed_input + noise, 0, 1)
            return modified_image
        elif isinstance(processed_input, str):
            # Text input - generate different outputs based on content
            if "image" in processed_input.lower():
                # Generate a simple image
                size = 64
                image = np.random.rand(size, size, 3)
                return image
            else:
                # Return JSON response
                return {
                    "analysis": f"Processed text: {processed_input}",
                    "word_count": len(processed_input.split()),
                    "sentiment": "positive",
                }
        else:
            # Default response
            return {
                "message": "Processed successfully",
                "type": str(type(processed_input)),
            }


def example_batch_request():
    """
    Example of how to structure and handle a batch request.
    """
    # Create model and batch handler
    model = ExampleModel()
    batch_handler = BatchBaseHandler(model)

    # Example batch request with the exact format you specified
    batch_event = {
        "input": {
            "batch": [
                {
                    "text": "Generate an image from this text",
                    "gcs_signed_url": "https://storage.googleapis.com/bucket/result1.png?signature=...",
                },
                {
                    "text": "Analyze this text sentiment",
                    "gcs_signed_url": "https://storage.googleapis.com/bucket/result2.json?signature=...",
                },
                {
                    "image_url": "https://example.com/input.jpg",
                    "gcs_signed_url": "https://storage.googleapis.com/bucket/result3.png?signature=...",
                },
                {
                    "text": "Process this without upload"
                    # No gcs_signed_url - result will be returned in response
                },
            ]
        },
        "id": "batch-job-123",
        "callback_url": "https://example.com/callback",  # Optional
    }

    # Process the batch
    result = batch_handler(batch_event)

    print("Batch processing result:")
    print(f"Status: {result['status']}")
    print(f"Batch size: {result['batch_size']}")
    print(f"Successful items: {result['successful_items']}")
    print(f"Failed items: {result['failed_items']}")
    print(f"Total processing time: {result['total_processing_time']:.2f}s")

    print("\nIndividual item results:")
    for item_result in result["batch_results"]:
        idx = item_result["batch_index"]
        if "error" in item_result:
            print(f"  Item {idx}: ERROR - {item_result['error']}")
        else:
            upload_status = item_result.get("gcs_upload", "no upload")
            print(f"  Item {idx}: SUCCESS - GCS upload: {upload_status}")

            # Show what type of output was generated
            if "prediction" in item_result:
                pred = item_result["prediction"]
                if isinstance(pred, np.ndarray):
                    print(f"    Output: Image array {pred.shape}")
                elif isinstance(pred, dict):
                    print(f"    Output: JSON data with keys: {list(pred.keys())}")
                else:
                    print(f"    Output: {type(pred)}")

    return result


def example_error_handling():
    """
    Example showing how batch handler deals with errors in individual items.
    """
    model = ExampleModel()
    batch_handler = BatchBaseHandler(model)

    # Batch with some problematic items
    batch_event = {
        "input": {
            "batch": [
                {"text": "Valid item 1"},
                {"invalid_url": "this will cause an error"},
                {"text": "Valid item 2"},
                # This would cause an error if the URL was real
                {"image_url": "https://invalid-domain-12345.com/nonexistent.jpg"},
            ]
        }
    }

    result = batch_handler(batch_event)

    print("Error handling example:")
    print(f"Total items: {result['batch_size']}")
    print(f"Successful: {result['successful_items']}")
    print(f"Failed: {result['failed_items']}")

    for item_result in result["batch_results"]:
        idx = item_result["batch_index"]
        if "error" in item_result:
            print(f"  Item {idx}: FAILED - {item_result['error']}")
        else:
            print(f"  Item {idx}: SUCCESS")

    return result


# Example handler setup for deployment
def create_batch_handler():
    """
    Function to create and return a batch handler for deployment.
    This would typically be in your main handler.py file.
    """
    model = ExampleModel()
    return BatchBaseHandler(model)


if __name__ == "__main__":
    print("=== BatchBaseHandler Example ===\n")

    print("1. Testing batch request with mixed outputs:")
    example_batch_request()

    print("\n2. Testing error handling:")
    example_error_handling()

    print("\n=== Usage in handler.py ===")
    print(
        """
# In your handler.py file:
from runpod_serverless_template import BatchBaseHandler
from your_model import YourModel

# Create handler
model = YourModel()
handler = BatchBaseHandler(model)

# Start RunPod serverless
import runpod
runpod.serverless.start({"handler": handler})
    """
    )

    print("\n=== Expected Input Format ===")
    print(
        """
{
  "input": {
    "batch": [
      {
        "text": "Your model input data here",
        "gcs_signed_url": "https://storage.googleapis.com/bucket/result1.png?signature=..."
      },
      {
        "image_url": "https://example.com/image.jpg",
        "gcs_signed_url": "https://storage.googleapis.com/bucket/result2.json?signature=..."
      }
    ]
  },
  "id": "job-123",
  "callback_url": "https://your-callback.com/webhook"  // Optional
}
    """
    )
