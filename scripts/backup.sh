#!/bin/bash

dataset_name="ner_indications"
backup_dir="/app/backup"
current_date="$(date '+%Y-%m-%d')"
backup_filename="$current_date.jsonl"
latest_backup_filename="latest.jsonl"

# Export the dataset with the current date as the filename
/usr/local/bin/python -m prodigy db-out "$dataset_name" > "$backup_dir/$backup_filename"

# Update the latest backup file
cp "$backup_dir/$backup_filename" "$backup_dir/$latest_backup_filename"