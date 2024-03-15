import os
import unittest
from unittest.mock import patch

from aider.io import InputOutput
from aider.repomap import RepoMap

from tests.utils import IgnorantTemporaryDirectory


class TestRepoMap(unittest.TestCase):
    def setUp(self):
        self.io = InputOutput()
        self.temp_dir = IgnorantTemporaryDirectory()

    def tearDown(self):
        del self.repo_map
        self.temp_dir.cleanup()

    def test_get_repo_map(self):
        test_files = [
            "test_file1.py",
            "test_file2.py",
            "test_file3.md",
            "test_file4.json",
        ]

        for file in test_files:
            with open(os.path.join(self.temp_dir.path, file), "w") as f:
                f.write("")

        self.repo_map = RepoMap(root=self.temp_dir.path, io=self.io)
        other_files = [os.path.join(self.temp_dir.path, file) for file in test_files]
        result = self.repo_map.get_repo_map([], other_files)

        for file in test_files:
            self.assertIn(file, result)

    def test_get_repo_map_with_identifiers(self):
        test_file1 = "test_file_with_identifiers.py"
        file_content1 = """\
class MyClass:
    def my_method(self, arg1, arg2):
        return arg1 + arg2

def my_function(arg1, arg2):
    return arg1 * arg2
"""

        test_file2 = "test_file_import.py"
        file_content2 = """\
from test_file_with_identifiers import MyClass

obj = MyClass()
print(obj.my_method(1, 2))
print(my_function(3, 4))
"""

        test_file3 = "test_file_pass.py"
        file_content3 = "pass"

        for file, content in [(test_file1, file_content1), (test_file2, file_content2), (test_file3, file_content3)]:
            with open(os.path.join(self.temp_dir.path, file), "w") as f:
                f.write(content)

        self.repo_map = RepoMap(root=self.temp_dir.path, io=self.io)
        other_files = [os.path.join(self.temp_dir.path, file) for file in (test_file1, test_file2, test_file3)]
        result = self.repo_map.get_repo_map([], other_files)

        self.assertIn(test_file1, result)
        self.assertIn("MyClass", result)
        self.assertIn("my_method", result)
        self.assertIn("my_function", result)
        self.assertIn(test_file3, result)

    def test_check_for_ctags_failure(self):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("ctags not found")
            repo_map = RepoMap(io=self.io)
            self.assertFalse(repo_map.has_ctags)

    def test_check_for_ctags_success(self):
        with patch("subprocess.check_output") as mock_run:
            mock_run.side_effect = [
                (
                    b"Universal Ctags 0.0.0(f25b4bb7)\n  Optional compiled features: +wildcards,"
                    b" +regex, +gnulib_fnmatch, +gnulib_regex, +iconv, +option-directory, +xpath,"
                    b" +json, +interactive, +yaml, +case-insensitive-filenames, +packcc,"
                    b" +optscript, +pcre2"
                ),
                (
                    b'{"_type": "tag", "name": "status", "path": "aider/main.py", "pattern": "/^   '
                    b' status = main()$/", "kind": "variable"}'
                ),
            ]
            repo_map = RepoMap(io=self.io)
            self.assertTrue(repo_map.has_ctags)

    def test_get_repo_map_without_ctags(self):
        test_files = [
            "test_file_without_ctags.py",
            "test_file1.txt",
            "test_file2.md",
            "test_file3.json",
            "test_file4.html",
            "test_file5.css",
            "test_file6.js",
        ]

        for file in test_files:
            with open(os.path.join(self.temp_dir.path, file), "w") as f:
                f.write("")

        self.repo_map = RepoMap(root=self.temp_dir.path, io=self.io)
        self.repo_map.has_ctags = False

        other_files = [os.path.join(self.temp_dir.path, file) for file in test_files]
        result = self.repo_map.get_repo_map([], other_files)

        for file in test_files:
            self.assertIn(file, result)


if __name__ == "__main__":
    unittest.main()
