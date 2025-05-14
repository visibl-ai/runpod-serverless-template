# RunPod Serverless AI Endpoint Template

This template provides a starting point for creating AI model serverless endpoints on RunPod.io.

## Project Structure

```
.
├── Dockerfile                 # Defines the container that will run your code
├── handler.py                 # Main entry point for the serverless function
├── pyproject.toml             # Poetry configuration for dependency management
├── runpod_endpoint/           # Python package directory
│   ├── __init__.py            # Package initialization
│   ├── handler.py             # Implementation of the handler function
│   └── model.py               # AI model implementation
└── README.md                  # This file
```

## Getting Started

1. **Customize the Model**: 
   - Update the `runpod_endpoint/model.py` file with your AI model implementation
   - Replace the placeholder code in the `AIModel` class with your actual model

2. **Update Dependencies**:
   - This project uses Poetry for dependency management
   - Add any additional dependencies your model needs to `pyproject.toml`
   - Run `poetry add package-name` to add new dependencies

3. **Test Locally** (optional):
   - Install dependencies: `poetry install`
   - Run the test script: `poetry run python test_local.py`

4. **Deploy**:
   - Choose either GitHub-based or Docker-based deployment (see deployment options below)
   - Create a new serverless endpoint on RunPod

## Using Poetry

This template uses [Poetry](https://python-poetry.org/) for dependency management instead of requirements.txt. Poetry makes it easier to manage dependencies with a cleaner, more predictable build process.

### Key Poetry Commands

```bash
# Install dependencies
poetry install

# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Run a script
poetry run python test_local.py
```

## API Format

### Input Format

```json
{
  "input": {
    // Your model-specific input parameters
    "image_url": "https://example.com/image.jpg",
    // or
    "text": "Example text input"
  },
  "callback_url": "https://your-server.com/webhook" // Optional: URL to receive results when processing completes
}
```

### Output Format

When not using a callback URL:
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

When using a callback URL, the response will be posted to your callback URL:
```json
{
  "status": "success",
  "output": {
    "prediction": "result",
    "confidence": 0.95,
    "processing_time": 0.5
  },
  "job_id": "job-uuid"
}
```

## Callback URL Functionality

The template supports asynchronous processing by providing a callback URL in your request. When the model finishes processing, the results will be sent to the specified URL as a POST request with the following characteristics:

- The request is made with a Content-Type of `application/json`
- The body includes the output result, status, and job ID
- Both successful results and errors are sent to the callback URL

This is particularly useful for long-running inference tasks where you don't want to keep an HTTP connection open.

## Deployment to RunPod

### Option 1: GitHub-based Deployment

1. **Push your code to a GitHub repository**

2. **Create a new Serverless Template on RunPod**:
   - Go to https://www.runpod.io/console/serverless/user/templates
   - Click "Connect GitHub Repo"
   - Select your repository
   - Configure the build settings:
     - Container Name: Choose a name for your container
     - Build Command: `docker build -t {IMAGE_NAME} .`
   - Save the template configuration

3. **Create a Serverless Endpoint**:
   - Go to https://www.runpod.io/console/serverless
   - Click "New Endpoint"
   - Select your GitHub-connected template
   - Configure the resources (GPU/Memory)
   - Deploy

### Option 2: Docker-based Deployment

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

### Synchronous Request (No Callback)

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

### Asynchronous Request (With Callback)

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
    },
    "callback_url": "https://your-server.com/webhook"
}

# The response here will just acknowledge the job was started
response = requests.post(endpoint_url, headers=headers, json=payload)
print(response.json())

# The actual results will be sent to your callback URL when processing completes
```

## Resources

- [RunPod Serverless Documentation](https://docs.runpod.io/docs/serverless-overview)
- [RunPod Python SDK](https://github.com/runpod/runpod-python)
- [RunPod GitHub Integration](https://docs.runpod.io/docs/github-integration)
- [Poetry Documentation](https://python-poetry.org/docs/) 