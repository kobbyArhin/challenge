#%%
import csv
import json
from github import Github, RateLimitExceededException
import re


#%%
def switch_token():
    global current_token_index
    current_token_index = (current_token_index + 1) % len(tokens)
    return tokens[current_token_index]

#%%
def extract_repo_and_pr(url):
    match = re.search(r'github\.com/([\w-]+)/([\w-]+)/pull/(\d+)', url)
    if match:
        repo_name = match.group(1) + '/' + match.group(2)
        pr_number = int(match.group(3))
        return repo_name, pr_number
    return None, None

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
        return get_pr_data_from_github(tokens, repo_name, pr_number)

#%%
tokens = [
  "YOUR_TOKEN_HERE"
]
current_token_index = 0
pr_data_list = []

# %%
with open('../../data/non_chatgpt/url_not_in_json.csv', 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        url = row["Unmatched URL"]
        repo_name, pr_number = extract_repo_and_pr(url)
        if repo_name and pr_number:
            pr_data = get_pr_data_from_github(tokens, repo_name, pr_number)
            if pr_data:
                pr_data_list.append(pr_data)

#%%
final_data = {"Sources": pr_data_list}
print(f"Collected {len(final_data['Sources'])} PRs")
with open('../../data/non_chatgpt/url_not_in_json.json', 'w', encoding='utf-8') as json_file:
    json.dump(final_data, json_file, indent=4)

# %%
