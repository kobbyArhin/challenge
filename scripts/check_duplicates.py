"""
This script identifies and prints duplicate pull request (PR) entries from a given JSON dataset based on their "RepoName" and "Number" attributes.

The process involves:

Reading the dataset from a specified file path.
Traversing through the dataset and using a combination of the "RepoName" and "Number" attributes as a unique key to identify PRs.
Checking if any such combination appears more than once in the dataset, indicating a duplicate.
Printing out the "RepoName" and "Number" combinations of all identified duplicates.
By the end of the execution, the script provides feedback on whether there are any duplicates in the dataset and, if so, lists them.
"""

#%%
import json

#%%
# with open('../snapshot_20230831/20230831_060603_pr_sharings.json', 'r') as file:
#     data = json.load(file)

with open('../data/no_chatgpt_prs.json', 'r') as file:
    data = json.load(file)

#%%
def find_duplicates(data):
    seen = {}
    duplicates = []

    for entry in data["Sources"]:
        key = (entry["RepoName"], entry["Number"])
        
        if key in seen:
            duplicates.append(key)
        else:
            seen[key] = 1

    return duplicates

#%%
duplicates = find_duplicates(data)

#%%
if duplicates:
    print("Found duplicates for the following RepoName and Number combinations:")
    for repo_name, number in duplicates:
        print(f"RepoName: {repo_name}, Number: {number}")
else:
    print("No duplicates found.")


#%%
