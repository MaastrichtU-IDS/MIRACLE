import json
import argparse
from tqdm import tqdm

def check_overlap(start, end, added_spans):
    for label in added_spans:
        for span_start, span_end in added_spans[label]:
            if not (end < span_start or span_end < start):
                return True
    return False

def process_jsonl(input_file, output_file):
    with open(input_file, 'r') as jsonl_file:
        jsonl_data = jsonl_file.readlines()

    processed_data_list = []

    for json_str in tqdm(jsonl_data, desc="Processing JSONL"):
        annotation_data = json.loads(json_str)

        if annotation_data.get("spans", None) is None:
            processed_data_list.append(annotation_data)
            continue

        # Create a dictionary to store all labels and their texts
        label_texts = {}

        # Create a dictionary to keep track of added spans
        added_spans = {}

        # Add the already annotated spans to the added_spans dictionary
        for span in annotation_data["spans"]:
            label = span["label"]
            start = span["start"]
            end = span["end"]
            if label in added_spans:
                added_spans[label].add((start, end))
            else:
                added_spans[label] = set()
                added_spans[label].add((start, end))

        # Iterate through spans and collect label texts
        for span in annotation_data["spans"]:
            label = span["label"]
            text = annotation_data["text"][span["start"]:span["end"]]
            if label in label_texts:
                label_texts[label].append(text)
            else:
                label_texts[label] = [text]

        # Iterate through tokens and add labels for all occurrences
        for label, texts in label_texts.items():
            for text in texts:
                if label not in added_spans:
                    added_spans[label] = set()

                for token in annotation_data["tokens"]:
                    # Make sure to not break any pre existing token
                    if token["text"] == text and (token["start"], token["end"]) not in added_spans[label]:
                        
                        start = token["start"]
                        end = token["end"]
                        
                        if not check_overlap(start, end, added_spans):
                            span = {
                                "start": start,
                                "end": end,
                                "token_start": token["id"],
                                "token_end": token["id"],
                                "label": label,
                            }
                            annotation_data["spans"].append(span)
                            added_spans[label].add((token["start"], token["end"]))

        # Sort spans by start position
        annotation_data["spans"] = sorted(annotation_data["spans"], key=lambda x: x["start"])
        processed_data_list.append(annotation_data)

    # Write the updated JSON objects to the output JSONL file
    with open(output_file, 'w') as output_jsonl:
        for processed_data in processed_data_list:
            output_jsonl.write(json.dumps(processed_data) + '\n')

    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotate all the occurances of all the labeled texts")
    parser.add_argument("input", required=True, help="Input JSONL file")
    parser.add_argument("output", required=True, help="Output JSONL file")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    process_jsonl(input_file, output_file)
