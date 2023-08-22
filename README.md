# 💫 MIRACLE (Medical Indication Recognition and Active Context Learning Engine)

A project that uses [Prodigy](http://prodi.gy) to train a model annotate Dailymed drug indication sections with their medical context.

## 🛠️ Build and deploy with Docker

1. Clone the repository
   
    ```bash
    git clone https://github.com/ebylmz/prodigy-drug-indication-annotation
    cd prodigy-drug-indication-annotation
    ```

2. Create a .env file

    ```bash
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
    prodigy train ./model --ner ner_indications --label-stats
    ```

4. Correcting the model’s suggestions and retraining

    To make adjustments on the model's annotations (exlude the already annotated samples from "ner_indication" dataset) 

    ```bash
    prodigy ner.correct ner_indications ./model/model-best ./data/indications.jsonl --label ./labels.txt --exclude ner_indications
    ```

    After correcting the model's suggestion, re-train the last-model and depending on the model's performance continue with correction and training.

    ```bash
    prodigy train ./model/model-last --ner ner_indications --label-stats
    ```

    You can use train-curve recipe to see whether more data improves the model or not. As a rule of thumb, if accuracy improves within the last 25%, training with more examples will likely result in better accuracy.

    ```bash
    prodigy train-curve --ner ner_indications --show-plot
    ```

    Checkout the [prodigy-recipes](https://github.com/explosion/prodigy-recipes) for more ways to use prodigy
