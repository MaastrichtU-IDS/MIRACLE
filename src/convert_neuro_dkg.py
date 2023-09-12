import pandas as pd
import argparse
import ast

def combine_columns(df, column1, column2, new_column_name):
    new_column = []

    for val1, val2 in zip(df[column1].astype(str), df[column2].astype(str)):
        list1 = list(ast.literal_eval(val1)) if val1.startswith('{') else [val1]
        list2 = list(ast.literal_eval(val2)) if val2.startswith('{') else [val2]
        

        uni_set = set(item for item in list1 + list2 if item != "nan")
        if not uni_set:
            new_column.append(None)
        elif len(uni_set) == 1:
            new_column.append(uni_set.pop())
        else:
            new_column.append(uni_set)

    df[new_column_name] = new_column 
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a CSV file from the neuro_dkg CSV byr combining and dropping columns')

    parser.add_argument('input_csv', help='Path to input CSV file')
    parser.add_argument('output_csv', help='Path to output CSV file')
    parser.add_argument('columns_file', help='Columns for the output CSV')

    args = parser.parse_args()

    # jsonl_file = args.output_jsonl
    df = pd.read_csv(args.input_csv)
    df = combine_columns(df, "AGE_GROUP", "MIN_AGE", "TARGET_GROUP")
    df = df.drop(columns=["AGE_GROUP", "MIN_AGE"], errors='ignore')
    df = df.rename(columns={'DISEASE': 'CONDITION', 'COMORBIDTY': 'CO_MORBIDITY'})

    with open(args.columns_file, 'r') as columns_file:
        columns = [line.strip() for line in columns_file]

    for col in df.columns:
        if not col in columns:
            df = df.drop(columns=[col], errors='ignore')

    df.to_csv(args.output_csv, index=False)
    print(f"Conversion complete. 'text' column extracted and written to '{args.output_csv}'")