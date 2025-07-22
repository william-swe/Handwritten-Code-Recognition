import Levenshtein, re
from pathlib import Path
from utils import OcrService
import matplotlib.pyplot as plt

MAX_COUNTER = 3

def normalize_text_for_comparison(text):
    """
    Normalize text by removing indentation whitespaces, line breaks, and redundant spaces.
    This preserves word spacing but removes formatting differences.
    """
    # Split into lines and strip leading/trailing whitespace from each line
    lines = text.split('\n')
    # Remove leading whitespace (indentation) from each line and normalize spaces within each line
    stripped_lines = [re.sub(r'\s+', ' ', line.strip()) for line in lines]
    # Join lines with single spaces, removing empty lines
    normalized = ' '.join(line for line in stripped_lines if line)
    return normalized

def collect_levenshtein_distances():
    # Collect Levenshtein distances for all services and ground truth files
    gt_dir = Path(__file__).resolve().parent.parent / 'ground_truth'
    # Only include ground truth files that match the pattern exam_<number>.txt or exam_<number1>_<number2>.txt
    all_gt_files = sorted([f for f in gt_dir.glob('*.txt') if re.match(r'exam_\d+(?:_\d+)?\.txt$', f.name)], key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s.name)])
    services = list(OcrService)
    # Group files by exam_<num1>
    gt_grouped = {}
    for f in all_gt_files:
        m = re.match(r'(exam_\d+)(?:_\d+)?\.txt$', f.name)
        if m:
            base = m.group(1)
            gt_grouped.setdefault(base, []).append(f)

    ld_table = {}  # {exam_<num1>: {service: (NLD, LD, result_file_name)}}
    avg_nld = {service: [] for service in services}
    for base, files in gt_grouped.items():
        ld_table[base + '.txt'] = {}
        for service in services:
            results_dir = Path(__file__).resolve().parent.parent / 'results' / service
            pattern = f'{service}_{base}_comp.txt'
            result_file = results_dir / pattern
            best_nld = ''
            best_ld = ''
            best_result_file = ''
            for gt_file in files:
                with open(gt_file, 'r', encoding='utf-8') as fgt:
                    gt_text = fgt.read()
                if not result_file.exists():
                    continue
                with open(result_file, 'r', encoding='utf-8') as f:
                    ocr_text = f.read()
                
                # Normalize texts for comparison (remove indentation and line breaks)
                gt_text_normalized = normalize_text_for_comparison(gt_text)
                ocr_text_normalized = normalize_text_for_comparison(ocr_text)
                
                if not gt_text_normalized and not ocr_text_normalized:
                    nld = 1.0
                    lev_dist = 0
                else:
                    lev_dist = Levenshtein.distance(gt_text_normalized, ocr_text_normalized)
                    nld = 1 - lev_dist / max(len(gt_text_normalized), len(ocr_text_normalized))
                if best_nld == '' or (isinstance(nld, float) and nld > best_nld):
                    best_nld = nld
                    best_ld = lev_dist
                    best_result_file = result_file.name
            if best_nld != '':
                avg_nld[service].append(best_nld)
            # Store tuple (NLD, LD, result_file_name) or ('', '', '')
            if best_nld != '':
                ld_table[base + '.txt'][service] = (best_nld, best_ld, best_result_file)
            else:
                ld_table[base + '.txt'][service] = ('', '', '')
    # Calculate averages
    avg_row = {service: (sum(avg_nld[service])/len(avg_nld[service]) if avg_nld[service] else 0) for service in services}
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

    # Group ground truth files by canonical (exam_<num>.txt)
    gt_files_all = sorted([f for f in gt_dir.glob('*.txt') if re.match(r'exam_\d+(?:_\d+)?\.txt$', f.name)], key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s.name)])
    gt_grouped = {}
    for f in gt_files_all:
        m = re.match(r'(exam_\d+)(?:_\d+)?\.txt$', f.name)
        if m:
            base = m.group(1)
            gt_grouped.setdefault(base, []).append(f)

    # Find all result files for this service
    result_files = list(results_dir.glob(f'{service}_*.txt'))
    def natural_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s.name)]
    result_files = sorted(result_files, key=natural_key)

    # Build a mapping from canonical base (exam_<num>) to all result files for its splits
    result_files_by_canonical = {}
    for result_file in result_files:
        m = re.match(rf'{service}_(exam_\d+(?:_\d+)?)_comp\.txt', result_file.name)
        if not m:
            continue
        base = m.group(1)
        # Canonical base is exam_<num>
        canonical_base = re.match(r'(exam_\d+)', base).group(1)
        result_files_by_canonical.setdefault(canonical_base, []).append(result_file)

    # If summary_gt_files is provided, use only those canonical ground truths (exam_<num>.txt)
    if summary_gt_files is not None:
        canonical_gt_names = [re.match(r'(exam_\d+)', f).group(1) for f in summary_gt_files if re.match(r'exam_\d+\.txt$', f)]
    else:
        canonical_gt_names = sorted(result_files_by_canonical.keys(), key=lambda s: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)])

    nld_list = []
    ld_list = []
    table_rows = []

    # Use summary_gt_files and ld_table if provided to fill the per-service table
    ld_table = None
    if hasattr(get_average_normalized_levenshtein, 'ld_table'):
        ld_table = getattr(get_average_normalized_levenshtein, 'ld_table')
    if summary_gt_files is not None and ld_table is not None:
        # Use the summary's NLD, LD, and result file values for this service
        for canonical_base in canonical_gt_names:
            canonical_gt_name = canonical_base + '.txt'
            nld_tuple = ld_table.get(canonical_gt_name, {}).get(service, ('', '', ''))
            nld_val, ld_val, result_file_name = nld_tuple
            if nld_val == '':
                table_rows.append(("-", canonical_gt_name, '-', '-'))
            else:
                table_rows.append((result_file_name, canonical_gt_name, ld_val, nld_val))
                nld_list.append(nld_val)
                ld_list.append(ld_val)
    else:
        for canonical_base in canonical_gt_names:
            # All result files for this canonical (splits)
            split_result_files = result_files_by_canonical.get(canonical_base, [])
            best_nld = None
            best_ld = None
            best_result_file = None
            best_gt_file = None
            # For each split result file, compare to all ground truths for this canonical
            for result_file in split_result_files:
                gt_files_to_compare = gt_grouped.get(canonical_base, [])
                if not gt_files_to_compare:
                    continue
                with open(result_file, 'r', encoding='utf-8') as f:
                    ocr_text = f.read()
                for gt_file_candidate in gt_files_to_compare:
                    with open(gt_file_candidate, 'r', encoding='utf-8') as fgt:
                        gt_text = fgt.read()
                    
                    # Normalize texts for comparison (remove indentation and line breaks)
                    gt_text_normalized = normalize_text_for_comparison(gt_text)
                    ocr_text_normalized = normalize_text_for_comparison(ocr_text)
                    
                    if not gt_text_normalized and not ocr_text_normalized:
                        nld = 0.0
                        lev_dist = 0
                    else:
                        lev_dist = Levenshtein.distance(gt_text_normalized, ocr_text_normalized)
                        nld = 1 - lev_dist / max(len(gt_text_normalized), len(ocr_text_normalized))
                    if (best_nld is None) or (nld > best_nld):
                        best_nld = nld
                        best_ld = lev_dist
                        best_result_file = result_file
                        best_gt_file = gt_file_candidate
            canonical_gt_name = canonical_base + '.txt'
            if best_nld is not None:
                nld_list.append(best_nld)
                ld_list.append(best_ld)
                table_rows.append((best_result_file.name, canonical_gt_name, best_ld, best_nld))
            else:
                # No result for this service/canonical ground truth, add a row with blanks
                table_rows.append(("-", canonical_gt_name, '-', '-'))

    # Sort table_rows by ground truth file name (exam_1.txt, exam_2.txt, ...)
    def gt_sort_key(row):
        # row[1] is canonical_gt_name, e.g., exam_1.txt
        parts = re.split(r'(\d+)', row[1])
        return [int(p) if p.isdigit() else p.lower() for p in parts]
    table_rows = sorted(table_rows, key=gt_sort_key)

    nld_vals = [v for v in nld_list if isinstance(v, (int, float))]
    ld_vals = [v for v in ld_list if isinstance(v, (int, float))]
    if nld_vals:
        avg_nld = sum(nld_vals) / len(nld_vals)
    else:
        avg_nld = 0.0
    if ld_vals:
        avg_ld = sum(ld_vals) / len(ld_vals)
    else:
        avg_ld = 0.0
    # Markdown table output only
    if table_rows:
        output_lines.append(f"## {service.capitalize()} OCR Results Table\n\n")
        output_lines.append("| OCR Output File | Ground Truth File | Levenshtein Distance | NLD |\n")
        output_lines.append("|:---:|:---:|:---:|:---:|\n")
        for row in table_rows:
            if isinstance(row[3], float):
                output_lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]:.4f} |\n")
            else:
                output_lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n")
        output_lines.append(f"| **Average** |  | **{avg_ld:.2f}** | **{avg_nld:.4f}** |\n")
        output_lines.append("\n")

if __name__ == "__main__":
    # Generate a summary table of Levenshtein distances for all OCR services
    ld_table, avg_row, services = collect_levenshtein_distances()
    output_lines = []

    output_lines.append("# OCR Result Summary\n\n")
    output_lines.append("## OCR Normalized Levenshtein Distance (NLD) Summary\n\n")
    # Dynamic header
    header = ["Ground Truth File"] + [
        f"{service.upper()} NLD" if service == 'gpt' else f"{service.title().replace('_', ' ')} NLD" 
        for service in services
    ]
    output_lines.append(f"| {' | '.join(header)} |\n")
    output_lines.append(f"|{'|'.join([':---:' for _ in header])}|\n")
    summary_gt_files = []
    for gt_file in ld_table:
        # Exclude if all services have missing NLD
        if all((ld_table[gt_file][service][0] if isinstance(ld_table[gt_file][service], tuple) else ld_table[gt_file][service]) == '' for service in services):
            continue
        summary_gt_files.append(gt_file)
        row = [gt_file]
        for service in services:
            val = ld_table[gt_file][service]
            nld_val = val[0] if isinstance(val, tuple) else val
            if nld_val == '':
                row.append("-")
            else:
                row.append(f"{nld_val:.3f}")
        output_lines.append(f"| {' | '.join(row)} |\n")
    avg_row_fmt = [f"{avg_row[service]:.3f}" if avg_row[service] != 0 else "-" for service in services]
    output_lines.append(f"| **Average** | {' | '.join(avg_row_fmt)} |\n\n")

    # --- Generate and insert graph ---
    # Prepare data for the graph
    service_labels = [service.upper() if service == 'gpt' else service.title().replace('_', ' ') for service in services]
    avg_nld_values = [avg_row[service] for service in services]
    plt.figure(figsize=(8, 6))
    bars = plt.bar(service_labels, avg_nld_values, color='skyblue')
    plt.ylabel('Average Normalized Levenshtein Distance (NLD)')
    plt.title('Average NLD by OCR Service')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.xticks(rotation=30, ha='right')
    # Set y-axis ticks to have a gap of 0.3
    import numpy as np
    min_y = 0
    max_y = max(avg_nld_values + [1.0])
    plt.yticks(np.arange(min_y, max_y + 0.3, 0.3))
    for bar, value in zip(bars, avg_nld_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{value:.3f}', ha='center', va='bottom')
    graph_path = Path(__file__).resolve().parent.parent / 'results' / 'avg_levenshtein_distance.png'
    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()
    # Insert image below the summary table
    output_lines.append(f'![Average Normalized Levenshtein Distance by OCR Service](avg_levenshtein_distance.png)\n\n')
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

    # Pass ld_table to get_average_normalized_levenshtein for summary-aligned per-service tables
    def get_avg_norm_lev_with_ld_table(service, output_lines, summary_gt_files, ld_table):
        get_average_normalized_levenshtein.ld_table = ld_table
        get_average_normalized_levenshtein(service, output_lines, summary_gt_files)
        del get_average_normalized_levenshtein.ld_table

    for service in OcrService:
        get_avg_norm_lev_with_ld_table(service, output_lines, summary_gt_set, ld_table)
    results_path = Path(__file__).resolve().parent.parent / 'results' / 'results.md'
    with open(results_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    print(f"Results written to {results_path}")
