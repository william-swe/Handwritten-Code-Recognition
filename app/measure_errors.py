import Levenshtein, re
from pathlib import Path
from utils import OcrService

def get_average_normalized_levenshtein(service_name: str):
    # Map service name to folder and file prefix
    service = OcrService(service_name)
    results_dir = Path(__file__).resolve().parent.parent / 'results' / service
    gt_dir = Path(__file__).resolve().parent.parent / 'ground_truth'

    # Find all result files for this service
    result_files = list(results_dir.glob(f'{service}_*.txt'))
    if not result_files:
        print(f"No result files found for {service} in {results_dir}")
        return

    nld_list = []
    for result_file in result_files:
        # Extract the base name (e.g., logic_4_comp from azure_logic_4_comp.txt)
        m = re.match(rf'{service}_(.*)\.txt', result_file.name)
        if not m:
            continue
        base = m.group(1)
        # Try to find the corresponding ground truth file
        # Remove _comp if present, and service prefix
        gt_base = base.replace('_comp', '')
        gt_file = gt_dir / f'{gt_base}.txt'
        if not gt_file.exists():
            print(f"Ground truth file not found for {result_file.name}: {gt_file}")
            continue
        with open(gt_file, 'r', encoding='utf-8') as f:
            gt_text = f.read()
        with open(result_file, 'r', encoding='utf-8') as f:
            ocr_text = f.read()
        if not gt_text.strip() and not ocr_text.strip():
            nld = 0.0
        else:
            # Calculate the normalised Levenshtein distance
            # The higher the value, the better the match
            nld = 1 - Levenshtein.distance(gt_text, ocr_text) / max(len(gt_text), len(ocr_text))
            # print(f'Levenshtein distance for {result_file.name} vs {gt_file.name}: {Levenshtein.distance(gt_text, ocr_text)}')
        nld_list.append(nld)
        print(f'NLD for {result_file.name} vs {gt_file.name}: {nld:.4f}')
    if nld_list:
        avg_nld = sum(nld_list) / len(nld_list)
        print(f'Average normalised Levenshtein distance for {service}: {avg_nld:.4f}')
    else:
        print(f'No valid file pairs found for {service}')

if __name__ == "__main__":
    # Example usage: get_average_normalized_levenshtein('azure')
    for service in OcrService:
        get_average_normalized_levenshtein(service)
        print('-' * 40)
    print("All services processed.")
