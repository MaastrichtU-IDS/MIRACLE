import pandas as pd
import json
import sys
import re

def clean_text(text):
    # Replace the matching sequences with a single newline
    regex_pattern = r'(\s){2,}\n'
    return re.sub(regex_pattern, '\n', text).strip()

def csv_to_jsonl(csv_file, jsonl_file):
    text_size_min = 100
    text_size_max = 800
    
    # Read CSV file into a DataFrame
    df = pd.read_csv(csv_file).drop_duplicates('indication')

    # Filter indications based on length between 100 and 400 characters
    filtered_indications = [
        clean_text(indication)
        for indication in df["indication"].tolist()
        if text_size_min <= len(indication) <= text_size_max
    ]

    # Prepare JSONL data
    jsonl_data = [{"text": indication, "meta": {"source": "Dailymed"}} for indication in filtered_indications]

    # Write each dictionary as a JSON object in the JSONL file
    with open(jsonl_file, 'w') as f:
        for record in jsonl_data:
            json.dump(record, f)
            f.write('\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [in: dailymed.csv] [dailymed.jsonl]") 
        
    csv_to_jsonl(sys.argv[1], sys.argv[2])