import os
import time
import numpy as np
from PIL import Image
import requests

class AIModel:
    """
    Sample AI model class that can be replaced with your actual model implementation.
    """
    
    def __init__(self):
        """
        Initialize the model, load weights, etc.
        This is called when the serverless container starts.
        """
        print("Initializing AI model...")
        
        # Add your model initialization code here
        # For example:
        # self.model = load_model_from_path("path/to/model")
        
        # Simulate model loading time
        time.sleep(2)
        
        print("Model initialized successfully")
        self.model_ready = True
    
    def preprocess(self, input_data):
        """
        Preprocess the input data before feeding it to the model.
        
        Args:
            input_data (dict): The raw input data
            
        Returns:
            The preprocessed data ready for model prediction
        """
        # Example preprocessing for different input types
        if "image_url" in input_data:
            # Download and process image
            img_url = input_data["image_url"]
            try:
                response = requests.get(img_url, stream=True)
                response.raise_for_status()
                img = Image.open(response.raw)
                # Resize, normalize, etc.
                img = img.resize((224, 224))
                img_array = np.array(img) / 255.0
                return img_array
            except Exception as e:
                raise ValueError(f"Failed to process image: {str(e)}")
                
        elif "text" in input_data:
            # Process text input
            text = input_data["text"]
            # Add your text preprocessing here
            return text
            
        else:
            # Handle other types of inputs
            return input_data
    
    def predict(self, input_data):
        """
        Run prediction with the model.
        
        Args:
            input_data (dict): The input data to the model
            
        Returns:
            The prediction results
        """
        if not self.model_ready:
            raise RuntimeError("Model is not initialized")
        
        # Preprocess the input
        processed_input = self.preprocess(input_data)
        
        # Run the model
        # Replace this with your actual model inference code
        # output = self.model.predict(processed_input)
        
        # Simulated model output for demonstration
        output = {
            "prediction": "sample_prediction",
            "confidence": 0.95,
            "processing_time": 0.5
        }
        
        return output
    
    def postprocess(self, output):
        """
        Postprocess the model output.
        
        Args:
            output: The raw model output
            
        Returns:
            The processed results
        """
        # Add any postprocessing steps here
        return output 