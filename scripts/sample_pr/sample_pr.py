#%%
import json
import csv
import numpy as np
from collections import defaultdict

#%%
weights = [0.16667, 0.16667, 0.16667, 0.16667, 0.16667, 0.16667]

#%%
with open('../../data/chatgpt/chatgpt_prs.json', 'r') as file:
     chatgpt = json.load(file)

#%%
with open('../../data/non_chatgpt/no_chatgpt_prs.json', 'r') as file:
     no_chatgpt = json.load(file)

#%%
def similarity_score(p, q, w=weights):
    denom = np.maximum(p, q)
    ratio = np.divide(np.abs(p - q), denom, where=denom!=0, out=np.zeros_like(denom, dtype=np.float64))
    return np.sum(w * (1 - ratio))
    # return np.sum(1 - ratio)

#%%
def convert_to_vector(pr, chatgpt_author=None):
    author_score = 1 if chatgpt_author is None or pr["Author"] == chatgpt_author else 0

    try:
        return np.array([
            author_score,
            pr["CommitsTotalCount"],
            pr["CommentsCount"],
            pr["ChangedFiles"],
            pr["Additions"],
            pr["Deletions"]
        ])
    except KeyError as e:
        print(f"Missing key: {e} for PR: {pr['URL']}")
        return np.array([
            author_score,
            pr.get("CommitsTotalCount", 0),
            pr.get("CommentsCount", 0),
            pr.get("ChangedFiles", 0),
            pr.get("Additions", 0),
            pr.get("Deletions", 0)
        ])


#%%
chatgpt_by_repo = defaultdict(list)
no_chatgpt_by_repo = defaultdict(list)

#%%
for index, pr in enumerate(chatgpt["Sources"]):
    if pr is not None:
        chatgpt_by_repo[pr["RepoName"]].append(pr)
    else:
        print(f"Encountered a None PR at index {index} in chatgpt['Sources']")


#%%
for index, pr in enumerate(no_chatgpt["Sources"]):
    if pr is not None:
        no_chatgpt_by_repo[pr["RepoName"]].append(pr)
    else:
        print(f"Encountered a None PR at index {index} in no_chatgpt['Sources']")

#%%
selected_prs_set = set()

#%%
table = []

#%%
sampled_prs_json = {"Sources": []}

#%%
for repo, prs in chatgpt_by_repo.items():
    for pr in prs:
        pr_vector = convert_to_vector(pr)
        similarities = [(other_pr, similarity_score(pr_vector, convert_to_vector(other_pr, chatgpt_author=pr["Author"]))) 
                        for other_pr in no_chatgpt_by_repo.get(repo, []) if other_pr["URL"] not in selected_prs_set]
        
        sorted_prs = sorted(similarities, key=lambda x: x[1], reverse=True)
        
        if sorted_prs:
            most_similar_pr = sorted_prs[0][0]
            sampled_prs_json["Sources"].append(most_similar_pr)
            selected_prs_set.add(most_similar_pr["URL"])
            
            table_entry = {
                "chatgpt_pr": pr["URL"],
                "non_chatgpt_pr": most_similar_pr["URL"],
                "similarity_score": sorted_prs[0][1]
            }
            table.append(table_entry)

# %%
with open('../../data/retry/sampled_non_chatgpt_prs.json', 'w') as f:
    json.dump(sampled_prs_json, f, indent=4)

#%%
for row in table:
    print(f"{row['chatgpt_pr']} - {row['non_chatgpt_pr']} : {row['similarity_score']:.2f}")

#%%
with open('../../data/retry/matched_pairs_score.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['ChatGPT PR', 'Non-ChatGPT PR', 'Similarity Score'])

    for row in table:
        writer.writerow([row['chatgpt_pr'], row['non_chatgpt_pr'], f"{row['similarity_score']:.2f}"])


# %%
all_chatgpt_pr_urls = {pr["URL"] for pr in chatgpt["Sources"]}

#%%
matched_chatgpt_prs = {entry["chatgpt_pr"] for entry in table}

#%%
with open('../../data/retry/matched_prs.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Matched PR URLs'])
    for matched_pr in matched_chatgpt_prs:
        writer.writerow([matched_pr])

#%%
unmatched_chatgpt_prs = all_chatgpt_pr_urls - matched_chatgpt_prs

#%%
print("PRs in chatgpt that did not get a match:")
for unmatched_pr in unmatched_chatgpt_prs:
    print(unmatched_pr)

#%%
with open('../../data/retry/unmatched_prs.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Unmatched PR URLs'])
    for unmatched_pr in unmatched_chatgpt_prs:
        writer.writerow([unmatched_pr])
# %%
print(len(matched_chatgpt_prs))
# %%
print(len(unmatched_chatgpt_prs))
# %%
