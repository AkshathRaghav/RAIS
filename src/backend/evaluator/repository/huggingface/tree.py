import json

from huggingface_hub import HfApi


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
        new_child = Node(next_part, "folder" if path_parts else "file")
        return self.add_child(new_child).find_or_create_path(path_parts)

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

    def build_tree_from_paths(self, paths):
        root = Node(path="", node_type="folder")

        for path in paths:
            path_parts = path.split("/")
            root.find_or_create_path(path_parts)

        return root

    def serialize_tree_to_file(self, root, file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(root.to_dict(), file, ensure_ascii=False, indent=4)

    def get_tree(self, repo_name):
        api = HfApi()
        return api.list_repo_files(repo_name)

    def make_tree(self, repo, file_path=None):
        root_node = build_tree_from_paths(get_tree(repo))

        if not file_path:
            return root_node.to_dict()
        else:
            serialize_tree_to_file(root_node, file_path)
