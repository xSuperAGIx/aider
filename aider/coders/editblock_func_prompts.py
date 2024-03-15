# flake8: noqa: E501

from typing import List

class CoderPrompts:
    pass

class EditBlockFunctionPrompts(CoderPrompts):
    def __init__(self):
        self.main_system = """\
Act as an expert software developer.
Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.

Once you understand the request you MUST use the `replace_lines` function to edit the files to make the needed changes.
"""
        self.system_reminder = """\
ONLY return code using the `replace_lines` function.
NEVER return code outside the `replace_lines` function.
"""
        self.files_content_prefix = "Here is the current content of the files:\n"
        self.files_no_full_files = "I am not sharing any files yet."
        self.redacted_edit_message = "No changes are needed."
        self.repo_content_prefix = (
            "Below here are summaries of other files! Do not propose changes to these "
            "read-only files without asking me first.\n"
        )

    def replace_lines(self, files_content: List[str], changes: List[str]) -> List[str]:
        """
        Edit the files in place using the provided changes.

        Parameters
        ----------
        files_content : List[str]
            The current content of the files to be edited.
        changes : List[str]
            The changes to be made to the files.

        Returns
        -------
        List[str]
            The edited files content.
        """
        for i, change in enumerate(changes):
            files_content[i] = change
        return files_content
