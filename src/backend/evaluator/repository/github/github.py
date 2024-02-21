from backend.evaluator.repository.github.tree import Tree
from backend.evaluator.repository.github.metadata import Metadata

import requests, re

class Github: 
    def __init__(self, owner, repo, branch):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.tree = None 
        self.metadata = None

    @property
    def file_tree(self):
        return self.tree.tree
    
    @property
    def repo_data(self):
        return { 
            'commit_history': self.metadata.root_metadata['commit_data'],
            'owner': self.metadata.owner_metadata,
            'organization': self.metadata.organization_metadata,
            'members': self.metadata.member_metadata,
            'metadata': {key: value for key, value in self.metadata.root_metadata.items() if key != 'commit_data'}
        }
    
    def get_tree(self, file_path=None):
        self.tree = Tree(owner=self.owner, repo=self.repo, branch=self.branch, file_path=file_path)

    def get_meta(self): 
        self.metadata = Metadata(owner=self.owner, repo=self.repo)

    def find_md_files(self):
        # Ensure we match .md files at the end of each line in the multiline string
        pattern = re.compile(r'^.*\.md$', re.MULTILINE)
        return pattern.findall(self.tree.tree_string)

    def check_keyword(self, keyword):
        pattern = re.compile(r'^.*' + keyword + '.*$', re.MULTILINE)
        return pattern.findall(self.tree.tree_string)

    def extract_markdown_headers(self, path):
        content = self.get_file(path)  # Assuming this function exists
        headers = re.findall(r'^#+\s*(.*)', content, re.MULTILINE)
        return headers

    def get_file(self, path): 
        url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # This is the file content as a string
        else:
            print(f"Failed to fetch file: HTTP {response.status_code}")
            return None

    def extract_code_elements(self, file_path):
        if file_path.endswith('.py'):
            file_raw = self.get_file(file_path)

            # Extract function names
            function_pattern = r'\bdef\b\s+(\w+)\('
            function_names = re.findall(function_pattern, file_raw)

            # Extract class names
            class_pattern = r'\bclass\b\s+(\w+)\s*:'
            class_names = re.findall(class_pattern, file_raw)

            # Extract called functions
            called_function_pattern = r'(\w+)\('
            called_functions = re.findall(called_function_pattern, file_raw)

            common_python_functions = [
                'print', 'len', 'type', 'range', 'open', 'input', 'int', 'str', 'float', 'list', 
                'dict', 'set', 'tuple', 'bool', 'max', 'min', 'abs', 'sum', 'round', 'sorted', 
                'reversed', 'enumerate', 'zip', 'map', 'filter', 'any', 'all', 'dir', 'help', 'id' , 'isinstance'
            ]

            called_functions = [func for func in called_functions if func not in common_python_functions and "__" not in func and len(func.replace('__', '')) > 5]
            
            return { 
                'functions': list(set(function_names)), 
                'classes':  list(set(class_names)), 
                'called_functions':  list(set(called_functions))
            }
        else: 
            return [] 

    def enrich_tree(self): 
        self.tree.tree = self.enirch(self.tree.tree)
        self.tree.enriched = True

    def enirch(self, tree, parent_path=''):
        tree = tree.copy()
        
        tree['path'] = f"{parent_path}/{tree['path']}" if parent_path else tree['path']

        # If this is a file, return its path
        if 'children' not in tree:
            return tree
        else: 
            tree['type'] = 'folder'

        # This is a folder, so we'll process its children
        children = []
        file_paths = []
        num_subfolders = 0
        num_subfiles = 0
        for child in tree.get('children', []):
            result = self.enirch(child, tree['path'])
            if result['type'] != 'folder':  # This is a file path
                file_paths.append(result['path'])
                num_subfiles += 1
            else:  # This is a folder
                num_subfolders += 1
                num_subfiles += result['number_of_subfiles']  # Add the number of subfiles in the subfolder
            children.append(result)

        # Extract keywords from the file paths
        keywords = {file_path: self.extract_code_elements(file_path) for file_path in file_paths}

        # Update the tree
        tree['children'] = children
        tree['keywords'] = keywords
        tree['number_of_subfolders'] = num_subfolders
        tree['number_of_subfiles'] = num_subfiles

        return tree