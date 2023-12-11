#%%
import json
import numpy as np
import csv

#%%
def similarity_score(p, q, weights=[0.16667, 0.16667, 0.16667, 0.16667, 0.16667, 0.16667]):
    denom = np.maximum(p, q)
    ratio = np.divide(np.abs(p - q), denom, where=denom!=0, out=np.zeros_like(denom, dtype=np.float64))
    return np.sum(weights * (1 - ratio))

#%%
def convert_to_vector(pr, chatgpt_author=None):
    author_score = 1 if chatgpt_author is None or pr["Author"] == chatgpt_author else 0
    return np.array([
        author_score,
        pr.get("CommitsTotalCount", 0),
        pr.get("CommentsCount", 0),
        pr.get("ChangedFiles", 0),
        pr.get("Additions", 0),
        pr.get("Deletions", 0)
    ])

#%%
def calculate_similarity_scores(chatgpt_json_path, no_chatgpt_json_path, matched_pairs_csv_path, output_csv_path):
    # Load PR data from JSON files
    with open(chatgpt_json_path, 'r') as file:
        chatgpt_prs = json.load(file)["Sources"]
    with open(no_chatgpt_json_path, 'r') as file:
        no_chatgpt_prs = json.load(file)["Sources"]

    # Convert PR data to dictionary for easy access
    chatgpt_prs_dict = {pr["URL"]: pr for pr in chatgpt_prs}
    no_chatgpt_prs_dict = {pr["URL"]: pr for pr in no_chatgpt_prs}

    # Read matched pairs from CSV
    pairs = []
    with open(matched_pairs_csv_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            pairs.append((row[0], row[1]))  # (ChatGPT PR, Non-ChatGPT PR)

    # Calculate similarity scores and save to CSV
    with open(output_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ChatGPT PR", "Non-ChatGPT PR", "Similarity Score"])

        for chatgpt_url, no_chatgpt_url in pairs:
            chatgpt_pr = chatgpt_prs_dict.get(chatgpt_url)
            no_chatgpt_pr = no_chatgpt_prs_dict.get(no_chatgpt_url)

            if chatgpt_pr and no_chatgpt_pr:
                score = similarity_score(
                    convert_to_vector(chatgpt_pr), 
                    convert_to_vector(no_chatgpt_pr, chatgpt_pr["Author"])
                )
                writer.writerow([chatgpt_url, no_chatgpt_url, round(score, 2)])

#%%
chatgpt_json_path = '../../data/analysis/matched_chatgpt_prs.json'
no_chatgpt_json_path = '../../data/analysis/matched_non_chatgpt_prs.json'
matched_pairs_csv_path = '../../data/pr_sample/final/matched_pairs.csv'
output_csv_path = '../../data/pr_sample/final/matched_pairs_score.csv'

#%%
calculate_similarity_scores(chatgpt_json_path, no_chatgpt_json_path, matched_pairs_csv_path, output_csv_path)

# %%
