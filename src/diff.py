import argparse
import json
import csv

class Stats:
    def __init__(self):
        self.exact_miss = 0 
        self.exact_catch= 0
        self.exact_catch_wrong_label= 0
        self.partly_catch= 0
        self.exactly_wrong = 0

def zip_annotation(model_span, gold_span, case):
    if model_span == None:
        model_ann = ""
        model_label = ""
    else:
        model_ann = model_span['text']
        model_label = model_span['label']
    
    if gold_span == None:
        gold_ann = ""
        gold_label = ""
    else:
        gold_ann = gold_span['text']
        gold_label = gold_span['label']

    return {
        'model_ann': model_ann,
        'gold_ann': gold_ann,
        'model_label': model_label,
        'gold_label': gold_label,
        'case': case
    } 

def process_datasets(model_jsonl, gold_jsonl):
    diff = []
    stats = Stats()
    total_sample = 0

    # Open the two JSONL files for reading
    with open(model_jsonl, 'r') as file1, open(gold_jsonl, 'r') as file2:
        for line1, line2 in zip(file1, file2):

            total_sample += 1
            # There are 5 cases
            # 1. exact miss
            # 2. exact catch
            # 3. exact catch but wrong label
            # 4. partly catch / partly miss / partly wrong
            # 5. exactly wrong 

            # Parse the JSON objects from the lines
            model_spans = json.loads(line1)['spans']
            gold_spans = json.loads(line2)['spans']
             
            m_i = 0
            g_i = 0
            min_length = min(len(model_spans), len(gold_spans))
            
            while m_i < min_length and g_i < min_length: 
                m_st = model_spans[m_i]['token_start']
                m_end = model_spans[m_i]['token_end']
                g_st = gold_spans[g_i]['token_start']
                g_end = gold_spans[g_i]['token_end']

                if m_end < g_st: 
                    # Model has token(s) which are not included in the gold dataset
                    diff.append(zip_annotation(model_spans[m_i], None, "exactly wrong"))
                    m_i += 1
                    stats.exactly_wrong += 1

                    # if model_spans[m_i]['token_start'] > g_end:
                    #     g_i += 1
                elif g_end < m_st:
                    # Model misses token(s) in gold dataset (exact miss)
                    diff.append(zip_annotation(None, gold_spans[g_i], "exact miss"))
                    g_i += 1
                    stats.exact_miss += 1
                    # if gold_spans[g_i]['token_start'] > m_end:
                    #     m_i += 1
                else:
                    # Save the indexes
                    mi = m_i
                    gi = g_i

                    # Define the case and iterate the index(s)
                    if m_st < g_st:
                        case = "partly catch / partly miss"
                        m_i += 1
                        stats.partly_catch += 1
                        if m_i < min_length and model_spans[m_i]['token_start'] > g_end:
                            g_i += 1
                    elif g_st < m_st:
                        case = "partly catch / partly miss"
                        stats.partly_catch += 1
                        g_i += 1
                        if g_i < min_length and gold_spans[g_i]['token_start'] > m_end:
                            m_i += 1
                    else:
                        # They can start with same token but can end up with different token
                        if m_end < g_end:
                            case = "partly catch / partly miss"
                            stats.partly_catch += 1
                            m_i += 1
                            if m_i < min_length and model_spans[m_i]['token_start'] > g_end:
                                g_i += 1
                        elif g_end < m_end:
                            case = "partly catch / partly miss"
                            stats.partly_catch += 1
                            g_i += 1
                            if g_i < min_length and gold_spans[g_i]['token_start'] > m_end:
                                m_i += 1
                        else:
                            if gold_spans[g_i]['label'] == model_spans[m_i]['label']:
                                case = "exact catch"
                                stats.exact_catch += 1
                            else:
                                case = "exact catch but wrong label"
                                stats.exact_catch_wrong_label += 1
                            m_i += 1
                            g_i += 1

                    # Model catches the gold dataset
                    diff.append(zip_annotation(model_spans[mi], gold_spans[gi], case))


            # Finish the remaining annotations if there are
            while m_i < len(model_spans):
                # Process only model
                diff.append(zip_annotation(model_spans[m_i], None, "exactly wrong"))
                m_i += 1
            while g_i < len(gold_spans):
                diff.append(zip_annotation(None, gold_spans[g_i], "exact miss"))
                g_i += 1

    return diff, stats, total_sample


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compares to dataset given in JSONL format and gives statistical informations')

    parser.add_argument('model_jsonl', help='Path to model annotated JSONL file')
    parser.add_argument('gold_jsonl', help='Path to gold standard JSONL file')
    parser.add_argument('output_csv', help='Path to output CSV file')

    args = parser.parse_args()

    diff, stats, total_sample = process_datasets(args.model_jsonl, args.gold_jsonl)

    # Print the results in csv file
    with open(args.output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ['Model', 'Gold', 'Model Label', 'Gold Label', 'Case'])
        writer.writeheader()

        writer.writerows({
            'Model': entry['model_ann'],
            'Gold': entry['gold_ann'],
            'Model Label': entry['model_label'],
            'Gold Label': entry['gold_label'],
            'Case': entry['case']
        } for entry in diff)

    # Print the summary of the comparison
    print(f"Comparison complete. Details written to '{args.output_csv}'")
    print(f"Comparison Summary from {total_sample} example:")
    print(f"Exact Miss: {stats.exact_miss}")
    print(f"Exact Catch: {stats.exact_catch}")
    print(f"Exact Catch but Wrong Label: {stats.exact_catch_wrong_label}")
    print(f"Partly Catch: {stats.partly_catch}")
    print(f"Exactly Wrong: {stats.exactly_wrong}")
