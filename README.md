# 💫 Drug Indication Annotation Using Prodigy

A project that uses [Prodigy](http://prodi.gy) to train a model annotate Dailymed drug indication sections with their medical context.

## Build and deploy using Docker

1. Clone the repository

    ```bash
    git clone https://github.com/ebylmz/prodigy-drug-indication-annotation
    cd prodigy-drug-indication-annotation
    ```

2. Create a .env file:

    ```bash
    PRODIGY_KEY=XXXX-XXXX-XXXX-XXXX
    PRODIGY_BASIC_AUTH_PASS=XXXX
    ```

3. Build and deploy with Docker:

    ```bash
    docker compose up --build
    ```

4. Sign in and start annotation
    
    Replace the X with your session name and open http://localhost:8080/?session=X. 
    Sign in with the username "prodigy-user" and the provided password. 

## List of Annotation Labels
1. DRUG: The drug name or the active ingredient
2. ROUTE: The route of administration (e.g. oral, intravenous, topical)
3. FORMULATION: The formulation of the drug (e.g. solution, tablet)
4. MECHANISM: The drug mechanism of action (e.g. protein inhibitor)
5. ADJUNCT_TO: Where the drug acts as an adjunctive therapy, use this label to identify what it is combined with.
6. ACTION: The action between the drug and the condition (e.g. treatment of, management of)
7. CONDITION: The condition that is indicated for the drug (e.g. tremors, pain)
8. BASECONDITION: The base condition is the underlying pathophysiological state in which the indicated condition is a symptom of (e.g. parkinson's, cancer)
9. ANATOMY: The specific anatomical part for which the condition is localized to.
10. CAUSED_BY: The cause of the condition that is to be treated (e.g. E. coli for an infection)
11. SYMPTOM: Symptoms that are mentioned that are part of the medical context of treatment, but is not the target of the treatment.
12. TARGET_GROUP: Group of patients or individuals for whom a particular drug is intended or designed to be used.
13. CO_MORBIDITY: Other conditions that may be present as part of the target group. 
14. CO_PRESCRIPTION: Other medications that may be in use by the target group.
15. HISTORY: Statements relating to the medical history of the target group.
16. TEMPORALITY: Statements relating to the temporality of the treatment.
17. MEDICAL_CTX: Statements that discuss the medical context beyond those mentioned above
18. EFFECT: Intended beneficial effects of the treatment.
19. SIDEEFFECT: Negative side effects of the treatment.
20. CONTRAINDICATION: The manner in which the drug should not or must not be be used.
21. INEFFECTIVE: The manner in which the drug is ineffective.


## Creating the Model

1. Manually annotate a new dataset using the provided labels.

    Download a spacy model (en_core_web_sm, en_core_web_md, en_core_web_lg) to fine tune.

    ```bash
    python -m spacy download [spacy-model] 
    python -m spacy download en_core_web_sm
    ```
    Use the ner.manual command to launch an instance of the annotation tool to generate a new annotation dataset using the indication text and the set of annotation labels.

    ```bash
    prodigy ner.manual [dataset-name] blank:en [indication-sentence-file-path] --label [labels-file-path]
    prodigy ner.manual ner_indications blank:en ./data/indications.jsonl --label ./labels.txt
    ```

    The server will be available on http://localhost:8080 by default, and user-specific annotations can be done at http://localhost:8080/?session=USERNAME. 

    Make sure to save your progress by clicking the small floppy disk icon or pressing CTRL-S.


1. Review the dataset

    View stats and list all datasets

    ```bash
    prodigy stats -l
    ```

    Annotations can be exported with the db-out command.

    ```bash
    prodigy db-out [dataset] > [dataset.jsonl]
    prodigy db-out ner_indications > ner_indication_annotations.jsonl
    ```

    Annotations can be imported with the db-in command.

    ```bash
    prodigy db-in [dataset] [dataset.jsonl]
    prodigy db-in ner_indications ner_indication_annotations.jsonl
    ```

    To review annotations and resolve conflicts.

    ```bash
    prodigy review [reviewed-dataset-name] [dataset] --label [labels-file-path]
    prodigy review ner_indications --label ./labels.txt
    ```
    
    To delete a dataset

    ```bash
    prodigy drop [dataset]
    ```

    To export the patterns.

    ```bash
    prodigy terms.to-patterns [dataset] [dataset-patterns.jsonl] --label [labels-file-path] -m blank:en
    prodigy terms.to-patterns ner_indications ./sample-patterns.jsonl --label ./labels.txt -m blank:en
    ```

2. Model training

    To train the model with the set of annotations, you provide the training dataset and an output directory for the model.
   
    ```bash
    prodigy train [output-model-dir] --ner [training-dataset] 
    prodigy train ./data/indication_model --ner ner_indications 
    ```

4. Correcting the model’s suggestions and retraining

    To make adjustments on the model's annotations (exlude the already annotated samples) 

    ```bash
    prodigy ner.correct [corrected-dataset] [model] [source] --label [labels-file-path] --exclude [previos-dataset]
    prodigy ner.correct ner_indications_correct ./data/indication_model/model-best ./data/indications.jsonl --label ./labels.txt --exclude ner_indications
    ```

    After correcting the model's suggestion, train again with the two dataset and depending on the model's performance continue with correction and training
    
    ```bash
    prodigy train ./data/indication_model --ner ner_indications_correct,ner_indications
    ```

    Checkout the prodigy-recipes repository for more ways to use prodigy: https://github.com/explosion/prodigy-recipes
