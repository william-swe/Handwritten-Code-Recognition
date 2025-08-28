# Docker Setup
Various ways
One way is manually create a .devcontainer folder and devcontainer.json and Dockerfile in it. For content, search Google or ask AI.

Download "Containers" extension for VSCode, then go to VSCode Command Prompt (or Ctrl + Shift + P or press F1) and search for something like "Dev Container: Build...", then select the folder that contains .devcontainer.

# GitHub Setup
Use .gitignore to ignore environment file (if you use), large files such as images, etc.

# OCR Setup
Typically includes those steps:
1.  Go to a host website.
2.  Signup an account.
3.  Generate a API key (keep the key private, never share or commit in Git).
4.  If you are not familiar with their API, find their cookbook for an example API call.
5.  Select a model.
6.  Check their limit on API calls and prices.
7.  Update class `OcrService` in `utils.py`.
8.  Update `SKIP_OCR_IMAGES` to skip specific images if necessary.

# File Explanation
1.  `<service_name>_ocr.py` are files used to run OCR from a <service> API (e.g., **azure_ocr** runs **Azure's** API service).
2.  `compress_images.py` is used to compress raw images, raw images should be located in `images/raw` folder. The raw images are usually large, which can cause some services to reject the images (e.g., Claude requires an image's size in bytes to be at most 5 MB).
3.  `measure_errors.py` is used to calculate **Normalised Levenshtein Distance (NLD)** by pairing results in the results folder with its counterparts in ground_truth folder.
4.  `utils.py` contains utilities needed to modulised the system.
5.  `requirements.txt` is used to keep track of dependencies, it can be installed by running `pip install -r requirements.txt`.
6.  `IMAGES.md` explains errors in images.
