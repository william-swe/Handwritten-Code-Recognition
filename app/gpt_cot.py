# Import external modules
from pathlib import Path

# Import self-made modules
from utils import OcrService, get_base64_encoded_image, gpt_analyse_read

# Define the OCR service being used and its model
SERVICE = OcrService.PSEUDO35
MODEL_NAME = "gpt-4o-mini"

system_prompt = "You are a perfect OCR assistant for extracting text from images without producing hallucinations."

prompt = """
<instructions>
    Here is a list of steps that you should follow to extract text from images:
    <steps>
        1. If you encounter a strikethrough or crossed-out word, you will ignore it.
        2. If you see an insertion sign, including (but not limited to) a caret ("^" or "v") or an arrow, you will insert the text at the indicated position.
        3. If you see a typo, a Java spelling/syntax mistake or a Java logical error, you never correct it, you will read the text as it is.
        4. Place the transcribed text inside this XML tag: <answer>your text here</answer>.
    </steps>
</instructions>
<question>
    Follow the above steps and extract text from this image.
</question>
"""

# List of example numbers
examples = tuple([
    24, # exam_24
    # 33, # exam_33
    # 48, # exam_48
    # 58, # exam_58
    # 36, # exam_36
    # 31, # exam_31
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
messages = [{
    "role": "system",
    "content": system_prompt
}]

# Add all example user/assistant pairs
for ex in example_data:
    messages.append({
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ex['encoded_img']}", "detail": "high"}},
            {"type": "text", "text": prompt}
        ]
    })
    messages.append({
        "role": "assistant",
        "content": ex["explanation"]
    })

# Add the main prompt for the actual image
messages.append({
    "role": "user",
    "content": [
        {"type": "image_url", "image_url": {"url": "", "detail": "high"}},  # Placeholder for actual image data
        {"type": "text", "text": prompt}
    ]
})
messages.append({
    "role": "assistant",
    "content": "Let's think step by step."
})

# with open('explaination.txt', 'w', encoding='utf-8') as f:
#     f.write(f"{example_data[5]['explanation']}\n")

gpt_analyse_read(SERVICE, MODEL_NAME, 1024, 0.0, messages)
