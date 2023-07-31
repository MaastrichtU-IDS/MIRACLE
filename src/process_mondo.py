import json
import sys
import csv
import re

# Function to convert a disease name to the desired JSON object format
def create_json_object(disease_name):
    words = disease_name.split()
    pattern = [{"lower": word.lower()} for word in words]
    return {"label": "CONDITION", "pattern": pattern}

def process_mondo(mondo_json_file, mondo_txt_file):
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
                # f_out.write(f"{match.group()} {node.get('lbl')}\n")
                writer.writerow({'ID': match.group(), 'label': node.get('lbl')})

def to_jsonl(diseases_csv_file, patterns_file):
    with open(diseases_csv_file, 'r') as infile, open(patterns_file, 'w') as outfile:
        reader = csv.reader(infile)
        for row in reader:
            json_object = create_json_object(row[1])
            outfile.write(json.dumps(json_object) + '\n')

# download mondo ontology: https://github.com/monarch-initiative/mondo/releases/latest/download/mondo.json
if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(f"Right usage: {sys.argv[0]} [in: mondo.json] [out: mondo_diseases.csv] [out: mondo_disease_patterns.jsonl]") 

    process_mondo(sys.argv[1], sys.argv[2])
    to_jsonl(sys.argv[2], sys.argv[3])