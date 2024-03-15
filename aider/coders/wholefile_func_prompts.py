# flake8: noqa: E501

from typing import Dict

class BasePrompts:
    def __init__(self):
        self.main_system = """Act as an expert software developer.
Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.

Once you understand the request you MUST use the `write_file` function to edit the files to make the needed changes."""

        self.system_reminder = """
ONLY return code using the `write_file` function.
NEVER return code outside the `write_file` function."""

        self.files_content_prefix = "Here is the current content of the files:\n"
        self.files_no_full_files = "I am not sharing any files yet."

        self.redacted_edit_message = "No changes are needed."

class WholeFileFunctionPrompts(BasePrompts):
    def __init__(self):
        super().__init__()
        self.repo_content_prefix = None
        self.chat_history = []

    def write_file(self, file_path: str, content: str, **kwargs) -> str:
        """Write the given content to the file at the given path.

        Returns:
            The content that was written to the file.
        """
        # Implement the write_file function here.
        pass

    def get_files_content(self, file_paths: Dict[str, str]) -> str:
        """Get the content of the given files.

        Args:
            file_paths: A dictionary mapping file paths to their content.

        Returns:
            A string containing the content of the given files.
        """
        files_content = ""
        for file_path, content in file_paths.items():
            files_content += f"File: {file_path}\nContent:\n{content}\n---\n"
        return files_content

