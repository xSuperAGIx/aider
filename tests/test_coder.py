import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock, sentinel

import git
import openai

from aider import models
from aider.coders import Coder
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput
from tests.utils import GitTemporaryDirectory


class TestCoder(unittest.TestCase):
    patch_methods = [
        "aider.coders.base_coder.check_model_availability",
        "aider.coders.base_coder.openai.ChatCompletion.create",
        "builtins.print",
    ]

    def setUp(self):
        self.mock_check = MagicMock()
        self.mock_check.return_value = True

        patcher = patch.multiple(
            "aider.coders.base_coder",
            check_model_availability=self.mock_check,
            openai=PropertyMock(),
        )
        self.mock_openai = patcher.start()
        self.mock_chat_completion_create = self.mock_openai.ChatCompletion.create

        self.mock_print = MagicMock()
        patcher = patch("builtins.print", self.mock_print)
        self.mock_print = patcher.start()

        self.mock_io = MagicMock()

        self.coder = Coder.create(models.GPT4, None, self.mock_io)

    def tearDown(self):
        patch.stopall()

    def test_should_dirty_commit(self):
        fname = Path("new.txt")
        fname.touch()
        repo = git.Repo(Path.cwd())
        repo.git.add(str(fname))
        repo.git.commit("-m", "new")

        coder = Coder.create(models.GPT4, None, self.mock_io)

        fname.write_text("hi")
        self.assertTrue(coder.should_dirty_commit("hi"))

        self.assertFalse(coder.should_dirty_commit("/exit"))
        self.assertFalse(coder.should_dirty_commit("/help"))

    def test_check_for_file_mentions(self):
        mock = MagicMock()
        mock.return_value = {sentinel.file1, sentinel.file2}
        self.coder.get_tracked_files = mock

        coder = Coder.create(models.GPT4, None, self.mock_io)

        coder.check_for_file_mentions("Please check file1 and file2")

        expected_files = {Path(coder.root) / sentinel.file1, Path(coder.root) / sentinel.file2}
        self.assertCountEqual(coder.abs_fnames, expected_files)

    def test_get_files_content(self):
        tempdir = Path(tempfile.mkdtemp())

        file1 = tempdir / "file1.txt"
        file2 = tempdir / "file2.txt"

        file1.touch()
        file2.touch()

        files = [file1, file2]

        coder = Coder.create(models.GPT4, None, self.mock_io, fnames=files)

        content = coder.get_files_content().splitlines()
        self.assertIn(str(file1), content)
        self.assertIn(str(file2), content)

    def test_check_for_ambiguous_filename_mentions(self):
        with GitTemporaryDirectory():
            io = InputOutput(pretty=False, yes=True)
            coder = Coder.create(models.GPT4, None, io)

            fname = Path("file1.txt")
            fname.touch()

            other_fname = Path("other") / "file1.txt"
            other_fname.parent.mkdir(parents=True, exist_ok=True)
            other_fname.touch()

            mock = MagicMock()
            mock.return_value = {str(fname), str(other_fname)}
            coder.get_tracked_files = mock

            coder.check_for_file_mentions(f"Please check {fname}!")

            self
