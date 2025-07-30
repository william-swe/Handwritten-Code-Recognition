# Import external modules
from pathlib import Path

# Import self-made modules
from utils import OcrService, get_base64_encoded_image, claude_analyse_read

# Define the OCR service being used and its model
SERVICE = OcrService.PSEUDO48
MODEL_NAME = "claude-3-5-sonnet-latest"
# MODEL_NAME = "claude-opus-4-0"

system_prompt = "You are a perfect OCR assistant for extracting text from images without producing hallucinations, and perfect at handling text insertion."

complex_prompt = """
<instructions>
    Here is a list of steps that you should follow to extract text from images:
    <steps>
        1. If you see an insertion sign, including (but not limited to) a caret ("^", "v", "<", or ">") or an arrow, you will insert the text at the indicated position.
        2. If you see a typo, or a Java spelling/syntax mistake, you never correct it, you will read the text as it is.
        3. Place the transcribed text inside this XML tag: <answer>your text here</answer>
    </steps>
</instructions>
<question>
    Follow the above steps and extract text from this image.
</question>
# """

# simple_prompt = "Please extract the text from the image below, never correcting typos or syntax mistakes. If you see an insertion sign, including (but not limited to) a caret ('^' or 'v') or an arrow, insert the text at the indicated position. Place the transcribed text inside this XML tag: <answer>your text here</answer>."

# List of example numbers
examples = tuple([
    # 24, # exam_24
    109, # exam_109
    120, # exam_120
    125, # exam_125
])

# Prepare example file paths and load their contents
example_data = []
for ex_num in examples:
    img_path = Path(f"images/compressed/example_{ex_num}_comp.png")
    exp_path = Path(f"explain/ex_example_{ex_num}.txt")

    # Read image (as bytes) and explanation
    encoded_img = get_base64_encoded_image(img_path) if img_path.exists() else None
    exp_text = exp_path.read_text(encoding="utf-8") if exp_path.exists() else None

    if not encoded_img or not exp_text:
        print(f"\033[93mWARNING: Skipping example {ex_num} due to missing files.\033[0m")
        continue

    example_data.append({
        "encoded_img": encoded_img,
        "explanation": exp_text
    })

# Prepare the message list for the Claude API
message_list = []

# Add all example user/assistant pairs
for ex in example_data:
    message_list.append({
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": ex["encoded_img"]}},
            {"type": "text", "text": complex_prompt}
        ]
    })
    message_list.append({
        "role": "assistant",
        "content": ex["explanation"]
    })

# Add the main prompt for the actual image
message_list.append({
    "role": "user",
    "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": ""}},  # Placeholder for actual image data
        {"type": "text", "text": complex_prompt}
    ]
})
message_list.append({
    "role": "assistant",
    "content": "Let's think step by step."
})

# claude_analyse_read(SERVICE, MODEL_NAME, 1024, 0.0, message_list, "", -1)
claude_analyse_read(SERVICE, MODEL_NAME, 1024, 0.0, message_list, system_prompt, -2)
