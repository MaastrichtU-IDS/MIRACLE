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
                target_group['AGE_GROUP'].append(response['hasAgeGroup']) 
            if response['hasMinAge']:
                target_group['MIN_AGE'].append(response['hasMinAge']) 
            if response['responseStatus']:
                target_group['RESPONSE_STATUS'].append(response['responseStatus']) 
            if response['hasCurrentMedication']:
                target_group['CURRENT_MEDICATION'].append(get_rdf_label(g_neuro_dkg, rdfs, response['hasCurrentMedication'])) 
            if response['hasComorbidity']:
                target_group['COMORBIDTY'].append(get_rdf_label(g_neuro_dkg, rdfs, response['hasComorbidity']))
            if response['treatmentDuration']:
                target_group['TREATMENT_DURATION'].append(get_rdf_label(g_neuro_dkg, rdfs, response['treatmentDuration'])) 
            if response['hasSymptom']:
                target_group['SYMPTOM'].append(get_rdf_label(g_neuro_dkg, rdfs, response['hasSymptom'])) 
            if response['hasTherapy']:
                target_group['THERAPY'].append(response['hasTherapy'])

    return target_group

def get_target_group(g_neuro_dkg, target_group_urls, ns1, rdfs):
    target_group = {
        'AGE_GROUP': [], 
        'MIN_AGE': [], 
        'TREATMENT_CODE': [], 
        'SYMPTOM': [], 
        'THERAPY': [], 
        'CURRENT_MEDICATION': [], 
        'TREATMENT_DURATION': [], 
        'RESPONSE_STATUS': [], 
        'COMORBIDTY': []
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
                target_group['AGE_GROUP'].append(response['hasAgeGroup']),
            if response['hasMinAge']:
                target_group['MIN_AGE'].append(response['hasMinAge']),
            if response['responseStatus']:
                target_group['RESPONSE_STATUS'].append(response['responseStatus']),
            if response['hasCurrentMedication']:
                target_group['CURRENT_MEDICATION'].append(get_rdf_label(g_neuro_dkg, rdfs, response['hasCurrentMedication'])),
            if response['hasComorbidity']:
                target_group['COMORBIDTY'].append(get_rdf_label(g_neuro_dkg, rdfs, response['hasComorbidity'])),
            if response['treatmentDuration']:
                target_group['TREATMENT_DURATION'].append(response['treatmentDuration']),
            if response['hasSymptom']:
                target_group['SYMPTOM'].append(get_rdf_label(g_neuro_dkg, rdfs, response['hasSymptom'])),
            if response['hasTherapy']:
                target_group['THERAPY'].append(get_rdf_label(g_neuro_dkg, rdfs, response['hasTherapy'])),
            if response['hasTreatment']:
                target_group['TREATMENT_CODE'].append(response['hasTreatment']),
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

    rows = []
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

        row = {}
        row['CONTEXT_NO'] = context_no 
        row['DRUG'] = drug 
        row['DISEASE'] = disease 
        row['text'] = indication_text 

        # Remove the treatment code
        target_group.pop('TREATMENT_CODE')
        
        for key in target_group.keys():
            if not target_group[key]:            
                continue
                
            row[key] = set()
            for value in target_group[key]:
                row[key].add(str(value))

            # If the set is consist of single entry, just add the row value as string 
            if len(row[key]) == 1:
                row[key] = target_group[key][0] 

        rows.append(row)

    with open(output_csv, mode='w', newline='') as csv_file:
        fieldnames = [
            'CONTEXT_NO', 'DRUG', 'DISEASE', 'AGE_GROUP', 'MIN_AGE', 
            'SYMPTOM', 'THERAPY', 'CURRENT_MEDICATION',
            'TREATMENT_DURATION', 'RESPONSE_STATUS', 'COMORBIDTY', 'text']
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def load_rdf_graph(file_path):
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract relations from RDF files and generate a CSV output.")
    parser.add_argument("neurodkg_file", help="Path to the neurodkg RDF file (neuro_dkg.ttl)")
    parser.add_argument("context_label_file", help="Path to the context label RDF file (context_label.ttl)")
    parser.add_argument("output_csv", help="Path to the output CSV file") 
    args = parser.parse_args()

    print("Loading RDF files...")
    g_neuro_dkg = load_rdf_graph(args.neurodkg_file)
    g_indications = load_rdf_graph(args.context_label_file)

    print("Extracting data and generating CSV...")
    extract(g_neuro_dkg, g_indications, args.output_csv)

    print("CSV generation complete. Output saved to", args.output_csv)