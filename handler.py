#!/usr/bin/env python

import runpod
from src.handler import handler

# Start the serverless function
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler}) 