from spacy.scorer import Scorer
from spacy.training.example import Example
from spacy_llm.util import assemble
import json
import csv
import argparse
from tqdm import tqdm 

def load_dataset(file_path):
    examples = []
    label_counts = {}  # Dictionary to store label counts
    total_annotations = 0  # Total number of annotations

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            if data['answer'] != 'ignore':
                text = data['text']
                entities = data['spans']
                annotations = {(span['start'], span['end'], span['label']) for span in entities}
                examples.append((text, annotations))

                # Update label counts
                for label in list(span['label'] for span in entities):
                    label_counts[label] = label_counts.get(label, 0) + 1
                total_annotations += len(entities)

    return examples, label_counts, total_annotations

def evaluate(ner_model, examples):
    scorer = Scorer()
    example_list = []
    with tqdm(total=len(examples), desc="Evaluating NER") as pbar:  # Initialize tqdm with the total number of examples
        for input_text, annotations in examples:
            doc = ner_model(input_text)
            gold = Example.from_dict(doc, {"entities": list(annotations)})
            example_list.append(gold)
            pbar.update(1)  # Update the progress bar for each processed example
    scores = scorer.score(example_list)
    return scores

def save_per_label_evaluation(filename, per_label_scores, label_counts, total_annotations):
    # Sort per-label scores by label count in descending order
    sorted_per_label_scores = sorted(per_label_scores.items(), key=lambda x: label_counts.get(x[0], 0), reverse=True)

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Label', 'Count', 'Frequency', 'Precision', 'Recall', 'F1 Score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for label, scores in sorted_per_label_scores:
            # Multiply by 100 and round to two decimal places
            precision = f"{scores['p'] * 100:.2f}"  
            recall = f"{scores['r'] * 100:.2f}" 
            f1_score = f"{scores['f'] * 100:.2f}" 
            label_count = label_counts.get(label, 0)
            frequency = f"{(label_count / total_annotations * 100):.2f}" if total_annotations > 0 else "0.00"
            writer.writerow({'Label': label, 'Count': label_count, 'Frequency': frequency, 'Precision': precision, 'Recall': recall, 'F1 Score': f1_score})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measures the LLM performance on the given dataset")
    parser.add_argument("dataset", help="Path to the Prodigy JSONL annotation dataset file")
    parser.add_argument("config", help="Path to the spaCy LLM configuration file")
    parser.add_argument("output", help="Path to the output statistics CSV file")

    args = parser.parse_args()

    dataset_path = args.dataset
    config_path = args.config
    output_path = args.output

    print(f"Dataset Path: {dataset_path}")
    print(f"Configuration File Path: {config_path}")
    print(f"Output CSV File Path: {output_path}")

    # Load the dataset and get label counts and total annotations
    examples, label_counts, total_annotations = load_dataset(dataset_path)

    # Load the LLM NER model with the custom configuration file
    nlp = assemble(config_path)

    # Evaluate the model on your dataset
    results = evaluate(nlp, examples)

    # Print overall precision, recall, and F1 scores with two-digit precision
    precision = results['ents_p'] * 100
    recall = results['ents_r'] * 100
    f1_score = results['ents_f'] * 100
    print(f"Precision: \t{precision:.2f}")
    print(f"Recall: \t{recall:.2f}")
    print(f"F1 Score: \t{f1_score:.2f}")

    # Print per-label evaluation results into a CSV file with two-digit precision
    per_label_scores = results['ents_per_type']
    save_per_label_evaluation(output_path, per_label_scores, label_counts, total_annotations)