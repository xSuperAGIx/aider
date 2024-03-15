INSTRUCTIONS_ADDENDUM_TEMPLATE = """
####

Use the above instructions to modify the supplied files: {file_list}

Keep and implement the existing function or class stubs, they will be called from unit tests.

Only use standard Python libraries, do not suggest installing any packages.
"""

TEST_FAILURES_TEMPLATE = """
####

See the testing errors above.

The tests are correct. Fix the code in {file_list} to resolve the errors.
"""

def generate_instructions_addendum(file_list):
    """Generates the instructions addendum message with the given file list."""
    return INSTRUCTIONS_ADDENDUM_TEMPLATE.format(file_list=file_list)

def generate_test_failures(file_list):
    """Generates the test failures message with the given file list."""
    return TEST_FAILURES_TEMPLATE.format(file_list=file_list)
