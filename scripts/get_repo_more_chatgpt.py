#%%
import csv

#%%
def filter_repositories(row):
    difference = int(row["Difference"])
    num_prs = int(row["Number of PRs"])
    return num_prs >= 2 * difference

#%%
with open('../data/repo_pr_date_ranges.csv', newline='') as input_csvfile:
    reader = csv.DictReader(input_csvfile)
    
    filtered_data = []
    for row in reader:
        if filter_repositories(row):
            filtered_row = {
                "Repository": row["Repository"],
                "Number of ChatGPT PRs": row["Number of PRs"],
                "PR from GitHub": row["PR from GitHub"],
                "No of Non ChatGPT PRs": row["Difference"]
            }
            filtered_data.append(filtered_row)

#%%
output_csvfile = '../data/repos_with_less_or_equal_chat.csv'

#%%
with open(output_csvfile, mode='w', newline='') as output_csvfile:
    fieldnames = ["Repository", "PR from GitHub", "Number of ChatGPT PRs", "No of Non ChatGPT PRs"]
    writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for row in filtered_data:
        writer.writerow(row)


#%%
print(f"Filtered rows saved to {output_csvfile}")

# %%
