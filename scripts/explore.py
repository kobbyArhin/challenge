# -*- coding: utf-8 -*-

"""
The script is a straightforward program that reads and prints the contents of a JSON file.

Here's a breakdown of its functionality:

Encoding Specification:

The script specifies the encoding as UTF-8 using the magic comment # -*- coding: utf-8 -*-. This ensures that the script will handle any characters in the UTF-8 character set properly.
File Loading:

Utilizes the json library to read the contents of a JSON file named 20230831_060603_pr_sharings.json, located in the directory ../snapshot_20230831/.
Data Display:

Once the JSON data is loaded into the variable pr, the script prints the entire content of the JSON file to the console.
In essence, this script is used for displaying the content of the specified JSON file to understand or inspect its data structure and values.
"""

#%%
import json


#%%
with open('../data/no_chatgpt_prs_sample.json', 'r') as file:
    data = json.load(file)
    
#%%
print(len(data['Sources']))

# %%
