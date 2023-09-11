import argparse
import json

class Stat:
    def __init__(self, sample, labels):
        self.sample = sample
        self.labels = labels

    def get_sample(self):
        return self.sample

    def get_labels(self):
        return self.labels

def select(samples, num_sample):
    # Sort the list in descending order based on the length of labels dictionary
    sorted_samples = sorted(samples, key=lambda stat: len(stat.get_labels()), reverse=True)
    return sorted_samples[:num_sample]

def count(input_file):
    samples = []  # List to store Stat objects
    label_counts = {}  # Dictionary to store label counts

    with open(input_file, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)

            diff = {}

            # Count different labels
            for span in data.get('spans', []):
                label = span['label']
                diff[label] = diff.get(label, 0) + 1

            # Update label instance counts
            for label in diff.keys():
                label_counts[label] = label_counts.get(label, 0) + 1

            samples.append(Stat(data, diff))

    return samples, label_counts

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select curated examples with the most different labels.')
    parser.add_argument('input_jsonl', help='Input JSONL file containing labeled examples.')
    parser.add_argument('output_jsonl', help='Output JSONL file containing selected examples with only the "text" field.')
    parser.add_argument('num_sample', type=int, help='Number of samples to select.')
    parser.add_argument('--text_only', action='store_true', help='Output only the "text" field (optional).')

    args = parser.parse_args()

    print(f"Counting samples from '{args.input_jsonl}'...")
    counted_samples, label_counts = count(args.input_jsonl)
    print(f"Found {len(counted_samples)} samples.")

    # Print label counts in descending order by count
    print("Sample Counts & Label:")
    sorted_label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
    for label, count in sorted_label_counts:
        print(f"{count} \t {label}")

    # Print the count of texts with different label counts
    print("\nDifferent Label Counts & Sample Counts")
    count_texts = {}
    for sample in counted_samples:
        n = len(sample.get_labels())
        count_texts[n] = count_texts.get(n, 0) + 1

    sorted_count_texts = sorted(count_texts.items(), key=lambda x: x[0], reverse=True)
    for diff_label_count, text_count in sorted_count_texts:
        print(f"{diff_label_count} \t {text_count}")

    if args.num_sample <= len(counted_samples):
        selected_samples = select(counted_samples, args.num_sample)
        print(f"Selected {args.num_sample} samples based on label count.")

        # Write the selected_samples as a JSONL file
        with open(args.output_jsonl, 'w') as output_file:
            if args.text_only:
                for sample in selected_samples:
                    output_file.write(json.dumps({'text': sample.get_sample()['text']}) + '\n')
            else:
                for sample in selected_samples:
                    output_file.write(json.dumps(sample.get_sample()) + '\n')

        print(f"Saved selected samples to '{args.output_jsonl}'.")
    else:
        print(f"Number of samples requested ({args.num_sample}) is greater than the available samples ({len(counted_samples)}).")
