import json
import sys
import csv

def create_json_object(text, label):
    words = text.split()
    pattern = [{"lower": word.lower()} for word in words]
    return {"label": label, "pattern": pattern}

def to_jsonl(csv_files, labels, jsonl_file):
    with open(jsonl_file, 'w') as outfile:
        for i, csv_file in enumerate(csv_files):
            label = labels[i]
            with open(csv_file, 'r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    json_object = create_json_object(row[1], label)
                    outfile.write(json.dumps(json_object) + '\n')

if __name__ == "__main__":
    if len(sys.argv) < 4 or (len(sys.argv) - 2) % 2 != 0:
        sys.exit(f"Right usage: {sys.argv[0]} [in: csv_file1.csv] [in: label1] [in: csv_file2.csv] [in: label2] ... [out: all_patterns.jsonl]") 

    csv_files = []
    labels = []
    for i in range(1, len(sys.argv)-2, 2):
        csv_files.append(sys.argv[i])
        labels.append(sys.argv[i+1])

    to_jsonl(csv_files, labels, sys.argv[-1])