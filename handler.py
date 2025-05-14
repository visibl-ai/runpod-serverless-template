import os
import runpod
from model import AIModel

# Initialize the model
model = AIModel()

def handler(event):
    """
    This is the main handler function that processes the incoming requests.
    
    Args:
        event (dict): Input event data, typically containing:
            - input (dict): The input data for the model
            
    Returns:
        dict: The prediction results
    """
    try:
        # Extract input data
        input_data = event.get("input", {})
        
        # Validate input data
        if not input_data:
            return {"error": "No input data provided"}
        
        # Process the input with the model
        result = model.predict(input_data)
        
        # Return the results
        return {
            "status": "success",
            "output": result
        }
    except Exception as e:
        # Log the error
        print(f"Error processing request: {str(e)}")
        
        # Return error response
        return {
            "status": "error", 
            "error": str(e)
        }

# Start the serverless function
runpod.serverless.start({"handler": handler}) 