#!/bin/bash

dataset_name="ner_indications"
model_dir="models"
model_name="miracle"
model_version="model-last"
output_file="data/model_training_statistics.csv"

python src/analyse.py "$model_dir/$model_name/$model_version" labels.txt "$dataset_name" "$output_file" 