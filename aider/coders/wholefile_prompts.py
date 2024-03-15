# flake8: noqa: E501

from typing import Any, Dict, List, Tuple

from .base_prompts import CoderPrompts

class WholeFilePrompts(CoderPrompts):
    main_system = """Act as an expert software developer.
Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.

Once you understand the request, you should:
1. Determine if any code changes are needed.
2. Explain any needed changes.
3. If changes are needed, return a dictionary with the filenames as keys and the updated file contents as values.
"""

    system_reminder = """To suggest changes to a file, you should return a dictionary with the filenames as keys and the updated file contents as values.
The dictionary should use the following format:

{
    'path/to/filename.js': '// entire file content ...',
    ...
}

Every filename in the dictionary should include any originally provided path.

To suggest changes to a file, you should return a dictionary with the entire content of the updated file.
Create a new file, you should return a dictionary with an appropriate filename, including any appropriate path.
"""

    files_content_prefix = "Here is the current content of the files:\n"
    files_no_full_files = "I am not sharing any files yet."

    redacted_edit_message = "No changes are needed."

    # this coder is not able to handle repo content
    repo_content_prefix = None

    def suggest_changes(self, requests: List[str]) -> Dict[str, str]:
        # your code here to suggest changes based on the requests
        # and return a dictionary with the filenames as keys and the updated file contents as values
        pass
