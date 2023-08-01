```bash
python -m venv .venv
source .venv/bin/activate
```

Create a .env file:

```bash
PRODIGY_KEY=AAAA-AAAA-AAAA-AAAA
PRODIGY_BASIC_AUTH_PASS=mypass
```

Install

```bash
pip install -e .
```

Run

```bash
prodigy ner.manual ner_indications blank:en data/indications.jsonl --label data/labels.txt --patterns data/patterns/all_patterns.jsonl
```