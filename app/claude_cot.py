# Import external modules
from pathlib import Path

# Import self-made modules
from utils import OcrService, get_base64_encoded_image, claude_analyse_read

# Define the OCR service being used and its model
SERVICE = OcrService.PSEUDO21
# MODEL_NAME = "claude-opus-4-0"
# MODEL_NAME = "claude-3-5-sonnet-latest"
MODEL_NAME = "claude-3-7-sonnet-latest"

system_prompt = "You are a perfect OCR assistant for extracting text from images without producing hallucinations."

prompt = """
<instructions>
    Here is a list of steps that you should follow to extract text from images:
    <steps>
        1. If you encounter a strikethrough or crossed-out word, you will ignore it.
        2. If you see an insertion sign, including (but not limited to) a caret ("^" or "v") or an arrow, you will insert the text at the indicated position.
        3. If you see a typo, a Java spelling/syntax mistake or a Java logical error, you never correct it, you will read the text as it is.
        4. Place the transcribed text inside this XML tag: <answer>your text here</answer>
    </steps>
</instructions>
<question>
    Follow the above steps and extract text from this image.
</question>
"""

# List of example numbers
examples = tuple([
    24, # exam_24
    33, # exam_33
    48, # exam_48
    58, # exam_58
    36, # exam_36
    31, # exam_31
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
        print(f"Skipping example {ex_num} due to missing files.")
        continue

    example_data.append({
        "encoded_img": encoded_img,
        "explanation": exp_text
    })

# Prepare the message list for the Claude API
message_list = [
    # Example 24
    {"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": example_data[0]["encoded_img"]}},
        {"type": "text", "text": prompt}
    ]},
    {"role": "assistant", "content": example_data[0]["explanation"]},

    # Example 33
    {"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": example_data[1]["encoded_img"]}},
        {"type": "text", "text": prompt}
    ]},
    {"role": "assistant", "content": example_data[1]["explanation"]},

    # # Example 48
    # {"role": "user", "content": [
    #     {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": example_data[2]["encoded_img"]}},
    #     {"type": "text", "text": prompt}
    # ]},
    # {"role": "assistant", "content": example_data[2]["explanation"]},

    # # Example 58
    # {"role": "user", "content": [
    #     {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": example_data[3]["encoded_img"]}},
    #     {"type": "text", "text": prompt}
    # ]},
    # {"role": "assistant", "content": example_data[3]["explanation"]},

    # # Example 36
    # {"role": "user", "content": [
    #     {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": example_data[4]["encoded_img"]}},
    #     {"type": "text", "text": prompt}
    # ]},
    # {"role": "assistant", "content": example_data[4]["explanation"]},

    # # Example 31
    # {"role": "user", "content": [
    #     {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": example_data[5]["encoded_img"]}},
    #     {"type": "text", "text": prompt}
    # ]},
    # {"role": "assistant", "content": example_data[5]["explanation"]},
    
    # Main prompt for the actual image
    {"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": ""}}, # Placeholder for actual image data
        {"type": "text", "text": prompt}
    ]},
    {"role": "assistant", "content": "Let's think step by step."},
]

# with open('explaination.txt', 'w', encoding='utf-8') as f:
#     f.write(f"{example_data[5]['explanation']}\n")

claude_analyse_read(SERVICE, MODEL_NAME, 1024, 0.0, message_list)
