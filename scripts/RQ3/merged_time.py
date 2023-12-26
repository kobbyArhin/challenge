
"""
This script performs the following high-level tasks:

Import Libraries:

Essential libraries are imported: numpy for numerical operations, json for data loading, datetime for date/time manipulations, and matplotlib for plotting.
Load Data:

A JSON file containing data about pull requests is loaded.
Calculate PR Statistics:

The script calculates the number of pull requests based on their state (merged, closed, open) and computes the percentage for each state.
Calculate Time to Merge:

The function calculate_merge_time computes the time it takes for a PR to merge based on its creation and merge timestamps.
Repository-wise Time to Merge:

The script then aggregates the merge times per repository.
Average Time Calculations:

For each repository, the average merge time is calculated. Additionally, the overall average merge time across all repositories is determined.
Display Results:

The script prints the calculated statistics and average times.
Boxplot Visualization:

Using matplotlib, a boxplot is generated to visualize the distribution of average merge times across repositories. The plot displays the mean and median values for clearer understanding and is saved as an image.
In essence, this script provides insights into the lifecycle of pull requests, focusing particularly on the average time it takes for them to merge across different repositories.
"""


#%%
import numpy as np
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from cliffs_delta import cliffs_delta

#%% 
def calculate_merge_time(pr):
    if pr["MergedAt"]:
        try:
            created_at = datetime.strptime(pr["CreatedAt"], '%Y-%m-%dT%H:%M:%SZ')
            merged_at = datetime.strptime(pr["MergedAt"], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            created_at = datetime.strptime(pr["CreatedAt"], '%Y-%m-%dT%H:%M:%S')
            merged_at = datetime.strptime(pr["MergedAt"], '%Y-%m-%dT%H:%M:%S')
        return (merged_at - created_at).total_seconds() / (60 * 60)
    return None

#%% 
def process_data(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    prs = data["Sources"]
    merge_times = [calculate_merge_time(pr) for pr in prs if pr["State"] == "MERGED"]
    merged_prs = [pr for pr in data["Sources"] if pr["MergedAt"]]
    return [time for time in merge_times if time is not None], merged_prs

#%% 
def plot_merge_times(chatgpt_times, non_chatgpt_times, plot_path):
    fig, ax = plt.subplots(figsize=(6, 4))
    data = [chatgpt_times, non_chatgpt_times]
    sns.violinplot(data=data, ax=ax, inner=None)

    means = [np.mean(times) for times in data]
    medians = [np.median(times) for times in data]
    positions = range(len(data))

    offset = 120

    for pos, mean, median in zip(positions, means, medians):
        ax.text(pos, mean - offset, f'Mean: {mean:.2f}', horizontalalignment='center', size='small', color='white', weight='semibold')
        ax.text(pos, median - offset, f'Median: {median:.2f}', horizontalalignment='center', size='small', color='white', weight='semibold')

    ax.set_xticklabels(['ChatGPT PRs', 'Non-ChatGPT PRs'])
    ax.set_ylabel('Merge Time (Hours)')
    ax.set_title('Comparison PR of Merge Times: ChatGPT vs. Non-ChatGPT PRs')

    plt.tight_layout()
    plt.savefig(plot_path, dpi=800)
    plt.show()

#%% 
chatgpt_json_path = '../../data/analysis/matched_chatgpt_prs.json'
non_chatgpt_json_path = '../../data/analysis/matched_non_chatgpt_prs.json'
plot_path = '../../plots/RQ3/comparison_merge_times.png'

chatgpt_times, chatgpt_prs = process_data(chatgpt_json_path)
non_chatgpt_times, non_chatgpt_prs = process_data(non_chatgpt_json_path)

#%%
_, p_value = stats.mannwhitneyu(chatgpt_times, non_chatgpt_times)
cliffs_size, cliffs_expl = cliffs_delta(chatgpt_times, non_chatgpt_times)
print(f"Statistical analysis of merged time, \nP-value = {p_value}, P-value < 0.05 = {p_value < 0.05}, \ncliff's delta effect size = {cliffs_size}, cliff's delta explanation = {cliffs_expl}\n")

#%% 
plot_merge_times(chatgpt_times, non_chatgpt_times, plot_path)

#%%
fields = ['CommitsTotalCount','Additions','Deletions','ChangedFiles']

#%%
for f in fields:
    chatgpt = [pr[f] for pr in chatgpt_prs if f in pr]
    non_chatgpt = [pr[f] for pr in non_chatgpt_prs if f in pr]
    print(f"The average number of {f} in Chagpt is {np.mean(chatgpt)}")
    print(f"The average number of {f} in Non-Chagpt is {np.mean(non_chatgpt)}")
    _, p_value = stats.mannwhitneyu(chatgpt, non_chatgpt)
    cliffs_size, cliffs_expl = cliffs_delta(chatgpt, non_chatgpt)
    print(f"Using {f}, \nP-value = {p_value}, P-value < 0.05 = {p_value < 0.05}, \ncliff's delta effect size = {cliffs_size}, cliff's delta explanation = {cliffs_expl}\n")


# %%
