import json 
import os 
import requests
import re 
import streamlit as st
 
class Node:
    def __init__(self, path, node_type):
        self.path = path
        self.type = node_type  
        self.children = []  

    def add_child(self, child):
        for existing_child in self.children:
            if existing_child.path == child.path:
                return existing_child
        self.children.append(child)
        return child

    def find_or_create_path(self, path_parts):
        if not path_parts:
            return self
        next_part = path_parts.pop(0)
        for child in self.children:
            if child.path == next_part and child.type == "folder":
                return child.find_or_create_path(path_parts)
        new_child = self.add_child(Node(next_part, "folder"))
        return new_child.find_or_create_path(path_parts)

    def to_dict(self):
        obj = {"path": self.path, "type": self.type}
        if self.children: 
            obj["children"] = [child.to_dict() for child in self.children]
        return obj

    def __del__(self):
        for child in self.children:
            del child

class Tree: 
    def __init__(self, **repo_data):
        self.tree = self.make_tree(**repo_data)  
        self.tree_string = ""  
        self.enriched = False  

    def build_tree(self, json_data):
        if not json_data:
            return None
        root = Node(path="", node_type="folder")

        for item in json_data["tree"]:
            path_parts = item["path"].split('/')
            if len(path_parts) > 1:  
                parent = root.find_or_create_path(path_parts[:-1])
                parent.add_child(Node(path_parts[-1], "file"))
            else:  
                root.add_child(Node(item["path"], "file" if item["type"] == "blob" else "folder"))

        return root

    def serialize_tree_to_file(self, root, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(root.to_dict(), file, ensure_ascii=False, indent=4)
        return 1

    def get_tree(self, url): 
        try: 
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer { st.session_state['GITHUB_AUTH_TOKEN']}",
            }
        except: 
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {os.environ.get('GITHUB_AUTH_TOKEN')}",
            }

        response = requests.get(url, headers=headers)
        print(response)
        return response.json() 

    def make_tree(self, owner, repo, branch, file_path=None):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=0"
        root_node = self.build_tree(self.get_tree(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=0")) 

        if not root_node:
            return None
            
        final = root_node.to_dict()
        if file_path: 
            self.serialize_tree_to_file(root_node, file_path)
        del root_node
        return final

    def file_tree_to_string(self, tree, parent_path=''):
        result = ""
        if 'children' in tree: 
            current_path = f"{parent_path}{tree['path']}/" if tree['path'] else parent_path
            for child in tree['children']:
                result += self.file_tree_to_string(child, current_path)
        else:
            current_path = f"{parent_path}{tree['path']}\n"
            result += current_path
        print(result)
        return result

    def file_tree_to_string2(self, tree, indent='', depth=0):
        lines = []

        # Add the current node to the lines
        lines.append(f"{indent}{tree['path'].split('/')[-1]}: ")

        # If this is a folder, recursively add its children
        if tree['type'] == 'folder' and depth < 2:
            for child in tree['children']:
                lines.append(self.file_tree_to_string2(child, indent + '  ', depth + 1))

        # Add the keywords to the lines
        if 'keywords' in tree:
            for file_path, keywords in tree['keywords'].items():
                if not keywords:
                    continue
                file_name = file_path.split('/')[-1]
                keywords = [x for y in keywords.values() for x in y][:10]
                lines.append(f"{indent}  {file_name}: {', '.join(keywords)}")

        return '\n'.join(lines)
        
    def __str__(self):
        if self.enriched:
            self.tree_string = self.file_tree_to_string2(self.tree)

        else: 
            self.tree_string = self.file_tree_to_string(self.tree)
        return self.tree_string