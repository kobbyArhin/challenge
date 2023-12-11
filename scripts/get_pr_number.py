
"""
This script carries out tasks related to the mapping of GitHub commits to their corresponding pull requests:

Initialization:

Import required modules such as Github API handler, JSON for data handling, and collections for advanced data structures.
Retrieve a GitHub token from an environment variable for authentication.
Mapping Commits to PRs:

The find_pr_numbers function takes in the repository's owner, repository name, a list of commit SHAs, and the GitHub token. It returns a dictionary mapping each commit SHA to its corresponding pull request number.
It fetches the repository from GitHub.
Iterates through all pull requests in the repository.
For each pull request, it gets the list of associated commits.
It checks if any of these commits match with the provided commit SHAs and updates the mapping.
Loading Commit Data:

Load a JSON file (20230831_063412_commit_sharings.json) containing details of various commits.
Handling Duplicate Commits:

Extract commit SHAs from the loaded data.
Identify and print the count of unique and duplicate commits.
Create a dictionary to count occurrences of each commit.
List commit SHAs that appear more than once in the data.
Aggregating Commits by Repository:

Iterate through the loaded data and group commit SHAs by their associated repository.
Fetching PR Numbers for Commits:

For each repository and its associated commits:
Determine the repository's owner and name.
Use the find_pr_numbers function to get the pull request numbers for each commit.
Append the result to the output data.
Writing Data to JSON Files:

Write the complete mapping of commit SHAs to pull request numbers to a JSON file (commit_pr.json).
Create a filtered version of the data, removing commits that do not map to any pull request, and save this to another JSON file (commit_pr_non_null.json).
This script helps in identifying the context in which a commit was made by mapping it to its related pull request. This can be useful for understanding the discussions and decisions leading to a particular code change.
"""


#%%
from github import Github
import json
from collections import defaultdict, Counter
import os
import glob

#%%
token = os.getenv('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')

#%%
def find_pr_numbers(owner, repo_name, commit_shas, token):
    g = Github(token)
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
    except Exception as e:
        print(f"Failed to get repo {owner}/{repo_name}, Error: {str(e)}")
        return {sha: None for sha in commit_shas}
    
    pr_numbers = {}
    pulls = repo.get_pulls(state='all')
    for pull in pulls:
        pr_number = pull.number
        commits = pull.get_commits()
        for commit in commits:
            sha = commit.sha
            if sha in commit_shas:
                pr_numbers[sha] = pr_number

    for sha in set(commit_shas) - set(pr_numbers.keys()):
        pr_numbers[sha] = None
        
    return pr_numbers


#%%
with open('../snapshot_20230831/20230831_063412_commit_sharings.json', 'r') as file:
     data = json.load(file)

print(len(data["Sources"]))

#%%

# pattern = '../*/*_commit_sharings.json'
# files = glob.glob(pattern)

# data = {'Sources': []}

# for file in files:
#     if not os.path.isfile(file):
#         continue
    
#     with open(file, 'r') as f:
#         file_data = json.load(f)
#         if 'Sources' in file_data:
#             data['Sources'].extend(file_data['Sources'])


# print(len(data["Sources"]))

#%%
all_commits = [source["Sha"] for source in data["Sources"]]
unique_commits = set(all_commits)
duplicate_commits_count = len(all_commits) - len(unique_commits)

print(f"Total Commits: {len(all_commits)}")
print(f"Unique Commits: {len(unique_commits)}")
print(f"Duplicate Commits: {duplicate_commits_count}")

#%%
from collections import defaultdict

commit_counts = defaultdict(int)
for source in data["Sources"]:
    sha = source["Sha"]
    commit_counts[sha] += 1

duplicate_commits = [commit for commit, count in commit_counts.items() if count > 1]

print(f"Duplicate Commits: {duplicate_commits}")


#%%
output_data = {"Commits": []}
#token = "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"

repo_commits = defaultdict(set)

#%%
# Aggregate all commit SHAs by repository
for source in data["Sources"]:
    if source["Type"] == "commit":
        repo_commits[source["RepoName"]].add(source["Sha"])

print(len(repo_commits))

#%%
# Find PR numbers for each commit SHA in each repository
for repo_name, commit_shas in repo_commits.items():
    owner, repo = repo_name.split("/")
    pr_numbers = find_pr_numbers(owner, repo, commit_shas, token)
    for sha, pr_number in pr_numbers.items():
        output_data["Commits"].append({
            "Repository": repo_name,
            "CommitHash": sha,
            "PRNumber": pr_number
        })

#%%
# Write the output data to a new JSON file
with open('../data/commit_pr.json', 'w') as f:
    json.dump(output_data, f, indent=4)

#%%
commit_pr = {"Commits": [commit for commit in output_data["Commits"] if commit["PRNumber"] is not None]}

#%%
with open('../data/commit_pr_non_null.json', 'w') as f:
    json.dump(commit_pr, f, indent=4)

# %%
