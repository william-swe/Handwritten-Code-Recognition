# Import external modules
import os, base64
from pathlib import Path

# Import self-made modules
from utils import define_directories, load_env_file, is_a_file_an_image, save_results_to_file

# Import Claude SDK modules
from anthropic import Anthropic

# Load environment variables
load_env_file()

# Access Claude API key from environment variables
api_key = os.getenv("CLAUDE_API_KEY")

# Check if the API key is set
if not api_key:
    print("CLAUDE_API_KEY is not set in the .env file.")
    exit(1)

# THE BELOW CODE IS ADAPTED FROM CLAUDE GUIDELINE:
# https://github.com/anthropics/anthropic-cookbook/blob/main/multimodal/how_to_transcribe_text.ipynb

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
        base_64_encoded_data = base64.b64encode(binary_data)
        base64_string = base_64_encoded_data.decode('utf-8')
        return base64_string

def analyse_read():
    """
    Function to analyse images using Claude AI service.
    It connects to the Claude service, retrieves images from a specified directory,
    and sends them to the Claude API for text recognition.
    The results are saved to a file in a specified results directory.
    """
    # Create a Claude client
    print("Connecting to Claude AI service...\n")
    client = Anthropic(api_key=api_key)
    MODEL_NAME = "claude-3-5-haiku-20241022"  # Specify the model to use

    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories('claude')

    if not image_files:
        print("No images found in the directory.")
        return

    print('---------- Claude service analysis started ----------')

    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        print(f"\nAnalysing {Path(image_path).name} by Claude service...")

        # Prepare the message list with the image and text prompt
        message_list = [
            {
                "role": 'user',
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image(image_path)}},
                    {"type": "text", "text": "Please transcribe this text. Only output the text and nothing else."}
                ]
            }
        ]
        
        # Send the request to the Claude API
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2048,
            messages=message_list
        )

        # Save recognised text to file
        save_results_to_file('claude', response.content[0].text, Path(image_path).stem, results_dir)

    print('\n---------- Claude service analysis finished ----------')

if __name__ == "__main__":
    try:
        analyse_read()
    except Exception as error:
        print(f"An error occurred: {error}")
        exit(1)

# https://docs.anthropic.com/en/api/client-sdks
'''
# Claude 4 Models
"claude-opus-4-20250514"
"claude-opus-4-0"  # alias
"claude-sonnet-4-20250514"
"claude-sonnet-4-0"  # alias

# Claude 3.7 Models
"claude-3-7-sonnet-20250219"
"claude-3-7-sonnet-latest"  # alias

# Claude 3.5 Models
"claude-3-5-haiku-20241022"
"claude-3-5-haiku-latest"  # alias
"claude-3-5-sonnet-20241022"
"claude-3-5-sonnet-latest"  # alias
"claude-3-5-sonnet-20240620"  # previous version

# Claude 3 Models
"claude-3-opus-20240229"
"claude-3-opus-latest"  # alias
"claude-3-sonnet-20240229"
"claude-3-haiku-20240307"
'''
