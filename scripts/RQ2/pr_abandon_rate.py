"""
This script calculates the abandonment rate of pull requests (PRs) from given JSON datasets. 
The abandonment rate is defined as the percentage of PRs that were closed without being merged.

The script processes two datasets:
1. Pull requests assisted by ChatGPT.
2. Pull requests not assisted by ChatGPT.

For each dataset, the script:
- Reads the dataset from a specified file path.
- Excludes PRs that are still open.
- Counts the number of total PRs (excluding those that are still open) and the number of abandoned PRs (closed without merging).
- Calculates the abandonment rate.
- Prints the statistics for each dataset.

The results offer insights into whether the use of ChatGPT assistance has any effect on the abandonment rate of PRs.
"""

#%%
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

#%%
def calculate_abandonment_rate_with_categories(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    total_prs = 0
    abandoned_prs = 0
    abandoned_categories = [] 
    merged_prs = 0
    merged_categories = [] 

    for pr in data['Sources']:
        if pr['State'] == "OPEN":
            continue

        total_prs += 1
        if pr['State'] == "CLOSED" and pr['MergedAt'] is None:
            abandoned_prs += 1
            abandoned_categories.append(pr['Category'])
        elif pr['State'] == "MERGED":
            merged_prs += 1
            merged_categories.append(pr['Category'])

    abandonment_rate = (abandoned_prs / total_prs) * 100 if total_prs > 0 else 0

    return {
        "all_prs": len(data['Sources']),
        "total_prs": total_prs,
        "abandoned_prs": abandoned_prs,
        "abandoned_categories": abandoned_categories,
        "merged_prs": merged_prs,
        "merged_categories": merged_categories,
        "abandonment_rate": abandonment_rate
    }

#%%
def combine_categories_for_plot(chatgpt_data, no_chatgpt_data):
    df_chatgpt_abandoned = pd.DataFrame({'Category': chatgpt_data['abandoned_categories'], 'Type': 'Abandoned ChatGPT-Generated PRs'})
    df_no_chatgpt_abandoned = pd.DataFrame({'Category': no_chatgpt_data['abandoned_categories'], 'Type': 'Abandoned Human-Generated PRs'})
    df_chatgpt_merged = pd.DataFrame({'Category': chatgpt_data['merged_categories'], 'Type': 'Merged ChatGPT-Generated PRs'})
    df_no_chatgpt_merged = pd.DataFrame({'Category': no_chatgpt_data['merged_categories'], 'Type': 'Merged Human-Generated PRs'})

    combined_df = pd.concat([df_chatgpt_abandoned, df_chatgpt_merged, df_no_chatgpt_abandoned, df_no_chatgpt_merged])
    return combined_df

#%%
def plot_prs_by_category(categories, title, save_path):
    plt.figure(figsize=(12, 8))
    sns.countplot(y=categories)
    plt.title(title)
    plt.xlabel('Number of PRs')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()

#%%
def plot_combined_prs_by_category(combined_df, save_path):
    plt.figure(figsize=(7, 4))
    hue_order = ['Merged ChatGPT-Generated PRs', 'Merged Human-Generated PRs', 
                 'Abandoned ChatGPT-Generated PRs', 'Abandoned Human-Generated PRs']
    palette = {'Merged ChatGPT-Generated PRs': 'green', 
               'Merged Human-Generated PRs': 'blue', 
               'Abandoned ChatGPT-Generated PRs': 'orange', 
               'Abandoned Human-Generated PRs': 'red'}

    sns.countplot(y='Category', hue='Type', data=combined_df, hue_order=hue_order, palette=palette)
    plt.title('PR Categories by Type')
    plt.xlabel('Number of PRs')
    plt.ylabel('')
    plt.legend(title='Type')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()


#%%
chatgpt_json_path = '../../data/analysis/matched_chatgpt_prs.json'
non_chatgpt_json_path = '../../data/analysis/matched_non_chatgpt_prs.json'

chatgpt_data = calculate_abandonment_rate_with_categories(chatgpt_json_path)
no_chatgpt_data = calculate_abandonment_rate_with_categories(non_chatgpt_json_path)

#%%
combined_df = combine_categories_for_plot(chatgpt_data, no_chatgpt_data)

#%%
plot_combined_prs_by_category(combined_df, '../../plots/RQ2/combined_pr_categories_plot.png')

#%%
# Print stats
print(f"All PRs with ChatGPT assistance: {chatgpt_data['all_prs']}")
print(f"Total PRs with ChatGPT assistance: {chatgpt_data['total_prs']}")
print(f"Abandoned PRs with ChatGPT assistance: {chatgpt_data['abandoned_prs']}")
print(f"Merged PRs with ChatGPT assistance: {chatgpt_data['merged_prs']}")
print(f"Abandonment Rate for PRs with ChatGPT assistance: {chatgpt_data['abandonment_rate']:.2f}%")

print(f"All PRs without ChatGPT assistance: {no_chatgpt_data['all_prs']}")
print(f"Total PRs without ChatGPT assistance: {no_chatgpt_data['total_prs']}")
print(f"Abandoned PRs without ChatGPT assistance: {no_chatgpt_data['abandoned_prs']}")
print(f"Merged PRs without ChatGPT assistance: {no_chatgpt_data['merged_prs']}")
print(f"Abandonment Rate for PRs without ChatGPT assistance: {no_chatgpt_data['abandonment_rate']:.2f}%")

# %%
from scipy.stats import mannwhitneyu
from cliffs_delta import cliffs_delta

# %%
def calculate_category_distribution(data):
    category_distribution = {}
    for category in data:
        if category not in category_distribution:
            category_distribution[category] = 1
        else:
            category_distribution[category] += 1
    return category_distribution
#%%
cat1_freq = calculate_category_distribution(no_chatgpt_data['merged_categories'])

#%%
def perform_mannwhitneyu_test(cat1, cat2, cat1_name, cat2_name):
    cat1_freq = list(calculate_category_distribution(cat1).values())
    cat2_freq = list(calculate_category_distribution(cat2).values())

    len_diff = len(cat1_freq) - len(cat2_freq)
    if len_diff > 0:
        cat2_freq.extend([0] * len_diff) 
    elif len_diff < 0:
        cat1_freq.extend([0] * abs(len_diff))

    u_stat, p_value = mannwhitneyu(cat1_freq, cat2_freq)
    cliffs_size, cliffs_expl = cliffs_delta(cat1_freq, cat2_freq)

    print(f"The Mann-Whitney U test between {cat1_name} and {cat2_name}:")
    print("U statistic:", u_stat)
    print("P-value:", p_value)
    print("Cliff's delta effect size:", cliffs_size)
    print("explanation:", cliffs_expl)


# %%
perform_mannwhitneyu_test(chatgpt_data['abandoned_categories'], chatgpt_data['merged_categories'], 'ChatGPT Abandoned', 'ChatGPT Merged')

#%%
perform_mannwhitneyu_test(no_chatgpt_data['abandoned_categories'], no_chatgpt_data['merged_categories'], 'Non-ChatGPT Abandoned', 'Non-ChatGPT Merged')

#%%
perform_mannwhitneyu_test(chatgpt_data['abandoned_categories'], no_chatgpt_data['abandoned_categories'], 'ChatGPT Abandoned', 'Non-ChatGPT Abandoned')

#%%
perform_mannwhitneyu_test(chatgpt_data['merged_categories'], no_chatgpt_data['merged_categories'], 'ChatGPT Merged', 'Non-ChatGPT Merged')

# %%
