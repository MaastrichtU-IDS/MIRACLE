import json
import sys
import csv
import re

def process(mondo_json_file, mondo_txt_file):
    # Opening JSON file using a context manager (with statement)
    with open(mondo_json_file) as f:
        data = json.load(f)

    with open(mondo_txt_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['ID', 'label'])
        writer.writeheader()

        for node in data['graphs'][0]['nodes']:
            match = re.search(r'(MONDO_\d+)', node.get('id'))
            if match != None:
                # Check if the disease ID is deprecated or not
                meta = node.get('meta')
                if meta != None and meta.get('deprecated') != None:
                    continue
                writer.writerow({'ID': match.group(), 'label': node.get('lbl')})

# download mondo ontology: https://github.com/monarch-initiative/mondo/releases/latest/download/mondo.json
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [in: mondo.json] [out: mondo.csv]") 

    print("Processing the Mondo JSONL file...")
    process(sys.argv[1], sys.argv[2])
    print(f'Completed. See the file "{sys.argv[2]}".')