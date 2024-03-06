from pydantic import BaseModel, PrivateAttr, Field
from typing import List, ForwardRef, Dict, Optional
from enum import Enum
import os

NodeRef = ForwardRef("NodeRef")

"""
Enum class for file type
"""


class NodeTypeEnum(str, Enum):
    file = "file"
    directory = "directory"


"""
Node class for Tree
"""


class Node(BaseModel):
    path: str  # unique identifier for the folder / file that this node represents
    type: NodeTypeEnum = Field  #
    parent: Optional['None'] = None  # if parent is None: at the root.
    children: Dict[str, 'Node'] = {}  # if len(children) is 0, node is a leaf.

    def add_child(self, path: str, child: 'Node') -> 'Node':
        if path:
            child: Node
            # does the next child node already exist
            if path in self.children:
                child = self.children[path]
            else:
                # check for path type

                full_path: str = "/".join([self.path, path])
                child_type: str = NodeTypeEnum.file if os.path.isfile(full_path) else NodeTypeEnum.directory
                child = Node(path="/".join([self.path, path]), type=child_type, parent=self)
                self.children[path] = child
            return child
        else:
            # Raise error
            raise Exception(f"No path provided for Node {child.dict()}")

    def to_dict(self):
        obj = {"path": self.path}
        if self.children:
            obj["children"] = [child.to_dict() for child in self.children]
            obj["type"] = "folder"
        else:
            obj["type"] = "file"
        return obj
if __name__ == "__main__":
    root = Node("/Users/ronnatarajan/PycharmProjects/RAIS/venv/bin/python",
        type = NodeTypeEnum.directory
    )

"""
# get parts of path
            remaining_path_parts = path.split("/")
            child_node_path: str = remaining_path_parts.pop(0)
            self.children.__setitem__(path, child)
            child.add_child("/".join(remaining_path_parts), child=)
"""

Node.update_forward_refs()

a = Node(path="a", type="github")

"""
Github tree:

import json
import os
import re

import requests
import streamlit as st

from src.backend.tools.logger import LoggerSetup


@st.cache_data(ttl=1800, max_entries=1000)
def get_tree(url):
    try:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {st.session_state['GITHUB_AUTH_TOKEN']}",
        }
    except:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GITHUB_AUTH_TOKEN')}",
        }

    response = requests.get(url, headers=headers)
    return response.json()


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
        obj = {"path": self.path}
        if self.children:
            obj["children"] = [child.to_dict() for child in self.children]
            obj["type"] = "folder"
        else:
            obj["type"] = "file"
        return obj

    def __del__(self):
        for child in self.children:
            del child


class Tree:
    def __init__(self, **repo_data):
        logging_setup = LoggerSetup("Tree")
        self.logger = logging_setup.get_logger()

        self.logger.info("Initializing Tree object...")

        self.tree = self.make_tree(**repo_data)
        self.enriched = False

        self.logger.info("Tree object initialized.")

    def build_tree(self, json_data):
        if not json_data:
            return None
        root = Node(path="", node_type="folder")

        for item in json_data["tree"]:
            path_parts = item["path"].split("/")
            if len(path_parts) > 1:
                parent = root.find_or_create_path(path_parts[:-1])
                parent.add_child(Node(path_parts[-1], "file"))
                # This is wrong lmao, identifying a folder/file is tough because it splits the path by '/'
                # Just print(path_parts) to see what I mean, you can't identify a file cuz of the different kinds of files
                # Ditch this for now, I'm doing some post processing later on in Node.to_dict()
            else:
                root.add_child(Node(item["path"], "file" if item["type"] == "blob" else "folder"))

        return root

    def serialize_tree_to_file(self, root, file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(root.to_dict(), file, ensure_ascii=False, indent=4)
        return 1

    def make_tree(self, owner, repo, branch, file_path=None):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=0"
        self.logger.info("Starting to make tree with provided repo data... %s", url)
        root_node = self.build_tree(get_tree(url))

        if not root_node:
            return None

        final = root_node.to_dict()
        if file_path:
            self.serialize_tree_to_file(root_node, file_path)
        del root_node

        self.logger.info("Tree successfully created.")
        return final

    def file_tree_to_string(self, tree, parent_path="", indent_level=0):
        result = ""
        indent_str = "---" * indent_level + "| "
        if "children" in tree:
            current_path = f"{parent_path}{tree['path']}/" if tree["path"] else parent_path
            if indent_level > 0:
                result += f"{indent_str}{current_path}\n"
            for child in tree["children"]:
                result += self.file_tree_to_string(child, current_path, indent_level + 1)
        else:
            current_path = f"{parent_path}{tree['path']}"
            result += f"{indent_str}{current_path}\n"
        return result

    def file_tree_to_string2(self, tree, indent="", depth=0):
        lines = []

        lines.append(f"{indent}{tree['path'].split('/')[-1]}: ")

        if tree["type"] == "folder" and depth < 2:
            for child in tree["children"]:
                lines.append(self.file_tree_to_string2(child, indent + "  ", depth + 1))

        if "keywords" in tree:
            for file_path, keywords in tree["keywords"].items():
                if not keywords:
                    continue
                file_name = file_path.split("/")[-1]
                keywords = [x for y in keywords.values() for x in y][:10]
                lines.append(f"{indent}  {file_name}: {', '.join(keywords)}")

        return "\n".join(lines)

    def __str__(self):
        if self.enriched:
            return self.file_tree_to_string2(self.tree)

        else:
            return self.file_tree_to_string(self.tree)

"""
