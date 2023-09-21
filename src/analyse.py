import os
import json
import csv
import argparse

def process_db(input_file: str):
    counts = {}  # Dictionary to store label counts

    with open(input_file, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)

            for span in data.get('spans', []):
                label = span['label']
                counts[label] = counts.get(label, 0) + 1

    return counts

def calculate_percentage(count, total):
    return round((count / total) * 100, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate label distribution statistics.")
    parser.add_argument("training_dataset", help="Path to the training dataset in JSONL format")
    parser.add_argument("output_csv", help="Path to the output CSV file to save statistics")
    parser.add_argument("--model_dir_path", help="Path to the model directory containing meta.json")

    args = parser.parse_args()

    # Load model performance data
    if args.model_dir_path:
        model_path = os.path.join(args.model_dir_path, "meta.json")
        with open(model_path) as file:
            performances = json.load(file)['performance']['ents_per_type']

    # Process the training dataset
    counts = process_db(args.training_dataset)
    total = sum(counts.values())

    # Sort label counts in descending order
    counts_sorted = sorted(counts.items(), key=lambda item: item[1], reverse=True)

    # Write statistics to the output CSV file
    with open(args.output_csv, 'w', newline='') as csvfile:
        if args.model_dir_path:
            headers = ['Label', 'Count', 'Frequency', 'Precision', 'Recall', 'F1Score']
        else:
            headers =  ['Label', 'Count', 'Frequency']
        
        writer = csv.DictWriter(csvfile, headers)
        writer.writeheader()

        if args.model_dir_path:
            perf_default = {'p': 0.00, 'r': 0.00, 'f': 0.00}
            writer.writerows({
                'Label': label,
                'Count': count,
                'Frequency': "%.2f" % round(calculate_percentage(count, total), 2),
                'Precision': "%.2f" % round(performances.get(label, perf_default)['p'] * 100, 2),
                'Recall': "%.2f" % round(performances.get(label, perf_default)['r'] * 100, 2),
                'F1Score': "%.2f" % round(performances.get(label, perf_default)['f'] * 100, 2)
            } for label, count in counts_sorted)
        else:
            writer.writerows({
                'Label': label,
                'Count': count,
                'Frequency': "%.2f" % round(calculate_percentage(count, total), 2),
            } for label, count in counts_sorted)

    # Print total annotation count and the location of the saved statistics
    print(f'Total # annotations: {total}')
    print(f'Statistics saved in "{args.output_csv}"')