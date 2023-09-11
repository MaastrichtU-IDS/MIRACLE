import argparse
import json
import csv

def extract(input_file, output_file):
    print("Extracting texts...")

    rows = []  
    labels = set()

    with open(input_file, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            row = {}

            row['text'] = data['text']

            for span in data.get('spans', []):
                label = span['label']
                if row.get(label, None) is None:
                    row[label] = set()
                    labels.add(label)
                row[label].add(span['text'])

            for key, value in row.items():
                if len(value) == 1:
                    row[key] = value.pop()

            rows.append(row)

    if not rows:
        print("No data found. Nothing to write to the CSV file.")
        return

    print("Writing to CSV file...")

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        header = sorted(labels)
        header.append('text')  # Add text column to the end
        writer.writerow(header) 

        for row in rows:
            row_values = [row.get(label, '') for label in header]
            writer.writerow(row_values) 

    print(f"CSV file '{output_file}' created successfully!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract labels and text from a JSONL file and create a CSV file.')
    parser.add_argument('input_file', help='Input JSONL file containing annotated samples')
    parser.add_argument('output_file', help='Output CSV file')

    args = parser.parse_args()

    extract(args.input_file, args.output_file)