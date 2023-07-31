import sys
import csv
import xml.etree.ElementTree as ET

def process(xmlfile, csvfile):
    # Create an ElementTree object using the iterative parsing approach
    context = ET.iterparse(xmlfile, events=("start", "end"))
    context = iter(context)
    event, root = next(context)

    # Get the namespace and create a namespace dictionary for XPath queries
    namespace_uri = root.tag.split('}')[0][1:]
    namespace_prefix = "ns"
    namespace_map = {namespace_prefix: namespace_uri}

    with open(csvfile, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, ['ID', 'Label'])
        writer.writeheader()
        # Get all "drug" tags that are immediate children of the root element
        for event, elem in context:
            if event == "end" and elem.tag == f"{{{namespace_uri}}}drug" and elem.attrib.get('type'):
                name = elem.find(f"{namespace_prefix}:name", namespaces=namespace_map)
                id = elem.find(f"{namespace_prefix}:drugbank-id", namespaces=namespace_map)
                writer.writerow({'ID': id.text, 'Label': name.text})
                # Clear the element to release memory
                root.clear()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Right usage: {sys.argv[0]} [in: drugbank.xml] [out: drugbank_drugs.csv]") 

    print("Processing the XML file...")
    drugs = process(sys.argv[1], sys.argv[2])
    print(f'Completed. See the file "{sys.argv[2]}".')
