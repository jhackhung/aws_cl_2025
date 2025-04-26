import logging
import boto3
import base64
import io
import json
from botocore.config import Config
from botocore.exceptions import ClientError
from PIL import Image
import os
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ImageError(Exception):
    "Custom exception for errors returned by Amazon Nova Canvas"

    def __init__(self, message):
        self.message = message


def generate_images(model_id, task_id, prompt, batch_count=1, height=1024, width=1024, cfg_scale=8.0, seed=0):
    """
    Generate multiple images using Amazon Nova Canvas model on demand.
    """
    logger.info(
        "Generating %d images with Amazon Nova Canvas model %s", batch_count, model_id)

    bedrock = boto3.client(
        service_name='bedrock-runtime',
        config=Config(read_timeout=300),
        region_name='us-east-1' 
    )

    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": batch_count,
            "height": height,
            "width": width,
            "cfgScale": cfg_scale,
            "seed": seed
        }
    })

    accept = "application/json"
    content_type = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())

    finish_reason = response_body.get("error")
    if finish_reason is not None:
        raise ImageError(f"Image generation error. Error is {finish_reason}")

    image_list = []
    for base64_image in response_body.get("images", []):
        base64_bytes = base64_image.encode('ascii')
        image_bytes = base64.b64decode(base64_bytes)
        image_list.append(image_bytes)

    logger.info(
        "Successfully generated %d images with Amazon Nova Canvas model %s",
        len(image_list), model_id)

    return image_list


def process_images(model_id, task_id, prompt, negative_prompt, base64_images, batch_count=1, height=1024, width=1024,  cfg_scale=8.0, seed=0, similarityStrength=0.7):
    """
    Process input images and optionally combine with a text prompt for image generation.
    """
    logger.info(
        "Processing %d input images with Amazon Nova Canvas model %s", len(base64_images), model_id)

    bedrock = boto3.client(
        service_name='bedrock-runtime',
        config=Config(read_timeout=300)
    )

    body = json.dumps({
        "taskType": "IMAGE_VARIATION",
        "imageVariationParams": {
            "text": prompt,
            "negativeText": negative_prompt,
            "images": base64_images,
            "similarityStrength": similarityStrength,  # Range: 0.2 to 1.0
        },
        "imageGenerationConfig": {
            "numberOfImages": batch_count,
            "height": height,
            "width": width,
            "cfgScale": cfg_scale,
        }
    })

    accept = "application/json"
    content_type = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())

    finish_reason = response_body.get("error")
    if finish_reason is not None:
        raise ImageError(f"Image processing error. Error is {finish_reason}")

    image_list = []
    for base64_image in response_body.get("images", []):
        base64_bytes = base64_image.encode('ascii')
        image_bytes = base64.b64decode(base64_bytes)
        image_list.append(image_bytes)

    logger.info(
        "Successfully processed %d images with Amazon Nova Canvas model %s",
        len(image_list), model_id)

    return image_list


def get_image_size(image_data):
    """
    Get the width and height of an image.
    Args:
        image_data: Either raw bytes or base64 string of an image.
    Returns:
        dict: A dictionary containing 'width' and 'height'.
    """
    try:
        # Handle both bytes and base64 string formats
        if isinstance(image_data, str):
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(image_data)
        else:
            # Already in bytes format
            image_bytes = image_data
            
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        logger.info(f"Detected image size: width={width}, height={height}")
        return {"width": width, "height": height}
    except Exception as e:
        logger.error(f"Failed to get image size: {str(e)}")
        raise ValueError("Invalid image format or corrupted image.")


def save_images(task_id, image_bytes_list, output_dir="generated_images"):
    """
    Save generated images to a dictionary with task IDs mapping to file paths.
    Args:
        image_bytes_list (list): List of image bytes to save.
        output_dir (str): Directory to save images to.
    Returns:
        dict: A dictionary mapping 'task_id' to list of saved image paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # save to s3
    saved_paths = []
    for i, image_bytes in enumerate(image_bytes_list):
        image = Image.open(io.BytesIO(image_bytes))
        filepath = os.path.join(output_dir, f"image_{timestamp}_{i}.jpg")
        image.save(filepath)
        saved_paths.append("/"+filepath.replace("\\", "/"))
        logger.info(f"Saved image to {filepath}")
    logger.info(f"Saved images with task ID {task_id} to {output_dir}")
    return saved_paths
    