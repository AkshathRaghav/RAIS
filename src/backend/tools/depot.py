import os, json

class Depot: 
  def __init__(self, root_path, paper_path, repo_path):
    self.root_path = root_path  
    self.paper_path = paper_path
    self.repo_path = repo_path

    if not os.path.exists(self.root_path):  
      os.makedirs(self.root_path)
    if not os.path.exists(os.path.join(self.root_path, 'mapping.json')):
      with open(os.path.join(self.root_path, 'mapping.json'), 'w') as file:
        file.write('[]')

    if not os.path.exists(self.paper_path):
      os.makedirs(self.paper_path)
    if not os.path.exists(self.repo_path):
      os.makedirs(self.repo_path)
    
  def append_mapping(self, mapped_obj): 
      with open(os.path.join(self.root_path, 'mapping.json'), 'r') as file:
        mapping = json.load(file)
      mapping += [mapped_obj]
      with open(os.path.join(self.root_path, 'mapping.json'), 'w') as file:
        json.dump(mapping, file, indent=2)

  def save(self, paper, github):
    mapping = {}

    if paper: 
      paper_paths = paper.save(self.paper_path)
      mapping[paper.paper_url] = { 
        **paper_paths
      }
    if github: 
      repo_paths = github.save(self.repo_path) 
      mapping[f"{github.owner}/{github.repo}"] = { 
        **repo_paths
      }

    self.append_mapping(mapping)

  
  def load_git(self, url, branch): 
    # Ensure url is in format of 'https://github.com/AkshathRaghav/cubord.io'
    with open(os.path.join(self.root_path, 'mapping.json'), 'r') as file:
      mapping = json.load(file)
      
    repo_name = "/".join(url.split('/')[-2:])
    for run in mapping: # each saved object, logic = (Paper | Github)
      if repo_name in run.keys():
        from backend.evaluator.repository.github.github import Github
        github_obj = Github(
          owner=url.split('/')[-2], 
          repo=url.split('/')[-1], 
          branch=branch if branch else 'main',
          depot=None
        )

        with open(run[repo_name]['tree'], 'r') as file:   
          github_obj.tree_object.tree = json.load(file)
        
        with open(run[repo_name]['repo_metadata'], 'r') as file: 
          repo_metadata = json.load(file)
        with open(run[repo_name]['commit_history'], 'r') as file: 
          repo_metadata['commit_history'] = json.load(file)
        with open(run[repo_name]['star_history'], 'r') as file: 
          repo_metadata['star_history'] = json.load(file)
        
        github_obj.metadata_object.root_metadata = repo_metadata

        if run[repo_name]['organization_metadata']: 
          with open(run[repo_name]['organization_metadata'], 'r') as file: 
            github_obj.metadata_object.organization_metadata = json.load(file)

        if run[repo_name]['owner_metadata']:
          with open(run[repo_name]['owner_metadata'], 'r') as file: 
            github_obj.metadata_object.owner_metadata = json.load(file)

        temp = {} 
        if 'members' in run[repo_name]:
          for member in run[repo_name]['members']: 
            with open(member, 'r') as file: 
              temp[member.split('/')[-1].replace('.json', '')] = json.load(file)  
          
          github_obj.metadata_object.member_metadata = temp

        return github_obj

    return None 

  
  def load_paper(self, paper: str):
    with open(os.path.join(self.root_path, 'mapping.json'), 'r') as file:
      mapping = json.load(file)
    
    for run in mapping: # each saved object, logic = (Paper | Github)
      if paper in run.keys():
        from backend.evaluator.paper.paper import Paper
        paper_obj = Paper(paper, depot=None) # Use None, otherwise circular linkage 
        paper_obj.paper = paper_obj.load_paper()

        with open(run[paper]['paper_metadata'], 'r') as file:
          paper_obj.paper_metadata = json.load(file)

        for author in run[paper]['authors']:
          with open(author, 'r') as file:        
            paper_obj.author_metadata[author.replace('../depot/papers/authors/', '').replace('.json', '')] = json.load(file)

        return paper_obj

    return None 
  



  


