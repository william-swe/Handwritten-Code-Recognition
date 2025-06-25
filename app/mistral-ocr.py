import os, glob, json, base64
from dotenv import load_dotenv
from pathlib import Path
from markdown import markdown
from bs4 import BeautifulSoup

from mistralai import Mistral, ImageURLChunk

# Point to the .env file in the parent directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Access mistral ai api
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    print("MISTRAL_API_KEY is not set in the .env file.")
    exit(1)

# print('api_key:', api_key)

# THE BELOW CODE IS ADOPTED FROM Mistral AI GUIDELINE:
# https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/structured_ocr.ipynb

def analyse_read():

    client = Mistral(api_key=api_key)
    
    # Define the directory containing images and the results directory
    images_dir = Path(__file__).resolve().parent.parent / 'images'
    image_files = glob.glob(str(images_dir / '*'))  # Get all files in the images directory
    results_dir = Path(__file__).resolve().parent.parent / 'results' / 'mistral'
    results_dir.mkdir(parents=True, exist_ok=True)  # Create results directory if it doesn't exist
    
    if not image_files:
        print(f"No images found in {images_dir}")
        return

    print('---------- Mistral AI service analysis started ----------')

    for image_path in image_files:
        image_file = Path(image_path)
        print(f"\nAnalysing {image_file.name} by Mistral AI service...")

        # Check if the file is an image
        if not image_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            print(f"Skipping {image_file.name}, not a supported image format.")
            continue

        # Encode image as base64 for API
        encoded = base64.b64encode(image_file.read_bytes()).decode()
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
        result_file = results_dir / f"mistral-{image_file.name}.txt"
        with open(result_file, 'w', encoding='utf-8') as out_f:
            out_f.write(plain_text)
        print(f"Saved recognised text to {result_file}")

    print('\n---------- Mistral AI service analysis finished ----------')

if __name__ == "__main__":
    try:
        analyse_read()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
