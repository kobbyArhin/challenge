
"""
This script performs the following high-level tasks:

Import Libraries:

Essential libraries are imported: json for data loading, csv for CSV file writing, and datetime for date/time manipulations.
Load Data:

A JSON file containing data about sources, specifically pull requests, is loaded.
Initialize Repositories' Information:

Two dictionaries (repo_date_ranges and repo_pr_count) are initialized to store the date range (min and max date) for pull requests and the count of pull requests for each repository, respectively.
Process Each Source in Data:

For each pull request source in the data:
The repository's name and creation date of the pull request are extracted.
The count of pull requests for the repository is updated.
The date range for the repository is updated based on the creation date of the pull request.
Export to CSV:

The script writes the processed data (repository, min date, max date, date range in days, number of PRs) to a CSV file named 'repo_pr_date_ranges.csv'. This provides a consolidated view of the activity duration and the number of pull requests for each repository.
In essence, this script processes pull request data to determine the activity duration and count of pull requests for different repositories and exports the results to a CSV file for further analysis or reporting.
"""


#%%
import json
import csv
from datetime import datetime, timedelta

#%%
with open('../snapshot_20230831/20230831_060603_pr_sharings.json', 'r') as file:
     data = json.load(file)

print(len(data["Sources"]))

#%%
repo_date_ranges = {}
repo_pr_count = {}

#%%
for source in data['Sources']:
    if source['Type'] == 'pull request': 
        repo_name = source['RepoName']
        created_at = datetime.strptime(source['CreatedAt'], '%Y-%m-%dT%H:%M:%SZ').date()
        
        if repo_name in repo_pr_count:
            repo_pr_count[repo_name] += 1
        else:
            repo_pr_count[repo_name] = 1

        if repo_name in repo_date_ranges:
            repo_date_ranges[repo_name]['min'] = min(repo_date_ranges[repo_name]['min'], created_at - timedelta(days=7))
            repo_date_ranges[repo_name]['max'] = max(repo_date_ranges[repo_name]['max'], created_at + timedelta(days=7))
        else:
            repo_date_ranges[repo_name] = {'min': created_at - timedelta(days=7), 'max': created_at + timedelta(days=7)}



#%%
# for repo, date_range in repo_date_ranges.items():
#     print(f"{repo}: {date_range['min']} to {date_range['max']}")

# %%
with open('../data/repo_pr_date_ranges.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Repository', 'Min Date', 'Max Date', 'Range', 'Number of PRs'])
    
    for repo, date_range in repo_date_ranges.items():
        date_range_days = (date_range['max'] - date_range['min']).days + 1
        num_prs = repo_pr_count.get(repo, 0)
        writer.writerow([repo, date_range['min'], date_range['max'], date_range_days, num_prs])
# %%
# with open('../data/repo_pr_count.csv', mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Repository', 'Number of PRs'])
    
#     for repo, count in repo_pr_count.items():
#         writer.writerow([repo, count])
# %%
