from enum import StrEnum, auto
from pathlib import Path

# Enum for OCR service names
# This allows for easy reference to different OCR services used in the application.
# All used services are listed here, and they can be extended in the future if needed.
class OcrService(StrEnum):
    AZURE = 'azure'
    MISTRAL = 'mistral'
    OPENAI = 'gpt'
    # ANTHROPIC = 'claude'
    PSEUDO1 = 'claude_no_prompt_eng'
    PSEUDO2 = 'claude_prompt_eng_no_examples'
    PSEUDO3 = 'claude_prompt_eng_5_set_examples'
    PSEUDO4 = 'claude_prompt_eng_7_set_examples'
    PSEUDO5 = 'combined_mistral_claude'

# Tuple of compressed image names to process for OCR (manually input)
PROCESSED_OCR_IMAGES = (
    'exam_1_comp.png',
    'exam_2_comp.png',
    'exam_4_comp.png',
    'exam_5_comp.png',
    'exam_6_comp.png',
    'exam_7_comp.png',
    'exam_8_comp.png',
    'exam_11_comp.png',
    'exam_12_comp.png',
    'exam_89_comp.png',
)

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

def natural_sort_files(file_list):
    import re
    return sorted(file_list, key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', Path(s).name)])
