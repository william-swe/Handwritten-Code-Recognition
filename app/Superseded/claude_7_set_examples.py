# Import external modules
import os, base64
from pathlib import Path

# Import self-made modules
from utils import OcrService, PROCESSED_OCR_IMAGES, define_directories, load_env_file, is_a_file_an_image, save_results_to_file

# Import Anthropic SDK modules
from anthropic import Anthropic

# Define the OCR service being used
SERVICE = OcrService.ANTHROPIC

# Load environment variables
load_env_file()

# Access Claude API key from environment variables
api_key = os.getenv("CLAUDE_API_KEY")

# Check if the API key is set
if not api_key:
    print("CLAUDE_API_KEY is not set in the .env file.")
    exit(1)

# THE BELOW CODE IS ADAPTED FROM ANTHROPIC GUIDELINE:
# https://github.com/anthropics/anthropic-cookbook/blob/main/multimodal/how_to_transcribe_text.ipynb

# Create a Claude client
print("Connecting to Claude AI service...\n")
client = Anthropic(api_key=api_key)
MODEL_NAME = "claude-opus-4-0"
# "claude-opus-4-0"
# "claude-3-5-sonnet-latest"

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

    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories(SERVICE)

    # Only process images in PROCESSED_OCR_IMAGES
    image_files = [f for f in image_files if Path(f).name in PROCESSED_OCR_IMAGES]

    if not image_files:
        print(f"No images found in {images_dir}.")
        return

    print('---------- Claude service analysis started ----------')

    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        print(f"\nAnalysing {Path(image_path).name} by Claude {MODEL_NAME.title()}...")

        prompt = """
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

        # system_prompt = "You are a perfect OCR assistant. You will transcribe the text in the image **exactly** as it appears, without making any corrections or improvements. Your goal is to provide an accurate digital version of the handwritten text for evaluation purposes."

        system_prompt = """
        You are a perfect OCR assistant for exam scripts.
        Your mission: transcribe _exactly_ what is written, and _only_ what is written.
        """

        # Read all example ground truth files
        gt_examples = []
        for i in range(1, 8):
            with open(f'ground_truth/examples_{i}.txt', 'r', encoding='utf-8') as f:
                gt_examples.append(f.read().strip())
        gt_examples_1, gt_examples_2, gt_examples_3, gt_examples_4, gt_examples_5, gt_examples_6, gt_examples_7 = gt_examples
        
        message_list = [
            # Examples: Syntax and logical errors
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image("images/compressed/examples_1_comp.png")}},
                {"type": "text", "text": prompt}
            ]},
            {"role": "assistant", "content": gt_examples_1},
            # Examples: Syntax and logical errors
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image("images/compressed/examples_2_comp.png")}},
                {"type": "text", "text": prompt}
            ]},
            {"role": "assistant", "content": gt_examples_2},
            # Examples: Syntax errors and cross-outs
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image("images/compressed/examples_3_comp.png")}},
                {"type": "text", "text": prompt}
            ]},
            {"role": "assistant", "content": gt_examples_3},
            # Examples: Syntax, logical errors, cross-outs, and insertions
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image("images/compressed/examples_4_comp.png")}},
                {"type": "text", "text": prompt}
            ]},
            {"role": "assistant", "content": gt_examples_4},
            # Examples: Syntax errors, cross-outs, and insertions
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image("images/compressed/examples_5_comp.png")}},
                {"type": "text", "text": prompt}
            ]},
            {"role": "assistant", "content": gt_examples_5},
            # Examples: Syntax, logical errors, cross-outs, and insertions
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image("images/compressed/examples_6_comp.png")}},
                {"type": "text", "text": prompt}
            ]},
            {"role": "assistant", "content": gt_examples_6},
            # Examples: Syntax errors, cross-outs, and insertions
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image("images/compressed/examples_7_comp.png")}},
                {"type": "text", "text": prompt}
            ]},
            {"role": "assistant", "content": gt_examples_7},

            # Prompt for the actual image
            {"role": 'user', "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": get_base64_encoded_image(image_path)}},
                {"type": "text", "text": prompt}
            ]}
        ]
        
        # Send the request to the Claude API
        response = client.messages.create(
            model=MODEL_NAME,
            system=system_prompt,
            messages=message_list,
            max_tokens=500,
            temperature=0.0,
        )

        # Save recognised text to file
        save_results_to_file(SERVICE, response.content[0].text, Path(image_path).stem, results_dir)

        print(f"Usage from Claude: {response.usage}")

    print('\n---------- Claude service analysis finished ----------')

if __name__ == "__main__":
    try:
        analyse_read()
    except Exception as error:
        print(f"An error occurred: {error}")
        exit(1)

# 28/6/2025
# Anthropic models available:
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

# https://github.com/anthropics/courses/blob/master/anthropic_api_fundamentals/06_vision.ipynb
# "Claude 3.5 Sonnet has the strongest vision capabilities"
