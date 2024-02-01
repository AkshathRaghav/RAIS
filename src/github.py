import json 
import os 
import requests

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

def build_tree(json_data):
    root = Node(path="", node_type="folder")

    for item in json_data["tree"]:
        path_parts = item["path"].split('/')
        if len(path_parts) > 1:  
            parent = root.find_or_create_path(path_parts[:-1])
            parent.add_child(Node(path_parts[-1], "file"))
        else:  
            root.add_child(Node(item["path"], "file" if item["type"] == "blob" else "folder"))

    return root

def serialize_tree_to_file(root, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(root.to_dict(), file, ensure_ascii=False, indent=4)

def get_tree(url): 
  headers = {
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}",
  }

  response = requests.get(url, headers=headers)

  if response.ok:
      return response.json() 
  else: 
      return {}

def make_tree(repo, branch, file_path=None):
  root_node = build_tree(get_tree(f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=0")) 

  if not file_path:
    return root_node.to_dict()
  else: 
    serialize_tree_to_file(root_node, file_path)

# make_tree('thuml/LogME', 'main')