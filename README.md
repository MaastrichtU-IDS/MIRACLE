# 🌟 MIRACLE (Medical Indication Recognition and Active Context Learning Engine)

A project that uses [Prodigy](http://prodi.gy) to train a model annotate Dailymed drug indication sections with their medical context.

## 🛠️ Build and deploy with Docker

1. Clone the repository
   
    ```bash
    git clone https://github.com/MaastrichtU-IDS/MIRACLE/
    cd miracle
    ```

2. Create a .env file

    ```
    PRODIGY_KEY=XXXX-XXXX-XXXX-XXXX
    PRODIGY_ALLOWED_SESSIONS=USERNAME_1,USERNAME_2
    PRODIGY_BASIC_AUTH_PASS=XXXX
    ```

3. Build and deploy with Docker

    ```bash
    docker compose up -d--build --remove-orphans
    ```
    
    View the logs
    
    ```bash
    docker compose logs
    ```

4. Enter container to run commands

    ```bash
    docker exec -it prodigy-dailymed bash
    ```

5. Stop and remove the container

    ```bash
    docker compose down
    ```

## 📋 List of Annotation Labels
1. DRUG: The drug name or the active ingredient. 
2. SALT: The salt form of the drug.
3. ROUTE: The route of administration (e.g. oral, intravenous, topical)
4. FORMULATION: The formulation of the drug (e.g. solution, tablet)
5. MECHANISM: The drug mechanism of action (e.g. protein inhibitor)
6. ACTION: The action between the drug and the condition (e.g. treatment of, management of)
7. SEVERITY: The severity of the indicated condition (e.g. mild-to-moderate, severe)
8. INDICATION: The condition that is indicated for the drug (e.g. tremors, pain)
9. BASECONDITION: The base condition is the underlying pathophysiological state in which the indicated condition is a symptom of (e.g. parkinson's, cancer)
10. ANATOMY: The specific anatomical part for which the condition is localized to (e.g. skin)
11. CAUSED_BY: The cause of the condition that is to be treated (e.g. E. coli for an infection)
12. SYMPTOM: Symptoms exhibited by the paitent, but is not the treatable indication.
13. TARGET_GROUP: Group of patients or individuals for whom a particular drug is intended or designed to be used.
14. CO_MORBIDITY: Other conditions that may be present as part of the target group.
15. CO_PRESCRIPTION: Other medications that may be in use by the target group.
16. HISTORY: Statements relating to the medical history of the target group.
17. TEMPORALITY: Statements relating to the temporality of the treatment.
18. INEFFECTIVE: The manner The sentence that specifies on what case the the drug is ineffective.
19. EFFECT: Intended beneficial effects of the treatment.
20. SIDEEFFECT: Negative side effects of the treatment.
21. CONTRAINDICATION: The sentence that specifies a contraindication, or where the drug should not or must not be be used.
22. MEDICAL_CTX: Statements that discuss the medical context beyond those mentioned above.

## 🚀 Creating the Model

1. Manually annotate samples using the provided labels to create a dataset for the training.
    
    Use the ner.manual command to launch an instance of the annotation tool to generate a new annotation dataset using the indication text and the set of annotation labels.

    ```bash
    prodigy ner.manual ner_indications blank:en ./data/indications.jsonl --label ./labels.txt
    ```

    The server will be available on http://localhost:8080 by default, and user-specific annotations can be done at http://localhost:8080/?session=USERNAME. For the first time you need to sign in with the username "prodigy-user" and the PRODIGY_BASIC_AUTH_PASS which should be in the .env file.

    Make sure to save your progress by clicking the small floppy disk icon or pressing CTRL-S.

2. Review the dataset

    List all datasets an sessions

    ```bash
    prodigy stats -ls
    ```

    Annotations can be exported with the db-out command.

    ```bash
    prodigy db-out ner_indications > ner_indications_annotations.jsonl
    ```

    Annotations can be imported with the db-in command.

    ```bash
    prodigy db-in ner_indications backup/latest.jsonl
    ```

    For multiple user session, there could be conflicts and they need to be resolved before the model training. 
    
    Review recipe enables to create a new dataset "ner_indications_review" by resolving conflicts in "ner_indications" dataset.

    ```bash
    prodigy review ner_indications_review ner_indications --label ./labels.txt
    ```
    
    To delete a dataset

    ```bash
    prodigy drop unused_dataset
    ```

3. Model training

    To train the model with the set of annotations, you provide the training dataset and an output directory for the model. 
    
    The model is saved as model-best and model-last in the given output directory. model-best indicates the best version and the model-last indicates the last version of model during the training iterations. 

    ```bash
    prodigy train ./models/miracle --ner ner_indications --label-stats
    ```

4. Correcting the model’s suggestions and retraining

    To make adjustments on the model's annotations (exlude the already annotated samples from "ner_indication" dataset) 

    ```bash
    prodigy ner.correct ner_indications ./models/miracle/model-best ./data/indications.jsonl --label ./labels.txt --exclude ner_indications
    ```

    After correcting the model's suggestion, re-train the last-model and depending on the model's performance continue with correction and training.

    ```bash
    prodigy train ./models/miracle --ner ner_indications --label-stats --base-model ./models/miracle/model-best
    ```

    You can use train-curve recipe to see whether more data improves the model or not. As a rule of thumb, if accuracy improves within the last 25%, training with more examples will likely result in better accuracy.

    ```bash
    prodigy train-curve --ner ner_indications --show-plot
    ```

    Checkout the [prodigy-recipes](https://github.com/explosion/prodigy-recipes) for more ways to use prodigy

5. Getting help from LLM

    To use a LLM with spaCy you’ll need a configuration file that tells spacy-llm how to construct a prompt for your task. We already made a configuration for OpenAI. You can find a sample configuration for OpenAI in 'spacy-llm-config.cfg'.

    You might be using a vendor like OpenAI, as a backend for your LLM. In such cases you’ll need to setup up secrets such that you can identify yourself.

    ```
    OPENAI_API_ORG = "org-..."
    OPENAI_API_KEY = "sk-..."
    ```

    This recipe marks entity predictions obtained from a large language model configured by spacy-llm and allows you to accept them as correct, or to manually curate them. 

    The ner.llm.correct recipe fetches examples from large language models while annotating and it allows you to accept them as correct, or to manually curate them.  
    
    ```bash
    dotenv run -- prodigy ner.llm.correct ner_indications spacy-llm-config.cfg data/indications.jsonl
    ```

    The ner.llm.fetch recipe can fetch a large batch of examples upfront.

    ```bash
    dotenv run -- prodigy ner.llm.fetch spacy-llm-config.cfg data/indications.jsonl data/llm_annotated.jsonl
    ```

    After downloading such a batch of examples you can use ner.manual to correct the annotations.

    ```bash
    prodigy ner.manual ner_indications blank:en data/llm_annotated.jsonl --label labels.txt
    ```
