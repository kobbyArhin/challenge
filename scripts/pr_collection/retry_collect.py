#%%
from github import Github
from datetime import datetime
import csv

#%%
g = Github("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")

#%%
with open('../data/sampling_issue.csv', mode='r') as file:
    reader = csv.reader(file)
    next(reader)
    sampling_repos = [row[0] for row in reader]

#%%
repo_dates = {}
with open('../data/repo_pr_date_ranges.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['Repository'] in sampling_repos:
            repo_dates[row['Repository']] = {'Min Date': row['Min Date'], 'Max Date': row['Max Date']}

#%%
repo_pr_counts = {}

#%%
with open("../data/sampled_issue_all_prs_no_date_filter.csv", mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Repository', 'PR Number', 'PR Title', 'Created At', 'URL'])

    for repo_name, dates in repo_dates.items():
        min_date = datetime.strptime(dates['Min Date'], '%Y-%m-%d').date()
        max_date = datetime.strptime(dates['Max Date'], '%Y-%m-%d').date()
        count = 0
        try:
            repository = g.get_repo(repo_name)
            prs = repository.get_pulls(state='all', sort='created', direction='asc')
            for pr in prs:
                # created_at = pr.created_at.date()
                # if min_date <= created_at <= max_date:
                writer.writerow([repo_name, pr.number, pr.title, pr.created_at, pr.html_url])
                count += 1
            repo_pr_counts[repo_name] = count
        except Exception as e:
            print(f"Failed to fetch PRs for {repo_name}. Error: {e}")

#%%
for repo, pr_count in repo_pr_counts.items():
    print(f"Repository: {repo}, Number of PRs: {pr_count}")

#%%
for repo, pr_count in repo_pr_counts.items():
    if pr_count == 1:
        print(f"Repository: {repo}, Number of PRs: {pr_count}")

#%%
for repo, dates in repo_dates.items():
    print(f"Repository: {repo}, Date Range: {dates['Min Date']} to {dates['Max Date']}")
# %%
