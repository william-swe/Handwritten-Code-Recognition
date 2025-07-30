import base64, os
from enum import StrEnum, auto
from pathlib import Path

# Import SDK modules
from anthropic import Anthropic
from openai import OpenAI

# Enum for OCR service names
# This allows for easy reference to different OCR services used in the application.
# All used services are listed here, and they can be extended in the future if needed.
class OcrService(StrEnum):
    # OPENAI = 'gpt'
    # PSEUDO6 = 'gpt_no_prompt_eng'
    # PSEUDO7 = 'gpt_prompt_eng_no_examples'
    # PSEUDO8 = 'gpt_prompt_eng_1_example'
    # PSEUDO9 = 'gpt_prompt_eng_3_examples'
    # PSEUDO10 = 'gpt_prompt_eng_5_examples'
    # PSEUDO11 = 'gpt_prompt_eng_7_examples'
    # PSEUDO12 = 'gpt_4.5_preview_prompt_eng_5_examples'
    # PSEUDO13 = 'gpt_4o_mini_prompt_eng_5_examples'

    # PSEUDO14 = 'combined_azure_gpt'
    # PSEUDO15 = 'combined_mistral_gpt'
    # PSEUDO5 = '[test1]_combined_mistral_claude'
    # PSEUDO44 = '[test2]_combined_mistral_claude'
    # PSEUDO45 = '[test3]_combined_mistral_claude'
    # PSEUDO16 = 'combined_azure_claude'
    # PSEUDO17 = 'claude_mistral_gpt'

    # ANTHROPIC = 'claude'
    # PSEUDO1 = 'claude_no_prompt_eng'
    # PSEUDO2 = 'claude_prompt_eng_no_examples'
    # PSEUDO3 = 'claude_prompt_eng_5_set_examples'
    # PSEUDO4 = 'claude_prompt_eng_7_set_examples'

    # PSEUDO18 = 'claude_cot_no_fh_opus_4'
    # PSEUDO19 = 'claude_cot_1_fh_opus_4'
    # PSEUDO20 = 'claude_cot_1_fh_3_7_sonnet'
    # PSEUDO21 = 'claude_cot_2_fh_3_7_sonnet' # example 24 + 33
    # PSEUDO28 = 'claude_cot_3_fh_3_7_sonnet' # example 24 + 6 + 12
    # PSEUDO29 = 'claude_no_cot_3_fh_3_7_sonnet' # example 24 + 6 + 12
    # PSEUDO22 = 'claude_cot_no_fh_3_5_sonnet_latest'
    # PSEUDO23 = 'claude_cot_1_fh_3_5_sonnet_latest' # example 24
    # PSEUDO24 = 'claude_cot_2_fh_3_5_sonnet_latest' # example 24 + 31/33
    # PSEUDO25 = 'claude_cot_6_fh_3_5_sonnet_latest'
    # PSEUDO30 = 'test_claude_no_cot_3_fh_3_7_sonnet' # example 24 + similar examples to exam_6 + exam_12
    # PSEUDO31 = 'claude_cot_x_fh_3_7_sonnet_latest' # for testing
    # PSEUDO32 = '[batch_17_7]_claude_cot_1_fh_3_5_sonnet_latest' # 39 clean snapshots
    # PSEUDO33 = '[batch]_claude_cot_3_fh_3_7_sonnet_latest'
    # PSEUDO34 = '[batch]_claude_cot_1_fh_3_7_sonnet_latest'
    # PSEUDO36 = '[batch]_claude_cot_1_fh_3_5_sonnet_latest' # 39 mixed snapshots
    # PSEUDO37 = '[insertion_only]_claude_cot_1_fh_3_5_sonnet_latest'

    # PSEUDO26 = 'gpt_cot_2_fh_4_1' # example 24 + 33
    # PSEUDO27 = 'gpt_cot_2_fh_4o_mini' # example 24 + 33
    # PSEUDO35 = 'gpt_cot_1_fh_4o_mini'
    # PSEUDO46 = '[insertion_only_claude]_simple_prompt_sonnet_3_5_latest'

    # NEW EXPERIMENTS WITH 10 NEW IMAGES FOR SYNTAX AND INSERTION

    # PSEUDO38 = '[syntax_insertion_claude]_simple_prompt_opus_4'
    # PSEUDO41 = '[syntax_insertion_claude]_zsp_opus_4'
    # PSEUDO42 = '[syntax_insertion_claude]_zsp_sonnet_3_5_latest'
    # PSEUDO44 = '[syntax_insertion_claude]_cot_fsp_sonnet_3_5_latest'
    # PSEUDO45 = '[ex][syntax_insertion_claude]_cot_fsp_24_120_sonnet_3_5_latest'
    # PSEUDO43 = '[syntax_insertion_gpt]_zsp_4o_mini'
    # PSEUDO47 = '[ex][syntax_insertion_claude]_cot_fsp_120_sonnet_3_5_latest'
    
    AZURE = 'azure'
    MISTRAL = 'mistral'
    PSEUDO40 = '[syntax_insertion_gpt]_simple_prompt_4o_mini'
    PSEUDO49 = '[syntax_insertion_gpt]_simple_prompt_4_1'
    PSEUDO39 = '[syntax_insertion_claude]_simple_prompt_sonnet_3_5_latest'
    PSEUDO43 = '[syntax_insertion_claude]_cot_zsp_sonnet_3_5_latest'
    PSEUDO48 = '[ex][syntax_insertion_claude]_cot_fsp_109_120_125_sonnet_3_5_latest'

# Tuple of compressed image names to process for OCR (manually input)
PROCESSED_OCR_IMAGES = (
    'exam_103_comp.png',
    'exam_104_comp.png',
    'exam_105_comp.png',
    'exam_106_comp.png',
    'exam_108_comp.png',
    'exam_113_comp.png',
    'exam_114_comp.png',
    'exam_116_comp.png',
    'exam_118_comp.png',
    'exam_128_comp.png',
    
    # 'exam_109_comp.png',
    # 'exam_120_comp.png',
    # 'exam_125_comp.png',

    # 'exam_43_comp.png',
    # 'exam_65_comp.png',
    # 'exam_89_comp.png',
    # 'exam_102_comp.png',
    # 'exam_107_comp.png',
    # 'exam_110_comp.png',
    # 'exam_111_comp.png',
    # 'exam_112_comp.png',
    # 'exam_115_comp.png',
    # 'exam_117_comp.png',
    # 'exam_119_comp.png',
    # 'exam_121_comp.png',
    # 'exam_122_comp.png',
    # 'exam_123_comp.png',
    # 'exam_124_comp.png',
    # 'exam_126_comp.png',
    # 'exam_127_comp.png',
    # 'exam_129_comp.png',
    # 'exam_130_comp.png',
    # 'exam_131_comp.png',
    # 'exam_132_comp.png',
    # 'exam_133_comp.png',
    # 'exam_134_comp.png',
    # 'exam_135_comp.png',
    # 'exam_136_comp.png',
    # 'exam_137_comp.png',
    # 'exam_138_comp.png',
    # 'exam_139_comp.png',
    # 'exam_140_comp.png',
    # 'exam_141_comp.png',
    # 'exam_142_comp.png',
    # 'exam_143_comp.png',
    # 'exam_144_comp.png',
    # 'exam_145_comp.png',
    # 'exam_146_comp.png',
    # 'exam_147_comp.png',
    # 'exam_148_comp.png',
    # 'exam_149_comp.png',
    # 'exam_150_comp.png',
    # 'exam_151_comp.png',
    # 'exam_152_comp.png',
    # 'exam_153_comp.png',
)

CLAUDE_SERVICE_PRICES = {
    "claude-opus-4-0": {
        "input_token": 15/10**6,  # $15 per million input tokens
        "output_token": 75/10**6  # $75 per million output tokens
    },
    "claude-sonnet-4-0": {
        "input_token": 3/10**6,  # $3 per million input tokens
        "output_token": 15/10**6  # $15 per million output tokens
    },
    "claude-3-5-sonnet-latest": {
        "input_token": 3/10**6,
        "output_token": 15/10**6
    },
    "claude-3-7-sonnet-latest": {
        "input_token": 3/10**6,
        "output_token": 15/10**6
    },
}

GPT_SERVICE_PRICES = {
    "gpt-4.1": {
        "input_token": 2/10**6,  # $2 per million input tokens
        "output_token": 8/10**6  # $8 per million output tokens
    },
    "gpt-4o-mini": {
        "input_token": 1.1/10**6,  # $1.1 per million input tokens
        "output_token": 4.4/10**6  # $4.4 per million output tokens
    },
}

def load_env_file():
    '''
    Load environment variables from a .env file located in the parent directory.
    Returns:
        None
    '''
    from pathlib import Path
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found at {env_path}. Please create it with the necessary variables.")
    
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

def define_directories(ocr_name):
    '''
    Define directories for images and results based on the OCR service name.
    Args:
        ocr_name (str): Name of the OCR service (e.g., 'azure', 'mistral', etc.)
    Returns:
        tuple: A tuple containing the images directory, list of image files, and results directory.
    '''
    if not ocr_name:
        raise ValueError('OCR service name must be provided.')
    
    import glob
    from pathlib import Path

    # Define the directories
    images_dir = Path(__file__).resolve().parent.parent / 'images/compressed'
    image_files = glob.glob(str(images_dir / '*'))  # Get all files in the images directory
    results_dir = Path(__file__).resolve().parent.parent / 'results' / ocr_name
    results_dir.mkdir(parents=True, exist_ok=True)  # Create results directory if it doesn't exist

    if not image_files:
        raise FileNotFoundError(f"No images found in {images_dir}. Please add images to this directory.")

    return images_dir, image_files, results_dir

def is_a_file_an_image(file_path):
    '''
    Check if the given file path is an image.
    Args:
        file_path (str): Path to the file to check.
    Returns:
        bool: True if the file is an image, False otherwise.
    '''
    from pathlib import Path
    image_extensions = ['.png', '.jpg', '.jpeg']
    return Path(file_path).suffix.lower() in image_extensions

def read_ground_truth_file():
    '''
    Read ground truth examples from text files.
    Returns:
        tuple: A tuple containing the ground truth examples.
    '''
    NUMBER_OF_EXAMPLES = 7
    gt_examples = []
    for i in range(1, NUMBER_OF_EXAMPLES + 1):
        with open(f'ground_truth/examples_{i}.txt', 'r', encoding='utf-8') as f:
            gt_examples.append(f.read().strip())

    return tuple(gt_examples)

def save_results_to_file(ocr_name, results, file_name, results_dir):
    '''
    Save the OCR results to a text file.
    Args:
        results (str): The OCR results to save.
        file_name (str): The name of the file to save the results in (without extension).
        results_dir (Path): The directory where the results will be saved.
    Returns:
        None
    '''
    result_file_path = results_dir / f"{ocr_name}_{file_name}.txt"
    with open(result_file_path, 'w', encoding='utf-8') as f:
        f.write(results)
    print(f"Results saved to {result_file_path}")

def read_an_OCR_output_file(ocr_filename, ocr_filepath):
    ocr_output = None
    if ocr_filepath.exists():
        with open(ocr_filepath, 'r', encoding='utf-8') as f:
            ocr_output = f.read()
    else:
        print(f"Warning: OCR output file not found: {ocr_filepath}")
    return ocr_output

def natural_sort_files(file_list):
    import re
    return sorted(file_list, key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', Path(s).name)])

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
        base_64_encoded_data = base64.b64encode(binary_data)
        base64_string = base_64_encoded_data.decode('utf-8')
        return base64_string

def extract_answer_from_tag(text: str) -> str:
    """
    Extracts and returns the content inside the first <answer>...</answer> tag in the string, with leading/trailing whitespace removed.
    If no such tag is found, returns the original string stripped.
    """
    import re
    match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def claude_analyse_read(service_name: OcrService, model: str, max_tokens: int, temperature: int, message_list: list[dict], system_prompt: str, idx_to_insert_image: int):
    # Check if the service_name is a valid OcrService enum
    if not isinstance(service_name, OcrService):
        raise ValueError(f"Invalid OCR service name: {service_name}. Must be an instance of OcrService enum.")

    # Check if the system prompt is provided
    if not system_prompt:
        print("System prompt is not provided.")

    # Load environment variables
    load_env_file()

    # Access Claude API key from environment variables
    api_key = os.getenv("CLAUDE_API_KEY")

    # Check if the API key is set
    if not api_key:
        print("CLAUDE_API_KEY is not set in the .env file.")
        exit(1)

    # Create a Claude client
    print("Connecting to Claude AI service...\n")
    client = Anthropic(api_key=api_key)

    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories(service_name)

    # Only process images in PROCESSED_OCR_IMAGES and sort them naturally
    image_files = [f for f in image_files if Path(f).name in PROCESSED_OCR_IMAGES]
    image_files = natural_sort_files(image_files)

    if not image_files:
        print(f"No images found in {images_dir}.")
        return

    print('---------- Claude service analysis started ----------')

    token_usage_rows = []
    total_input_tokens = 0
    total_output_tokens = 0
    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        # Insert the image to the prompt
        message_list[idx_to_insert_image]["content"][0]["source"]["data"] = get_base64_encoded_image(image_path)

        print(f"\nAnalysing {Path(image_path).name} by {model}...")

        # Send the request to the Claude API
        response = client.messages.create(
            model=model,
            system=system_prompt,
            messages=message_list,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Clean and save recognised text to file
        cleaned_text = extract_answer_from_tag(response.content[0].text)
        save_results_to_file(service_name, cleaned_text, Path(image_path).stem, results_dir)

        # Track token usage
        usage = getattr(response, 'usage', None)
        input_tokens = output_tokens = ''
        if usage:
            input_tokens = getattr(usage, 'input_tokens', '')
            output_tokens = getattr(usage, 'output_tokens', '')
            # Accumulate totals for price calculation
            if isinstance(input_tokens, int):
                total_input_tokens += input_tokens
            elif str(input_tokens).isdigit():
                total_input_tokens += int(input_tokens)
            if isinstance(output_tokens, int):
                total_output_tokens += output_tokens
            elif str(output_tokens).isdigit():
                total_output_tokens += int(output_tokens)
        token_usage_rows.append(f"| {Path(image_path).name} | {input_tokens} | {output_tokens} |\n")

    # Write token usage table to Markdown file in the Claude results directory
    token_usage_path = results_dir / 'claude_token_usage.md'
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
            input_sum = sum(int(row.split('|')[2].strip()) for row in token_usage_rows if row.split('|')[2].strip().isdigit())
            output_sum = sum(int(row.split('|')[3].strip()) for row in token_usage_rows if row.split('|')[3].strip().isdigit())
            count = len([row for row in token_usage_rows if row.split('|')[2].strip().isdigit() and row.split('|')[3].strip().isdigit()])
            if count > 0:
                avg_input = round(input_sum / count, 1)
                avg_output = round(output_sum / count, 1)
                with open(token_usage_path, 'a', encoding='utf-8') as f:
                    f.write(f"| **Average** | {avg_input} | {avg_output} |\n")
        except Exception as e:
            print(f"Error calculating averages for token usage: {e}")

    # Calculate and append total price usage
    price_info = CLAUDE_SERVICE_PRICES.get(model, None)
    total_price = None
    if price_info:
        input_price = price_info.get("input_token", 0)
        output_price = price_info.get("output_token", 0)
        total_price = (total_input_tokens * input_price) + (total_output_tokens * output_price)
        with open(token_usage_path, 'a', encoding='utf-8') as f:
            f.write(f"\n**Total price usage for model '{model}': ${total_price:.4f}**\n")
    else:
        with open(token_usage_path, 'a', encoding='utf-8') as f:
            f.write(f"\n**Total price usage for model '{model}': Unknown (model not in CLAUDE_SERVICE_PRICES)**\n")

    print('\n---------- Claude service analysis finished ----------')

def gpt_analyse_read(service_name: OcrService, model: str, max_tokens: int, temperature: int, messages: list[dict], idx_to_insert_image: int):
    # Check if the service_name is a valid OcrService enum
    if not isinstance(service_name, OcrService):
        raise ValueError(f"Invalid OCR service name: {service_name}. Must be an instance of OcrService enum.")

    # Load environment variables
    load_env_file()

    # Access Claude API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")

    # Check if the API key is set
    if not api_key:
        print("OPENAI_API_KEY is not set in the .env file.")
        exit(1)

    # Create a GPT client
    print("Connecting to GPT AI service...\n")
    client = OpenAI(api_key=api_key)

    # Define directories and get image files
    images_dir, image_files, results_dir = define_directories(service_name)

    # Only process images in PROCESSED_OCR_IMAGES and sort them naturally
    image_files = [f for f in image_files if Path(f).name in PROCESSED_OCR_IMAGES]
    image_files = natural_sort_files(image_files)

    if not image_files:
        print(f"No images found in {images_dir}.")
        return

    print('---------- OpenAI service analysis started ----------')

    token_usage_rows = []
    total_input_tokens = 0
    total_output_tokens = 0
    for image_path in image_files:
        # Check if the file is an image
        if not is_a_file_an_image(image_path):
            print(f"\nSkipping {Path(image_path).name}, not a supported image format.")
            continue

        # Insert the image to the prompt
        messages[idx_to_insert_image]["content"][0]["image_url"]["url"] = f"data:image/png;base64,{get_base64_encoded_image(image_path)}"

        print(f"\nAnalysing {Path(image_path).name} by {model}...")

        # Send the request to the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Clean and save recognised text to file
        cleaned_text = extract_answer_from_tag(response.choices[0].message.content)
        save_results_to_file(service_name, cleaned_text, Path(image_path).stem, results_dir)

        # Track token usage
        usage = getattr(response, 'usage', None)
        input_tokens = output_tokens = ''
        if usage:
            input_tokens = getattr(usage, 'prompt_tokens', '')
            output_tokens = getattr(usage, 'completion_tokens', '')
            # Accumulate totals for price calculation
            if isinstance(input_tokens, int):
                total_input_tokens += input_tokens
            elif str(input_tokens).isdigit():
                total_input_tokens += int(input_tokens)
            if isinstance(output_tokens, int):
                total_output_tokens += output_tokens
            elif str(output_tokens).isdigit():
                total_output_tokens += int(output_tokens)
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
            input_sum = sum(int(row.split('|')[2].strip()) for row in token_usage_rows if row.split('|')[2].strip().isdigit())
            output_sum = sum(int(row.split('|')[3].strip()) for row in token_usage_rows if row.split('|')[3].strip().isdigit())
            count = len([row for row in token_usage_rows if row.split('|')[2].strip().isdigit() and row.split('|')[3].strip().isdigit()])
            if count > 0:
                avg_input = round(input_sum / count, 1)
                avg_output = round(output_sum / count, 1)
                with open(token_usage_path, 'a', encoding='utf-8') as f:
                    f.write(f"| **Average** | {avg_input} | {avg_output} |\n")
        except Exception as e:
            print(f"Error calculating averages for token usage: {e}")

    # Calculate and append total price usage
    price_info = GPT_SERVICE_PRICES.get(model, None)
    total_price = None
    if price_info:
        input_price = price_info.get("input_token", 0)
        output_price = price_info.get("output_token", 0)
        total_price = (total_input_tokens * input_price) + (total_output_tokens * output_price)
        with open(token_usage_path, 'a', encoding='utf-8') as f:
            f.write(f"\n**Total price usage for model '{model}': ${total_price:.4f}**\n")
    else:
        with open(token_usage_path, 'a', encoding='utf-8') as f:
            f.write(f"\n**Total price usage for model '{model}': Unknown (model not in GPT_SERVICE_PRICES)**\n")

    print('\n---------- GPT service analysis finished ----------')

class HandwritingColor(StrEnum):
    BLACK = auto()
    BLUE  = auto()
    GRAY  = auto()

class HandwritingLegibility(StrEnum):
    ILLEGIBLE = auto()
    POOR      = auto()
    FAIR      = auto()
    GOOD      = auto()
    EXCELLENT = auto()

class HandwritingInsertion(StrEnum):
    ABOVE     = auto()
    BELOW     = auto()
    ANNOTATE  = auto()

class HandwritingDeletion(StrEnum):
    CROSS_OUT_WORDS      = auto()
    CROSS_OUT_SYMBOLS    = auto()

class HandwritingError(StrEnum):
    SYNTAX = auto()
    LOGIC  = auto()

class HandwritingAnnotation(StrEnum):
    CICLE = auto()
    ARROW = auto()
    TEXT  = auto()

class HandwritingCharacter(StrEnum):
    SPECIAL_CHARACTER = auto()

image_tags: dict[str, set[StrEnum]] = {
    'exam_1.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_2.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_3.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR
    },
    'exam_4.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ANNOTATE,
        HandwritingDeletion.CROSS_OUT_WORDS,
        HandwritingDeletion.CROSS_OUT_SYMBOLS
    },
    'exam_5.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_6.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS,
        HandwritingError.SYNTAX
    }, # MARKED
    'exam_7.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS,
        HandwritingError.SYNTAX
    },
    'exam_8.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_9.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_10.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_11.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_12.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_13.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_14.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD
    },
    'exam_15.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_16.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD
    },
    'exam_17.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_18.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_19.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_20.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR
    },
    'exam_21.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_22.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR
    },
    'exam_23.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.POOR,
        HandwritingInsertion.BELOW,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_24.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.POOR,
        HandwritingInsertion.ABOVE,
        HandwritingInsertion.BELOW,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_25.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_26.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_27.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_28.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_29.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_30.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_31.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_32.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingInsertion.ANNOTATE,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_33.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingInsertion.ANNOTATE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_34.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_35.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_36.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_37.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.EXCELLENT
    },
    'exam_38.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT
    },
    'exam_39.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingAnnotation.CICLE,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS,
    }, # MARKED
    'exam_40.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_41.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingError.SYNTAX
    }, # MARKED
    'exam_42.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_43.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD
    },
    'exam_44.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD
    },
    'exam_45.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_46.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ANNOTATE,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_47.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_48.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_49.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT
    },
    'exam_50.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_51.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_52.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_53.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_54.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_55.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingError.SYNTAX
    },
    'exam_56.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_57.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD,
    }, # MARKED
    'exam_58.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD,
    },
    'exam_59.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD,
    },
    'exam_60.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.POOR,
    }, # MARKED
    'exam_61.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.POOR,
    }, # MARKED
    'exam_62.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_63.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD,
        HandwritingError.SYNTAX
    },
    'exam_64.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.EXCELLENT
    },
    'exam_65.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_66.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_67.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_68.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_69.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_70.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_71.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_72.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_73.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_74.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.BELOW,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_75.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_76.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_77.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_78.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingAnnotation.ARROW,
        HandwritingInsertion.ABOVE,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_79.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingInsertion.ABOVE,
        HandwritingInsertion.ANNOTATE,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_80.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingInsertion.ABOVE,
        HandwritingAnnotation.TEXT,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_81.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.FAIR,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_82.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT
    },
    'exam_83.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT
    },
    'exam_84.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT
    },
    'exam_85.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_86.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT
    },
    'exam_87.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingCharacter.SPECIAL_CHARACTER,
        HandwritingDeletion.CROSS_OUT_WORDS
    }, # MARKED
    'exam_88.png': {
        HandwritingColor.BLACK,
        HandwritingLegibility.EXCELLENT,
        HandwritingError.SYNTAX
    },
    'exam_89.png': {
        HandwritingColor.BLUE,
        HandwritingLegibility.GOOD,
        HandwritingError.SYNTAX
    }, # MARKED
    'exam_90.png': {
        HandwritingColor.BLUE,
        HandwritingLegibility.GOOD
    },
    'exam_91.png': {
        HandwritingColor.BLUE,
        HandwritingLegibility.GOOD
    },
    'exam_92.png': {
        HandwritingColor.BLUE,
        HandwritingLegibility.GOOD
    },
    'exam_93.png': {
        HandwritingColor.BLUE,
        HandwritingLegibility.GOOD,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_94.png': {
        HandwritingColor.BLUE,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.BELOW,
        HandwritingDeletion.CROSS_OUT_WORDS
    },
    'exam_95.png': {
        HandwritingColor.BLUE,
        HandwritingLegibility.GOOD,
        HandwritingError.SYNTAX
    },
    'exam_96.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.EXCELLENT
    },
    'exam_97.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.EXCELLENT
    },
    'exam_98.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_99.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD
    },
    'exam_100.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.FAIR
    }, # MARKED
    'exam_101.png': {
        HandwritingColor.GRAY,
        HandwritingLegibility.GOOD,
        HandwritingInsertion.ABOVE,
        HandwritingInsertion.BELOW,
        HandwritingDeletion.CROSS_OUT_WORDS
    } # MARKED
}
