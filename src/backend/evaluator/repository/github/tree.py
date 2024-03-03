import json
import os
import re

import requests
import streamlit as st

from backend.tools.logger import LoggerSetup

headers = {
    "Accept": "application/vnd.github.star+json",
    "Authorization": f"Bearer {os.environ.get('GITHUB_AUTH_TOKEN')}",
}


@st.cache_data(ttl=1800, max_entries=1000)
def get_tree(url):
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

        self.tree = None
        self.enriched = False
        self._repo_data = repo_data

        self.logger.info("Tree object initialized.")

    def __call__(self):
        self.tree = self.make_tree(**self._repo_data)
        del self._repo_data

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

    def __str__(self):
        return self.file_tree_to_string(self.tree)
