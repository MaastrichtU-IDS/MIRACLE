#!/bin/bash

dataset_name="ner_indications"
output_file="data/model_training_statistics.csv"

python src/analyse.py model/model-last labels.txt "$dataset_name" "$output_file" 
