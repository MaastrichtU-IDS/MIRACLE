import argparse
import ast
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from fuzzywuzzy import fuzz

# Define a function for text similarity (you can adjust the threshold)
def is_similar(str1, str2, similarity_threshold):
    return fuzz.ratio(str1, str2) > similarity_threshold

def calculate_ner_metrics(gold_standard_col, ner_annotations_col, similarity_threshold):
    # Initialize counters for True Positives (TP), False Positives (FP), and False Negatives (FN)
    tp = 0
    fp = 0
    fn = 0

    # Iterate through each annotation in the gold standard
    for labels, preds in zip(gold_standard_col, ner_annotations_col):
        label_list = list(ast.literal_eval(labels)) if labels.startswith('{') else [labels]
        pred_list = list(ast.literal_eval(preds)) if preds.startswith('{') else [preds]
        
        for label in label_list:
            found_match = False
            for pred in pred_list:
                if is_similar(label, pred, similarity_threshold):
                    found_match = True
                    tp += 1
                    break  # Exit the inner loop once a match is found
            if not found_match:
                fn += 1

    # Calculate false positives (FP) by subtracting true positives (TP) from the total ner_annotations
    fp = len(ner_annotations_col) - tp

    # Calculate precision, recall, and F1 score (avoid division by zero)
    if tp + fp == 0:
        precision = 0
    else:
        precision = tp / (tp + fp)

    if tp + fn == 0:
        recall = 0
    else:
        recall = tp / (tp + fn)

    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1

def compare_csv_columns(gold_csv, model_csv, similarity_threshold, exclude_columns=None):
    # Read CSV files into pandas DataFrames
    gold_df = pd.read_csv(gold_csv)
    model_df = pd.read_csv(model_csv)

    # Exclude specified columns
    if exclude_columns:
        gold_df = gold_df.drop(columns=exclude_columns, errors='ignore')
        model_df = model_df.drop(columns=exclude_columns, errors='ignore')

    # Initialize dictionaries to store metrics for each column
    precision_dict = {}
    recall_dict = {}
    f1_dict = {}

    # Iterate through columns in both DataFrames
    for column in gold_df.columns:
        gold_col = gold_df[column].astype(str)
        model_col = model_df[column].astype(str)
        # Calculate metrics for the current column
        precision, recall, f1 = calculate_ner_metrics(gold_col, model_col, similarity_threshold)

        # Store metrics in dictionaries
        precision_dict[column] = precision
        recall_dict[column] = recall
        f1_dict[column] = f1

    return precision_dict, recall_dict, f1_dict

def calculate_overall_metrics(precision_dict, recall_dict, f1_dict):
    # Calculate overall metrics by taking weighted averages based on the number of columns
    num_columns = len(precision_dict)
    overall_precision = sum(precision_dict.values()) / num_columns
    overall_recall = sum(recall_dict.values()) / num_columns
    overall_f1 = sum(f1_dict.values()) / num_columns

    return overall_precision, overall_recall, overall_f1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare two CSV files and calculate NER metrics.")
    parser.add_argument("gold_csv", help="Path to the gold annotations CSV file")
    parser.add_argument("model_csv", help="Path to the model annotations CSV file")
    parser.add_argument("--threshold", type=int, default=60, help="Similarity threshold (default: 60)")
    parser.add_argument("--exclude-columns", nargs="+", help="Columns to exclude during comparison")

    args = parser.parse_args()

    gold_csv = args.gold_csv
    model_csv = args.model_csv
    similarity_threshold = args.threshold
    exclude_columns = args.exclude_columns

    precision_dict, recall_dict, f1_dict = compare_csv_columns(gold_csv, model_csv, similarity_threshold, exclude_columns)

    overall_precision, overall_recall, overall_f1 = calculate_overall_metrics(precision_dict, recall_dict, f1_dict)

    # Print the metrics for each column
    for column in precision_dict:
        print(f"Column: {column}")
        print(f"Precision: {precision_dict[column]}")
        print(f"Recall: {recall_dict[column]}")
        print(f"F1 Score: {f1_dict[column]}\n")

    # Print the overall performance
    print("Overall Precision:", overall_precision)
    print("Overall Recall:", overall_recall)
    print("Overall F1 Score:", overall_f1)