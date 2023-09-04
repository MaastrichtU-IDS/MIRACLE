import argparse
import csv
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

def get_indication_text(g_indications, context_url, nkgi_indications, rdfs):
    context_number = context_url.split("/")[-1]

    query = prepareQuery(
        """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?indication_text
        WHERE {
            nkgi_indications:%s rdfs:label ?indication_text .
        }
        """ % context_number,
        initNs={"nkgi_indications": nkgi_indications}
    )

    result = g_indications.query(query)
    return list(result)[0]["indication_text"] if result else "Unknown"

def get_target_group(g_neuro_dkg, target_group_url, ns1):
    query = prepareQuery(
        """
        PREFIX ns1: <http://www.w3id.org/>

        SELECT ?ageGroup
        WHERE {
            <%s> ns1:neurodkg:hasAgeGroup ?ageGroup .
        }
        """ % target_group_url,
        initNs={"ns1": ns1}
    )

    result = g_neuro_dkg.query(query)
    return list(result)[0]["ageGroup"] if result else "Unknown" 


def get_disease_name(g_neuro_dkg, disease_url, rdfs):
    if not disease_url.startswith("http://"):
        return disease_url

    query = prepareQuery(
        """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?diseaseName
        WHERE {
            <%s> rdfs:label ?diseaseName .
        }
        """ % disease_url,
        initNs={"rdfs": rdfs}
    )

    result = g_neuro_dkg.query(query)
    return list(result)[0]["diseaseName"] if result else "Unknown" 

def get_drug_name(g_neuro_dkg, drug_url, ns1, rdfs):
    drug_id = drug_url.split("/")[-1]

    query = prepareQuery(
        """
        PREFIX ns1: <http://www.w3id.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?drugName
        WHERE {
            ns1:%s rdfs:label ?drugName .
        }
        """ % drug_id,
        initNs={"ns1": ns1, "rdfs": rdfs}
    )

    result = g_neuro_dkg.query(query)
    return list(result)[0]["drugName"] if result else "Unknown" 

def parse(g_neuro_dkg, g_neuro_dkg_biolink, g_indications, output_csv):
    nkgi = Namespace("https://w3id.org/neurodkg/instance/")
    nkgi_indications = Namespace("http://www.w3id.org/neurodkg/Instances/")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    ns1 = Namespace("http://www.w3id.org/")

    # Define the SPARQL query for neurodkg file
    query_neurodkg = prepareQuery(
        """
        PREFIX ns1: <http://www.w3id.org/>
        SELECT ?context ?drug ?disease ?targetGroup
        WHERE {
            ?context a ns1:neurodkg:DrugDiseaseTargetGroup ;
                     ns1:neurodkg:drug ?drug ;
                     ns1:neurodkg:disease ?disease ;
                     ns1:neurodkg:targetGroup ?targetGroup .
        }
        """
    )

    with open(output_csv, mode='w', newline='') as csv_file:
        fieldnames = ['DRUG', 'CONDITION', 'TARGET_GROUP', 'text']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in g_neuro_dkg.query(query_neurodkg):
            context_url = row["context"]
            drug_url = row["drug"]
            disease_url = row["disease"]
            target_group_url = row["targetGroup"]

            indication_text = get_indication_text(g_indications, context_url, nkgi_indications, rdfs)
            drug = get_drug_name(g_neuro_dkg, drug_url, ns1, rdfs)
            disease = get_disease_name(g_neuro_dkg, disease_url, rdfs)
            target_group = get_target_group(g_neuro_dkg, target_group_url, ns1)

            # Write data to CSV file
            writer.writerow({'DRUG': drug, 'CONDITION': disease, 'TARGET_GROUP': target_group, 'text': indication_text})

def load_rdf_graph(file_path):
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract information from RDF files.")
    parser.add_argument("neurodkg_file", help="Path to the neurodkg RDF file")
    parser.add_argument("neurodkg__biolink_file", help="Path to the neurodkg biolink RDF file")
    parser.add_argument("indications_file", help="Path to the indication text RDF file")
    parser.add_argument("output_csv", help="Path to the output CSV file") 
    args = parser.parse_args()

    # Load the RDF files into graphs
    g_neuro_dkg = load_rdf_graph(args.neurodkg_file)
    g_neuro_dkg_biolink = load_rdf_graph(args.neurodkg__biolink_file)
    g_indications = load_rdf_graph(args.indications_file)

    parse(g_neuro_dkg, g_neuro_dkg_biolink, g_indications, args.output_csv) 
