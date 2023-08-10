#!/bin/bash

# export the dataset with name of current date
/usr/local/bin/python -m prodigy db-out ner_indications_correct > /app/data/backup/"$(date '+%Y-%m-%d')".jsonl