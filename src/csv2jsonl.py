import pandas as pd
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a Prodigy annotation sample file by using "text" column from the given CSV file')

    parser.add_argument('input_csv', help='Path to input CSV file')
    parser.add_argument('output_jsonl', help='Path to output JSONL file')

    args = parser.parse_args()

    jsonl_file = args.output_jsonl
    df = pd.read_csv(args.input_csv, usecols=['text'])
    df.to_json(jsonl_file, orient='records', lines=True, force_ascii=False)

    print(f"Conversion complete. 'text' column extracted and written to '{jsonl_file}'")