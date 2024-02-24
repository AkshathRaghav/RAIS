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
        file.write('{}')
    else: 
      with open(os.path.join(self.root_path, 'mapping.json'), 'r') as file:
        self.mapping = json.load(file)
    if not os.path.exists(self.paper_path):
      os.makedirs(self.paper_path)
    if not os.path.exists(self.repo_path):
      os.makedirs(self.repo_path)

  def save(self, paper, github):
    if paper: paper_paths = paper.save(self.paper_path)
    if github: repo_paths = github.save(self.repo_path) 
    
    if github and paper: 
      with open(os.path.join(self.root_path, 'mapping.json'), 'r') as file:
        mapping = json.load(file)
        mapping
        mapping[paper.paper_url] = { 
          **paper_paths,
          **repo_paths
        }
      with open(os.path.join(self.root_path, 'mapping.json'), 'w') as file:
        json.dump(mapping, file)



  


