import argparse
import csv
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

def get_response_first(qresult, label):
    li = list(qresult)
    return li[0][label] if li else None

def get_rdf_label(g_neuro_dkg, rdfs, url):
    if url is None:
        return None
    elif not url.startswith("http://"):
        return url
    query = prepareQuery(
        """
        SELECT ?label
        WHERE {
            <%s> rdfs:label ?label .
        }
        """ % url,
        initNs={"rdfs": rdfs}
    )

    return get_response_first(g_neuro_dkg.query(query), "label") 

def get_indication_text(g_indications, context_no, nkgi_indications, rdfs):
    if context_no is None:
        return None

    query = prepareQuery(
        """
        SELECT ?indicationText
        WHERE {
            nkgi_indications:%s rdfs:label ?indicationText .
        }
        """ % context_no,
        initNs={"nkgi_indications": nkgi_indications, "rdfs": rdfs}
    )

    return get_response_first(g_indications.query(query), "indicationText")


def get_diseases(g_neuro_dkg, rdfs, disease_urls):
    diseases = set()
    for url in disease_urls:
        disease = get_rdf_label(g_neuro_dkg, rdfs, url)
        diseases.add(str(disease))
    
    return diseases.pop() if len(diseases) == 1 else diseases   


def get_treatment_group(g_neuro_dkg, target_group, ns1, rdfs):
    for treatment in target_group['TREATMENT_CODE']:
        url = "<http://www.w3id.org/neurodkg/Instances/" + treatment + ">"

        query = prepareQuery(
            """
            SELECT ?hasAgeGroup ?hasMinAge ?responseStatus ?hasCurrentMedication ?hasComorbidity ?treatmentDuration ?hasSymptom ?hasTherapy
            WHERE {
                OPTIONAL { %s ns1:neurodkg:hasAgeGroup ?hasAgeGroup }
                OPTIONAL { %s ns1:neurodkg:hasMinAge ?hasMinAge }
            
                OPTIONAL { %s ns1:neurodkg:hasCurrentMedication ?hasCurrentMedication }
                OPTIONAL { %s ns1:neurodkg:responseStatus ?responseStatus }
                OPTIONAL { %s ns1:neurodkg:hasComorbidity ?hasComorbidity }

                OPTIONAL { %s ns1:neurodkg:treatmentDuration ?treatmentDuration }
                OPTIONAL { %s ns1:neurodkg:hasSymptom ?hasSymptom }
                OPTIONAL { %s ns1:neurodkg:hasTherapy ?hasTherapy }
            }
            """ % (url, url, url, url, url, url, url, url),
            initNs={"ns1": ns1}
        )

        for response in g_neuro_dkg.query(query):
            if response['hasAgeGroup']:
                target_group['AGE_GROUP'].add(str(response['hasAgeGroup'])) 
            if response['hasMinAge']:
                target_group['MIN_AGE'].add(str(response['hasMinAge'])) 
            if response['responseStatus']:
                target_group['RESPONSE_STATUS'].add(str(response['responseStatus'])) 
            if response['hasCurrentMedication']:
                target_group['CURRENT_MEDICATION'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['hasCurrentMedication']))) 
            if response['hasComorbidity']:
                target_group['COMORBIDTY'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['hasComorbidity'])))
            if response['treatmentDuration']:
                target_group['TREATMENT_DURATION'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['treatmentDuration']))) 
            if response['hasSymptom']:
                target_group['SYMPTOM'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['hasSymptom']))) 
            if response['hasTherapy']:
                target_group['THERAPY'].add(str(response['hasTherapy']))

    return target_group

def get_target_group(g_neuro_dkg, target_group_urls, ns1, rdfs):
    target_group = {
        'AGE_GROUP': set(), 
        'MIN_AGE': set(), 
        'TREATMENT_CODE': set(), 
        'SYMPTOM': set(), 
        'THERAPY': set(), 
        'CURRENT_MEDICATION': set(), 
        'TREATMENT_DURATION': set(), 
        'RESPONSE_STATUS': set(), 
        'COMORBIDTY': set()
    }
    
    for url in target_group_urls:
        query = prepareQuery(
            """
            SELECT ?hasAgeGroup ?hasMinAge ?responseStatus ?hasCurrentMedication ?hasComorbidity ?hasTreatment ?treatmentDuration ?hasSymptom ?hasTherapy
            WHERE {
                OPTIONAL { <%s> ns1:neurodkg:hasAgeGroup ?hasAgeGroup }
                OPTIONAL { <%s> ns1:neurodkg:hasMinAge ?hasMinAge }
            
                OPTIONAL { <%s> ns1:neurodkg:responseStatus ?responseStatus }
                OPTIONAL { <%s> ns1:neurodkg:hasCurrentMedication ?hasCurrentMedication }
                OPTIONAL { <%s> ns1:neurodkg:hasComorbidity ?hasComorbidity }
                OPTIONAL { <%s> ns1:neurodkg:hasTreatment ?hasTreatment }

                OPTIONAL { <%s> ns1:neurodkg:treatmentDuration ?treatmentDuration }
                OPTIONAL { <%s> ns1:neurodkg:hasSymptom ?hasSymptom }
                OPTIONAL { <%s> ns1:neurodkg:hasTherapy ?hasTherapy }
            }
            """ % (url, url, url, url, url, url, url, url, url),
            initNs={"ns1": ns1}
        )

        for response in g_neuro_dkg.query(query):
            if response['hasAgeGroup']:
                target_group['AGE_GROUP'].add(str(response['hasAgeGroup'])),
            if response['hasMinAge']:
                target_group['MIN_AGE'].add(str(response['hasMinAge'])),
            if response['responseStatus']:
                target_group['RESPONSE_STATUS'].add(str(response['responseStatus'])),
            if response['hasCurrentMedication']:
                target_group['CURRENT_MEDICATION'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['hasCurrentMedication']))),
            if response['hasComorbidity']:
                target_group['COMORBIDTY'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['hasComorbidity']))),
            if response['treatmentDuration']:
                target_group['TREATMENT_DURATION'].add(str(response['treatmentDuration'])),
            if response['hasSymptom']:
                target_group['SYMPTOM'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['hasSymptom']))),
            if response['hasTherapy']:
                target_group['THERAPY'].add(str(get_rdf_label(g_neuro_dkg, rdfs, response['hasTherapy']))),
            if response['hasTreatment']:
                target_group['TREATMENT_CODE'].add(str(response['hasTreatment'])),
                get_treatment_group(g_neuro_dkg, target_group, ns1, rdfs)
    
    return target_group

def extract(g_neuro_dkg, g_indications, output_csv):
    nkgi_indications = Namespace("http://www.w3id.org/neurodkg/Instances/")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    ns1 = Namespace("http://www.w3id.org/")

    # The type/class DrugDiseaseTargetGroup can contain multiple disease and target groups
    query_seperator = ','
    query = prepareQuery(
        """
        SELECT ?context ?drug (GROUP_CONCAT(?disease; SEPARATOR="%s") AS ?diseases) (GROUP_CONCAT(?targetGroup; SEPARATOR="%s") AS ?targetGroups)
        WHERE {
            ?context a ns1:neurodkg:DrugDiseaseTargetGroup ;
                    ns1:neurodkg:drug ?drug ;
                    ns1:neurodkg:disease ?disease .
            OPTIONAL { ?context ns1:neurodkg:targetGroup ?targetGroup }
        }
        GROUP BY ?context ?drug ?disease
        """ % (query_seperator, query_seperator),
        initNs={"ns1": ns1}
    )

    text_to_row = {}  # Dictionary to collect rows by 'text' value

    for result in g_neuro_dkg.query(query):
        context_url = result["context"]
        drug_url = result["drug"]
        
        context_no = context_url.split("/")[-1]
        target_group_urls = result["targetGroups"].split(query_seperator)
        disease_urls = result["diseases"].split(query_seperator)
        
        drug = get_rdf_label(g_neuro_dkg, rdfs, drug_url)
        disease = get_diseases(g_neuro_dkg, rdfs, disease_urls)
        target_group = get_target_group(g_neuro_dkg, target_group_urls, ns1, rdfs)
        indication_text = get_indication_text(g_indications, context_no, nkgi_indications, rdfs)

        if not indication_text:
            continue

        # Create a dictionary representing the row
        row = {
            'CONTEXT_NO': context_no,
            'DRUG': drug,
            'DISEASE': disease,
            'text': indication_text,
        }

        # Remove the treatment code
        target_group.pop('TREATMENT_CODE')
        
        for key in target_group.keys():
            ann_set = target_group[key] # Set of annotations
            set_len = len(ann_set)
            if set_len == 1:
                row[key] = next(iter(ann_set))
            elif set_len > 1:
                row[key] = ann_set

        # Collect rows by 'text' value
        if indication_text not in text_to_row:
            text_to_row[indication_text] = row.copy()
        else:
            # Merge rows with the same 'text' value
            for key, value in row.items():
                if not value or key == 'text':
                    continue
                
                if not text_to_row[indication_text].get(key, None):
                    text_to_row[indication_text][key] = value
                
                if isinstance(text_to_row[indication_text][key], str):
                    if isinstance(value, str):
                        if text_to_row[indication_text][key] != value:
                            tmp = text_to_row[indication_text][key]
                            text_to_row[indication_text][key] = set()
                            text_to_row[indication_text][key].add(tmp)
                            text_to_row[indication_text][key].add(value)
                    else:
                        value.add(text_to_row[indication_text])
                        text_to_row[indication_text] = value
                else:
                    if isinstance(value, str):
                        text_to_row[indication_text][key].add(str(value))
                    else:
                        text_to_row[indication_text][key] = text_to_row[indication_text][key].union(value)
                        if len(text_to_row[indication_text][key]) == 1:
                            text_to_row[indication_text][key] = text_to_row[indication_text][key].pop()
    
    # Convert the text_to_row dictionary to a list of rows
    combined_rows = list(text_to_row.values())

    counts = {
        'DRUG': 0, 'DISEASE': 0, 'AGE_GROUP': 0, 'MIN_AGE': 0, 
        'SYMPTOM': 0, 'THERAPY': 0, 'CURRENT_MEDICATION': 0,
        'TREATMENT_DURATION': 0, 'RESPONSE_STATUS': 0, 'COMORBIDTY': 0
    }

    # Count the number of annotations
    skipped_column = ['CONTEXT_NO', 'text']
    for row in combined_rows:
        for key, value in row.items():
            if key in skipped_column:
                continue
            if isinstance(value, str):
                counts[key] = counts.get(key, 0) + 1
            else:
                counts[key] = counts.get(key, 0) + len(value)

    total = sum(counts.values())
    # Sort the counts by value in descending order
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)

    return combined_rows, sorted_counts, total
    
def load_rdf_graph(file_path):
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

def calculate_frequency(count, total):
    return round((count / total) * 100, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract relations from NeuroDKG RDF files and generate a CSV output.")
    parser.add_argument("neurodkg_file", help="Path to the NeuroDKG RDF file (neuro_dkg.ttl)")
    parser.add_argument("context_label_file", help="Path to the context label RDF file (context_label.ttl)")
    parser.add_argument("output_csv", help="Path to the output CSV file") 
    parser.add_argument('--stats_csv', action='store_true', default=False, help='Output statistics in CSV format')
    args = parser.parse_args()

    print("Loading RDF files...")
    g_neuro_dkg = load_rdf_graph(args.neurodkg_file)
    g_indications = load_rdf_graph(args.context_label_file)

    print("Extracting data and generating CSV...")
    combined_rows, counts, total = extract(g_neuro_dkg, g_indications, args.output_csv)

    # Print the total number of rows
    print(f'Total number of rows extracted: {len(combined_rows)}')

    for label, count in counts:
        print("%s:\t%s" % (label, count))

    ann_out_csv = args.output_csv

    # Check if the CSV flag is provided and output statistics in CSV format
    if args.stats_csv:
        stats_filename = ann_out_csv.replace('.csv', '_stats.csv')
        with open(stats_filename, mode='w', newline='') as csv_file:
            fieldnames = ['Label', 'Count', 'Frequency']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for label, count in counts:
                writer.writerow({
                    'Label': label, 
                    'Count': count, 
                    'Frequency': "%.2f" % calculate_frequency(count, total)
                })
        print("Statistics saved to", stats_filename)

    with open(ann_out_csv, mode='w', newline='') as csv_file:
        fieldnames = [
            'CONTEXT_NO', 'DRUG', 'DISEASE', 'AGE_GROUP', 'MIN_AGE', 
            'SYMPTOM', 'THERAPY', 'CURRENT_MEDICATION',
            'TREATMENT_DURATION', 'RESPONSE_STATUS', 'COMORBIDTY', 'text']
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)

    print("CSV generation complete. Output saved to", ann_out_csv)