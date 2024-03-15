import os
import pathlib
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import dataclasses
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aider import diffs

from ..dump import dump  # noqa: F401
from .base_coder import Coder
from .single_wholefile_func_prompts import SingleWholeFileFunctionPrompts


class FileUpdate:
    def __init__(self, path: str, content: str):
        self.path = path
        self.content = content


class StatusCode:
    SUCCESS = 0
    FAILURE = 1


class SingleWholeFileFunctionCoder(Coder):
    functions: List[Dict[str, Union[str, Dict[str, Any]]]] = [
        dict(
            name="write_file",
            description="write new content into the file",
            parameters=dict(
                type="object",
                required=["explanation", "content"],
                properties=dict(
                    explanation=dict(
                        type="string",
                        description=(
                            "Step by step plan for the changes to be made to the code "
                            "(future tense, markdown format)"
                        ),
                    ),
                    content=dict(
                        type="string",
                        description="Content to write to the file",
                    ),
                ),
            ),
        ),
    ]

    def __init__(self, *args, **kwargs):
        self.gpt_prompts = SingleWholeFileFunctionPrompts()
        super().__init__(*args, **kwargs)

    @property
    def abs_root_path(self) -> Path:
        return Path(os.path.abspath(os.getcwd()))

    def update_cur_messages(self, content: str, edited: bool):
        if edited:
            self.cur_messages += [
                dict(role="assistant", content=self.gpt_prompts.redacted_edit_message)
            ]
        else:
            self.cur_messages += [dict(role="assistant", content=content)]

    def get_context_from_history(self, history: List[Dict[str, str]]) -> str:
        context = ""
        if history:
            context += "# Context:\n"
            for msg in history:
                if msg["role"] == "user":
                    context += msg["role"].upper() + ": " + msg["content"] + "\n"
        return context

    @lru_cache(maxsize=None)
    def live_diffs(self, fname: str, content: str, final: bool) -> str:
        lines = content.splitlines(keepends=True)

        full_path = self.abs_root_path / fname

        with suppress(FileNotFoundError):
            content = full_path.read_text()
            orig_lines = content.splitlines()
        else:
            orig_lines = []

        show_diff = diffs.diff_partial_update(
            orig_lines,
            lines,
            final,
            fname=fname,
        ).splitlines()

        return "\n".join(show_diff)

    def render_incremental_response(self, final: bool = False) -> str:
        if self.partial_response_content:
            return self.partial_response_content

        args = self.parse_partial_args()

        if not args:
            return ""

        explanation = args.get("explanation")
        files = args.get("files", [])

        res = ""
        if explanation:
            res += f"{explanation}\n\n"

        for i, file_upd in enumerate(files):
            path = file_upd.path
            content = file_upd.content

            this_final = (i < len(files) - 1) or final
            res += self.live_diffs(path, content, this_final)

        return res

    def update_files(self) -> Tuple[StatusCode, List[str]]:
        name = self.partial_response_function_call.get("name")
        if name and name != "write_file":
            return StatusCode.FAILURE, [f'Unknown function_call name="{name}", use name="write_file"']

        args = self.parse_partial_args()
        if not args:
            return StatusCode.FAILURE, []

        content = args["content"]
        path = self.get_inchat_relative_files()[0]

        if not isinstance(content, str):
            return StatusCode.FAILURE, ["Content must be a string."]

        if not self.allowed_to_edit(path, content):
            return StatusCode.FAILURE, ["Permission denied."]

        return StatusCode.SUCCESS, [path]
