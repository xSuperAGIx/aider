import codecs
import os
import shutil
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest import TestCase

from aider import models
from aider.coders import Coder
from aider.commands import Commands
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput


class TestCommands(TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.tempdir = tempfile.TemporaryDirectory()
        os.chdir(self.tempdir.name)

    def tearDown(self):
        os.chdir(self.original_cwd)
        self.tempdir.cleanup()

    def test_cmd_add(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(models.GPT35, None, io)
        commands = Commands(io, coder)

        # Call the cmd_add method with 'foo.txt' and 'bar.txt' as a single string
        commands.cmd_add("foo.txt bar.txt")

        # Check if both files have been created in the temporary directory
        self.assertTrue(os.path.exists("foo.txt"))
        self.assertTrue(os.path.exists("bar.txt"))

    def test_cmd_add_with_glob_patterns(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(models.GPT35, None, io)
        commands = Commands(io, coder)

        # Create some test files
        (Path("test1.py")).touch()
        (Path("test2.py")).touch()
        (Path("test.txt")).touch()

        # Call the cmd_add method with a glob pattern
        commands.cmd_add("*.py")

        # Check if the Python files have been added to the chat session
        self.assertIn(str(Path("test1.py")), coder.abs_fnames)
        self.assertIn(str(Path("test2.py")), coder.abs_fnames)

        # Check if the text file has not been added to the chat session
        self.assertNotIn(str(Path("test.txt")), coder.abs_fnames)

    def test_cmd_add_no_match(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(models.GPT35, None, io)
        commands = Commands(io, coder)

        # Call the cmd_add method with a non-existent file pattern
        commands.cmd_add("*.nonexistent")

        # Check if no files have been added to the chat session
        self.assertEqual(len(coder.abs_fnames), 0)

    def test_cmd_add_drop_directory(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(models.GPT35, None, io)
        commands = Commands(io, coder)

        os.mkdir("test_dir")
        os.mkdir("test_dir/another_dir")
        (Path("test_dir/test_file1.txt")).touch()
        (Path("test_dir/test_file2.txt")).touch()
        (Path("test_dir/another_dir/test_file.txt")).touch()

        # Call the cmd_add method with a directory
        commands.cmd_add("test_dir test_dir/test_file2.txt")

        # Check if the files have been added to the chat session
        self.assertIn(str(Path("test_dir/test_file1.txt")), coder.abs_fnames)
        self.assertIn(str(Path("test_dir/test_file2.txt")), coder.abs_fnames)
        self.assertIn(str(Path("test_dir/another_dir/test_file.txt")), coder.abs_fnames)

        commands.cmd_drop("test_dir/another_dir")
        self.assertIn(str(Path("test_dir/test_file1.txt")), coder.abs_fnames)
        self.assertIn(str(Path("test_dir/test_file2.txt")), coder.abs_fnames)
        self.assertNotIn(
            str(Path("test_dir/another_dir/test_file.txt")), coder.abs_fnames
        )

    def test_cmd_drop_with_glob_patterns(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(models.GPT35, None, io)
        commands = Commands(io, coder)

        subdir = Path("subdir")
        subdir.mkdir()
        (subdir / "subtest1.py").touch()
        (subdir / "subtest2.py").touch()

        Path("test1.py").touch()
        Path("test2.py").touch()

        # Add some files to the chat session
        commands.cmd_add("*.py")

        self.assertEqual(len(coder.abs_fnames), 2)

        # Call the cmd_drop method with a glob pattern
        commands.cmd_drop("*2.py")

        self.assertIn(str(Path("test1.py")), coder.abs_fnames)
        self.assertNotIn(str(Path("test2.py")), coder.abs_fnames)

    def test_cmd_add_bad_encoding(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=
