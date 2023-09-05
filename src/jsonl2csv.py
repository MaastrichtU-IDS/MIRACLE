import argparse
import json
import csv

def extract_labels_and_text(input_file, output_file):
    with open(input_file, 'r') as jsonl_file, open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['DRUG', 'CONDITION', 'TARGET_GROUP', 'TEXT'])  # Header row

        for line in jsonl_file:
            data = json.loads(line)
            text = data['text']
            spans = data.get('spans', [])

            # This just takes the first annotation !!!!!!!!!
            drug = next((span['text'] for span in spans if span['label'] == 'DRUG'), '')
            condition = next((span['text'] for span in spans if span['label'] == 'CONDITION'), '')
            target_group = next((span['text'] for span in spans if span['label'] == 'TARGET_GROUP'), '')

            writer.writerow([drug, condition, target_group, text])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract labels and text from JSONL and create a CSV file.')
    parser.add_argument('input_file', help='Input JSONL file')
    parser.add_argument('output_file', help='Output CSV file')

    args = parser.parse_args()

    extract_labels_and_text(args.input_file, args.output_file)