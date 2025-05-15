# RunPod Serverless Template Package

This package provides a template for creating AI model serverless endpoints on RunPod.io. It can be used as a standalone template or imported into other projects as a dependency.

## Features

- **Base Classes**: Provides base classes for models and handlers that you can extend
- **Result Delivery**: Supports synchronous responses, callbacks, and GCS signed URL uploads
- **Error Handling**: Built-in error handling and reporting
- **Example Code**: Includes example implementations to get started quickly

## Project Structure

```
.
├── Dockerfile                 # Defines the container that will run your code
├── .dockerignore              # Specifies files to exclude from Docker builds
├── handler.py                 # Main entry point for the serverless function
├── pyproject.toml             # Poetry configuration for dependency management
├── runpod_serverless_template/# Core template package
│   ├── __init__.py            # Package initialization
│   ├── core/                  # Core functionality
│   │   ├── __init__.py        # Core module initialization
│   │   ├── handler.py         # Base handler class
│   │   └── model.py           # Base model class
│   └── utils/                 # Utility functions
│       ├── __init__.py        # Utility module initialization
│       └── gcs.py             # Google Cloud Storage utilities
├── examples/                  # Example implementations
│   └── custom_model_example.py# Example of custom model implementation
├── scripts/                   # Test scripts directory
│   ├── test_local.py          # Script for local testing
│   ├── test_with_gcs.py       # Script for testing with GCS signed URLs
│   ├── test_sync_endpoint.py  # Script for testing deployed endpoint (synchronous)
│   ├── test_async_endpoint.py # Script for testing deployed endpoint (asynchronous)
│   └── input_examples.json    # Example JSON input for testing
├── config.env.example         # Example environment configuration file for testing
└── README.md                  # This file
```

## Using as a Template for a New Project

1. **Clone this repository**:
   ```bash
   git clone https://github.com/yourusername/runpod-serverless-template.git my-runpod-project
   cd my-runpod-project
   ```

2. **Create Your Model Implementation**:
   - Create a new file (e.g., `mymodel.py`) with your custom model implementation
   - Make sure your model class inherits from `BaseModel`
   - Implement the required methods: `_initialize_model` and `_run_inference`
   - See the example in `examples/custom_model_example.py` for guidance

3. **Update the Handler**:
   - Modify `handler.py` to import and use your custom model

4. **Update Dependencies**:
   - Add any additional dependencies your model needs to `pyproject.toml`
   - Run `poetry add package-name` to add new dependencies

5. **Test Locally**:
   - Install dependencies: `poetry install`
   - Run the test script: `poetry run python scripts/test_local.py`

6. **Deploy**:
   - Build the Docker image: `docker build -t yourusername/your-model:latest .`
   - Push to Docker Hub: `docker push yourusername/your-model:latest`
   - Create a new serverless endpoint on RunPod

## Using as a Package in Another Project

You can use this template as a package in your own project:

1. **Add as a dependency**:
   ```bash
   # Using poetry
   poetry add git+https://github.com/yourusername/runpod-serverless-template.git

   # Using pip
   pip install git+https://github.com/yourusername/runpod-serverless-template.git
   ```

2. **Create your custom model**:
   ```python
   from runpod_serverless_template import BaseModel

   class MyCustomModel(BaseModel):
       def _initialize_model(self):
           # Load your model here
           pass

       def _run_inference(self, processed_input):
           # Run inference with your model
           return {"prediction": "result"}
   ```

3. **Create a handler**:
   ```python
   import runpod
   from runpod_serverless_template import BaseHandler
   from my_package.model import MyCustomModel

   # Initialize the model
   model = MyCustomModel()

   # Create a handler with your model
   handler = BaseHandler(model)

   # Start the serverless function
   if __name__ == "__main__":
       runpod.serverless.start({"handler": handler})
   ```

See the `examples/custom_model_example.py` file for a complete example.

## Base Classes

### BaseModel

The `BaseModel` class provides a foundation for AI models with methods for preprocessing, inference, and postprocessing.

**Required Methods to Override**:

- `_initialize_model(self)`: Load your model weights and prepare for inference
- `_run_inference(self, processed_input)`: Run inference with your model

**Optional Methods to Override**:

- `preprocess(self, input_data)`: Customize input preprocessing
- `postprocess(self, output)`: Customize output formatting

### BaseHandler

The `BaseHandler` class handles all the RunPod serverless integration, including:

- Processing inputs from RunPod
- Calling your model
- Handling errors
- Delivering results via direct response, callback, or GCS signed URL

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
  "callback_url": "https://your-server.com/webhook", // Optional: URL to receive results
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

## Result Delivery Options

The template provides three ways to receive results from your endpoint:

### 1. Synchronous (Direct Response)

The simplest approach is to wait for the response directly in the same HTTP request.

### 2. Asynchronous (Callback URL)

For longer-running tasks, you can provide a `callback_url` in your request. When the model finishes processing, the results will be sent to the specified URL.

### 3. Google Cloud Storage (Signed URL)

For storing large results, you can provide a `gcs_signed_url` parameter. The endpoint will upload results directly to the provided GCS bucket location.

## Testing Your Endpoint

This template includes scripts to help you test your endpoint. See the `scripts/` directory for details.

## Deployment to RunPod

### GitHub-based Deployment

1. **Push your code to a GitHub repository**

2. **Create a new Serverless Template on RunPod**:
   - Go to https://www.runpod.io/console/serverless/user/templates
   - Click "Connect GitHub Repo"
   - Select your repository
   - Configure the build settings

### Docker-based Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t your-dockerhub-username/your-model:latest .
   ```

2. **Push to Docker Hub**:
   ```bash
   docker push your-dockerhub-username/your-model:latest
   ```

3. **Create a Serverless Endpoint on RunPod**:
   - Go to https://www.runpod.io/console/serverless
   - Click "New Endpoint"
   - Select your Docker image
   - Configure the resources (GPU/Memory)
   - Deploy

## Example Usage

See `examples/custom_model_example.py` for a detailed example of how to use this template in your project.

## Example Model

The template includes an example model implementation to help you get started:

### PyTorch Model Example

`examples/custom_model_example.py` demonstrates:
- Creating a PyTorch model
- Handling different input types (feature vectors, text, images)
- Implementing preprocessing and postprocessing
- Integrating with CUDA for GPU acceleration

You can use this example as a starting point for your own implementation.

## Resources

- [RunPod Serverless Documentation](https://docs.runpod.io/docs/serverless-overview)
- [RunPod Python SDK](https://github.com/runpod/runpod-python)
- [RunPod GitHub Integration](https://docs.runpod.io/docs/github-integration)
- [Poetry Documentation](https://python-poetry.org/docs/)
