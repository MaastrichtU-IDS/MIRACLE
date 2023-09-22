#!/bin/bash

model_preds_jsonl="data/dataset/annotations_miracle_neuro_dkg.jsonl"
model_preds_csv="data/dataset/annotations_miracle_neuro_dkg.csv"
neuro_dkg_gold_csv="data/neuro_dkg/neuro_dkg_gold_for_miracle.csv"
output_file="data/analysis/neuro_dkg_miracle_analysis.csv"

# Convert Prodigy annotations JSONL file to CSV file  
python src/jsonl2csv.py $model_preds_jsonl $model_preds_csv --labels_file "data/neuro_dkg/labels_neuro_dkg_for_miracle.txt"

# Measure the model performance by comparing models predictions on NeuroDKG dataset  
python src/compare_neuro_dkg.py $neuro_dkg_gold_csv $model_preds_csv $output_file --exclude_columns text