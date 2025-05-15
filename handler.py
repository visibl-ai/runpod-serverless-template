#!/usr/bin/env python

import runpod

from examples.custom_model_example import MyCustomModel

# Import the base handler and example model
from runpod_serverless_template import BaseHandler

# This is the main entry point for the serverless function
# To use this template, create a custom model class inheriting from BaseModel
# and update the imports and initialization below.


# Initialize the model
model = MyCustomModel()

# Create a handler with your model
handler = BaseHandler(model)

# Start the serverless function
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
