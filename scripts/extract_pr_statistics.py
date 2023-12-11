"""
This script extracts various statistics from pull request data present in JSON format and saves the results in CSV files.

The extracted statistics include:
- Repository Name
- Pull Request Number
- Pull Request URL
- State of the Pull Request (e.g., MERGED, CLOSED)
- Comments Count
- Total Commits Count
- Duration from the time the Pull Request was created to when it was closed
- Duration from the time the Pull Request was created to when it was merged.

The script processes two datasets:
1. Pull requests assisted by ChatGPT.
2. Pull requests not assisted by ChatGPT.

The extracted statistics are saved into separate CSV files for each dataset.
"""


#%%
import json
import csv
from datetime import datetime

#%%
def extract_duration(start, end):
    if start and end:
        start_dt = datetime.fromisoformat(remove_Z_if_present(start))
        end_dt = datetime.fromisoformat(remove_Z_if_present(end))
        duration = end_dt - start_dt
        return duration
    return ''


#%%
def remove_Z_if_present(datetime_str):
    return datetime_str[:-1] if datetime_str.endswith('Z') else datetime_str


#%%
def extract_stats(json_data, save_path):
    pr_data = []
    for pr in json_data['Sources']:
        repo_name = pr['RepoName']
        pr_number = pr['Number']
        pr_url = pr['URL']
        state = pr['State']
        comments_count = pr['CommentsCount']
        commits_count = pr['CommitsTotalCount']
        duration_created_to_closed = extract_duration(pr['CreatedAt'], pr['ClosedAt'])
        duration_created_to_merged = extract_duration(pr['CreatedAt'], pr['MergedAt'])

        pr_data.append([
            repo_name, 
            pr_number, 
            pr_url, 
            state, 
            comments_count, 
            commits_count, 
            duration_created_to_closed, 
            duration_created_to_merged
        ])

    # Write the extracted data to a CSV file
    with open(save_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['RepoName', 'PR Number', 'PR URL', 'State', 'CommentsCount', 'CommitsTotalCount', 'Duration Created to Closed', 'Duration Created to Merged'])
        writer.writerows(pr_data)

#%%
#STATISTICS FOR CHATGPR ASSISTED PR
with open('../data/chatgpt_prs.json', 'r') as file:
    chatgpt = json.load(file)

#%%
extract_stats(chatgpt, '../data/chatgpt_pr_stats.csv')

#%%
#STATISTICS FOR CHATGPR ASSISTED PR
with open('../data/no_chatgpt_prs.json', 'r') as file:
    non_chatgpt = json.load(file)

#%%
extract_stats(non_chatgpt, '../data/no_chatgpt_pr_stats.csv')
# %%
