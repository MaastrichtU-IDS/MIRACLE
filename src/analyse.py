import os
import json
import csv
import argparse

def process_db(input_file):
    counts = {}  # Dictionary to store label counts

    with open(input_file, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)

            for span in data.get('spans', []):
                label = span['label']
                counts[label] = counts.get(label, 0) + 1

    return counts

def calculate_frequency(count, total):
    return round((count / total) * 100, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate label distribution statistics for a dataset, optionally with an evaluation dataset and model performance metrics.")
    parser.add_argument("training_dataset", help="Path to the dataset (either the whole dataset or the training dataset) in JSONL format")
    parser.add_argument("output_csv", help="Path to the output CSV file to save statistics")
    parser.add_argument("--eval_dataset", help="Path to the optional evaluation dataset in JSONL format")
    parser.add_argument("--model", help="Path to the optional model directory containing meta.json")

    args = parser.parse_args()

    # Load model performance data
    if args.model:
        model_path = os.path.join(args.model, "meta.json")
        with open(model_path) as file:
            performances = json.load(file)['performance']['ents_per_type']

    # Process the training dataset
    train_counts = process_db(args.training_dataset)
    total_train = sum(train_counts.values())

    # Process the evaluation dataset
    if args.eval_dataset:
        eval_counts = process_db(args.eval_dataset)
        total_eval = sum(eval_counts.values())
    else:
        eval_counts = {}
        total_eval = 0

    # Sort label counts in descending order
    train_counts_sorted = sorted(train_counts.items(), key=lambda item: item[1], reverse=True)
    eval_counts_sorted = sorted(eval_counts.items(), key=lambda item: item[1], reverse=True)

    # Write statistics to the output CSV file
    with open(args.output_csv, 'w', newline='') as csvfile:
        headers = ['Label']
        
        if args.eval_dataset:
            headers.extend(['Total Count', 'Total Frequency', 'Count Train', 'Count Eval'])
        else:    
            headers.extend(['Count', 'Frequency'])
        
        if args.model:
            headers.extend(['Precision', 'Recall', 'F-measure'])
        
        writer = csv.DictWriter(csvfile, headers)
        writer.writeheader()

        perf_default = {'p': 0.00, 'r': 0.00, 'f': 0.00}
        
        for label, count in train_counts_sorted:
            row = {
                'Label': label
            }
            
            if args.eval_dataset:
                row['Total Count'] = count + eval_counts.get(label, 0)
                row['Total Frequency'] = "%.2f" % calculate_frequency(count + eval_counts.get(label, 0), total_train + total_eval)
                row['Count Train'] = count
                row['Count Eval'] = eval_counts.get(label, 0)
            else:            
                row['Count'] = count + eval_counts.get(label, 0)
                row['Frequency'] = "%.2f" % calculate_frequency(count, total_train)

            if args.model:
                row['Precision'] = "%.2f" % round(performances.get(label, perf_default)['p'] * 100, 2)
                row['Recall'] = "%.2f" % round(performances.get(label, perf_default)['r'] * 100, 2)
                row['F-measure'] = "%.2f" % round(performances.get(label, perf_default)['f'] * 100, 2)
            
            writer.writerow(row)
    
    # Print total annotation count and the location of the saved statistics
    if args.eval_dataset:
        print(f'Total number of annotations in the training dataset: {total_train}')
        print(f'Total number of annotations in the evaluation dataset: {total_eval}')
    else:
        print(f'Total number of annotations in the dataset: {total_train}')
    print(f'Statistics saved in "{args.output_csv}"')