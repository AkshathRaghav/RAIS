from backend.evaluator.repository.github.tree import Tree
from backend.evaluator.repository.github.metadata import Metadata
from backend.tools.depot import Depot   
import requests, re, os, json
from backend.tools.logger import LoggerSetup  

class Github: 
    def __init__(self, owner, repo, branch, depot: Depot):  
        logging_setup = LoggerSetup('Github')
        self.logger = logging_setup.get_logger()

        self.owner = owner
        self.repo = repo
        self.branch = branch
        
        # Check if the repository has already been processed
        if (owner, repo, branch) in [(x['owner'].replace('.json', '').replace('../depot/repository/owner/', ''), x['repo'], x['branch']) for x in depot.mapping.values() if x]:
            self.logger.info('Repository already processed. Skipping...')
            return

        self.tree_object = None 
        self.metadata_object = None

        self.logger.info('Github object created for %s/%s/%s', owner, repo, branch)

    @property
    def tree(self):
        return self.tree_object.tree

    @property
    def metadata(self):
        return { 
            'commit_history': [
                list(x) for x in 
                zip(
                    self.metadata_object.root_metadata['commit_name'], 
                    self.metadata_object.root_metadata['commit_date']
                    )
            ],
            'owner': self.metadata_object.owner_metadata,
            'organization': self.metadata_object.organization_metadata,
            'members': self.metadata_object.member_metadata,
            'metadata': {key: value for key, value in self.metadata_object.root_metadata.items() if key != 'commit_name' or key != 'commit_date'}
        }
        
    def __str__(self): 
        return str(self.tree_object)

    def save(self, path): 
        sub_repo_path = os.path.join(path, self.owner+'_'+self.repo)
        os.makedirs(sub_repo_path, exist_ok=True)

        self.logger.info('Saving tree...')
        with open(os.path.join(sub_repo_path, 'tree.json'), 'w') as file:
            json.dump(self.tree, file)
        self.logger.info('Tree saved.')

        self.logger.info('Saving metadata...')
        with open(os.path.join(sub_repo_path, 'metadata.json'), 'w') as file:
            json.dump(self.metadata['metadata'], file)
        self.logger.info('Metadata saved.')

        self.logger.info('Saving commit history...')
        with open(os.path.join(sub_repo_path, 'commit_history.json'), 'w') as file:
            json.dump(self.metadata['commit_history'], file)
        self.logger.info('Commit history saved.')

        self.logger.info('Saving tree (formatted)...')
        with open(os.path.join(sub_repo_path, 'tree_formatted.txt'), 'w') as file:
            file.write(str(self.tree_object))
        self.logger.info('Tree (formatted) saved.')

        for key in ['owner', 'organization']:
            os.makedirs(os.path.join(path, key), exist_ok=True)
            if self.metadata[key]: 
                self.logger.info(f'Saving {key}...')
                with open(os.path.join(path, key, f'{self.metadata[key]["name"]}.json'), 'w') as file:
                    json.dump(self.metadata[key], file)
                self.logger.info(f'{key.capitalize()} saved.')

        key = 'members'
        os.makedirs(os.path.join(path, key), exist_ok=True)
        self.logger.info(f'Saving {key}...')
        for member in self.metadata['members']: 
            with open(os.path.join(path, key, f'{member}.json'), 'w') as file:
                json.dump(self.metadata[key][member], file)
            self.logger.info(f'{member} saved.')
        self.logger.info(f'Saved {key}...')

        return { 
            'repo': self.repo,
            'branch': self.branch,
            'tree': os.path.join(sub_repo_path, 'tree.json'),
            'repo_metadata': os.path.join(sub_repo_path, 'metadata.json'),
            'commit_history': os.path.join(sub_repo_path, 'commit_history.json'),
            'tree_formatted': os.path.join(sub_repo_path, 'tree_formatted.txt'),
            'owner': os.path.join(path, 'owner', f'{self.metadata["owner"]["name"]}.json'),
            'organization': os.path.join(path, 'organization', f'{self.metadata["organization"]["name"]}.json') if self.metadata['organization'] else None,
            'members': [os.path.join(path, 'members', f'{member}.json') for member in self.metadata['members']]
        }
            

    def get_tree(self, file_path=None):
        self.tree_object = Tree(owner=self.owner, repo=self.repo, branch=self.branch, file_path=file_path)

    def get_meta(self):
        for _, _ in self.aget_meta():
            pass 

    def aget_meta(self): 
        self.metadata_object = Metadata(owner=self.owner, repo=self.repo)
        return self.metadata_object.agenerate()

    def find_md_files(self):
        pattern = re.compile(r'^.*\.md$', re.MULTILINE)
        return pattern.findall(self.tree_object.tree_string)

    def check_keyword(self, keyword):
        pattern = re.compile(r'^.*' + keyword + '.*$', re.MULTILINE)
        return pattern.findall(self.tree_object.tree_string)

    def extract_markdown_headers(self, path):
        content = self.get_file(path)  
        headers = re.findall(r'^#+\s*(.*)', content, re.MULTILINE)
        return headers

    def get_file(self, path): 
        url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  
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
        # check if enrched is an attribute of tree_object
        if not hasattr(self.tree_object, 'enriched'):
            self.logger.error('Tree has not been fetched yet.')
            exit() 
        self.tree_object.enriched = True
        return self.enrich_tree_attributes(self.tree_object.tree)

    def enrich_tree_attributes(self, node):
        # Initialize counts and sets for the current node
        num_subfolders, num_subfiles = 0, 0
        num_files_direct, num_folders_direct = 0, 0
        file_types = set()

        # Check if the current node has 'children' attribute
        if 'children' in node:
            for child in node['children']:
                if child.get('type') == 'file':
                    # Update direct file count and types for the current level
                    num_files_direct += 1
                    file_extension = child['path'].split('.')[-1]
                    file_types.add(file_extension)
                elif child.get('type') == 'folder':
                    # Recursively enrich child folder and update counts and types
                    child_subfolders, child_subfiles, child_files_direct, child_folders_direct, child_file_types = self.enrich_tree_attributes(child)
                    
                    # Update direct folder count for the current level
                    num_folders_direct += 1
                    
                    # Update cumulative counts with child's counts
                    num_subfolders += child_subfolders + 1  # Include the child folder itself
                    num_subfiles += child_subfiles
                    file_types = file_types.union(child_file_types)

            # Set attributes for the current node
            node['number_of_subfolders'] = num_subfolders
            node['number_of_subfiles'] = num_subfiles
            node['number_of_files'] = num_files_direct
            node['number_of_folders'] = num_folders_direct
            node['file_types'] = list(file_types)  # Convert set to list for easier handling

        # Base case for leaf nodes (files)
        else:
            # Files don't contribute to folder counts but need to be counted in their parent's file types
            file_extension = node['path'].split('.')[-1]
            file_types.add(file_extension)
        
        # Return counts and types for parent nodes to aggregate
        return num_subfolders, num_subfiles, num_files_direct, num_folders_direct, file_types
