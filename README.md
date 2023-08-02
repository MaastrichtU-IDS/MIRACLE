# 💫 Drug Indication annotation using Prodi.gy

A project that uses [Prodigy](http://prodi.gy) to train a model to perform Dailymed indication annotation with their medical context


## Build using Docker

1. Clone the repository

    ```bash
    git clone https://github.com/ebylmz/prodigy-drug-indication-annotation
    cd prodigy-drug-indication-annotation
    ```

2. Create a .env file:

    ```bash
    PRODIGY_KEY=XXXX-XXXX-XXXX-XXXX
    PRODIGY_BASIC_AUTH_PASS=mypass
    ```

3. Build with Docker:

    ```bash
    docker build -t prodigy .
    ```

4. Run with Docker on http://localhost:8080

    ```bash
    docker run -d -p 8080:8080 --name prodigy prodigy
    ```

    You can also use a different annotation file and labels:

    ```bash
    docker run -d -p 8080:8080 --name prodigy  -e DATASET_NAME=sample -e SAMPLE_SENTENCES_FILE=sample-sentences.txt -e LABELS_FILE=labels.txt umids/prodigy:latest
    ```

## List of Annotation Labels

* DRUG: This refers to the official drug name or the active ingredient
* ROUTE: The route of administration (e.g. oral, intravenous, topical)
* FORMULATION: The formulation of the drug (e.g. solution, tablet)
* ADJUNCT_TO: Where the drug acts as an adjunctive therapy, use this label to identify what it is combined with.
* ACTION: The action between the drug and the condition (e.g. treatment of, management of)
* CONDITION: The condition that is indicated for the drug (e.g. tremors, pain)
* BASECONDITION: The base condition is the underlying pathophysiological state in which the indicated condition is a symptom of (e.g. parkinson's, cancer)
* SYMPTOM: Symptoms that are mentioned that are part of the medical context of treatment.
* TARGET_GROUP: Group of patients or individuals for whom a particular drug is intended or designed to be used.
* CO_MORBIDITY:
* CO_PRESCRIPTION:
* HISTORY:
* TEMPORALITY:
* MEDICAL_CTX: Any sentences that discuss the medical context of the indication (notwithstanding age)
* MECHANISM:
* EFFECT: Any beneficial effects identified in the text as a result of the treatment.
* SIDEEFFECT: Side effects that appear in the statement.
* CONTRAINDICATION: Where the drug should not be used.
* INEFFECTIVE: Where the drug is ineffective.


## Creating the Model

1. Manually annoate and create new dataset

    You can download and use different spacy model(s) (en_core_web_sm, en_core_web_md, en_core_web_lg)

    ```bash
    python -m spacy download [spacy-model] 
    python -m spacy download en_core_web_sm 
    ```

    ```bash
    prodigy ner.manual [dataset-name] blank:en [indication-sentence-file-path] --label [labels-file-path] --patterns [patterns-file-path]
    prodigy ner.manual ner_indications blank:en ./data/indications.jsonl --label ./labels.txt --patterns ./data/patterns.jsonl
    ```

    The server will then start up and you can start annotating. Don't forget to save your progress by clicking CTR-S. Then you can export your annotations.

    ```bash
    prodigy db-out [dataset] --dry > [dataset.jsonl]
    prodigy db-out ner_indications --dry > sample_annotations.jsonl
    ```

2. Review the dataset

    View stats and list all datasets

    ```bash
    prodigy stats -l
    ```

    To remove a dataset

    ```bash
    prodigy drop [dataset]
    ```

    Review annotations and outputs to resolve conflicts.

    ```bash
    prodigy review [reviewed-dataset-name] [dataset] --label [labels-file-path]
    prodigy review sample-review ner_indications --label ./labels.txt
    ```

    You can export the patterns.

    ```bash
    prodigy terms.to-patterns [dataset] [dataset-patterns.jsonl] --label [labels-file-path] -m blank:en
    prodigy terms.to-patterns ner_indications ./sample-patterns.jsonl --label ./labels.txt -m blank:en
    ```

3. Model training

    ```bash
    prodigy train [output-model-dir] --ner [training-dataset] 
    prodigy train ./data/tmp_model --ner ner_indications 
    ```

4. Correcting the model’s suggestions and retraining

    Make adjustments on the model's annotations (exlude the already annotated samples) 

    ```bash
    prodigy ner.correct [corrected-dataset] [model] [source] --label [labels-file-path] --exclude [previos-dataset]
    prodigy ner.correct ner_indications_correct ./data/tmp_model/model-best ./data/indications.jsonl --label ./labels.txt --exclude ner_indications
    ```

    After correcting the model's suggestion, train again with the two dataset and depending on the model's performance continue with correction and training
    
    ```bash
    prodigy train ./data/indication_model --ner ner_indications_correct,ner_indications
    ```

> Checkout the prodigy-recipes repository for more ways to use prodigy: https://github.com/explosion/prodigy-recipes