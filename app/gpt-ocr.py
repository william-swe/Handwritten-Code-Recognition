# Import external modules
import os, base64
from pathlib import Path

# Import self-made modules
from utils import define_directories, load_env_file, is_a_file_an_image, save_results_to_file

# Import OpenAI modules
from openai import OpenAI

# Load environment variables
load_env_file()

# Access OPENAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is set
if not api_key:
    print("OPENAI_API_KEY is not set in the .env file.")
    exit(1)

OpenAI.api_key = api_key

# THE BELOW CODE IS ADOPTED FROM OPENAI GUIDELINE:
# https://platform.openai.com/docs/guides/images-vision?api-mode=responses&format=url

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

client = OpenAI()

def analyse_read():
    """
    Function to analyse images using OpenAI's OCR capabilities.
    It connects to the OpenAI service, retrieves images from a specified directory,
    encodes them to Base64, and sends them to the OpenAI API for text recognition.
    The results are saved to a file in a specified results directory.
    """
    # Create an OpenAI client
    print("Connecting to OpenAI service...\n")

    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories('gpt')
    
    if not image_files:
        print("No images found in the directory.")
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
                    "role": "system", "content": "You are an OCR assistant."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Please transcribe the handwritten text in this image."},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{base64_image}",
                        },
                    ],
                }
            ],
        )

        # Save recognised text to file
        save_results_to_file('gpt', response.output_text, Path(image_path).stem, results_dir)

    print('\n---------- OpenAI service analysis finished ----------')

if __name__ == "__main__":
    try:
        analyse_read()
    except Exception as error:
        print(f"An error occurred: {error}")
        exit(1)
