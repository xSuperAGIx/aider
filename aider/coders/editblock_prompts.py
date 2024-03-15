# flake8: noqa: E501

from typing import List, Tuple

class Fence:
    OPEN = "{fence[0]}"
    CLOSE = "{fence[1]}"

class FileChange:
    def __init__(self, file_path: str, changes: List[str]):
        self.file_path = file_path
        self.changes = changes

