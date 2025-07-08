# Import external modules
import os, base64
from pathlib import Path

# Import self-made modules
from utils import OcrService, PROCESSED_OCR_IMAGES, define_directories, load_env_file, is_a_file_an_image, save_results_to_file, natural_sort_files

# Import OpenAI modules
from openai import OpenAI

# Define the OCR service being used
SERVICE = OcrService.OPENAI

# Load environment variables
load_env_file()

# Access OPENAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is set
if not api_key:
    print("OPENAI_API_KEY is not set in the .env file.")
    exit(1)

# Create an OpenAI client
print("Connecting to OpenAI service...\n")
client = OpenAI(api_key=api_key)
MODEL_NAME = "gpt-4.1"

# THE BELOW CODE IS ADAPTED FROM OPENAI GUIDELINE:
# https://platform.openai.com/docs/guides/images-vision?api-mode=responses&format=url

# Function to encode an image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyse_read():
    """
    Function to analyse images using OpenAI's OCR capabilities.
    It connects to the OpenAI service, retrieves images from a specified directory,
    encodes them to Base64, and sends them to the OpenAI API for text recognition.
    The results are saved to a file in a specified results directory.
    """

    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories(SERVICE)
    
    # Only process images in PROCESSED_OCR_IMAGES and sort them naturally
    image_files = [f for f in image_files if Path(f).name in PROCESSED_OCR_IMAGES]
    image_files = natural_sort_files(image_files)

    if not image_files:
        print(f"No images found in {images_dir}.")
        return

    print('---------- OpenAI service analysis started ----------')

    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        print(f"\nAnalysing {Path(image_path).name} by OpenAI service...")

        # Getting the Base64 string
        base64_image = encode_image(image_path)

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Please transcribe this text. Only output the text and nothing else."},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{base64_image}",
                        },
                    ],
                }
            ],
        )

        # Save recognised text to file
        save_results_to_file(SERVICE, response.output_text, Path(image_path).stem, results_dir)

    print('\n---------- OpenAI service analysis finished ----------')

if __name__ == "__main__":
    try:
        analyse_read()
    except Exception as error:
        print(f"An error occurred: {error}")
        exit(1)

# 28/6/2025
# OPENAI available models:
# https://platform.openai.com/docs/models
