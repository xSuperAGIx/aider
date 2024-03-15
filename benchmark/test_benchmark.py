# flake8: noqa: E501

import unittest

from benchmark import cleanup_test_output


class TestCleanupTestOutput(unittest.TestCase):
    """Test the `cleanup_test_output` function."""

    def test_cleanup_test_output_ok(self, output: str, expected: str) -> None:
        """Test cleaning up test output with OK status."""
        self.assertEqual(cleanup_test_output(output), expected)

    def test_cleanup_test_output_timing(self, output: str, expected: str) -> None:
        """Test cleaning up test output with timing info."""
        self.assertEqual(cleanup_test_output(output), expected)

    def test_cleanup_test_output_error(self, output: str, expected: str) -> None:
        """Test cleaning up test output with error message."""
        self.assertEqual(cleanup_test_output(output), expected)

    def test_cleanup_test_output_ok(self) -> None:
        output = "Ran 5 tests in 0.003s\nOK"
        expected = "\nOK"
        self.test_cleanup_test_output_ok(output, expected)

    def test_cleanup_test_output_timing(self) -> None:
        output = """\
F
======================================================================
FAIL: test_cleanup_test_output (test_benchmark.TestCleanupTestOutput.test_cleanup_test_output)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/gauthier/Projects/aider/benchmark/test_benchmark.py", line 14, in test_cleanup_test_output
    self.assertEqual(cleanup_test_output(output), expected)
AssertionError: 'OK' != 'OKx'
- OK
+ OKx
?   +
"""
        expected = """\
F
====
FAIL: test_cleanup_test_output (test_benchmark.TestCleanupTestOutput.test_cleanup_test_output)
----

