#!/usr/bin/env sh
set -e

# Start Prodigy
prodigy db-in ner_indications data/annotations.jsonl --rehash
prodigy ner.manual ner_indications blank:en data/indications.jsonl --label labels.txt --patterns data/patterns.jsonl