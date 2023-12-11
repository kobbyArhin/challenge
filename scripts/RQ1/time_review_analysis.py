"""
This script provides a comprehensive analysis of the time taken for pull requests (PRs) to receive their first review or to be closed. It processes PR datasets, calculates relevant statistics, and then visualizes the data using box plots.

Here's a breakdown of the functionalities:

Data Extraction:

Extracts and processes the 'CreatedAt' timestamp and 'FirstReviewTime' timestamp of each PR from the provided JSON datasets.
If a 'FirstReviewTime' is not available, it uses the 'ClosedAt' timestamp as an alternative.
Calculates the duration between PR creation and its first review or closure.
Stores relevant details (e.g., 'RepoName', 'Number', 'URL', and 'ReviewTime') for further analysis.
Visualization:

Visualizes the times-to-review for PRs using a box plot.
The plot showcases the distribution of times taken for PRs to be reviewed or closed.
Median and mean values are indicated as dashed lines on the box plot for reference.
Statistics Calculation:

Computes basic statistics (mean, median, minimum, and maximum) for the review times.
Presents these statistics in a user-friendly format, showing them in days, hours, minutes, and seconds.
The script executes these functions for two datasets:

PRs with ChatGPT assistance.
PRs without ChatGPT assistance.
The end goal is to provide insights into how quickly PRs are addressed, comparing PRs with and without the assistance of ChatGPT.
"""

#%%
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import statistics
import scipy.stats as stats
from cliffs_delta import cliffs_delta

#%% Function to remove 'Z' if present in datetime string
def remove_Z_if_present(datetime_str):
    return datetime_str[:-1] if datetime_str.endswith('Z') else datetime_str

#%% Function to extract times to review
def extract_times_to_review_with_category(data):
    pr_details = []
    reviewed_prs = []
    for source in data['Sources']:
        created_at = datetime.fromisoformat(remove_Z_if_present(source['CreatedAt']))
        category = source['Category'] # Extract the category
        
        first_review_time = source.get('FirstReviewTime')
        if first_review_time:
            review_time = datetime.fromisoformat(remove_Z_if_present(first_review_time))
            reviewed_prs.append(source)
        elif source['ClosedAt']:
            review_time = datetime.fromisoformat(remove_Z_if_present(source['ClosedAt']))
            reviewed_prs.append(source)
        else:
            continue
        
        time_to_review = review_time - created_at
        pr_details.append((time_to_review, category)) # Store time and category
    
    return pr_details, reviewed_prs


#%% Function to visualize review times with bean plot
def visualize_review_times(review_times, title, save_path):
    days = [r.total_seconds() / (3600) for r in review_times]

    mean_val = np.mean(days)
    median_val = np.median(days)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=days, ax=ax, inner=None)

    ax.set_ylabel('Time to Review (Hours)')
    ax.set_title(title)

    # Adding mean and median lines
    ax.axhline(median_val, color='blue', linestyle='dashed', linewidth=1)
    ax.text(0.5, median_val, f'Median: {median_val:.2f}', horizontalalignment='right', verticalalignment='center', color='blue')
    ax.axhline(mean_val, color='red', linestyle='dashed', linewidth=1)
    ax.text(0.5, mean_val, f'Mean: {mean_val:.2f}', horizontalalignment='right', verticalalignment='center', color='red')

    plt.tight_layout()
    plt.savefig(save_path, dpi=800)
    plt.show()

#%%
def visualize_review_times_by_category(review_times_with_category, save_path):
    categories = set([category for _, category in review_times_with_category])
    data_to_plot = {category: [] for category in categories}

    for time, category in review_times_with_category:
        hours = time.total_seconds() / 3600  # Calculate time in hours
        data_to_plot[category].append(hours)

    averages = {cat: np.mean(vals) for cat, vals in data_to_plot.items()}
    
    sorted_cats = sorted(averages, key=averages.get)

    # Create horizontal bar plot
    fig, ax = plt.subplots(figsize=(12, 8))
    y_positions = range(len(sorted_cats))
    ax.barh(y_positions, [averages[cat] for cat in sorted_cats], color='skyblue')
    ax.set_yticks(y_positions)
    ax.set_yticklabels(sorted_cats)
    ax.set_xlabel('Average Time to First Response (hours)')
    ax.set_title('Average Time to First Response by Type of Changes in PR (Non-ChatGPT)')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()

#%%
def convert_to_hours(time_tuple):
    days, hours, minutes, seconds = time_tuple
    total_hours = days * 24 + hours + minutes / 60 + seconds / 3600
    return total_hours

#%% Function to visualize combined review times with bean plot
def visualize_combined_review_times(chatgpt_review_times, no_chatgpt_review_times, save_path):
    chatgpt_times = [time for time, _ in chatgpt_review_times_with_category]
    non_chatgpt_times = [time for time, _ in no_chatgpt_review_times_with_category]

    chatgpt_hours = [t.total_seconds() / 3600 for t in chatgpt_times]
    no_chatgpt_hours = [t.total_seconds() / 3600 for t in non_chatgpt_times]

    data_to_plot = [chatgpt_hours, no_chatgpt_hours]

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.violinplot(data=data_to_plot, ax=ax, inner=None)

    means = [np.mean(times) for times in data_to_plot]
    medians = [np.median(times) for times in data_to_plot]
    positions = range(len(data_to_plot))

    for pos, mean, median in zip(positions, means, medians):
        ax.text(pos, mean, f'Mean: {mean:.2f}', horizontalalignment='center', size='small', color='black', weight='semibold')
        ax.text(pos, median, f'Median: {median:.2f}', horizontalalignment='center', size='small', color='white', weight='semibold')

    ax.set_xticklabels(['ChatGPT-Generated PRs', 'Human-Generated PRs'])
    ax.set_ylabel('Time to First Response (Hours)')
    ax.set_title('Comparison of Time to First Response')
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(save_path, dpi=800)
    plt.show()

#%% 
with open('../../data/analysis/matched_chatgpt_prs.json', 'r') as file:
    chatgpt_data = json.load(file)
chatgpt_review_times_with_category, chatgpt = extract_times_to_review_with_category(chatgpt_data)

#%% 
with open('../../data/analysis/matched_non_chatgpt_prs.json', 'r') as file:
    no_chatgpt_data = json.load(file)

no_chatgpt_review_times_with_category, non_chatgpt = extract_times_to_review_with_category(no_chatgpt_data)
#%% Visualize both ChatGPT and Non-ChatGPT review times together
visualize_combined_review_times(chatgpt_review_times_with_category, no_chatgpt_review_times_with_category, '../../plots/RQ1/combined_review_times.png')

#%%
chatgpt_times = [time for time, _ in chatgpt_review_times_with_category]
non_chatgpt_times = [time for time, _ in no_chatgpt_review_times_with_category]
chatgpt_times_hours = [t.total_seconds() / 3600 for t in chatgpt_times]
non_chatgpt_times_hours = [t.total_seconds() / 3600 for t in non_chatgpt_times]

#%%
_, p_value = stats.mannwhitneyu(chatgpt_times_hours, non_chatgpt_times_hours)
cliffs_size, cliffs_expl = cliffs_delta(chatgpt_times_hours, non_chatgpt_times_hours)
print(f"Statistical analysis of time to first response, \nP-value = {p_value}, P-value < 0.05 = {p_value < 0.05}, \ncliff's delta effect size = {cliffs_size}, cliff's delta explanation = {cliffs_expl}\n")
# %%
fields = ['CommitsTotalCount','CommentsCount','ReviewerCount','Additions','Deletions','ChangedFiles']

#%%
for f in fields:
    chatgpt_f = [pr[f] for pr in chatgpt if f in pr]
    non_chatgpt_f = [pr[f] for pr in non_chatgpt if f in pr]
    _, p_value = stats.mannwhitneyu(chatgpt_f, non_chatgpt_f)
    cliffs_size, cliffs_expl = cliffs_delta(chatgpt_f, non_chatgpt_f)
    print(f"Using {f}, \nP-value = {p_value}, P-value < 0.05 = {p_value < 0.05}, \ncliff's delta effect size = {cliffs_size}, cliff's delta explanation = {cliffs_expl}\n")
# %%
