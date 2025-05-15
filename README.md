# RunPod Serverless AI Endpoint Template

This template provides a starting point for creating AI model serverless endpoints on RunPod.io.

## Project Structure

```
.
├── Dockerfile                 # Defines the container that will run your code
├── .dockerignore              # Specifies files to exclude from Docker builds
├── handler.py                 # Main entry point for the serverless function
├── pyproject.toml             # Poetry configuration for dependency management
├── src/                       # Python package directory
│   ├── __init__.py            # Package initialization
│   ├── handler.py             # Implementation of the handler function
│   └── model.py               # AI model implementation
├── scripts/                   # Test scripts directory (excluded from Docker build)
│   ├── test_local.py          # Script for local testing (before deployment)
│   ├── test_with_gcs.py       # Script for testing with GCS signed URLs
│   ├── test_sync_endpoint.py  # Script for testing deployed endpoint (synchronous)
│   ├── test_async_endpoint.py # Script for testing deployed endpoint (asynchronous)
│   └── input_examples.json    # Example JSON input for testing
├── config.env.example         # Example environment configuration file for testing
└── README.md                  # This file
```

## Getting Started

1. **Customize the Model**:
   - Update the `src/model.py` file with your AI model implementation
   - Replace the placeholder code in the `AIModel` class with your actual model

2. **Update Dependencies**:
   - This project uses Poetry for dependency management
   - Add any additional dependencies your model needs to `pyproject.toml`
   - Run `poetry add package-name` to add new dependencies

3. **Test Locally** (optional):
   - Install dependencies including development tools: `poetry install`
   - Run the test script: `poetry run python scripts/test_local.py`

4. **Deploy**:
   - Choose either GitHub-based or Docker-based deployment (see deployment options below)
   - Create a new serverless endpoint on RunPod

## Using Poetry

This template uses [Poetry](https://python-poetry.org/) for dependency management instead of requirements.txt. Poetry makes it easier to manage dependencies with a cleaner, more predictable build process.

### Dependency Management

The project separates runtime dependencies from development dependencies:

- **Runtime dependencies**: Required packages for the endpoint to function in production
- **Development dependencies**: Tools only needed for local development and testing

This separation ensures that Docker builds are optimized and don't include unnecessary packages.

### Key Poetry Commands

```bash
# Install all dependencies (including dev)
poetry install

# Install only runtime dependencies (like in Docker)
poetry install --without dev

# Add a runtime dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Run a script with Poetry environment
poetry run python scripts/test_local.py
```

## Environment Setup for Testing

The test scripts support using environment variables for your RunPod API credentials and test inputs. This makes it easier to run tests without typing the same parameters repeatedly.

### Setting Up Environment Variables

1. **Create a `.env` file** by copying the example:
   ```bash
   cp config.env.example .env
   ```

2. **Edit the `.env` file** with your actual values:
   ```
   RUNPOD_API_KEY=your_api_key_here
   RUNPOD_ENDPOINT_ID=your_endpoint_id_here
   DEFAULT_TEST_IMAGE_URL=https://example.com/your_test_image.jpg
   DEFAULT_TEST_TEXT="Your test prompt here"
   ```

3. **Run tests without specifying credentials**:
   ```bash
   # The API key and endpoint ID are now loaded from .env
   python scripts/test_sync_endpoint.py
   ```

### Environment Variables Used

| Variable | Description |
|----------|-------------|
| `RUNPOD_API_KEY` | Your RunPod API key |
| `RUNPOD_ENDPOINT_ID` | ID of your serverless endpoint |
| `DEFAULT_TEST_TEXT` | Default text input for testing |
| `DEFAULT_TEST_IMAGE_URL` | Default image URL for testing |

## Docker Optimization

The template includes a `.dockerignore` file that excludes development and testing files from the Docker build context. This ensures:

- Smaller Docker images
- Faster build times
- Enhanced security by excluding sensitive local configs
- Only production-necessary code is included in the container

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
  "callback_url": "https://your-server.com/webhook", // Optional: URL to receive results when processing completes
  "gcs_signed_url": "https://storage.googleapis.com/your-bucket/results.json?X-Goog-Signature=..." // Optional: GCS URL to upload results
}
```

### Output Format

When not using a callback URL or signed URL:
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

When using a GCS signed URL, the results will be uploaded to the provided URL, and the response will include information about the upload:
```json
{
  "status": "success",
  "output": {
    "prediction": "result",
    "confidence": 0.95,
    "processing_time": 0.5
  },
  "gcs_upload": "success"
}
```

## Result Delivery Options

The template provides three ways to receive results from your endpoint:

### 1. Synchronous (Direct Response)

The simplest approach is to wait for the response directly in the same HTTP request. This works well for quick inference tasks but can time out for longer-running tasks.

### 2. Asynchronous (Callback URL)

For longer-running tasks, you can provide a `callback_url` in your request. When the model finishes processing, the results will be sent to the specified URL as a POST request with:
- Content-Type: `application/json`
- Body includes the output result, status, and job ID
- Both successful results and errors are sent to the callback URL

### 3. Google Cloud Storage (Signed URL)

For storing large results or when you need more flexibility in result handling, you can provide a `gcs_signed_url` parameter. The endpoint will:
- Upload results directly to the provided GCS bucket location
- Use PUT request with Content-Type: `application/json`
- Include upload status information in the response

## Testing Your Endpoint

This template includes scripts to help you test your endpoint:

### 1. Local Testing (Before Deployment)

```bash
# Test locally before deployment
poetry run python scripts/test_local.py

# Test with a specific signed URL
poetry run python scripts/test_local.py --signed-url "https://storage.googleapis.com/your-bucket/object?signature=..."
```

### 2. Testing Deployed Endpoint (Synchronous)

```bash
# Test synchronous requests to the deployed endpoint (using environment variables)
python scripts/test_sync_endpoint.py

# Or with explicit parameters
python scripts/test_sync_endpoint.py --endpoint-id YOUR_ENDPOINT_ID --api-key YOUR_API_KEY --text "Your test text"

# Or with an image URL
python scripts/test_sync_endpoint.py --image-url "https://example.com/image.jpg"

# Or with a JSON file for complex inputs
python scripts/test_sync_endpoint.py --json-input scripts/input_examples.json
```

### 3. Testing Deployed Endpoint with GCS Signed URL

```bash
# Test with a GCS signed URL
python scripts/test_with_gcs.py --endpoint-id YOUR_ENDPOINT_ID --api-key YOUR_API_KEY --signed-url "YOUR_SIGNED_URL" --text "Your test text"
```

### 4. Testing Deployed Endpoint (Asynchronous with Callbacks)

For async testing with callbacks, you'll need a publicly accessible URL that can receive the results:

```bash
# Use a service like webhook.site or RequestBin to create a temporary URL for testing

# Test asynchronous requests with callbacks
python scripts/test_async_endpoint.py --callback-url "YOUR_WEBHOOK_URL" --text "Your test text"
```

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
