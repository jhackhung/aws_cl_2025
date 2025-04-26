import boto3
import json
import os
import sys

# --- Configuration ---
# Choose the AWS region where you have Bedrock model access
# If running on EC2/Lambda with an IAM role, region might be inferred
# Or set via AWS_REGION environment variable
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Choose the Bedrock model for prompt enhancement.
# Claude 3 Sonnet is a good balance of capability and cost.
# Claude 3 Haiku is faster and cheaper, might be sufficient.
# Claude 3 Opus is the most powerful but most expensive.
# Other models like Titan Text could also be used, but API structure differs.
MODEL_ID = "amazon.nova-pro-v1:0"
# MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# --- Bedrock Client Initialization ---
try:
    # It's better practice to let Boto3 find credentials via standard methods
    # (env vars, shared credential file, IAM role) rather than hardcoding.
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=AWS_REGION
        # If explicit credentials needed (less secure, avoid if possible):
        # aws_access_key_id=YOUR_ACCESS_KEY,
        # aws_secret_access_key=YOUR_SECRET_KEY,
        # aws_session_token=YOUR_SESSION_TOKEN # Optional
    )
except Exception as e:
    print(f"Error initializing Bedrock client: {e}")
    print("Please ensure your AWS credentials and region are configured correctly,")
    print("and that you have Bedrock model access in the specified region.")
    sys.exit(1)

# --- Prompt Enhancement Function ---
def enhance_pc_case_prompt(original_prompt: str, model_id: str = MODEL_ID) -> str:
    """
    Uses a Bedrock LLM to enhance a basic PC case design prompt.

    Args:
        original_prompt: The user's initial simple prompt.
        model_id: The Bedrock model ID to use for enhancement.

    Returns:
        The enhanced, detailed prompt string, or an error message.
    """
    print(f"Original Prompt: '{original_prompt}'")
    print(f"Using model: {model_id}")

    # --- Construct the Meta-Prompt for the LLM ---
    # This instructs the LLM on how to perform the enhancement task.
    system_prompt = """You are an expert prompt engineer specializing in generating highly detailed prompts for AI image generation models, focusing specifically on PC computer case designs. Your task is to take a user's simple idea for a PC case and expand it into a rich, descriptive, and evocative prompt.

    When enhancing the prompt, consider and include details about:
    1.  **Style/Aesthetics:** (e.g., futuristic, minimalist, cyberpunk, steampunk, brutalist, organic, retro, industrial, fantasy-inspired)
    2.  **Form Factor/Size:** (e.g., ATX Mid-Tower, Mini-ITX SFF, Full Tower, Open Air, Test Bench, unique custom shape)
    3.  **Materials:** (e.g., brushed aluminum, matte black steel, tempered glass side panel, mesh front, wood accents, carbon fiber, polished chrome, acrylic)
    4.  **Key Features:** (e.g., prominent RGB lighting (strips, fans, zones), large side window, unique ventilation patterns (honeycomb, gills), integrated handles, LCD screen display, custom water cooling loop visibility, cable management features)
    5.  **Color Scheme:** (e.g., monochromatic black, stark white, black with red accents, silver and blue, vibrant neon colors)
    6.  **Lighting & Atmosphere:** (e.g., subtle ambient glow, dramatic studio lighting, cinematic lighting, volumetric light, neon glow, backlit components)
    7.  **Rendering Style:** (e.g., photorealistic render, concept art sketch, 3D octane render, unreal engine render, product shot, blueprint style, technical drawing)
    8.  **Composition/Setting:** (e.g., isolated on white background, on a clean desk setup, in a futuristic lab, against a dark textured background)

    Generate ONLY the enhanced image prompt itself, ready to be used. Do not include any conversational text before or after the prompt. Make it consice (less than 50 words)."""


    # --- Invoke Bedrock Model ---
    try:
        user_message = system_prompt+f"Enhance the following PC case design idea into a detailed image generation prompt:\n\n'{original_prompt}'"
        conversation = [
        {
        "role": "user",
        "content": [{"text": user_message}],
        }
        ]

        print("Invoking Bedrock model...")
        streaming_response = bedrock_runtime.converse_stream(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 200, "temperature": 0.5, "topP": 0.9},
        )
        result=""
         # Extract and print the streamed response text in real-time.
        for chunk in streaming_response["stream"]:
            if "contentBlockDelta" in chunk:
                text = chunk["contentBlockDelta"]["delta"]["text"]
                print(text, end="")
                result+=text
        return result
    except bedrock_runtime.exceptions.AccessDeniedException as e:
        print(f"Error: Access Denied. Ensure the correct IAM permissions and model access for {model_id} in region {AWS_REGION}.")
        print(f"Details: {e}")
        return f"Error: Access Denied for model {model_id}."
    except Exception as e:
        print(f"Error invoking Bedrock model {model_id}: {e}")
        return f"Error: An unexpected error occurred: {e}"
