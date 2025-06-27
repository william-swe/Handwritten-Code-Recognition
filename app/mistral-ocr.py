# Import external modules
import os, json, base64
from pathlib import Path
from markdown import markdown
from bs4 import BeautifulSoup

# Import self-made modules
from utils import define_directories, load_env_file, is_a_file_an_image, save_results_to_file

# Import Mistral AI modules
from mistralai import Mistral, ImageURLChunk

# Load environment variables
load_env_file()

# Access Mistral API key from environment variables
api_key = os.getenv("MISTRAL_API_KEY")

# Check if the API key is set
if not api_key:
    print("MISTRAL_API_KEY is not set in the .env file.")
    exit(1)


# THE BELOW CODE IS ADAPTED FROM Mistral AI GUIDELINE:
# https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/structured_ocr.ipynb

def analyse_read():
    """
    Function to analyse images using Mistral AI service.
    It connects to the Mistral service, retrieves images from a specified directory,
    and sends them to the Mistral API for text recognition.
    The results are saved to a file in a specified results directory.
    """
    # Create a Mistral client
    print("Connecting to Mistral AI service...\n")
    client = Mistral(api_key=api_key)
    
    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories('mistral')

    if not image_files:
        print("No images found in the directory.")
        return

    print('---------- Mistral AI service analysis started ----------')

    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        print(f"\nAnalysing {Path(image_path).name} by Mistral AI service...")

        # Encode image as base64 for API
        encoded = base64.b64encode(Path(image_path).read_bytes()).decode()
        base64_data_url = f"data:image/jpeg;base64,{encoded}"

        # Process image with OCR
        image_response = client.ocr.process(
            document=ImageURLChunk(image_url=base64_data_url),
            model="mistral-ocr-latest"
        )

        # Convert response to JSON
        response_dict = json.loads(image_response.model_dump_json())

        # Extract plain text from all pages' markdown
        plain_text_pages = []
        for page in response_dict.get('pages', []):
            markdown_text = page.get('markdown', '')
            html = markdown(markdown_text)
            soup = BeautifulSoup(html, features="html.parser")
            plain_text_pages.append(soup.get_text())
        plain_text = '\n'.join(plain_text_pages)

        # Save recognised text to file
        save_results_to_file('mistral', plain_text, Path(image_path).stem, results_dir)

    print('\n---------- Mistral AI service analysis finished ----------')

if __name__ == "__main__":
    try:
        analyse_read()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
