import json
import os
import re

import requests

os.environ["PYTHONPATH"] = "/".join(os.getcwd().split("/")[:-1]) + "/src/"
print(os.environ["PYTHONPATH"])
os.environ["GITHUB_AUTH_TOKEN"] = "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"
from backend.evaluator.paper.paper import Paper
from backend.evaluator.repository.github.github import Github
from backend.tools.depot import Depot

# Ensure you've either downloaded from depot/ folder from the drive or have the below structure setup
# - depot/
#   - papers/
#     - authors/
#   - repository/
#     - owner/
#     - organization/
#     - member/

depot = Depot(root_path="../depot", paper_path="../depot/papers", repo_path="../depot/repository")

import pandas as pd

mapping = pd.read_csv("/home/aksha/Workbench/Research/Labs/cves/depot/mapping.csv")

for row in mapping.iterrows():
    entry = row[1]
    print(entry)
    git = Github(
        owner=entry["Github"].split("/")[-2],
        repo=entry["Github"].split("/")[-1],
        branch=entry["Branch"] if "Branch" in entry and str(entry["Branch"]) != "nan" else "main",
        depot=depot,
    )
    if git.processed:
        git = None
    else:
        git.get_meta(level="owner")

        git.get_tree()
        git.enrich_tree()

    if str(row[1]["Paper"]) != "nan":
        paper = Paper(entry["Paper"], depot=depot)
        if paper.processed:
            paper = None
        else:
            paper.get_paper()
    else:
        paper = None

    depot.save(paper, git)
