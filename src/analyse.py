import sys
import os
import json
import csv
from collections import Counter
from prodigy.components.db import connect
from prodigy.util import get_labels

def process_db(db_name: str, counts: Counter):
    db = connect()
    examples = db.get_dataset(db_name)
    total = 0
    for eg in examples:
        # Access the annotated labels
        eg_labels = [span["label"] for span in eg.get("spans", [])]
        for label in eg_labels:
            counts[label] += 1
            total += 1
    return total

if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(f"Right usage: {sys.argv[0]} [in: model_dir_path] [in: labels.txt] [in: training-dataset] [out: label_dist.csv]") 

    # Read the model meta data
    model_path = os.path.join(sys.argv[1], "meta.json")

    with open(model_path) as file:
        performances = json.load(file)['performance']['ents_per_type']

    # Initialize a Counter object with the labels
    counts = Counter()
    for label in get_labels(sys.argv[2]):
        counts[label] = 0

    total = process_db(sys.argv[3], counts)

    perf_default = {'p': 0.0, 'r': 0.0, 'f': 0.0}

    # Sort the counts in decreasing order
    counts_sorted = sorted(counts.items(), key=lambda item: item[1], reverse=True)

    # Write the results into given CSV file
    with open(sys.argv[4], 'w', newline='') as csvfile:
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

    print(f'Total # annotation is {total}. Statistics saved in "{sys.argv[4]}"')