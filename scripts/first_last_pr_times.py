"""
This script is designed to inspect pull request (PR) datasets and identify the earliest and latest PR entries based on their creation timestamp ('CreatedAt'). It provides a quick look at the time range covered by the datasets.

Here's a breakdown of the functionalities:

Data Processing:

Reads and processes the 'CreatedAt' timestamp of each PR from the provided JSON datasets.
Sorts the PR entries based on their creation timestamps.
Time Range Extraction:

Identifies the PR with the earliest creation timestamp and the PR with the latest creation timestamp.
Stores and returns details of these PRs, such as 'CreatedAt' timestamp and 'URL'.
The script executes these functions for two datasets:

PRs with ChatGPT assistance.
PRs without ChatGPT assistance.
The end goal is to provide insights into the time frame covered by the PR datasets and offer a quick reference to the earliest and latest PRs in each dataset.
"""

#%%
import json

#%%
def extract_times_from_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    sorted_sources = sorted(data["Sources"], key=lambda x: x["CreatedAt"])

    first_entry = {
        "CreatedAt": sorted_sources[0]["CreatedAt"],
        "URL": sorted_sources[0]["URL"]
    }

    last_entry = {
        "CreatedAt": sorted_sources[-1]["CreatedAt"],
        "URL": sorted_sources[-1]["URL"]
    }

    return first_entry, last_entry

#%%
file_path = 'data/chatgpt_prs.json'
first, last = extract_times_from_file(file_path)
print("First CreatedAt:", first["CreatedAt"], "URL:", first["URL"])
print("Last CreatedAt:", last["CreatedAt"], "URL:", last["URL"])


# %%
file_path = 'data/no_chatgpt_prs.json'
first, last = extract_times_from_file(file_path)
print("First CreatedAt:", first["CreatedAt"], "URL:", first["URL"])
print("Last CreatedAt:", last["CreatedAt"], "URL:", last["URL"])

# %%
