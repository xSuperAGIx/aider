import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aider import models
from aider.coders import Coder
from aider.coders.wholefile_coder import WholeFileCoder
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput


class TestWholeFileCoder(unittest.TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()
        os.chdir(self.tempdir)

        self.patcher = patch("aider.coders.base_coder.check_model_availability")
        self.mock_check = self.patcher.start()
        self.mock_check.return_value = True

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tempdir, ignore_errors=True)

        self.patcher.stop()

    def test_no_files(self):
        io = InputOutput(yes=True)
        coder = WholeFileCoder(main_model=models.GPT35, io=io, fnames=[])
        coder.partial_response_content = (
            'To print "Hello, World!" in most programming languages, you can use the following'
            ' code:\n\n```python\nprint("Hello, World!")\n```\n\nThis code will output "Hello,'
            ' World!" to the console.'
        )

        with self.assertRaises(ValueError):
            coder.render_incremental_response(True)

    def test_no_files_new_file_should_ask(self):
        io = InputOutput(yes=False)
        coder = WholeFileCoder(main_model=models.GPT35, io=io, fnames=[])
        coder.partial_response_content = (
            'To print "Hello, World!" in most programming languages, you can use the following'
            ' code:\n\nfoo.js\n```python\nprint("Hello, World!")\n```\n\nThis code will output'
            ' "Hello, World!" to the console.'
        )
        coder.update_files()
        self.assertFalse(Path("foo.js").exists())

    def test_update_files(self):
        sample_file = "sample.txt"
        with open(sample_file, "w") as f:
            f.write("Original content\n")

        io = InputOutput(yes=True)
        coder = WholeFileCoder(main_model=models.GPT35, io=io, fnames=[sample_file])

        coder.partial_response_content = f"{sample_file}\n```\nUpdated content\n```"

        edited_files = coder.update_files()

        self.assertIn("sample.txt", edited_files)

        with open(sample_file, "r") as f:
            updated_content = f.read()
        self.assertEqual(updated_content, "Updated content\n")

    def test_update_files_live_diff(self):
        sample_file = "sample.txt"
        with open(sample_file, "w") as f:
            f.write("\n".join(map(str, range(0, 100))))

        io = InputOutput(yes=True)
        coder = WholeFileCoder(main_model=models.GPT35, io=io, fnames=[sample_file])

        coder.partial_response_content = f"{sample_file}\n```\n0\n\1\n2\n"

        lines = coder.update_files(mode="diff").splitlines()

        self.assertLess(len(lines), 20)

    def test_update_files_with_existing_fence(self):
        sample_file = "sample.txt"
        original_content = """
Here is some quoted text:


"""
        with open(sample_file, "w") as f:
            f.write(original_content)

        io = InputOutput(yes=True)
        coder = WholeFileCoder(main_model=models.GPT35, io=io, fnames=[sample_file])

        coder.choose_fence()

        self.assertNotEqual(coder.fence[0], "```")

        coder.partial_response_content = (
            f"{sample_file}\n{coder.fence[0]}\nUpdated content\n{coder.fence[1]}"
        )

        edited_files = coder.update_files()

        self.assertIn("sample.txt", edited_files)

        with open(sample_file, "r") as f:
            updated_content = f.read()
        self.assertEqual(updated_content, "Updated content\n")

    def test_update_files_bogus_path_prefix(self):
        sample_file = "sample.txt"
        with open(sample_file, "w") as f:
            f.write("Original content\n")

        io = InputOutput(yes=True)
        coder = WholeFileCoder(main_model=models.GPT35, io=io, fnames=[sample_file])

        coder.partial_response_content = f"path/to/{sample_file}\n```\nUpdated content\n```"

        edited_files = coder.update_files()

        self.assertIn("sample.txt", edited_files)

        with open(sample_file, "r") as f:
            updated_content = f.read()
        self.assertEqual(updated_content, "Updated content\n")

    def test_update_files_not_in_chat(self):

