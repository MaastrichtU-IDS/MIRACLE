import json
import sys
import csv

# Function to convert a drug name toll the desired JSON object format
def create_json_object(drug_name):
    words = drug_name.split()
    pattern = [{"lower": word.lower()} for word in words]
    #TODO: We can also include the drug id here 
    return {"label": "DRUG", "pattern": pattern}


def to_jsonl(drug_csv_file, patterns_file):
    with open(drug_csv_file, 'r') as infile, open(patterns_file, 'w') as outfile:
        reader = csv.reader(infile)
        for row in reader:
            json_object = create_json_object(row[1])
            outfile.write(json.dumps(json_object) + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [in: drugs.csv] [out: patterns.jsonl]") 

    to_jsonl(sys.argv[1], sys.argv[2])