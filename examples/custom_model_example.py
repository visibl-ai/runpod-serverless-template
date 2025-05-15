"""
Example of how to implement a custom model using the runpod-serverless-template package.

This file demonstrates:
1. How to create a custom model by inheriting from BaseModel
2. How to implement the required methods
3. How to use the model with the RunPod serverless handler
"""

import time

import torch
import torch.nn as nn

from runpod_serverless_template import BaseHandler, BaseModel


class MyCustomModel(BaseModel):
    """
    Custom model implementation for a specific AI task.

    This example shows a PyTorch model, but you can use any ML framework
    like TensorFlow, JAX, ONNX, etc.
    """

    def _initialize_model(self):
        """
        Initialize the model with custom logic.

        This method is called once when the model is first loaded.
        Load your weights, initialize your model architecture, etc. here.
        """
        print("Loading MyCustomModel...")

        # Example: Load a PyTorch model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Define a simple neural network for demonstration
        self.model = nn.Sequential(nn.Linear(10, 64), nn.ReLU(), nn.Linear(64, 1)).to(
            self.device
        )

        # Example: Load weights from a file
        # self.model.load_state_dict(torch.load("model_weights.pth"))

        print(f"Model loaded on {self.device}")

    def preprocess(self, input_data):
        """
        Custom preprocessing logic.

        This method takes the raw input from the API request and
        prepares it for the model.
        """
        # Handle different input types
        if "features" in input_data:
            # For vector inputs (e.g., feature vectors)
            features = input_data["features"]
            return torch.tensor(features, dtype=torch.float32).to(self.device)
        elif "text" in input_data:
            # Example: Process text input - this would typically involve tokenization
            # For this example, we'll just return the text for the parent class to handle
            return super().preprocess(input_data)
        elif "image_url" in input_data:
            # For image inputs, use the parent class implementation
            # which downloads and processes the image
            return super().preprocess(input_data)
        else:
            # Fall back to base class for other input types
            return super().preprocess(input_data)

    def _run_inference(self, processed_input):
        """
        Run inference with the model.

        This method is called after preprocessing and should return the raw model output.
        """
        # Different handling based on input type
        if isinstance(processed_input, torch.Tensor):
            # For tensor inputs (feature vectors)
            with torch.no_grad():
                output = self.model(processed_input)
                return output.cpu().numpy().tolist()
        elif isinstance(processed_input, str):
            # Example text processing
            return {
                "text_analysis": f"Analyzed: {processed_input}",
                "sentiment": 0.8,
                "length": len(processed_input),
            }
        elif isinstance(processed_input, dict):
            # Generic input
            return {
                "result": "Generic processing completed",
                "input_type": "dictionary",
            }
        else:
            # Generic fallback
            return {
                "result": "Processed with default handler",
                "input_type": str(type(processed_input)),
            }

    def postprocess(self, output):
        """
        Format the model output for the API response.

        This method takes the raw model output and formats it into the final
        API response structure.
        """
        # Add metadata to enrich the response
        if isinstance(output, dict):
            output.update(
                {
                    "model_name": "MyCustomModel",
                    "version": "1.0.0",
                    "framework": "PyTorch",
                    "timestamp": time.time(),
                }
            )
        else:
            # If output is not a dict, wrap it
            output = {
                "prediction": output,
                "model_name": "MyCustomModel",
                "version": "1.0.0",
                "framework": "PyTorch",
                "timestamp": time.time(),
            }

        return output


# Example of how to use this model in a handler.py file:
if __name__ == "__main__":
    # 1. Create an instance of your custom model
    model = MyCustomModel()

    # 2. Create a handler with your model
    handler = BaseHandler(model)

    # 3. Start the serverless function
    import runpod

    runpod.serverless.start({"handler": handler})

    # Note: This is normally in handler.py, not in the model file.
    # This is just for demonstration purposes.
