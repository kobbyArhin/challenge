#%%
import csv
import json
from datetime import datetime

#%%
all_prs = []
with open('../data/sampled_issue_all_prs_no_date_filter.csv', mode='r') as file:
    reader = csv.DictReader(file)
    all_prs = [row for row in reader]

#%%
issues_data = {}
with open('../data/retry/retry_prs.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        repo = row['Repository']
        chatgpt_prs = int(row['ChatGPT PRs'])
        issues_data[repo] = chatgpt_prs

#%%
pr_range_data = {}
with open('../data/repo_pr_date_ranges.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        repo = row['Repository']
        max_date = row['Max Date']
        pr_range_data[repo] = max_date

#%%
sampled_prs = []
tt = 0
tp = 0
for repo, max_date in pr_range_data.items():
    repo_prs = sorted([pr for pr in all_prs if pr['Repository'] == repo], key=lambda x: x['Created At'], reverse=True)
    index_of_max_date = next((i for i, pr in enumerate(repo_prs) if pr['Created At'] <= max_date), 0)
    sample_size = issues_data.get(repo, 0) * 2

    if sample_size > len(repo_prs):
        diff = sample_size - len(repo_prs)
        tt += diff
        print(repo+" lacking Prs: "+str(diff))
        continue

    selected_prs = []
    i = index_of_max_date
    while len(selected_prs) < sample_size and i >= 0:
        selected_prs.append(repo_prs[i])
        i -= 1

    i = index_of_max_date + 1
    while len(selected_prs) < sample_size and i < len(repo_prs):
        selected_prs.append(repo_prs[i])
        i += 1

    sampled_prs.extend(selected_prs)
    tp+=len(selected_prs)
print(tt)
print(tp)

#%%
with open('../data/chatgpt_prs.json', 'r') as f:
    chatgpt_prs_data = json.load(f)
chatgpt_prs_urls = [pr['URL'] for pr in chatgpt_prs_data['Sources']]

#%%
non_chatgpt_sample = []
matched_chatgpt_pr = []

for pr in sampled_prs:
    if pr['URL'] not in chatgpt_prs_urls:
        non_chatgpt_sample.append(pr)
    else:
        matched_chatgpt_pr.append(pr)

#%%
with open('../data/matched_prs.csv', mode='a', newline='', encoding='utf-8') as file: 
    csv_writer = csv.writer(file)
    for pr in matched_chatgpt_pr:
        csv_writer.writerow([pr['URL']])

#%%
with open('../data/new_non_chatgpt_sample.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Repository', 'PR Number', 'PR Title', 'Created At', 'URL'])
    for pr in non_chatgpt_sample:
        writer.writerow([pr['Repository'], pr['PR Number'], pr['PR Title'], pr['Created At'], pr['URL']])

#%%
repo_stats = {}

for pr in sampled_prs:
    repo = pr['Repository']
    date = datetime.strptime(pr['Created At'], '%Y-%m-%d %H:%M:%S').date()

    if repo not in repo_stats:
        repo_stats[repo] = {'min_date': date, 'max_date': date, 'count': 0}

    repo_stats[repo]['count'] += 1
    repo_stats[repo]['min_date'] = min(repo_stats[repo]['min_date'], date)
    repo_stats[repo]['max_date'] = max(repo_stats[repo]['max_date'], date)

#%%
with open('../data/new_sample_range.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Repository', 'Min Date', 'Max Date', 'Duration (days)', 'Number of PRs'])
    for repo, stats in repo_stats.items():
        duration = (stats['max_date'] - stats['min_date']).days + 1
        writer.writerow([repo, stats['min_date'], stats['max_date'], duration, stats['count']])

#%%
with open('../data/sampled_issue_all_prs_no_date_filter.json', 'r') as json_file:
    all_prs = json.load(json_file)

print(len(all_prs['Sources']))
#%%
selected_data = []

#%%
for pr_sample in non_chatgpt_sample:
    sample_url = pr_sample.get('URL')
    
    for pr in all_prs['Sources']:
        if pr.get('URL') == sample_url:
            selected_data.append(pr)
            break

# %%
sampled_prs_json = {"Sources": []}
sampled_prs_json["Sources"].extend(selected_data)
print(len(sampled_prs_json['Sources']))

#%%
with open('../data/issue_non_chatgpt_prs.json', 'w') as f:
    json.dump(sampled_prs_json, f, indent=4)

#%%
