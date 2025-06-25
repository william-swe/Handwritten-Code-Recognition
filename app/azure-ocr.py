import os
from dotenv import load_dotenv
from pathlib import Path
import glob

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

# Point to the .env file in the parent directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Access azure api
api_key = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")
endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")

# print('api_key:', api_key)
# print('endpoint:', endpoint)

# THE BELOW CODE IS ADOPTED FROM AZURE DOCUMENT INTELLIGENCE GUIDELINE:
# https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/Python(v4.0)/Read_model/sample_analyze_read.py

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return "[{}, {}], [{}, {}], [{}, {}], [{}, {}]".format(
        bounding_box[0], bounding_box[1],
        bounding_box[2], bounding_box[3],
        bounding_box[4], bounding_box[5],
        bounding_box[6], bounding_box[7]
    )

def analyze_read():
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )

    images_dir = Path(__file__).resolve().parent.parent / 'images'
    results_dir = Path(__file__).resolve().parent.parent / 'results' / 'azure'
    results_dir.mkdir(parents=True, exist_ok=True)  # Create results directory if it doesn't exist
    image_files = glob.glob(str(images_dir / '*'))  # Get all files in the images directory
    if not image_files:
        print(f"No images found in {images_dir}")
        return

    print('---------- Azure service analysis started ----------')

    for image_path in image_files:
        file_name = os.path.basename(image_path)
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

    print()
    print('---------- Azure service analysis done ----------')

if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError

    try:
        analyze_read()
    except HttpResponseError as error:
        if error.error is not None:
            print(f"Received service error: {error.error}")
            raise
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Invalid request: {error}")
        raise
