import argparse
import ast
import pandas as pd
from fuzzywuzzy import fuzz

def is_similar(str1, str2, similarity_threshold):
    return fuzz.ratio(str1, str2) > similarity_threshold

def calculate_ner_metrics(gold_standard_col, ner_annotations_col, similarity_threshold):
    # Initialize counters for True Positives (TP), False Positives (FP), and False Negatives (FN)
    tp = 0
    fp = 0
    fn = 0
    ann_count = 0 # Number of annotation(s) 

    # Iterate through each annotation in the gold standard
    for labels, preds in zip(gold_standard_col, ner_annotations_col):
        label_list = list(ast.literal_eval(labels)) if labels.startswith('{') else [labels]
        pred_list = list(ast.literal_eval(preds)) if preds.startswith('{') else [preds]

        if label_list[0] != 'nan':
            ann_count += len(label_list)

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
    positive_predictions = tp + fp
    positives_actuals = tp + fn

    # Precision measures how many of the positive predictions made are correct (true positives)
    precision = tp / positive_predictions if positive_predictions > 0 else 0
    # Recall measures how many of the positive cases the classifier correctly predicted, over all the positive cases in the data
    recall = tp / positives_actuals if positives_actuals > 0 else 0
    sum_precision_recall = precision + recall
    # F1-Score is the harmonic mean of precision and recall
    f1 = 2 * (precision * recall) / sum_precision_recall if sum_precision_recall > 0 else 0

    return precision, recall, f1, ann_count

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
    ann_count_dict = {}

    # Iterate through columns in both DataFrames
    for column in gold_df.columns:
        gold_col = gold_df[column].astype(str)
        model_col = model_df[column].astype(str)
        # Calculate metrics for the current column
        precision, recall, f1, ann_count = calculate_ner_metrics(gold_col, model_col, similarity_threshold)

        # Store metrics in dictionaries
        precision_dict[column] = precision
        recall_dict[column] = recall
        f1_dict[column] = f1
        ann_count_dict[column] = ann_count
    return precision_dict, recall_dict, f1_dict, ann_count_dict

def calculate_overall_metrics(precision_dict, recall_dict, f1_dict):
    # Calculate overall metrics by taking weighted averages based on the number of columns
    num_columns = len(precision_dict)
    overall_precision = sum(precision_dict.values()) / num_columns
    overall_recall = sum(recall_dict.values()) / num_columns
    overall_f1 = sum(f1_dict.values()) / num_columns

    return overall_precision, overall_recall, overall_f1

def calculate_frequency(count, total):
    return round((count / total) * 100, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare two CSV files and calculate NER metrics.")
    parser.add_argument("gold_csv", help="Path to the CSV file containing gold standard annotations")
    parser.add_argument("model_csv", help="Path to the CSV file containing model-generated annotations")
    parser.add_argument("output_csv", help="Path to the output statistics CSV file")
    parser.add_argument("--threshold", type=int, default=60, help="Similarity threshold for matching annotations (default: 60)")
    parser.add_argument("--exclude_columns", nargs="+", help="List of columns to exclude during comparison")

    args = parser.parse_args()

    gold_csv = args.gold_csv
    model_csv = args.model_csv
    output_csv = args.output_csv
    similarity_threshold = args.threshold
    exclude_columns = args.exclude_columns

    print("Comparing CSV files and calculating NER metrics...")
    
    precision_dict, recall_dict, f1_dict, ann_count_dict = compare_csv_columns(gold_csv, model_csv, similarity_threshold, exclude_columns)

    overall_precision, overall_recall, overall_f1 = calculate_overall_metrics(precision_dict, recall_dict, f1_dict)

    total_ann_count = sum(ann_count_dict.values())

    # Create a DataFrame to store the results
    results_df = pd.DataFrame({
        "Label": list(precision_dict.keys()),
        "Count": list(ann_count_dict.values()),
        "Frequency": ["%.2f" % calculate_frequency(ann_count_dict[column], total_ann_count) for column in precision_dict],
        "Precision": ["%.2f" % round(precision_dict[column] * 100, 2) for column in precision_dict],
        "Recall": ["%.2f" % round(recall_dict[column] * 100, 2) for column in precision_dict],
        "F1Score": ["%.2f" % round(f1_dict[column] * 100, 2) for column in precision_dict]
    })

    # Write the results to the output CSV file
    results_df = results_df.sort_values(by="Count", ascending=False)
    results_df.to_csv(output_csv, index=False)

    print("NER metrics have been calculated and saved to", output_csv)

    # Print the overall performance
    print("Overall Precision:", "%.2f" % round(overall_precision * 100, 2))
    print("Overall Recall:", "%.2f" % round(overall_recall * 100, 2))
    print("Overall F1 Score:", "%.2f" % round(overall_f1 * 100, 2))
