"""
Examples of what should go in the postprocess method.

The postprocess method is where you:
1. Format raw model outputs into user-friendly results
2. Handle GCS uploads (images vs JSON)
3. Add metadata and confidence scores
4. Convert outputs to appropriate formats
5. Apply any final transformations
"""

import json
import time

import numpy as np
from PIL import Image

from runpod_serverless_template import BaseModel


class TextAnalysisModel(BaseModel):
    """Example: Text analysis model with rich postprocessing."""

    def _initialize_model(self):
        print("Loading text analysis model...")

    def _run_inference(self, processed_input):
        # Simulate model output
        return {
            "logits": [0.1, 0.8, 0.05, 0.05],  # Raw probabilities
            "embeddings": np.random.rand(512).tolist(),
            "attention_weights": np.random.rand(20, 20).tolist(),
        }

    def postprocess(self, output, gcs_signed_url=None):
        """
        Postprocess text analysis results.
        """
        # Extract raw outputs
        logits = output["logits"]
        embeddings = output["embeddings"]

        # Convert logits to human-readable predictions
        sentiment_labels = ["negative", "positive", "neutral", "mixed"]
        confidence_scores = self._softmax(logits)
        predicted_class = sentiment_labels[np.argmax(confidence_scores)]
        max_confidence = float(np.max(confidence_scores))

        # Create structured result
        result = {
            "sentiment": predicted_class,
            "confidence": max_confidence,
            "all_scores": {
                label: float(score)
                for label, score in zip(sentiment_labels, confidence_scores)
            },
            "embedding_preview": embeddings[:10],  # First 10 dimensions only
            "model_info": {
                "version": "1.2.0",
                "architecture": "transformer-based",
                "last_updated": "2024-01-15",
            },
        }

        # Handle GCS upload - the parent class will automatically determine
        # whether to upload as JSON (since this is structured data)
        return super().postprocess(result, gcs_signed_url)

    def _softmax(self, logits):
        """Apply softmax to convert logits to probabilities."""
        exp_logits = np.exp(np.array(logits) - np.max(logits))
        return exp_logits / np.sum(exp_logits)


class ImageGenerationModel(BaseModel):
    """Example: Image generation model with image output processing."""

    def _initialize_model(self):
        print("Loading image generation model...")

    def _run_inference(self, processed_input):
        # Simulate generating an image
        height, width = 512, 512
        # Create a sample image (in practice this would be your model output)
        image_array = np.random.rand(height, width, 3)
        return {
            "generated_image": image_array,
            "seed": 12345,
            "steps": 50,
            "guidance_scale": 7.5,
        }

    def postprocess(self, output, gcs_signed_url=None):
        """
        Postprocess image generation results.
        """
        # Extract the generated image
        image_array = output["generated_image"]

        # Convert to proper image format
        if image_array.max() <= 1.0:
            # Convert from [0,1] to [0,255]
            image_array = (image_array * 255).astype(np.uint8)

        # Create metadata
        result = {
            "prediction": image_array,  # This will be uploaded as an image
            "metadata": {
                "seed": output["seed"],
                "steps": output["steps"],
                "guidance_scale": output["guidance_scale"],
                "image_size": f"{image_array.shape[1]}x{image_array.shape[0]}",
                "channels": image_array.shape[2] if len(image_array.shape) > 2 else 1,
            },
            "generation_info": {
                "model_type": "diffusion",
                "format": "RGB",
                "quality_score": 0.85,  # Simulated quality assessment
            },
        }

        # Handle GCS upload - the parent class will detect this is an image
        # and upload it as PNG/JPEG instead of JSON
        return super().postprocess(result, gcs_signed_url)


class ObjectDetectionModel(BaseModel):
    """Example: Object detection with complex output processing."""

    def _initialize_model(self):
        print("Loading object detection model...")

    def _run_inference(self, processed_input):
        # Simulate object detection output
        return {
            "boxes": [[10, 20, 100, 150], [200, 50, 350, 200]],
            "scores": [0.95, 0.87],
            "class_ids": [1, 3],
            "raw_features": np.random.rand(1000).tolist(),
        }

    def postprocess(self, output, gcs_signed_url=None):
        """
        Postprocess object detection results.
        """
        boxes = output["boxes"]
        scores = output["scores"]
        class_ids = output["class_ids"]

        # Class mapping
        class_names = {0: "background", 1: "person", 2: "car", 3: "dog", 4: "cat"}

        # Filter low-confidence detections
        confidence_threshold = 0.5
        filtered_detections = []

        for box, score, class_id in zip(boxes, scores, class_ids):
            if score >= confidence_threshold:
                detection = {
                    "bbox": {
                        "x": box[0],
                        "y": box[1],
                        "width": box[2] - box[0],
                        "height": box[3] - box[1],
                    },
                    "confidence": float(score),
                    "class_name": class_names.get(class_id, f"unknown_{class_id}"),
                    "class_id": int(class_id),
                }
                filtered_detections.append(detection)

        # Create comprehensive result
        result = {
            "detections": filtered_detections,
            "summary": {
                "total_objects": len(filtered_detections),
                "confidence_threshold": confidence_threshold,
                "classes_detected": list(
                    set(d["class_name"] for d in filtered_detections)
                ),
            },
            "model_metadata": {
                "architecture": "YOLO-v8",
                "input_size": "640x640",
                "num_classes": len(class_names),
            },
        }

        # This will be uploaded as JSON since it's structured data
        return super().postprocess(result, gcs_signed_url)


class MultiModalModel(BaseModel):
    """Example: Model that can output either images or text based on input."""

    def _initialize_model(self):
        print("Loading multi-modal model...")

    def _run_inference(self, processed_input):
        if (
            isinstance(processed_input, str)
            and "generate image" in processed_input.lower()
        ):
            # Generate an image
            return {
                "type": "image",
                "data": np.random.rand(256, 256, 3),
                "prompt": processed_input,
            }
        else:
            # Generate text
            return {
                "type": "text",
                "data": f"Analysis of: {processed_input}",
                "confidence": 0.92,
            }

    def postprocess(self, output, gcs_signed_url=None):
        """
        Postprocess multi-modal outputs - different handling for different types.
        """
        output_type = output["type"]

        if output_type == "image":
            # Handle image output
            image_data = output["data"]
            if image_data.max() <= 1.0:
                image_data = (image_data * 255).astype(np.uint8)

            result = {
                "prediction": image_data,  # Will be uploaded as image
                "type": "image_generation",
                "prompt": output["prompt"],
                "dimensions": f"{image_data.shape[1]}x{image_data.shape[0]}",
            }
        else:
            # Handle text output
            result = {
                "prediction": output["data"],  # Will be uploaded as JSON
                "type": "text_analysis",
                "confidence": output["confidence"],
                "word_count": len(output["data"].split()),
            }

        # Add common metadata
        result["processing_timestamp"] = time.time()
        result["model_version"] = "multimodal-v2.1"

        return super().postprocess(result, gcs_signed_url)


# Example of what NOT to do in postprocess
class BadExampleModel(BaseModel):
    """Example showing what NOT to do in postprocess."""

    def _initialize_model(self):
        pass

    def _run_inference(self, processed_input):
        return "some result"

    def postprocess(self, output, gcs_signed_url=None):
        """
        BAD EXAMPLE - Don't do these things:
        """
        # ❌ DON'T: Do heavy computation here (should be in _run_inference)
        # time.sleep(5)  # Heavy processing

        # ❌ DON'T: Ignore the gcs_signed_url parameter
        # return output  # Missing GCS upload handling

        # ❌ DON'T: Return raw model outputs without formatting
        # return output  # No metadata, no user-friendly format

        # ❌ DON'T: Manually handle GCS uploads (parent class does this)
        # if gcs_signed_url:
        #     upload_to_signed_url(gcs_signed_url, output)

        # ✅ DO: Format output and call parent class
        result = {"prediction": output, "formatted": True, "user_friendly": True}
        return super().postprocess(result, gcs_signed_url)


def main():
    """Test the different postprocess examples."""

    print("=== Text Analysis Example ===")
    text_model = TextAnalysisModel()
    text_result = text_model.predict(
        {
            "text": "I love this product!",
            "gcs_signed_url": "https://storage.googleapis.com/bucket/sentiment.json",
        }
    )
    print(
        f"Text result: {text_result['sentiment']} (confidence: {text_result['confidence']:.2f})"
    )
    print(f"GCS upload: {text_result.get('gcs_upload', 'no upload')}")

    print("\n=== Image Generation Example ===")
    image_model = ImageGenerationModel()
    image_result = image_model.predict(
        {
            "text": "generate a beautiful landscape",
            "gcs_signed_url": "https://storage.googleapis.com/bucket/generated.png",
        }
    )
    print(f"Image shape: {image_result['prediction'].shape}")
    print(f"GCS upload: {image_result.get('gcs_upload', 'no upload')}")

    print("\n=== Object Detection Example ===")
    detection_model = ObjectDetectionModel()
    detection_result = detection_model.predict(
        {
            "image_url": "https://example.com/photo.jpg",
            "gcs_signed_url": "https://storage.googleapis.com/bucket/detections.json",
        }
    )
    print(f"Objects detected: {detection_result['summary']['total_objects']}")
    print(f"Classes: {detection_result['summary']['classes_detected']}")


if __name__ == "__main__":
    main()


"""
Summary: What should go in postprocess():

1. ✅ Format raw model outputs into user-friendly results
2. ✅ Add metadata, confidence scores, model info
3. ✅ Convert data types (normalize images, format text)
4. ✅ Filter or threshold results (remove low-confidence predictions)
5. ✅ Structure outputs consistently
6. ✅ Call super().postprocess() to handle GCS uploads
7. ✅ Add timestamps, version info, etc.

What should NOT go in postprocess():
1. ❌ Heavy computation (put in _run_inference instead)
2. ❌ Input preprocessing (put in preprocess instead)
3. ❌ Manual GCS upload handling (parent class handles this)
4. ❌ Model loading/initialization (put in _initialize_model)
5. ❌ Raw outputs without formatting
"""
