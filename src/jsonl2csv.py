import argparse
import json
import csv

def extract(input_file, output_file, labels_file):
    print("Extracting texts...")

    # Read labels from the labels file if provided
    labels = set()
    if labels_file:
        with open(labels_file, 'r') as labels_txt:
            labels = set(line.strip() for line in labels_txt)

    rows = []  

    with open(input_file, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            row = {'text': data['text']}

            for span in data.get('spans', []):
                label = span['label']
                row.setdefault(label, set()).add(span['text'])

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
    parser.add_argument('--labels_file', help='Path for labels to make sure all the labels are present as columns in the output CSV file (Optional).')

    args = parser.parse_args()

    extract(args.input_file, args.output_file, args.labels_file)