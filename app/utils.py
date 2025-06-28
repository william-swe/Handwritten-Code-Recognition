from enum import StrEnum

class OcrService(StrEnum):
    AZURE = 'azure'
    MISTRAL = 'mistral'
    OPENAI = 'gpt'
    ANTHROPIC = 'claude'

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
