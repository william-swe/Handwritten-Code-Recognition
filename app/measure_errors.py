import Levenshtein, re
from pathlib import Path
from utils import OcrService
import matplotlib.pyplot as plt  # Add this import

def collect_levenshtein_distances():
    # Collect Levenshtein distances for all services and ground truth files
    gt_dir = Path(__file__).resolve().parent.parent / 'ground_truth'
    all_gt_files = sorted([f for f in gt_dir.glob('*.txt')], key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s.name)])
    services = list(OcrService)
    ld_table = {}  # {gt_file: {service: LD}}
    avg_ld = {service: [] for service in services}
    for gt_file in all_gt_files:
        gt_name = gt_file.name
        with open(gt_file, 'r', encoding='utf-8') as f:
            gt_text = f.read()
        ld_table[gt_name] = {}
        for service in services:
            results_dir = Path(__file__).resolve().parent.parent / 'results' / service
            # Find corresponding result file
            pattern = f'{service}_{gt_name.replace(".txt", "_comp.txt")}'
            result_file = results_dir / pattern
            if not result_file.exists():
                ld = ''
            else:
                with open(result_file, 'r', encoding='utf-8') as f:
                    ocr_text = f.read()
                if not gt_text.strip() and not ocr_text.strip():
                    ld = 0
                else:
                    ld = Levenshtein.distance(gt_text, ocr_text)
                    avg_ld[service].append(ld)
            ld_table[gt_name][service] = ld
    # Calculate averages
    avg_row = {service: (sum(avg_ld[service])/len(avg_ld[service]) if avg_ld[service] else 0) for service in services}
    return ld_table, avg_row, services

def get_service_gt_files(service_name):
    # Return set of ground truth files actually processed by a service
    service = OcrService(service_name)
    results_dir = Path(__file__).resolve().parent.parent / 'results' / service
    gt_dir = Path(__file__).resolve().parent.parent / 'ground_truth'
    result_files = list(results_dir.glob(f'{service}_*.txt'))
    gt_files = set()
    for result_file in result_files:
        m = re.match(rf'{service}_(.*)_comp\.txt', result_file.name)
        if not m:
            continue
        base = m.group(1)
        gt_file = f'{base}.txt'
        if (gt_dir / gt_file).exists():
            gt_files.add(gt_file)
    return gt_files

def get_average_normalized_levenshtein(service_name: str, output_lines, summary_gt_files=None):
    # Map service name to folder and file prefix
    service = OcrService(service_name)
    results_dir = Path(__file__).resolve().parent.parent / 'results' / service
    gt_dir = Path(__file__).resolve().parent.parent / 'ground_truth'

    # Find all result files for this service
    result_files = list(results_dir.glob(f'{service}_*.txt'))
    if not result_files:
        return

    # Sort result files by filename (natural sort for numbers)
    def natural_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s.name)]
    result_files = sorted(result_files, key=natural_key)

    nld_list = []
    ld_list = []
    table_rows = []  # For Markdown table
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
            continue
        if summary_gt_files is not None and gt_file.name not in summary_gt_files:
            continue  # Only include files in the summary table
        with open(gt_file, 'r', encoding='utf-8') as f:
            gt_text = f.read()
        with open(result_file, 'r', encoding='utf-8') as f:
            ocr_text = f.read()
        if not gt_text.strip() and not ocr_text.strip():
            nld = 0.0
            lev_dist = 0
        else:
            lev_dist = Levenshtein.distance(gt_text, ocr_text)
            nld = 1 - lev_dist / max(len(gt_text), len(ocr_text))
        nld_list.append(nld)
        ld_list.append(lev_dist)
        table_rows.append((result_file.name, gt_file.name, lev_dist, nld))
    if nld_list:
        avg_nld = sum(nld_list) / len(nld_list)
    else:
        avg_nld = 0.0
    if ld_list:
        avg_ld = sum(ld_list) / len(ld_list)
    else:
        avg_ld = 0.0
    # Markdown table output only
    if table_rows:
        output_lines.append(f"## {service.capitalize()} OCR Results Table\n\n")
        output_lines.append("| OCR Output File | Ground Truth File | Levenshtein Distance | NLD |\n")
        output_lines.append("|:---:|:---:|:---:|:---:|\n")
        for row in table_rows:
            output_lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]:.4f} |\n")
        output_lines.append(f"| **Average** |  | **{avg_ld:.2f}** | **{avg_nld:.4f}** |\n")
        output_lines.append("\n")

if __name__ == "__main__":
    # Generate a summary table of Levenshtein distances for all OCR services
    ld_table, avg_row, services = collect_levenshtein_distances()
    output_lines = []
    output_lines.append("# OCR Result Summary\n\n")
    output_lines.append("## OCR Levenshtein Distance Summary\n\n")
    # Dynamic header
    header = ["Ground Truth File"] + [
        f"{service.upper()} LD" if service == 'gpt' else f"{service.title().replace('_', ' ')} LD" 
        for service in services
    ]
    output_lines.append(f"| {' | '.join(header)} |\n")
    output_lines.append(f"|{'|'.join([':---:' for _ in header])}|\n")
    summary_gt_files = []
    for gt_file in ld_table:
        # Exclude if all services have missing LD
        if all(ld_table[gt_file][service] == '' for service in services):
            continue
        summary_gt_files.append(gt_file)
        row = [gt_file]
        for service in services:
            val = ld_table[gt_file][service]
            row.append(f"{val}" if val != '' else "-")
        output_lines.append(f"| {' | '.join(row)} |\n")
    avg_row_fmt = [f"{avg_row[service]:.2f}" if avg_row[service] != 0 else "-" for service in services]
    output_lines.append(f"| **Average** | {' | '.join(avg_row_fmt)} |\n\n")

    # --- Generate and insert graph ---
    # Prepare data for the graph
    service_labels = [service.upper() if service == 'gpt' else service.title().replace('_', ' ') for service in services]
    avg_ld_values = [avg_row[service] for service in services]
    plt.figure(figsize=(8, 6))
    bars = plt.bar(service_labels, avg_ld_values, color='skyblue')
    plt.ylabel('Average Levenshtein Distance')
    plt.title('Average Levenshtein Distance by OCR Service')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.xticks(rotation=30, ha='right')
    for bar, value in zip(bars, avg_ld_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{value:.2f}', ha='center', va='bottom')
    graph_path = Path(__file__).resolve().parent.parent / 'results' / 'avg_levenshtein_distance.png'
    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()
    # Insert image below the summary table
    output_lines.append(f'![Average Levenshtein Distance by OCR Service](avg_levenshtein_distance.png)\n\n')
    # --- End graph ---

    # Check for differences in ground truth files between summary and each service
    summary_gt_set = set(summary_gt_files)
    for service in services:
        service_gt_set = get_service_gt_files(service)
        if summary_gt_set != service_gt_set:
            only_in_summary = summary_gt_set - service_gt_set
            only_in_service = service_gt_set - summary_gt_set
            if only_in_summary:
                print(f"Ground truth files in summary but not in {service}: {sorted(only_in_summary)}")
            if only_in_service:
                print(f"Ground truth files in {service} but not in summary: {sorted(only_in_service)}")

    # Results for each service
    for service in OcrService:
        get_average_normalized_levenshtein(service, output_lines, summary_gt_set)
    results_path = Path(__file__).resolve().parent.parent / 'results' / 'results.md'
    with open(results_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    print(f"Results written to {results_path}")
