"""
This code defines and executes a function to enhance and update JSON data related to GitHub pull requests:

Loading the JSON Data:

Load the existing JSON data from a provided file path.
GitHub Connection Setup:

Connect to the GitHub API using a provided personal access token.
Iterating Over JSON Sources:

For each source entry in the JSON data:
Check if the source is of type 'pull request'.
Extract the repository name and pull request number.
Fetch the pull request details from GitHub.
Enhancing the Source Data:

Add/Update the 'CommentsCount' for the pull request.
Fetch reviews of the pull request and filter out reviews made by bots.
Determine the earliest ('FirstReviewTime') and latest ('FinalReviewTime') review times among human reviewers.
Remove the 'ChatgptSharing' key from the source entry, if present.
Error Handling:

Gracefully handle any errors that occur while updating a pull request's data and log the error.
Saving the Updated Data:

Save the updated JSON data back to a specified file.
Execution:

The function is called to update the data for a given JSON file path and GitHub token.
"""


#%%
import json
import csv
from github import Github

#%%
def update_json_data(github_token, json_file_path):
    # Load the exclusions from the CSV
    exclusions = set()
    with open('../../data/prs_in_json_not_captured.csv', mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            exclusions.add((row["Repository"], int(row["PR Number"])))

    # Load the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    g = Github(github_token)

    filtered_sources = []
    for source in data['Sources']:
        if source['Type'] == "pull request" and (source['RepoName'], source['Number']) not in exclusions:
            filtered_sources.append(source)

    # Update only the filtered sources (exclude PRs in exclude.csv)
    for source in filtered_sources:
        repo_name = source['RepoName']
        pr_number = source['Number']

        try:
            repo = g.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            source['CommentsCount'] = pr.comments

            reviews = pr.get_reviews()

            human_reviews = [review for review in reviews if review.user and review.user.type == 'Bot']

            first_review_time = None
            final_review_time = None
            if human_reviews:
                review_times = [review.submitted_at for review in human_reviews]
                first_review_time = min(review_times)
                final_review_time = max(review_times)

            source['FirstReviewTime'] = first_review_time.strftime('%Y-%m-%dT%H:%M:%SZ') if first_review_time else None
            source['FinalReviewTime'] = final_review_time.strftime('%Y-%m-%dT%H:%M:%SZ') if final_review_time else None

            human_reviewer_names = list(set([review.user.login for review in human_reviews]))
            source['ReviewerCount'] = len(human_reviewer_names)
            source['Reviewers'] = human_reviewer_names

            if 'ChatgptSharing' in source:
                del source['ChatgptSharing']
        except Exception as e:
            print(f"Failed to update data for {repo_name} PR #{pr_number}. Error: {e}")

    data['Sources'] = filtered_sources

    with open('../../data/chatgpt/chatgpt_prs_bot.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)



#%%
YOUR_GITHUB_TOKEN = "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"
JSON_FILE_PATH = "../../snapshot_20230831/20230831_060603_pr_sharings.json"

#%%
update_json_data(YOUR_GITHUB_TOKEN, JSON_FILE_PATH)

# %%
