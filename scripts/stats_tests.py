#%%
import json
import scipy.stats as stats
from cliffs_delta import cliffs_delta

#%%
def read_json_and_extract_field(json_file, field):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return [source[field] for source in data['Sources'] if field in source]

#%%
def calculate_statistical_significance(file1, file2, field):
    data1 = read_json_and_extract_field(file1, field)
    data2 = read_json_and_extract_field(file2, field)

    _, p_value = stats.mannwhitneyu(data1, data2)
    cliffs_size, cliffs_expl = cliffs_delta(data1, data2)

    return field, p_value, cliffs_size, cliffs_expl

#%%
file1 = '../data/analysis/matched_chatgpt_with_classes.json'
file2 = '../data/analysis/matched_non_chatgpt_with_classes.json'
fields = ['CommitsTotalCount','CommentsCount','ReviewerCount','Additions','Deletions','ChangedFiles']

#%%
for f in fields:
    field, p_value, cliffs_size, cliffs_expl = calculate_statistical_significance(file1, file2, f)
    print(f"Using {field}, \nP-value = {p_value}, P-value < 0.05 = {p_value < 0.05}, \ncliff's delta effect size = {cliffs_size}, cliff's delta explanation = {cliffs_expl}\n")

# %%
