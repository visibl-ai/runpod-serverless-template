import os
import runpod
import requests
from runpod_endpoint.model import AIModel

# Initialize the model
model = AIModel()

def handler(event):
    """
    This is the main handler function that processes the incoming requests.
    
    Args:
        event (dict): Input event data, typically containing:
            - input (dict): The input data for the model
            - callback_url (str, optional): URL to send results to when processing is complete
            
    Returns:
        dict: The prediction results
    """
    try:
        # Extract input data
        input_data = event.get("input", {})
        callback_url = event.get("callback_url")
        
        # Validate input data
        if not input_data:
            return {"error": "No input data provided"}
        
        # Process the input with the model
        result = model.predict(input_data)
        
        # If a callback URL is provided, send the result
        if callback_url:
            try:
                # Create the response payload
                payload = {
                    "status": "success",
                    "output": result,
                    "job_id": event.get("id", "unknown")
                }
                
                # Send the result to the callback URL
                response = requests.post(
                    callback_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Check if the callback was successful
                response.raise_for_status()
                
                # Return a message indicating the result was sent
                return {
                    "status": "success",
                    "message": f"Result sent to callback URL: {callback_url}",
                    "job_id": event.get("id", "unknown")
                }
            except Exception as callback_error:
                # Log the error but still return the result
                print(f"Error sending result to callback URL: {str(callback_error)}")
                return {
                    "status": "success",
                    "output": result,
                    "callback_error": str(callback_error)
                }
        
        # If no callback URL, return the result directly
        return {
            "status": "success",
            "output": result
        }
    except Exception as e:
        # Log the error
        print(f"Error processing request: {str(e)}")
        
        # If a callback URL is provided, send the error
        if callback_url:
            try:
                # Create the error payload
                payload = {
                    "status": "error",
                    "error": str(e),
                    "job_id": event.get("id", "unknown")
                }
                
                # Send the error to the callback URL
                requests.post(
                    callback_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
            except Exception as callback_error:
                print(f"Error sending error to callback URL: {str(callback_error)}")
        
        # Return error response
        return {
            "status": "error", 
            "error": str(e)
        } 