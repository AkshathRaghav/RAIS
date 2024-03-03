from tree import Tree


class HuggingFace:
    def __init__(self, url):
        self.url = url
        self.tree = None

    def __call__(self, file_path=None):
        self.tree = Tree(repo=self.url, file_path=file_path)
