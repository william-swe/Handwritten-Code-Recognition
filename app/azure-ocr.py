# Import external modules
import os
from pathlib import Path

# Import self-made modules
from utils import define_directories, load_env_file, is_a_file_an_image, save_results_to_file

# Import Azure SDK modules
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_env_file()

# Access Azure Document Intelligence API key and endpoint from environment variables
api_key = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")
endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")

# Check if the API key and endpoint are set
if not api_key or not endpoint:
    print("DOCUMENTINTELLIGENCE_API_KEY or DOCUMENTINTELLIGENCE_ENDPOINT is not set in the .env file.")
    exit(1)

# print('api_key:', api_key)
# print('endpoint:', endpoint)

# THE BELOW CODE IS ADOPTED FROM AZURE DOCUMENT INTELLIGENCE GUIDELINE:
# https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/Python(v4.0)/Read_model/sample_analyze_read.py

def analyse_read():
    """
    Function to analyse images using Azure Document Intelligence service.
    It connects to the Azure service, retrieves images from a specified directory,
    and sends them to the Azure Document Intelligence API for text recognition.
    The results are saved to a file in a specified results directory.
    """
    # Create a Document Intelligence client
    print("Connecting to Azure Document Intelligence service...\n")
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )

    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories('azure')

    if not image_files:
        print("No images found in the directory.")
        return

    print('---------- Azure service analysis started ----------')

    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        print(f"\nAnalysing {Path(image_path).name} by Azure service...")

        # Open the image file and send it to the Azure Document Intelligence service
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
        save_results_to_file('azure', '\n'.join(lines), Path(image_path).stem, results_dir)

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
