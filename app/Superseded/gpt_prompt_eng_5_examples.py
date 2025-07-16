# Import external modules
import os, base64
from pathlib import Path

# Import self-made modules
from utils import OcrService, PROCESSED_OCR_IMAGES, define_directories, load_env_file, is_a_file_an_image, read_ground_truth_file, save_results_to_file, natural_sort_files

# Import OpenAI modules
from openai import OpenAI

# Define the OCR service being used
SERVICE = OcrService.PSEUDO10

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

        system_prompt = f"""
        <role>
        You are a perfect OCR assistant for exam scripts.
        </role>
        <mission>
        Transcribe _exactly_ what is written, and _only_ what is written.
        </mission>
        <context>
        You will be acting as an OCR (Optical Character Recognition). Your goal is to transcribe a student's handwritten text in an exam paper to its digital version. This task is crucial as markers will use the digital text to evaluate the student's work. It is of utmost importance that you transcribe the text exactly as it appears, without making any corrections or improvements.
        </context>
        <instructions>
        Here are some important rules for the transcription task:
        - Transcribe the text exactly as it appears in the handwritten version. Do not correct any typos, syntax errors, or logical errors you may notice.
        - Do NOT transcribe any text that is crossed out.
        - When you see an insertion sign indicated in the image, please insert the inserted text to where the sign points to.
        - Please output only the transcribed text and nothing else. Remember, accuracy in transcription is important than anything else.
        </instructions>
        <question>
        Transcribe the text in the image. Only output the text and nothing else.
        </question>
        Think about your answer first before you respond.
        """

        prompt = "Extract the text in the image. Only output the text and nothing else."

        # Read all example ground truth files
        gt_examples = read_ground_truth_file()
        gt_examples_1, gt_examples_2, gt_examples_3, gt_examples_4, gt_examples_5, gt_examples_6, gt_examples_7 = gt_examples

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
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image('images/compressed/examples_1_comp.png')}", "detail": "high"}}
                    ]
                },
                {
                    "role": "assistant",
                    "content": gt_examples_1
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image('images/compressed/examples_2_comp.png')}", "detail": "high"}}
                    ]
                },
                {
                    "role": "assistant",
                    "content": gt_examples_2
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image('images/compressed/examples_3_comp.png')}", "detail": "high"}}
                    ]
                },
                {
                    "role": "assistant",
                    "content": gt_examples_3
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image('images/compressed/examples_4_comp.png')}", "detail": "high"}}
                    ]
                },
                {
                    "role": "assistant",
                    "content": gt_examples_4
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image('images/compressed/examples_5_comp.png')}", "detail": "high"}}
                    ]
                },
                {
                    "role": "assistant",
                    "content": gt_examples_5
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
