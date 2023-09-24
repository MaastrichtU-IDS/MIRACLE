# 🌟 MIRACLE (Medical Indication Recognition and Active Context Learning Engine)

MIRACLE is a project that leverages [Prodigy](http://prodi.gy) to train a model that annotates DailyMed drug indication sections with their corresponding medical context.


## 🛠️ Build and Deploy with Docker

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

4. Enter the container to run commands

    ```bash
    docker exec -it prodigy-dailymed bash
    ```

5. Stop and remove the container

    ```bash
    docker compose down
    ```

## 📋 List of Annotation Labels
MIRACLE uses the following annotation labels:

1. DRUG: The drug name or active ingredient.
2. SALT: The salt form of the drug.
3. ROUTE: The route of administration (e.g., oral, intravenous, topical).
4. FORMULATION: The formulation of the drug (e.g., solution, tablet).
5. MECHANISM: The drug's mechanism of action (e.g., protein inhibitor).
6. ACTION: The action between the drug and the condition (e.g., treatment of, management of).
7. SEVERITY: The severity of the indicated condition (e.g., mild-to-moderate, severe).
8. INDICATION: The condition that the drug is indicated for (e.g., tremors, pain).
9. BASECONDITION: The underlying pathophysiological state in which the indicated condition is a symptom of (e.g., Parkinson's, cancer).
10. ANATOMY: The specific anatomical part for which the condition is localized (e.g., skin).
11. CAUSED_BY: The cause of the condition that is to be treated (e.g., E. coli for an infection).
12. SYMPTOM: Symptoms exhibited by the patient but not the treatable indication.
13. TARGET_GROUP: The group of patients or individuals for whom a particular drug is intended or designed to be used.
14. CO_MORBIDITY: Other conditions that may be present in the target group.
15. CO_PRESCRIPTION: Other medications that may be in use by the target group.
16. HISTORY: Statements relating to the medical history of the target group.
17. TEMPORALITY: Statements relating to the temporality of the treatment.
18. INEFFECTIVE: The manner in which the drug is ineffective.
19. EFFECT: Intended beneficial effects of the treatment.
20. SIDEEFFECT: Negative side effects of the treatment.
21. CONTRAINDICATION: Statements specifying when the drug should not be used.
22. MEDICAL_CTX: Statements discussing the medical context beyond the labels mentioned above.

## 🚀 Creating the Model

### Annotation and Training

1. Start by manually annotating samples using the provided labels to create a training dataset. Use the following command:
    
    ```bash
    prodigy ner.manual ner_indications blank:en ./data/dailymed/curation.jsonl --label ./labels.txt
    ```

    The server will be available on http://localhost:8080 by default, and user-specific annotations can be done at http://localhost:8080/?session=USERNAME. For the first time you need to sign in with the username "prodigy-user" and the PRODIGY_BASIC_AUTH_PASS which should be in the .env file.

    💾 Make sure to save your progress by clicking the small floppy disk icon or pressing CTRL-S.

2. Review the Dataset and Manage Annotations:

    List all datasets an sessions:

    ```bash
    prodigy stats -ls
    ```

    Annotations can be both exported and imported using the 'db-out' and 'db-in' commands, respectively

    Export annotations:

    ```bash
    prodigy db-out ner_indications > data/annotations/ner_indications_annotations.jsonl
    ```

    Import annotations:

    ```bash
    prodigy db-in ner_indications backup/latest.jsonl
    ```

    Resolve conflicts in multiple-user sessions using the review recipe:

    ```bash
    prodigy review ner_indications_review ner_indications --label ./labels.txt
    ```
    
    Delete unused datasets:

    ```bash
    prodigy drop unused_dataset
    ```

3. Model Training

    To train the model with the set of annotations, you provide the training dataset and an output directory for the model. 
    
    The model is saved as model-best and model-last in the given output directory. model-best indicates the best version and the model-last indicates the last version of model during the training iterations. 

    ```bash
    prodigy train ./models/miracle --ner ner_indications --label-stats
    ```

### Correcting the Model’s Suggestions and Retraining

1. Correcting

    Correct the model's suggestions (excluding already annotated samples from "ner_indications" dataset):
    ```bash
    prodigy ner.correct ner_indications ./models/miracle/model-best ./data/dailymed/curation.jsonl --label ./labels.txt --exclude ner_indications
    ```

2. Retraining

    After correcting the model's suggestion, re-train the last-model and depending on the model's performance continue with correction and training.

    ```bash
    prodigy train ./models/miracle --ner ner_indications --label-stats --base-model ./models/miracle/model-best
    ```

    You can use train-curve recipe to see whether more data improves the model or not. As a rule of thumb, if accuracy improves within the last 25%, training with more examples will likely result in better accuracy.

    ```bash
    prodigy train-curve --ner ner_indications --show-plot
    ```

    For more ways to use Prodigy, explore the [prodigy-recipes](https://github.com/explosion/prodigy-recipes) repository.

### LLM Integration

1. Creating Configuration File
    
    To use a LLM with spaCy you’ll need a configuration file that tells spacy-llm how to construct a prompt for your task. We already made a configuration for OpenAI. You can find a sample configuration for OpenAI in 'spacy-llm-config.cfg'.

    You might be using a vendor like OpenAI, as a backend for your LLM. In such cases you’ll need to setup up secrets such that you can identify yourself.

    ```
    OPENAI_API_ORG = "org-..."
    OPENAI_API_KEY = "sk-..."
    ```

2. LLM Prompt

    The ner.llm.correct recipe fetches examples from large language models while annotating and it allows you to accept them as correct, or to manually curate them.  

    ```bash
    dotenv run -- prodigy ner.llm.correct ner_indications spacy-llm-config.cfg data/dailymed/curation.jsonl
    ```

    The ner.llm.fetch recipe can fetch a large batch of examples upfront.

    ```bash
    dotenv run -- prodigy ner.llm.fetch spacy-llm-config.cfg data/dailymed/curation.jsonl data/model_annotations/annotations_curation_md__gpt3.jsonl
    ```

    After downloading such a batch of examples you can use ner.manual to correct the annotations.

    ```bash
    prodigy ner.manual ner_indications blank:en data/model_annotations/annotations_curation_md__gpt3.jsonl --label labels.txt
    ```

## 📊 Results

### F1 Scores

This table provides a clear overview of the F1 scores achieved by different models on various datasets.

| Model / Dataset  | curation_md | curation_gpt3 | NeuroDKG |
|------------------|-------------|---------------|----------|
| **miracle**      | 61.02       | -             | 64.89    |
| **gpt3_trained** | 28.15       | 53.51         | 65.75    |
| **GPT-3.5**      | 25.46       | -             | 71.44    |

### Folder Structure for Analysis
The analysis of datasets and models is available in the result folder. The results are organized into two main folders for ease of access:

1. **Dataset Analysis:** The 'dataset_analysis' folder contains files that provide insights into label counts and frequencies for various datasets.

2. **Model Performance Analysis:** The 'model_perf_analysis' directory contains files that present precision, recall, and F1 scores for each label based on the selected model, along with label count and frequency details.

### Naming Convention
In the analysis files, we follow a specific naming convention to make it easy to identify the dataset and model used for each analysis:

- Files that include 'train' after the dataset name indicate that the analysis pertains to the training portion (80%) of the dataset.
- Files that include 'eval' after the dataset name indicate that the analysis pertains to the evaluation portion (20%) of the entire dataset.

All the datasets used in the analysis can be found in the 'data' folder.

### File Naming Examples
Here are some examples of the naming convention:

- `curation_gpt3_train_analysis.csv`
  - Dataset: curation_gpt3 (train)

- `curation_md_train_analysis.csv`
  - Dataset: curation_md (train)

- `neuro_dkg__gpt3_trained_analysis.csv`
  - Dataset: neuro_dkg
  - Model: gpt3_trained

- `curation_md_eval__miracle_analysis.csv`
  - Dataset: curation_md (eval)
  - Model: miracle

These analysis files provide valuable insights into the performance of different models on various datasets.

### 📈 Future Directions
For future work, consider the following:

- Annotation processes could be performed by a team following a well-defined annotation protocol to improve dataset quality.
- Training a new model with the updated annotation dataset while ensuring a high F1 score.
- Annotating all DailyMed indication texts with this new model to create a comprehensive database.