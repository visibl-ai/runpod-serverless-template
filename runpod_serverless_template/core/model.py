"""
Base model class for AI models running on RunPod serverless endpoints.
"""

import json
import time
import traceback
from abc import ABC, abstractmethod

import numpy as np
import requests
from PIL import Image

from runpod_serverless_template.utils.gcs import (
    upload_image_to_signed_url,
    upload_to_signed_url,
)


class BaseModel(ABC):
    """
    Base class for AI models to be deployed on RunPod.

    Subclass this to implement your specific model functionality.
    """

    def __init__(self):
        """
        Initialize the model.
        This is called when the serverless container starts.
        """
        print("Initializing base model...")
        self.model_ready = False
        self._initialize_model()
        self.model_ready = True
        print("Model initialized successfully")

    @abstractmethod
    def _initialize_model(self):
        """
        Initialize the model, load weights, etc.
        Override this method in your subclass.
        """
        pass

    def preprocess(self, input_data):
        """
        Preprocess the input data before feeding it to the model.

        Args:
            input_data (dict): The raw input data

        Returns:
            The preprocessed data ready for model prediction
        """
        # Basic implementation for common input types
        if "image_url" in input_data:
            return self._preprocess_image(input_data["image_url"])
        elif "text" in input_data:
            return self._preprocess_text(input_data["text"])
        else:
            # Default handling for other input types
            return input_data

    def _preprocess_image(self, image_url):
        """
        Default image preprocessing implementation.
        Override this in your subclass for custom image preprocessing.

        Args:
            image_url (str): URL of the image to process

        Returns:
            numpy.ndarray: Processed image as numpy array
        """
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            img = Image.open(response.raw)
            # Default resize to common input size
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            return img_array
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

    def _preprocess_text(self, text):
        """
        Default text preprocessing implementation.
        Override this in your subclass for custom text preprocessing.

        Args:
            text (str): Text to process

        Returns:
            str: Processed text
        """
        # Simple text preprocessing
        return text.strip()

    @abstractmethod
    def _run_inference(self, processed_input):
        """
        Run the actual model inference.
        Override this method in your subclass.

        Args:
            processed_input: The preprocessed input data

        Returns:
            The raw model output
        """
        pass

    def _is_image_output(self, output):
        """
        Check if the output is image data that should be uploaded as an image.

        Args:
            output: The model output to check

        Returns:
            bool: True if output should be treated as image data
        """
        return (
            isinstance(output, np.ndarray) and len(output.shape) >= 2
        ) or isinstance(output, Image.Image)

    def handle_error(self, error, stage, input_data=None, gcs_signed_url=None):
        """
        Handle errors that occur during processing.
        Override this method for custom error handling and formatting.

        Args:
            error (Exception): The error that occurred
            stage (str): The stage where the error occurred ('preprocess', 'inference', 'postprocess')
            input_data: The input data being processed when error occurred
            gcs_signed_url (str, optional): GCS signed URL for uploading error info

        Returns:
            dict: Formatted error result
        """
        # Create base error information
        error_result = {
            "status": "error",
            "error": str(error),
            "error_type": type(error).__name__,
            "stage": stage,
            "timestamp": time.time(),
        }

        # Add traceback for debugging (you might want to exclude this in production)
        if hasattr(self, "include_traceback") and self.include_traceback:
            error_result["traceback"] = traceback.format_exc()

        # Add model-specific error context
        try:
            model_context = self._get_error_context(error, stage, input_data)
            if model_context:
                error_result["model_context"] = model_context
        except Exception as context_error:
            print(f"Error getting model context: {str(context_error)}")

        # Handle GCS upload for error if URL provided
        if gcs_signed_url:
            try:
                upload_success = upload_to_signed_url(gcs_signed_url, error_result)
                error_result["gcs_upload"] = "success" if upload_success else "failed"
            except Exception as upload_error:
                print(f"Error uploading error to GCS: {str(upload_error)}")
                error_result["gcs_upload"] = "failed"

        return error_result

    def _get_error_context(self, error, stage, input_data):
        """
        Get model-specific error context.
        Override this method to add custom error context.

        Args:
            error (Exception): The error that occurred
            stage (str): The stage where the error occurred
            input_data: The input data being processed

        Returns:
            dict: Additional error context (or None)
        """
        # Default implementation provides basic context
        context = {
            "model_ready": self.model_ready,
            "input_type": (
                type(input_data).__name__ if input_data is not None else "unknown"
            ),
        }

        # Add stage-specific context
        if stage == "preprocess":
            if isinstance(input_data, dict):
                context["input_keys"] = list(input_data.keys())
        elif stage == "inference":
            context["processed_input_type"] = type(input_data).__name__
        elif stage == "postprocess":
            context["output_type"] = type(input_data).__name__

        return context

    def _predict_single(self, input_data, gcs_signed_url=None):
        """
        Run prediction for a single input item.

        Args:
            input_data (dict): Single input item
            gcs_signed_url (str, optional): GCS signed URL for uploading results

        Returns:
            dict: Prediction result for the single item
        """
        start_time = time.time()

        try:
            # Preprocess the input
            try:
                processed_input = self.preprocess(input_data)
            except Exception as e:
                return self.handle_error(e, "preprocess", input_data, gcs_signed_url)

            # Run the model
            try:
                raw_output = self._run_inference(processed_input)
            except Exception as e:
                return self.handle_error(
                    e, "inference", processed_input, gcs_signed_url
                )

            # Postprocess the output (including GCS upload if URL provided)
            try:
                result = self.postprocess(raw_output, gcs_signed_url=gcs_signed_url)
            except Exception as e:
                return self.handle_error(e, "postprocess", raw_output, gcs_signed_url)

            # Calculate processing time and add metadata
            processing_time = time.time() - start_time

            if isinstance(result, dict):
                result["processing_time"] = processing_time
                result["status"] = "success"
            else:
                # If result is not a dict, wrap it in one
                result = {
                    "prediction": result,
                    "processing_time": processing_time,
                    "status": "success",
                }

            return result

        except Exception as e:
            # Catch-all for any unexpected errors
            return self.handle_error(e, "unknown", input_data, gcs_signed_url)

    def predict(self, input_data):
        """
        Run prediction with the model.
        Supports both single inputs and batch inputs.

        Args:
            input_data (dict): The input data to the model
                              Can be a single input or contain a "batch" key with list of inputs

        Returns:
            dict: The prediction results
        """
        if not self.model_ready:
            error = RuntimeError("Model is not initialized")
            return self.handle_error(error, "initialization", input_data)

        # Check if this is a batch request
        if isinstance(input_data, dict) and "batch" in input_data:
            return self._predict_batch(input_data["batch"])
        else:
            # Single prediction - extract GCS URL if present
            gcs_signed_url = (
                input_data.pop("gcs_signed_url", None)
                if isinstance(input_data, dict)
                else None
            )
            return self._predict_single(input_data, gcs_signed_url=gcs_signed_url)

    def _predict_batch(self, batch_items):
        """
        Run prediction for a batch of inputs.

        Args:
            batch_items (list): List of input items to process

        Returns:
            dict: Batch prediction results
        """
        batch_start_time = time.time()
        results = []

        for i, item in enumerate(batch_items):
            # Make a copy to avoid modifying the original
            item_copy = item.copy() if isinstance(item, dict) else item

            # Extract GCS signed URL if present in this batch item
            gcs_signed_url = (
                item_copy.pop("gcs_signed_url", None)
                if isinstance(item_copy, dict)
                else None
            )

            # Run prediction for this item
            item_result = self._predict_single(item_copy, gcs_signed_url=gcs_signed_url)

            # Add item index for tracking
            if isinstance(item_result, dict):
                item_result["batch_index"] = i
            else:
                item_result = {"prediction": item_result, "batch_index": i}

            results.append(item_result)

        # Calculate total batch processing time
        total_processing_time = time.time() - batch_start_time

        return {
            "status": "success",
            "batch_results": results,
            "batch_size": len(batch_items),
            "total_processing_time": total_processing_time,
            "successful_items": len(
                [r for r in results if r.get("status") == "success"]
            ),
            "failed_items": len([r for r in results if r.get("status") == "error"]),
        }

    def postprocess(self, output, gcs_signed_url=None):
        """
        Postprocess the model output and optionally upload to GCS.
        Override this in your subclass for custom postprocessing.

        Args:
            output: The raw model output
            gcs_signed_url (str, optional): GCS signed URL to upload results to

        Returns:
            dict: The processed results, including upload status if applicable
        """
        # Default implementation - format the output
        if isinstance(output, dict):
            result = output
        else:
            result = {"prediction": output}

        # Handle GCS upload if signed URL is provided
        if gcs_signed_url:
            try:
                # Check if output contains image data that should be uploaded as image
                if "prediction" in result and self._is_image_output(
                    result["prediction"]
                ):
                    upload_success = upload_image_to_signed_url(
                        gcs_signed_url, result["prediction"]
                    )
                elif self._is_image_output(output):
                    upload_success = upload_image_to_signed_url(gcs_signed_url, output)
                else:
                    upload_success = upload_to_signed_url(gcs_signed_url, result)

                result["gcs_upload"] = "success" if upload_success else "failed"
            except Exception as e:
                print(f"Error uploading to GCS: {str(e)}")
                result["gcs_upload"] = "failed"

        return result
