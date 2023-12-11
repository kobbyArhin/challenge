
"""
This script performs the following tasks related to GitHub pull requests:

Loading Initial Data:

Load data from a JSON file (20230831_060603_pr_sharings.json), which contains details of various pull requests.
Load data from a CSV file (repo_all_prs.csv), which also has pull request information.
Set URL Collections:

Extract and form a set of pull request URLs from the JSON data.
Extract and form a set of pull request URLs from the CSV data.
Identifying Missing Pull Requests:

Determine pull requests that are present in the CSV but not in the JSON (prs_in_csv_not_json).
Determine pull requests that are present in the JSON but not in the CSV (prs_in_json_not_csv).
Exporting Missing Data to CSVs:

Write the list of pull requests (prs_in_csv_not_json) to a CSV file (no_chatgpt_prs.csv).
Write the list of pull requests (prs_in_json_not_csv) to another CSV file (prs_in_json_not_captured.csv).
Fetching Pull Request Details from GitHub:

A function get_pr_data_from_github is defined to:
Connect to the GitHub API using a personal access token.
Fetch detailed information about a pull request given its repository name and number.
Extract various pull request properties including author, title, body, creation time, review times, state, and more.
Return the data in a structured dictionary format.
Updating Missing Pull Request Details:

For each pull request identified as missing in the JSON data (no_chatgpt_prs.csv), fetch its detailed information using the get_pr_data_from_github function.
Store this detailed information in the pr_data_list.
Exporting Enhanced JSON:

Formulate the final data structure with the key "Sources" and value being the pr_data_list.
Write this enhanced data to a new JSON file (no_chatgpt_prs.json).
"""

#%%
import csv
import json
from github import Github, RateLimitExceededException
import random

#%%
with open('../snapshot_20230831/20230831_060603_pr_sharings.json', 'r') as json_file:
    json_data = json.load(json_file)

#%%
csv_data = []
with open('../data/repo_all_prs.csv', mode='r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    csv_data = list(reader)

#%%
# Replace URL with RepoName and Number for identification
json_pr_identifiers = {(item["RepoName"]+'/'+str(item["Number"])) for item in json_data["Sources"]}
csv_pr_identifiers = {(row["Repository"]+'/'+str(row["PR Number"])) for row in csv_data}

#%%
# Update the comparison logic
prs_in_csv_not_json = [row for row in csv_data if (row["Repository"]+'/'+str(row["PR Number"])) not in json_pr_identifiers]
prs_in_json_not_csv = [item for item in json_data["Sources"] if (item["RepoName"]+'/'+str(item["Number"])) not in csv_pr_identifiers]

#%%
with open('../data/no_chatgpt_prs.csv', mode='w', newline='', encoding='utf-8') as file:
    fieldnames = csv_data[0].keys()  
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(prs_in_csv_not_json)

#%%
with open('../data/prs_in_json_not_captured.csv', mode='w', newline='', encoding='utf-8') as file:
    fieldnames = ['Repository', 'PR Number', 'PR Title', 'Created At', 'URL'] 
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for item in prs_in_json_not_csv:
        writer.writerow({
            'Repository': item['RepoName'],
            'PR Number': item['Number'],
            'PR Title': item['Title'],
            'Created At': item['CreatedAt'].split('T')[0] + ' ' + item['CreatedAt'].split('T')[1].split('Z')[0],
            'URL': item['URL']
        })
    
#%%
def switch_token():
    global current_token_index
    current_token_index = (current_token_index + 1) % len(tokens)
    return tokens[current_token_index]

#%%
def get_pr_data_from_github(tokens, repo_name, pr_number):
    global current_token_index
    token = tokens[current_token_index]
    g = Github(token)
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        first_review_time = None
        final_review_time = None
        reviews = pr.get_reviews()

        human_reviews = [review for review in reviews if review.user and review.user.type != 'Bot']

        human_reviewer_names = list(set([review.user.login for review in human_reviews]))

        if human_reviews:
            review_times = [review.submitted_at for review in human_reviews]
            first_review_time = min(review_times)
            final_review_time = max(review_times)

        pr_data = {
            "Type": "pull request",
            "URL": pr.html_url,
            "Author": pr.user.login,
            "RepoName": repo_name,
            "RepoLanguage": repo.language,
            "Number": pr.number,
            "Title": pr.title,
            "Body": pr.body,
            "CreatedAt": pr.created_at.isoformat(),
            "ClosedAt": pr.closed_at.isoformat() if pr.closed_at else None,
            "MergedAt": pr.merged_at.isoformat() if pr.merged_at else None,
            "UpdatedAt": pr.updated_at.isoformat(),
            "State": pr.state.upper(),
            "Additions": pr.additions,
            "Deletions": pr.deletions,
            "ChangedFiles": pr.changed_files,
            "CommentsCount": pr.comments,
            "CommitsTotalCount": pr.commits,
            "CommitShas": [commit.sha for commit in pr.get_commits()],
            "FirstReviewTime": first_review_time.strftime('%Y-%m-%dT%H:%M:%SZ') if first_review_time else None,
            "FinalReviewTime": final_review_time.strftime('%Y-%m-%dT%H:%M:%SZ') if final_review_time else None,
            "ReviewerCount": len(human_reviewer_names),
            "Reviewers": human_reviewer_names
        }
        return pr_data
    except RateLimitExceededException: 
        print(f"Rate limit exceeded for token {token}. Switching to next token...")
        switch_token()
        g = Github(tokens[current_token_index])


#%%
tokens = [
  "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"
]

#%%
current_token_index = 0

#%%
pr_data_list = []

#%%
with open('../data/sampled_issue_all_prs_no_date_filter.csv', 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        repo_name = row["Repository"]
        pr_number = int(row["PR Number"])
        pr_data_list.append(get_pr_data_from_github(tokens, repo_name, pr_number))

#%%
final_data = {"Sources": pr_data_list}
print(len(final_data['Sources']))
#%%
with open('../data/sampled_issue_all_prs_no_date_filter.json', 'w', encoding='utf-8') as json_file:
    json.dump(final_data, json_file, indent=4)

# %%
