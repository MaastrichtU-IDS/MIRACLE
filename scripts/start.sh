#!/usr/bin/env sh
set -e

prodigy ner.manual ner_indications blank:en data/indications.jsonl --label labels.txt --patterns data/patterns.jsonl
