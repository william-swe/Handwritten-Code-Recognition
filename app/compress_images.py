import os
from pathlib import Path
from PIL import Image
import glob

def compress_images():
    images_dir = Path(__file__).resolve().parent.parent / 'images' / 'raw'
    compressed_dir = Path(__file__).resolve().parent.parent / 'images' / 'compressed'
    compressed_dir.mkdir(parents=True, exist_ok=True)
    image_files = glob.glob(str(images_dir / '*'))
    
    max_size = (1200, 1200)  # Max width, height
    max_bytes = 5 * 1024 * 1024  # 5 MB
    
    for image_path in image_files:
        image_file = Path(image_path)
        if not image_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            continue
        try:
            img = Image.open(image_file)
            img.thumbnail(max_size, Image.LANCZOS)
            out_path = compressed_dir / (image_file.name + '_comp')
            # For JPEG, use quality option; for PNG, use optimize
            if image_file.suffix.lower() in ['.jpg', '.jpeg']:
                img.save(out_path, 'JPEG', quality=40, optimize=True)
            elif image_file.suffix.lower() == '.png':
                # Save as PNG first
                img.save(out_path, 'PNG', optimize=True)
                # If still too large, convert to JPEG
                if out_path.stat().st_size > max_bytes:
                    out_path_jpg = out_path.with_suffix('.jpg')
                    img = img.convert('RGB')
                    img.save(out_path_jpg, 'JPEG', quality=40, optimize=True)
                    out_path.unlink()  # Remove PNG
                    out_path = out_path_jpg
            # Check final size
            if out_path.stat().st_size > max_bytes:
                print(f"Warning: {out_path.name} is still over 5 MB after compression.")
            print(f"Compressed {image_file.name} -> {out_path}")
        except Exception as e:
            print(f"Failed to compress {image_file.name}: {e}")

if __name__ == "__main__":
    compress_images()
