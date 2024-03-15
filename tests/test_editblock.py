# flake8: noqa: E501

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aider import models
from aider.coders import Coder
from aider.coders import editblock_coder as eb
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.mock_check = MagicMock()
        self.mock_check.return_value = True

    def tearDown(self):
        pass

    def test_replace_most_similar_chunk(self):
        whole = "This is a sample text.\nAnother line of text.\nYet another line.\n"
        part = "This is a sample text"
        replace = "This is a replaced text."
        expected_output = "This is a replaced text..\nAnother line of text.\nYet another line.\n"

        result = eb.replace_most_similar_chunk(whole, part, replace)
        self.assertEqual(result, expected_output)

    # ... (other test methods remain unchanged)

    def test_full_edit_dry_run(self):
        # Create a few temporary files
        _, file1 = tempfile.mkstemp()

        orig_content = "one\ntwo\nthree\n"

        with open(file1, "w", encoding="utf-8") as f:
            f.write(orig_content)

        files = [file1]

        # Initialize the Coder object with the mocked IO and mocked repo
        coder = Coder.create(
            models.GPT4,
            "diff",
            io=InputOutput(dry_run=True),
            fnames=files,
            dry_run=True,
        )

        def mock_send(*args, **kwargs):
            coder.partial_response_content = f"""
Do this:

{Path(file1).name}
<<<<<<< ORIGINAL
two
=======
new
>>>>>>> UPDATED

"""
            coder.partial_response_function_call = dict()

        coder.send = MagicMock(side_effect=mock_send)

        # Call the run method with a message
        coder.run(with_message="hi")

        content = Path(file1).read_text(encoding="utf-8")
        self.assertEqual(content, orig_content)


if __name__ == "__main__":
    unittest.main()
