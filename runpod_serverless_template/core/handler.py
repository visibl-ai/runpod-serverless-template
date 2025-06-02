"""
Base handler for RunPod serverless endpoints.
"""

import requests

from runpod_serverless_template.utils.gcs import (
    upload_image_to_signed_url,
    upload_to_signed_url,
)


class BaseHandler:
    """
    Base handler class for RunPod serverless endpoints.

    This class handles the common operations of a RunPod serverless endpoint:
    - Processing inputs
    - Error handling
    - Result delivery (direct response, callback, or GCS upload)
    """

    def __init__(self, model_instance):
        """
        Initialize the handler with a model instance.

        Args:
            model_instance: An instance of a class that implements the BaseModel interface
        """
        self.model = model_instance

    def __call__(self, event):
        """
        Handle the incoming request.

        Args:
            event (dict): Input event data from RunPod

        Returns:
            dict: The response to send back
        """
        try:
            # Extract input data
            input_data = event.get("input", {})
            callback_url = event.get("callback_url")
            gcs_signed_url = event.get("gcs_signed_url")

            # Validate input data
            if not input_data:
                return {"error": "No input data provided"}

            # Process the input with the model
            result = self.model.predict(input_data)

            # Create the response payload
            payload = {
                "status": "success",
                "output": result,
                "job_id": event.get("id", "unknown"),
            }

            # If a GCS signed URL is provided, upload the result
            if gcs_signed_url:
                upload_success = upload_to_signed_url(gcs_signed_url, payload)

                if upload_success:
                    # Add information about the upload to the response
                    payload["gcs_upload"] = "success"
                else:
                    # Add error information if upload failed
                    payload["gcs_upload"] = "failed"

            # If a callback URL is provided, send the result
            if callback_url:
                return self._handle_callback(callback_url, payload)

            # If no callback URL, return the result directly
            return payload
        except Exception as e:
            # Handle errors
            return self._handle_error(e, event)

    def _handle_callback(self, callback_url, payload):
        """
        Handle sending results to a callback URL.

        Args:
            callback_url (str): URL to send results to
            payload (dict): The result payload

        Returns:
            dict: Response indicating the result was sent
        """
        try:
            # Send the result to the callback URL
            response = requests.post(
                callback_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            # Check if the callback was successful
            response.raise_for_status()

            # Return a message indicating the result was sent
            return {
                "status": "success",
                "message": f"Result sent to callback URL: {callback_url}",
                "job_id": payload.get("job_id"),
                "gcs_upload": payload.get("gcs_upload"),
            }
        except Exception as callback_error:
            # Log the error but still return the result
            print(f"Error sending result to callback URL: {str(callback_error)}")
            return {
                "status": "success",
                "output": payload.get("output"),
                "callback_error": str(callback_error),
                "gcs_upload": payload.get("gcs_upload"),
            }

    def _handle_error(self, error, event):
        """
        Handle errors during request processing.

        Args:
            error (Exception): The error that occurred
            event (dict): Original input event

        Returns:
            dict: Error response
        """
        # Log the error
        print(f"Error processing request: {str(error)}")

        # Prepare error payload
        error_payload = {
            "status": "error",
            "error": str(error),
            "job_id": event.get("id", "unknown"),
        }

        # If a GCS signed URL is provided, try to upload the error
        if event.get("gcs_signed_url"):
            try:
                upload_to_signed_url(event.get("gcs_signed_url"), error_payload)
            except Exception as gcs_error:
                print(f"Error uploading error to signed URL: {str(gcs_error)}")

        # If a callback URL is provided, send the error
        if event.get("callback_url"):
            try:
                # Send the error to the callback URL
                requests.post(
                    event.get("callback_url"),
                    json=error_payload,
                    headers={"Content-Type": "application/json"},
                )
            except Exception as callback_error:
                print(f"Error sending error to callback URL: {str(callback_error)}")

        # Return error response
        return error_payload


class BatchBaseHandler:
    """
    Batch handler class for RunPod serverless endpoints.

    This class handles batch requests with the format:
    { "input": { "batch": [{ ... }, { ... }] } }

    Each batch item can have its own gcs_signed_url for individual uploads.
    """

    def __init__(self, model_instance):
        """
        Initialize the handler with a model instance.

        Args:
            model_instance: An instance of a class that implements the BaseModel interface
        """
        self.model = model_instance

    def __call__(self, event):
        """
        Handle the incoming batch request.

        Args:
            event (dict): Input event data from RunPod with format:
                         { "input": { "batch": [{ ... }] } }

        Returns:
            dict: The batch response
        """
        try:
            # Extract input data
            input_data = event.get("input", {})
            callback_url = event.get("callback_url")

            # Validate input data structure
            if not input_data:
                return {"error": "No input data provided"}

            if "batch" not in input_data:
                return {
                    "error": "No batch data provided. Expected format: {'input': {'batch': [...]}}"
                }

            batch_items = input_data["batch"]
            if not isinstance(batch_items, list):
                return {"error": "Batch data must be a list"}

            if not batch_items:
                return {"error": "Batch list is empty"}

            # Process the batch (GCS upload is now handled in model.postprocess)
            batch_result = self.model.predict(input_data)

            # Ensure proper format for batch results
            if "batch_results" in batch_result:
                batch_result["job_id"] = event.get("id", "unknown")
            else:
                # Fallback in case something went wrong
                batch_result = {
                    "status": "error",
                    "error": "Invalid batch result format",
                    "job_id": event.get("id", "unknown"),
                }

            # If a callback URL is provided, send the result
            if callback_url:
                return self._handle_callback(callback_url, batch_result)

            # If no callback URL, return the result directly
            return batch_result

        except Exception as e:
            # Handle errors
            return self._handle_error(e, event)

    def _handle_callback(self, callback_url, payload):
        """
        Handle sending batch results to a callback URL.

        Args:
            callback_url (str): URL to send results to
            payload (dict): The batch result payload

        Returns:
            dict: Response indicating the result was sent
        """
        try:
            # Send the result to the callback URL
            response = requests.post(
                callback_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            # Check if the callback was successful
            response.raise_for_status()

            # Return a message indicating the result was sent
            return {
                "status": "success",
                "message": f"Batch result sent to callback URL: {callback_url}",
                "job_id": payload.get("job_id"),
                "batch_size": payload.get("batch_size"),
                "successful_items": payload.get("successful_items"),
                "failed_items": payload.get("failed_items"),
            }
        except Exception as callback_error:
            # Log the error but still return the result
            print(f"Error sending batch result to callback URL: {str(callback_error)}")
            return {
                "status": "success",
                "output": payload,
                "callback_error": str(callback_error),
            }

    def _handle_error(self, error, event):
        """
        Handle errors during batch request processing.

        Args:
            error (Exception): The error that occurred
            event (dict): Original input event

        Returns:
            dict: Error response
        """
        # Log the error
        print(f"Error processing batch request: {str(error)}")

        # Prepare error payload
        error_payload = {
            "status": "error",
            "error": str(error),
            "job_id": event.get("id", "unknown"),
        }

        # If a callback URL is provided, send the error
        if event.get("callback_url"):
            try:
                # Send the error to the callback URL
                requests.post(
                    event.get("callback_url"),
                    json=error_payload,
                    headers={"Content-Type": "application/json"},
                )
            except Exception as callback_error:
                print(f"Error sending error to callback URL: {str(callback_error)}")

        # Return error response
        return error_payload
