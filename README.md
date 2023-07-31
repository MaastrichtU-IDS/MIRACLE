```bash
python -m venv .venv
source .venv/bin/activate
```

Install

```bash
pip install -e .
```
Run

```bash
prodigy ner.manual ner_indications blank:en data/indications.jsonl --label data/labels.txt --patterns data/patterns/all_patterns.jsonl
```