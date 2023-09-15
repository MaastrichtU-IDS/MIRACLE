import argparse
import json
import random

def split_jsonl(input_file, train_output_file, eval_output_file, split_ratio, random_seed=None):
    total_samples = 0
    num_ignored = 0

    print(f"Loading data from {input_file}...")
    with open(input_file, 'r') as jsonl_file:
        data = []
        for line in jsonl_file:
            total_samples += 1
            item = json.loads(line)
            if item.get('answer') != 'ignore':
                data.append(item)
            else:
                num_ignored += 1

    # Set a random seed for reproducibility if provided
    if random_seed is not None:
        random.seed(random_seed)

    random.shuffle(data)
    num_samples = len(data)
    num_train_samples = int(num_samples * split_ratio)
    num_eval_samples = num_samples - num_train_samples

    print(f"Number of samples:")
    print(f"Total:  \t {total_samples}")
 
    if num_ignored > 0:
        print(f"Ignored:\t {num_ignored}")
 
    print(f"Train:  \t {num_train_samples}")
    print(f"Eval:   \t {num_eval_samples}")

    train_data = data[:num_train_samples]
    eval_data = data[num_train_samples:]

    print(f"Writing train data to {train_output_file}...")
    with open(train_output_file, 'w') as train_file:
        for item in train_data:
            train_file.write(json.dumps(item) + '\n')

    print(f"Writing eval data to {eval_output_file}...")
    with open(eval_output_file, 'w') as eval_file:
        for item in eval_data:
            eval_file.write(json.dumps(item) + '\n')

    print("Splitting and writing complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split JSONL data into training and evaluation sets.')
    parser.add_argument('input_file', help='Input JSONL file')
    parser.add_argument('train_output_file', help='Output training JSONL file')
    parser.add_argument('eval_output_file', help='Output evaluation JSONL file')
    parser.add_argument('--split_ratio', type=float, default=0.8, help='Split ratio (default: 0.8)')
    parser.add_argument('--random_seed', type=int, default=None, help='Random seed for reproducibility')

    args = parser.parse_args()

    split_jsonl(args.input_file, args.train_output_file, args.eval_output_file, args.split_ratio, args.random_seed)
