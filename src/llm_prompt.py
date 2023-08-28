import argparse
import jsonlines
from spacy_llm.util import assemble

def process_text(text):
    doc = nlp(text)
    print(doc)
    for ent in doc.ents:
        print(ent, ent.label_)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSONL file containing text data (Run with dotenv run --)")
    parser.add_argument("input_jsonl_file", help="Path to the input JSONL file")

    args = parser.parse_args()

    # Assemble a spaCy pipeline from the config
    nlp = assemble("spacy-llm-config.cfg")

    # Open the JSONL file and process each entry
    with jsonlines.open(args.input_jsonl_file) as reader:
        for item in reader:
            text = item.get('text', '')  # Get 'text' field from the JSON entry
            process_text(text)