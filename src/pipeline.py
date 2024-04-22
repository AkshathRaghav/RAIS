from backend.tools.depot import Depot
from backend.evaluator.repository.github.github import Github
from backend.evaluator.paper.paper import Paper
import os
import requests
import json
import re
from collections import Counter
import pandas as pd

os.environ["PYTHONPATH"] = "/".join(os.getcwd().split("/")[:-1]) + "/src/"
print(os.environ["PYTHONPATH"])
os.environ["GITHUB_AUTH_TOKEN"] = "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"


# Ensure you've either downloaded from depot/ folder from the drive or have the below structure setup
# - depot/
#   - papers/
#     - authors/
#   - repository/
#     - owner/
#     - organization/
#     - member/

depot = Depot(
    root_path="../depot", paper_path="../depot/papers", repo_path="../depot/repository"
)



with open('/home/aksha/Workbench/Research/Labs/cves/depot/mapping.json') as f: 
    mapping = json.load(f)

gits = []
for record in mapping: 
  for rec in record: 
    if 'branch' in record[rec]: 
      gits.append([rec, record[rec]['branch']])


def calculate_file_tree_metrics(file_tree):
    file_type_counts = {}
    max_files_in_folder = 0
    tree_depth = 0
    cohesive_folders_count = 0
    total_folders_count = 0

    def traverse(node, current_depth):
        nonlocal max_files_in_folder, tree_depth, cohesive_folders_count, total_folders_count
        if current_depth > tree_depth:
            tree_depth = current_depth
        max_files_in_folder = max(max_files_in_folder, node.get('number_of_files', 0))
        
        if 'children' in node:
            folder_file_types = set()
            for child in node['children']:
                if 'children' not in child:
                    file_extension = child['path'].split('.')[-1]
                    folder_file_types.add(file_extension)
                    file_type_counts[file_extension] = file_type_counts.get(file_extension, 0) + 1
                else:
                    traverse(child, current_depth + 1)
            
            # Increment the folder counts
            if folder_file_types:
                total_folders_count += 1
                if len(folder_file_types) == 1:
                    cohesive_folders_count += 1

    traverse(file_tree, 0)

    # Calculating percentages for file types
    total_files = sum(file_type_counts.values())
    file_type_percentages = {file_type: round(float(count / total_files), 2) * 100 for file_type, count in file_type_counts.items()}

    # Calculating File Type Cohesion Percentage
    file_type_cohesion_percentage = (cohesive_folders_count / total_folders_count) * 100 if total_folders_count else 0

    return file_type_percentages, tree_depth, max_files_in_folder, file_type_cohesion_percentage
def convert_to_year_month(datetime_string):
    datetime_obj = pd.to_datetime(datetime_string)
    year_month = datetime_obj.strftime('%Y-%m')
    return year_month
def load_license(git): 
    files = git.find_files('LICENSE')
    if not files: return None
    x = git.load_file(files[0])
    if not x: 
        return None
    return x


def make_df(git, commit_history): 
    file_type_percentages, depth_of_tree, max_files, file_type_cohesion_percentage = calculate_file_tree_metrics(git.tree)
    repo_data = {
        "members": [len(git.metadata['metadata']['members'])],
        "stars": [git.metadata['metadata']['stars']],
        "commits": [git.metadata['metadata']['commits']],
        "forks": [git.metadata['metadata']['forks']],
        "issues": [git.metadata['metadata']['issues']],
        "watchers": [git.metadata['metadata']['watchers']],
        "prs": [git.metadata['metadata']['prs']],
        "num_md_files": [len(git.find_files_by_suffix(".md"))],
        "total_subfolders": [git.tree['number_of_subfolders']],
        "has_wiki": [int(git.metadata['metadata']['has_wiki'])],
        "has_readme": [int(bool(git.find_files("README.md")))],
        "has_dependencies": [int(bool(git.find_files("requirements.txt") + git.find_files_by_suffix(".lock") + git.find_files("Pipfile") + git.find_files(".toml")))],
        "has_config": [int(bool(git.find_files_by_suffix(".yaml") + git.find_files_by_suffix(".yml")))],
        "has_license": [int(bool(git.find_files("LICENSE")))],
        "has_contributing": [int(bool(git.find_files("CONTRIBUTING.md")))],
        "has_code_of_conduct": [int(bool(git.find_files("CODE_OF_CONDUCT.md")))],
        "has_workflows": [int(bool(git.find_files(".github/workflows")))],
        "has_organization": [int(bool(git.metadata['metadata']['organization']))],
        "owner_followers": [git.metadata['owner']['followers']],
        "owner_repo_count": [git.metadata['owner']['repo_count']],
        "owner_stars": [git.metadata['owner']['metadata']['stars']],
        "owner_watchers": [git.metadata['owner']['metadata']['watchers']],
        "owner_prs": [git.metadata['owner']['metadata']['prs']],
        "license": [load_license(git)],
        "depth_of_tree": [depth_of_tree],
        "max_files_in_folder": [max_files],
        "file_type_cohesion_percentage": [file_type_cohesion_percentage],
        "file_type_percentages": [file_type_percentages],
    }
    return pd.DataFrame(repo_data)

df = pd.DataFrame() 

for gi in gits: 
  git = depot.load_git(gi[0], gi[1])
  commit_history = [convert_to_year_month(x[1]) for x in git.metadata['commit_history']]
  df_ = make_df(git, commit_history)
  df = pd.concat([df, df_], ignore_index=True)

df.to_csv('repo_data.csv', index=False)