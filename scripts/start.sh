#!/bin/bash

dataset_name="ner_indications"
model_dir="models"
model_name="toy_model"
model_version="model-last"

# prodigy db-in ner_indications backup/latest.jsonl
# prodigy ner.manual ner_indications blank:en data/indications.jsonl --label labels.txt
prodigy ner.correct "$dataset_name" "$model_dir/$model_name/$model_version" ./data/indications.jsonl --label ./labels.txt --exclude "$dataset_name"