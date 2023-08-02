#!/usr/bin/env sh

python src/process_mondo.py data/mondo.json data/mondo.csv
python src/process_drugbank.py data/drugbank.xml data/drugbank.csv
python src/pattern_creator.py data/drugbank.csv DRUG data/mondo.csv CONDITIONS data/patterns.jsonl