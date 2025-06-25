import os, glob
from dotenv import load_dotenv
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.exceptions import HttpResponseError

# Point to the .env file in the parent directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Access azure api
api_key = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")
endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")

if not api_key or not endpoint:
    print("DOCUMENTINTELLIGENCE_API_KEY or DOCUMENTINTELLIGENCE_ENDPOINT is not set in the .env file.")
    exit(1)

# print('api_key:', api_key)
# print('endpoint:', endpoint)

# THE BELOW CODE IS ADOPTED FROM AZURE DOCUMENT INTELLIGENCE GUIDELINE:
# https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/Python(v4.0)/Read_model/sample_analyze_read.py

def analyse_read():
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )

    # Define the directory containing images and the results directory
    images_dir = Path(__file__).resolve().parent.parent / 'images'
    image_files = glob.glob(str(images_dir / '*'))  # Get all files in the images directory
    results_dir = Path(__file__).resolve().parent.parent / 'results' / 'azure'
    results_dir.mkdir(parents=True, exist_ok=True)  # Create results directory if it doesn't exist

    if not image_files:
        print(f"No images found in {images_dir}")
        return

    print('---------- Azure service analysis started ----------')

    for image_path in image_files:
        image_file = Path(image_path)

        # Check if the file is an image
        if not image_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            print(f"Skipping {image_file.name}, not a supported image format.")
            continue

        file_name = image_file.stem  # Get the file name without extension
        result_file = results_dir / f"azure-{file_name}.txt"
        print(f"\nAnalysing {file_name} by Azure service...")
        with open(image_path, 'rb') as f:
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-read", f
            )
            result = poller.result()

        # Collect all lines of text
        lines = []
        for page in result.pages:
            for line in page.lines:
                lines.append(line.content)

        # Save recognised text to file
        with open(result_file, 'w', encoding='utf-8') as out_f:
            out_f.write('\n'.join(lines))
        print(f"Saved recognised text to {result_file}")

    print('\n---------- Azure service analysis finished ----------')

if __name__ == "__main__":

    try:
        analyse_read()
    except HttpResponseError as error:
        if error.error is not None:
            print(f"Received service error: {error.error}")
            raise
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Invalid request: {error}")
        raise
