"""
This code interacts with the GitHub API to fetch and verify pull request data for various repositories based on specified date ranges:

Initialization:

Set up a GitHub connection using a personal access token.
Load a list of repositories and their associated date ranges from the CSV file 'repo_pr_date_ranges.csv'.
Duplicate Repository Check:

Check and print any duplicate repository entries.
Fetching Pull Requests from GitHub:

For each repository and its date range:
Fetch pull requests created within that date range.
Save these pull requests in 'repo_all_prs.csv' with columns for the repository name, PR number, PR title, creation date, and PR URL.
Update each repository's data with the number of PRs fetched from GitHub.
Updating Repository Data:

Overwrite the initial 'repo_pr_date_ranges.csv' to include the count of PRs fetched from GitHub.
Calculating and Storing Discrepancies:

Calculate the difference between the number of PRs specified in the CSV and the actual number fetched from GitHub.
Update 'repo_pr_date_ranges.csv' to include a new 'Difference' column showing this discrepancy for each repository.
"""

#%%
from github import Github
from datetime import datetime
import csv
from collections import Counter

#%%
g = Github("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")

#%%
repositories = []
with open('../data/repo_pr_date_ranges.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        repositories.append(row)

#%%
repo_names = [repo['Repository'] for repo in repositories]
duplicates = [item for item, count in Counter(repo_names).items() if count > 1]

#%%
if duplicates:
    print(f"Found duplicate repositories: {', '.join(duplicates)}")
else:
    print("No duplicate repositories found.")

#%%
with open("../data/pr_collection/repo_all_prs.csv", mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Repository', 'PR Number', 'PR Title', 'Created At', 'URL'])

    for repo in repositories:
        repo_name = repo['Repository']
        min_date = datetime.strptime(repo['Min Date'], '%Y-%m-%d').date()
        max_date = datetime.strptime(repo['Max Date'], '%Y-%m-%d').date()

        try:
            repository = g.get_repo(repo_name)
            prs = repository.get_pulls(state='all', sort='created', direction='asc')
            count = 0
            for pr in prs:
                created_at = pr.created_at.date()
                if min_date <= created_at <= max_date:
                    writer.writerow([repo_name, pr.number, pr.title, pr.created_at, pr.html_url])
                    count += 1
            repo['PR from GitHub'] = count
        except Exception as e:
            print(f"Failed to fetch PRs for {repo_name}. Error: {e}")

#%%
with open('../data/repo_pr_date_ranges.csv', mode='w', newline='', encoding='utf-8') as file:
    fieldnames = ['Repository', 'Min Date', 'Max Date', 'Range', 'Number of PRs', 'PR from GitHub']
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    for repo in repositories:
        writer.writerow(repo)

# %%
with open('../data/repo_pr_date_ranges.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames + ['Difference']
    rows = []
    for row in reader:
        number_of_prs = int(row['Number of PRs'])
        pr_from_github = int(row['PR from GitHub'])
        row['Difference'] = pr_from_github - number_of_prs  
        rows.append(row)
        
#%%
with open('../data/repo_pr_date_ranges.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    
# %%
