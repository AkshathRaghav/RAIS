import os 
import requests
import json
import re
os.environ['PYTHONPATH'] = os.getcwd()
os.environ['GITHUB_AUTH_TOKEN'] = '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'
from backend.evaluator.paper.paper import Paper
from backend.evaluator.repository.github.github import Github
from backend.tools.depot import Depot

db = [
    { "paper": "https://arxiv.org/abs/2106.12915", "repo": "https://github.com/deel-ai/relu-prime", "branch": "master" },
    { "paper": "https://arxiv.org/abs/2203.01928", "repo": "https://github.com/JonathanCrabbe/Label-Free-XAI" }, 
    { "paper": "https://arxiv.org/abs/2204.04601", "repo": "https://github.com/YuYang0901/LaViSE" }, 
    { "paper": "https://arxiv.org/abs/2210.12529", "repo": "https://github.com/ericzhao28/multidistributionlearning", "branch": "master" }, 
    { "paper": "https://arxiv.org/abs/2202.02763", "repo": "https://github.com/oxcsml/riemannian-score-sde" }, 
    { "paper": "https://arxiv.org/abs/2303.14969", "repo": "https://github.com/GitGyun/visual_token_matching" }, 
    { "paper": "https://arxiv.org/abs/2301.09505", "repo": "https://github.com/lsj2408/Graphormer-GD", "branch": "master" },
    { "paper": "https://arxiv.org/abs/2209.14988", "repo": "https://github.com/ashawkey/stable-dreamfusion" }, 
    { "paper": "https://arxiv.org/abs/2012.09816", "repo": "https://github.com/nagra-insight/knowledge-distillation", "branch": "master" }, 
    { "paper": "https://arxiv.org/abs/2210.05492", "repo": "https://github.com/facebookresearch/diplomacy_cicero" }
]

for entry in db: 

  # Ensure you've either downloaded from depot/ folder from the drive or have the below structure setup 
  # - depot/
  #   - papers/
  #     - authors/
  #   - repository/
  #     - owner/
  #     - organization/ 
  #     - member/

  depot = Depot(
    root_path='../depot', 
    paper_path='../depot/papers',
    repo_path='../depot/repository'
  )
  git = Github(owner=entry['repo'].split('/')[-2], 
    repo=entry['repo'].split('/')[-1], 
    branch=entry['branch'] if 'branch' in entry else 'main', 
    depot=depot
  ) 
  paper = Paper(
    entry['paper'], 
    depot=depot
  )


  git.get_meta()

  git.get_tree()
  git.enrich_tree()

  paper.get_paper()

  depot.save(paper, git)