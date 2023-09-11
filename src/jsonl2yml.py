import json
import yaml
import argparse

def get_text(tokens, token_start, token_end):
    texts = ""
    token_list = tokens[token_start:token_end + 1]
    for i, token in enumerate(token_list):
        text = token["text"]
        if token["ws"] == True and i != len(token_list) - 1:
            texts += text + " " 
        else:
            texts += text 
        

    return texts
def jsonl_to_yaml(input_file, output_file):
    samples = []

    # Read the JSONL file line by line and parse each line as JSON
    with open(input_file, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line.strip())
            if data["answer"] == "ignore":
                continue
            entities = {}
            for span in data.get('spans', []):
                label = span['label']
                if not entities.get(label, None):
                    # Use set to prevent dublication
                    entities[label] = set()
                entities[label].add(get_text(data["tokens"], span["token_start"], span["token_end"]))

            for key, value in entities.items():
                # Convert set to list 
                entities[key] = list(value)

            samples.append({
                'text': data['text'],
                'entities': entities
            })
            
    yaml_str = yaml.dump(samples, default_flow_style=False, width=float("inf"))
    # yaml_str =  yaml.dump(samples, default_flow_style=False)
    # Write the YAML data to the output file
    with open(output_file, 'w') as yaml_file:
        yaml_file.write(yaml_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSONL to YAML')
    parser.add_argument('input_file', help='Input JSONL file path')
    parser.add_argument('output_file', help='Output YAML file path')

    args = parser.parse_args()

    jsonl_to_yaml(args.input_file, args.output_file)
    print(f"Data from {args.input_file} has been converted and written to {args.output_file}")