"""
Example demonstrating the new standardized error handling in BaseModel.

This shows:
1. How errors are automatically handled at different stages
2. How to override error handling for custom behavior
3. How errors are formatted and uploaded to GCS
4. How to add custom error context
"""

import time

import numpy as np

from runpod_serverless_template import BaseModel, BatchBaseHandler


class BasicErrorHandlingModel(BaseModel):
    """Basic model using default error handling."""

    def _initialize_model(self):
        print("Loading basic model...")
        # Simulate some model loading

    def _run_inference(self, processed_input):
        # This model intentionally has some failure modes for demonstration
        if isinstance(processed_input, str):
            if "crash" in processed_input.lower():
                raise RuntimeError("Model crashed due to input containing 'crash'")
            elif "memory" in processed_input.lower():
                raise MemoryError("Out of memory processing this input")
            else:
                return {"text_analysis": f"Processed: {processed_input}"}
        else:
            return {"result": "processed successfully"}


class CustomErrorHandlingModel(BaseModel):
    """Model with custom error handling and context."""

    def __init__(self):
        super().__init__()
        # Enable traceback in errors for debugging
        self.include_traceback = True

    def _initialize_model(self):
        print("Loading custom error handling model...")
        self.model_version = "2.1.0"
        self.error_count = 0

    def _run_inference(self, processed_input):
        if isinstance(processed_input, str) and "fail" in processed_input.lower():
            raise ValueError("Input validation failed: contains 'fail'")
        return {"custom_result": f"Custom processing of: {processed_input}"}

    def handle_error(self, error, stage, input_data=None, gcs_signed_url=None):
        """Custom error handling with additional context."""
        # Increment error counter
        self.error_count += 1

        # Call the parent error handler first
        error_result = super().handle_error(error, stage, input_data, gcs_signed_url)

        # Add custom fields
        error_result.update(
            {
                "model_version": self.model_version,
                "total_errors": self.error_count,
                "custom_error_id": f"ERR_{int(time.time())}_{self.error_count}",
                "severity": self._classify_error_severity(error),
                "suggested_action": self._get_suggested_action(error, stage),
            }
        )

        # Log the error internally
        print(f"Custom error logged: {error_result['custom_error_id']}")

        return error_result

    def _get_error_context(self, error, stage, input_data):
        """Add custom error context."""
        # Get base context
        context = super()._get_error_context(error, stage, input_data)

        # Add custom context
        context.update(
            {
                "model_version": self.model_version,
                "previous_errors": self.error_count,
                "memory_usage": "simulated_memory_info",
                "stage_specific_info": self._get_stage_info(stage, input_data),
            }
        )

        return context

    def _classify_error_severity(self, error):
        """Classify error severity."""
        if isinstance(error, (MemoryError, SystemError)):
            return "critical"
        elif isinstance(error, (ValueError, TypeError)):
            return "warning"
        else:
            return "error"

    def _get_suggested_action(self, error, stage):
        """Get suggested action for the error."""
        suggestions = {
            "preprocess": "Check input format and data types",
            "inference": "Verify model is loaded correctly and input is valid",
            "postprocess": "Check output format and GCS configuration",
        }

        if isinstance(error, MemoryError):
            return "Reduce input size or restart the service"
        elif isinstance(error, ValueError):
            return "Validate input data format and content"
        else:
            return suggestions.get(stage, "Contact support")

    def _get_stage_info(self, stage, input_data):
        """Get stage-specific debugging information."""
        if stage == "preprocess":
            return {"input_size": len(str(input_data)) if input_data else 0}
        elif stage == "inference":
            return {"input_type": type(input_data).__name__}
        elif stage == "postprocess":
            return {"output_processing": True}
        else:
            return {}


def test_basic_error_handling():
    """Test basic error handling with default behavior."""
    print("=== Testing Basic Error Handling ===")

    model = BasicErrorHandlingModel()

    # Test successful case
    print("\n1. Successful case:")
    result = model.predict({"text": "normal input"})
    print(f"Status: {result['status']}")
    print(f"Result: {result.get('prediction', 'N/A')}")

    # Test preprocessing error
    print("\n2. Preprocessing error (invalid input):")
    result = model.predict({"invalid_data": None})
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")
    print(f"Stage: {result['stage']}")

    # Test inference error
    print("\n3. Inference error (model crash):")
    result = model.predict({"text": "this will crash the model"})
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")
    print(f"Error type: {result['error_type']}")

    # Test with GCS upload
    print("\n4. Error with GCS upload:")
    result = model.predict(
        {
            "text": "memory error input",
            "gcs_signed_url": "https://storage.googleapis.com/bucket/error.json",
        }
    )
    print(f"Status: {result['status']}")
    print(f"GCS Upload: {result.get('gcs_upload', 'N/A')}")


def test_custom_error_handling():
    """Test custom error handling with additional context."""
    print("\n=== Testing Custom Error Handling ===")

    model = CustomErrorHandlingModel()

    # Test successful case
    print("\n1. Successful case:")
    result = model.predict({"text": "good input"})
    print(f"Status: {result['status']}")

    # Test custom error handling
    print("\n2. Custom error with enhanced context:")
    result = model.predict({"text": "this will fail validation"})
    print(f"Status: {result['status']}")
    print(f"Custom Error ID: {result['custom_error_id']}")
    print(f"Severity: {result['severity']}")
    print(f"Suggested Action: {result['suggested_action']}")
    print(f"Model Version: {result['model_version']}")
    print(f"Model Context Keys: {list(result.get('model_context', {}).keys())}")

    # Test multiple errors to see counter
    print("\n3. Multiple errors (testing counter):")
    for i in range(2):
        result = model.predict({"text": f"fail test {i+1}"})
        print(
            f"Error {i+1} - ID: {result['custom_error_id']}, Total: {result['total_errors']}"
        )


def test_batch_error_handling():
    """Test error handling in batch processing."""
    print("\n=== Testing Batch Error Handling ===")

    model = CustomErrorHandlingModel()
    handler = BatchBaseHandler(model)

    # Mixed batch with successes and failures
    batch_event = {
        "input": {
            "batch": [
                {"text": "good input 1"},
                {"text": "this will fail"},
                {"text": "good input 2"},
                {"text": "another fail case"},
                {
                    "text": "final good input",
                    "gcs_signed_url": "https://storage.googleapis.com/bucket/result.json",
                },
            ]
        }
    }

    result = handler(batch_event)

    print(f"Batch Status: {result['status']}")
    print(f"Total Items: {result['batch_size']}")
    print(f"Successful: {result['successful_items']}")
    print(f"Failed: {result['failed_items']}")

    print("\nIndividual Results:")
    for item_result in result["batch_results"]:
        idx = item_result["batch_index"]
        status = item_result.get("status", "unknown")
        if status == "error":
            error_id = item_result.get("custom_error_id", "N/A")
            print(f"  Item {idx}: ERROR - {error_id}")
        else:
            print(f"  Item {idx}: SUCCESS")


def test_error_with_gcs_upload():
    """Test error handling with GCS uploads."""
    print("\n=== Testing Error Handling with GCS Upload ===")

    model = CustomErrorHandlingModel()

    # Test error that gets uploaded to GCS
    result = model.predict(
        {
            "text": "this will definitely fail",
            "gcs_signed_url": "https://storage.googleapis.com/bucket/detailed_error.json",
        }
    )

    print(f"Status: {result['status']}")
    print(f"Error uploaded to GCS: {result.get('gcs_upload', 'N/A')}")
    print(f"Error contains traceback: {'traceback' in result}")
    print(f"Model context included: {'model_context' in result}")


if __name__ == "__main__":
    print("=== Error Handling Examples ===")

    test_basic_error_handling()
    test_custom_error_handling()
    test_batch_error_handling()
    test_error_with_gcs_upload()

    print("\n=== Summary ===")
    print(
        """
Error handling is now centralized in BaseModel with:

✅ Automatic error catching at each stage (preprocess, inference, postprocess)
✅ Standardized error format with status, error_type, stage, timestamp
✅ Optional traceback inclusion for debugging
✅ Custom error context via _get_error_context()
✅ Overridable handle_error() method for custom error handling
✅ Automatic GCS upload of error details
✅ Proper error handling in batch processing

To customize error handling:
1. Override handle_error() for custom error formatting
2. Override _get_error_context() for additional debugging info
3. Set self.include_traceback = True for detailed stack traces
4. Add custom error classification and suggested actions
    """
    )
