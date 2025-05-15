"""
Base model class for AI models running on RunPod serverless endpoints.
"""

import time
from abc import ABC, abstractmethod

import numpy as np
import requests
from PIL import Image


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

    def predict(self, input_data):
        """
        Run prediction with the model.

        Args:
            input_data (dict): The input data to the model

        Returns:
            dict: The prediction results
        """
        if not self.model_ready:
            raise RuntimeError("Model is not initialized")

        # Record the start time for latency measurement
        start_time = time.time()

        # Preprocess the input
        processed_input = self.preprocess(input_data)

        # Run the model
        raw_output = self._run_inference(processed_input)

        # Postprocess the output
        result = self.postprocess(raw_output)

        # Calculate processing time
        processing_time = time.time() - start_time

        # Add metadata to the result
        if isinstance(result, dict):
            result["processing_time"] = processing_time
        else:
            # If result is not a dict, wrap it in one
            result = {"prediction": result, "processing_time": processing_time}

        return result

    def postprocess(self, output):
        """
        Postprocess the model output.
        Override this in your subclass for custom postprocessing.

        Args:
            output: The raw model output

        Returns:
            The processed results
        """
        # Default implementation returns output as is
        return output
