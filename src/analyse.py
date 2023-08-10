import sys
import csv
from collections import Counter
from prodigy.components.db import connect

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
    if len(sys.argv) != 4:
        sys.exit(f"Right usage: {sys.argv[0]} [in: dataset-name] [in: labels.txt] [out: label_dist.csv]") 

    counts = Counter()
    with open(sys.argv[2]) as file:
        for line in file:
            # Remove the new line and initialize the label
            counts[line.strip()] = 0

    total = process_db(sys.argv[1], counts)
    counts_sorted = sorted(counts.items(), key=lambda item: item[1], reverse=True)

    # Write the results into a CSV file
    with open(sys.argv[3], 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['label', 'count', 'distribution'])
        writer.writeheader()
        writer.writerows({'label': label, 'count': count, 'distribution': round((count / total) * 100, 2)} for label, count in counts_sorted)

    print(f'Total # annotation {total}. Statistics are saved in "{sys.argv[3]}"')