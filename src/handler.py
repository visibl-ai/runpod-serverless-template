import os
import json
import runpod
import requests
from src.model import AIModel

# Initialize the model
model = AIModel()

def upload_to_signed_url(signed_url, data):
    """
    Upload data to a Google Cloud Storage signed URL.
    
    Args:
        signed_url (str): The GCS signed URL to upload to
        data (dict): The data to upload
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        # Upload to the signed URL
        response = requests.put(
            signed_url,
            data=json_data,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }
        )
        
        # Check if the upload was successful
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error uploading to signed URL: {str(e)}")
        return False

def handler(event):
    """
    This is the main handler function that processes the incoming requests.
    
    Args:
        event (dict): Input event data, typically containing:
            - input (dict): The input data for the model
            - callback_url (str, optional): URL to send results to when processing is complete
            - gcs_signed_url (str, optional): Signed URL to upload results to GCS
            
    Returns:
        dict: The prediction results
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
        result = model.predict(input_data)

        # Create the response payload
        payload = {
            "status": "success",
            "output": result,
            "job_id": event.get("id", "unknown")
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
            try:
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
                    "job_id": event.get("id", "unknown"),
                    "gcs_upload": payload.get("gcs_upload")
                }
            except Exception as callback_error:
                # Log the error but still return the result
                print(f"Error sending result to callback URL: {str(callback_error)}")
                return {
                    "status": "success",
                    "output": result,
                    "callback_error": str(callback_error),
                    "gcs_upload": payload.get("gcs_upload")
                }
        
        # If no callback URL, return the result directly
        return payload
    except Exception as e:
        # Log the error
        print(f"Error processing request: {str(e)}")
        
        # Prepare error payload
        error_payload = {
            "status": "error", 
            "error": str(e),
            "job_id": event.get("id", "unknown")
        }
        
        # If a GCS signed URL is provided, try to upload the error
        if event.get("gcs_signed_url"):
            try:
                upload_to_signed_url(event.get("gcs_signed_url"), error_payload)
            except Exception as gcs_error:
                print(f"Error uploading error to signed URL: {str(gcs_error)}")
        
        # If a callback URL is provided, send the error
        if callback_url:
            try:
                # Send the error to the callback URL
                requests.post(
                    callback_url,
                    json=error_payload,
                    headers={"Content-Type": "application/json"}
                )
            except Exception as callback_error:
                print(f"Error sending error to callback URL: {str(callback_error)}")
        
        # Return error response
        return error_payload 