import os
import json
import csv
import argparse
from collections import Counter
from prodigy.components.db import connect
from prodigy.util import get_labels

def process_db(db_name: str, counts: Counter):
    db = connect()
    examples = db.get_dataset(db_name)
    total = 0
    for eg in examples:
        eg_labels = [span["label"] for span in eg.get("spans", [])]
        for label in eg_labels:
            counts[label] += 1
            total += 1
    return total

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate label distribution statistics.")
    parser.add_argument("model_dir_path", help="Path to the model directory")
    parser.add_argument("training_dataset", help="Name of the training dataset")
    parser.add_argument("labels_file", help="Path to the labels.txt file")
    parser.add_argument("output_csv", help="Path to the output CSV file")

    args = parser.parse_args()

    model_path = os.path.join(args.model_dir_path, "meta.json")

    with open(model_path) as file:
        performances = json.load(file)['performance']['ents_per_type']

    counts = Counter()
    for label in get_labels(args.labels_file):
        counts[label] = 0

    total = process_db(args.training_dataset, counts)

    perf_default = {'p': 0.0, 'r': 0.0, 'f': 0.0}

    counts_sorted = sorted(counts.items(), key=lambda item: item[1], reverse=True)

    with open(args.output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['Label', 'Count', 'Distribution', 'Precision', 'Recall', 'F1Score'])
        writer.writeheader()

        writer.writerows({
            'Label': label,
            'Count': count,
            'Distribution': round((count / total) * 100, 2),
            'Precision': round(performances.get(label, perf_default)['p'] * 100, 2),
            'Recall': round(performances.get(label, perf_default)['r'] * 100, 2),
            'F1Score': round(performances.get(label, perf_default)['f'] * 100, 2)
        } for label, count in counts_sorted)

    print(f'Total # annotation is {total}. Statistics saved in "{args.output_csv}"')