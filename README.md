# RunPod Serverless AI Endpoint Template

This template provides a starting point for creating AI model serverless endpoints on RunPod.io.

## Project Structure

```
.
├── Dockerfile         # Defines the container that will run your code
├── handler.py         # The main serverless handler that processes requests
├── model.py           # Model implementation
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Getting Started

1. **Customize the Model**: 
   - Update the `model.py` file with your AI model implementation
   - Replace the placeholder code in the `AIModel` class with your actual model

2. **Update Requirements**:
   - Add any additional dependencies your model needs to `requirements.txt`

3. **Test Locally** (optional):
   - Create a test script to validate your handler locally before deploying

4. **Build and Deploy**:
   - Build your Docker image
   - Push to your container registry (Docker Hub, etc.)
   - Create a new serverless endpoint on RunPod using your image

## API Format

### Input Format

```json
{
  "input": {
    // Your model-specific input parameters
    "image_url": "https://example.com/image.jpg",
    // or
    "text": "Example text input"
  }
}
```

### Output Format

```json
{
  "status": "success",
  "output": {
    "prediction": "result",
    "confidence": 0.95,
    "processing_time": 0.5
  }
}
```

## Deployment to RunPod

1. **Build the Docker image**:
   ```bash
   docker build -t your-dockerhub-username/runpod-serverless-template:latest .
   ```

2. **Push to Docker Hub**:
   ```bash
   docker push your-dockerhub-username/runpod-serverless-template:latest
   ```

3. **Create a Serverless Endpoint on RunPod**:
   - Go to https://www.runpod.io/console/serverless
   - Click "New Endpoint"
   - Select your Docker image
   - Configure the resources (GPU/Memory)
   - Deploy

## Example Usage

```python
import requests

endpoint_url = "https://api.runpod.ai/v2/your-endpoint-id/run"
api_key = "your-api-key"

headers = {
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "input": {
        "image_url": "https://example.com/image.jpg"
    }
}

response = requests.post(endpoint_url, headers=headers, json=payload)
print(response.json())
```

## Resources

- [RunPod Serverless Documentation](https://docs.runpod.io/docs/serverless-overview)
- [RunPod Python SDK](https://github.com/runpod/runpod-python) 