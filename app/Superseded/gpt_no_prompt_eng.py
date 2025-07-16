# Import external modules
import os, base64
from pathlib import Path

# Import self-made modules
from utils import OcrService, PROCESSED_OCR_IMAGES, define_directories, load_env_file, is_a_file_an_image, save_results_to_file, natural_sort_files

# Import OpenAI modules
from openai import OpenAI

# Define the OCR service being used
SERVICE = OcrService.PSEUDO6

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

# THE BELOW CODE IS ADAPTED FROM OPENAI GUIDELINE and COOKBOOK:
# https://platform.openai.com/docs/guides/images-vision?api-mode=responses&format=url
# https://cookbook.openai.com/examples/data_extraction_transformation

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

    # Prepare to track token usage
    token_usage_rows = []
    total_input_tokens = 0
    total_output_tokens = 0
    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        print(f"\nAnalysing {Path(image_path).name} by {MODEL_NAME}...")

        # Getting the Base64 string
        base64_image = encode_image(image_path)

        system_prompt = """
        Your task is to convert a student's handwritten exam answer into a plain digital text file, preserving exactly what was written. Follow these rules strictly:

        1. Verbatim transcription: Do not correct any spelling, grammar, punctuation, or logical errors. Output exactly what appears on the page, including all typos and errors (if any).
        2. Skip deletions: If text is crossed out (strikethrough, scribbles, or over-writing), do not include it in the transcript.
        3. Handle insertions: When you see insertion marks (carets, arrows, or interline numbers), place the inserted text at the correct point in the flow. Do not omit or re-order anything else.
        4. Maintain structure: Preserve line breaks so that each answer block mirrors the student's layout.
        5. No commentary: Do not add explanations, headings, or metadata. Only output the raw transcribed text.
        6. Consistent formatting: Use plain UTF-8 text. Do not wrap lines arbitrarily—only break lines where the student did.

        Whenever you are unsure about an insertion, guess conservatively and flag it by surrounding with square brackets, e.g. [unclear insertion], but still place it in the spot indicated.
        """

        prompt = "Transcribe the text in the image. Only output the text and nothing else."

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                    ]
                }
            ],
            temperature=0.0,
            max_tokens=300,
        )

        # Save recognised text to file
        save_results_to_file(SERVICE, response.choices[0].message.content, Path(image_path).stem, results_dir)

        # Track token usage
        usage = getattr(response, 'usage', None)
        input_tokens = output_tokens = ''
        if usage:
            input_tokens = getattr(usage, 'prompt_tokens', '')
            output_tokens = getattr(usage, 'completion_tokens', '')
        # Fallback for OpenAI SDK: try total_tokens if above not present
        if not input_tokens and hasattr(usage, 'total_tokens'):
            input_tokens = getattr(usage, 'total_tokens', '')
        # Add to totals if possible
        try:
            total_input_tokens += int(input_tokens) if str(input_tokens).isdigit() else 0
            total_output_tokens += int(output_tokens) if str(output_tokens).isdigit() else 0
        except Exception:
            pass
        token_usage_rows.append(f"| {Path(image_path).name} | {input_tokens} | {output_tokens} |\n")

    # Write token usage table to Markdown file in the GPT results directory
    token_usage_path = results_dir / 'gpt_token_usage.md'
    # Write header if file does not exist
    if not token_usage_path.exists():
        with open(token_usage_path, 'w', encoding='utf-8') as f:
            f.write("| OCR Input File | Input Tokens | Output Tokens |\n|:---:|:---:|:---:|\n")
    # Append rows
    with open(token_usage_path, 'a', encoding='utf-8') as f:
        for row in token_usage_rows:
            f.write(row)
        # Compute and append averages if any rows were written
        if token_usage_rows:
            try:
                count = len([row for row in token_usage_rows if row.split('|')[2].strip().isdigit() and row.split('|')[3].strip().isdigit()])
                avg_input = round(total_input_tokens / count, 1) if count else 0
                avg_output = round(total_output_tokens / count, 1) if count else 0
                f.write(f"| **Average** | {avg_input} | {avg_output} |\n")
                # Calculate and write total cost
                input_cost = total_input_tokens * 2.00 / 1_000_000
                output_cost = total_output_tokens * 8.00 / 1_000_000
                total_cost = input_cost + output_cost
                f.write(f"\n**Total cost:** ${total_cost:.4f} (Input: ${input_cost:.4f}, Output: ${output_cost:.4f})\n")
            except Exception as e:
                print(f"Error calculating averages or cost for token usage: {e}")

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
