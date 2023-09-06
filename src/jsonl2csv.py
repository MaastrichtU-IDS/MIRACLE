import argparse
import json
import csv
from collections import defaultdict

def extract_labels_and_text(input_file, output_file, header_labels_file):
    print("Extracting labels and text...")

    with open(header_labels_file, 'r') as labels_file:
        header_labels = [line.strip() for line in labels_file]
    header_labels.append('text')
    rows = []  # Create a list to store the rows

    with open(input_file, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)

            row = {key: set() for key in header_labels}

            row['text'] = data['text']

            for span in data.get('spans', []):
                row[span['label']].add(span['text'])

            for key, value in row.items():
                if not value:
                    row[key] = None
                elif len(value) == 1:
                    row[key] = value.pop()

            rows.append(row.values())

    print("Writing to CSV file...")

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header_labels)  # Use the labels from the file as CSV header
        writer.writerows(rows)  # Use writerows to write all rows at once

    print(f"CSV file '{output_file}' created successfully!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract labels and text from JSONL and create a CSV file.')
    parser.add_argument('input_file', help='Input JSONL file')
    parser.add_argument('output_file', help='Output CSV file')
    parser.add_argument('labels_file', help='File containing labels')

    args = parser.parse_args()

    extract_labels_and_text(args.input_file, args.output_file, args.labels_file)
