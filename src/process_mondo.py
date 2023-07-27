import json
import sys

# Function to convert a drug name to the desired JSON object format
def create_json_object(drug_name):
    words = drug_name.split()
    pattern = [{"lower": word.lower()} for word in words]
    return {"label": "DISEASE", "pattern": pattern}

def process_mondo(mondo_json_file, mondo_txt_file):
    # Opening JSON file using a context manager (with statement)
    with open(mondo_json_file) as f:
        data = json.load(f)

    # Accessing the 'nodes' list directly and printing 'ibl' values
    with open(mondo_txt_file, 'w') as f_out:
        for node in data['graphs'][0]['nodes']:
            ibl = node.get('lbl')
            if ibl is not None:
                # Writing the 'ibl' values to the output file
                f_out.write(ibl + '\n')

def to_jsonl(mondo_txt_file, mondo_patterns_file):
    # Read drug names from the TXT file
    with open(mondo_txt_file, 'r') as f:
        drug_names = f.read().splitlines()

    # Create and write JSON objects to the JSONL file
    with open(mondo_patterns_file, 'w') as f:
        for drug_name in drug_names:
            json_object = create_json_object(drug_name)
            f.write(json.dumps(json_object) + '\n')

# download mondo ontology: https://github.com/monarch-initiative/mondo/releases/latest/download/mondo.json

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(f"Right usage: {sys.argv[0]} [in: mondo.json] [out: mondo_disease.txt] [out: mondo_patterns.jsonl]") 

    process_mondo(sys.argv[1], sys.argv[2])
    to_jsonl(sys.argv[2], sys.argv[3])