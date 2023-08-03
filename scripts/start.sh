#!/usr/bin/env sh
set -e

# Show the stats, just for the logs
python -m prodigy stats

# Start Prodigy
# prodigy ner.manual ner_indications blank:en data/indications.jsonl --label labels.txt --patterns data/patterns.jsonl