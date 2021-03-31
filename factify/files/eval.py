import csv, math
from os import listdir
from os.path import isfile, join
import os
import pandas as pd

csv.field_size_limit(2147483647)
eval_file = 'relevance_scores.csv'
results_path = 'outputs'
files = [join(results_path, f) for f in listdir(results_path) if isfile(join(results_path, f))]

query_relevances = []
query_rels_ideal = []
for qi in range(0, 56):
    query_relevances.append(dict())
    query_rels_ideal.append([])

with open(eval_file, encoding="utf8") as evlf:
    evals = csv.reader(evlf)
    next(evals, None)
    for ev in evals:
        qid = int(ev[10])
        pid = ev[9]
        rel = int(ev[5])
        rel_conf = float(ev[6])
        query_relevances[qid-1][pid] = rel
        query_rels_ideal[qid-1].append(rel)

results = dict()
results_mrr = dict()
results_mrr_hi = dict()
results_precision_hi = dict()
results_precision = dict()

notin = 0
for cutoff in [20, 10, 5, 1]:

    # Calculate the ideal DCG for the queries.
    query_norms = []
    for qi in range(0, 56):
        query_rels_ideal[qi].sort(reverse=True)
        norm = 0
        i = 1
        for rel in query_rels_ideal[qi]:
            if i <= cutoff:
                norm += rel / math.log(i + 1, 2)
            i += 1
        query_norms.append(norm)


    for system_file in files:
        # Process a result file.
        # The file should be sorted with respect to query id and relevance score
        algo = os.path.basename(system_file) + "_" + str(cutoff)
        print(algo)
        results[algo] = []
        results_mrr_hi[algo] = []
        results_precision_hi[algo] = []
        with open(system_file, encoding="utf8") as system_f:
            result_reader = csv.reader(system_f, delimiter='\t')
            res_rank = 1
            qi = -1
            score = 0
            mrr = -1
            correct_count = 0
            correct_count_all = 0

            is_missing = False
            for row in result_reader:
                if int(row[0]) != qi:
                    if qi != -1:
                        # Start processing the next query. Assuming that the results are sorted w.r.t qid.
                        print(score/query_norms[qi-1])
                        results[algo].append(score / query_norms[qi-1])
                        results_mrr_hi[algo].append(1 / mrr)
                        results_precision_hi[algo].append(correct_count / cutoff)
                    qi = int(row[0])
                    res_rank = 1
                    score = 0
                    mrr = -1
                    correct_count = 0
                    is_missing = False

                if res_rank <= cutoff:
                    if row[1] in query_relevances[qi-1]:
                        score += (query_relevances[qi-1][row[1]]) / math.log(res_rank+1, 2)

                        if query_relevances[qi-1][row[1]] == 5:
                            correct_count += 1
                        if mrr == -1 and (query_relevances[qi-1][row[1]] == 5):
                            mrr = res_rank
                    else:
                        print("Missing Relevance : " + str(qi) + " " + row[1] + "----" + row[2])
                        notin += 1
                res_rank += 1

            # Finalize the last query
            print(score / query_norms[qi - 1])
            results[algo].append(score / query_norms[qi - 1])
            results_mrr_hi[algo].append(1 / mrr)
            results_precision_hi[algo].append(correct_count / cutoff)

# Writing out all the results in an Excel file.
df = pd.DataFrame(results)
mrr_res = pd.DataFrame(results_mrr_hi)
prec_res = pd.DataFrame(results_precision_hi)
writer = pd.ExcelWriter('NDCG.xlsx')

df.to_excel(excel_writer=writer, sheet_name="NDCG")
mrr_res.to_excel(excel_writer=writer, sheet_name="MRR")
prec_res.to_excel(excel_writer=writer, sheet_name="Precision")
writer.save()
print(notin)