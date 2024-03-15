import math
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import editblock_prompts
import io_utils


class EditBlockCoder(io_utils.Coder):
    def __init__(self, *args: Any, **kwargs: Any):
        self.gpt_prompts = editblock_prompts.EditBlockPrompts()
        super().__init__(*args, **kwargs)

    def update_cur_messages(self, content: str, edited: bool):
        self.cur_messages.append({"role": "assistant", "content": content})

    def update_files(self) -> List[str]:
        content = self.partial_response_content

        edited_files = []
        for path, original, updated in find_original_update_blocks(content):
            full_path = self.allowed_to_edit(path)
            if not full_path:
                continue

            content = self.io.read_text(full_path)
            content = do_replace(full_path, content, original, updated)
            if content:
                self.io.write_text(full_path, content)
                edited_files.append(path)
                continue

            self.io.tool_error(f"Failed to apply edit to {path}")

        return edited_files


def try_dotdotdots(whole: str, part: str, replace: str) -> Optional[str]:
    dots_re = re.compile(r"(^\s*\.\.\.\n)", re.MULTILINE | re.DOTALL)

    part_pieces = re.split(dots_re, part)
    replace_pieces = re.split(dots_re, replace)

    if len(part_pieces) != len(replace_pieces):
        raise ValueError("Unpaired ... in edit block")

    if len(part_pieces) == 1:
        return None

    all_dots_match = all(part_pieces[i] == replace_pieces[i] for i in range(1, len(part_pieces), 2))

    if not all_dots_match:
        raise ValueError("Unmatched ... in edit block")

    part_pieces = [part_pieces[i] for i in range(0, len(part_pieces), 2)]
    replace_pieces = [replace_pieces[i] for i in range(0, len(replace_pieces), 2)]

    pairs = zip(part_pieces, replace_pieces)
    for part, replace in pairs:
        if not part and not replace:
            continue

        if not part and replace:
            if not whole.endswith("\n"):
                whole += "\n"
            whole += replace
            continue

        if whole.count(part) != 1:
            raise ValueError(
                "No perfect matching chunk in edit block with ... or part appears more than once"
            )

        whole = whole.replace(part, replace, 1)

    return whole


def replace_part_with_missing_leading_whitespace(whole: str, part: str, replace: str) -> Optional[str]:
    whole_lines = whole.splitlines()
    part_lines = part.splitlines()
    replace_lines = replace.splitlines()

    if all((not pline or pline[0].isspace()) for pline in part_lines):
        return

    for i in range(len(whole_lines) - len(part_lines) + 1):
        leading_whitespace = ""
        for j, c in enumerate(whole_lines[i]):
            if c == part_lines[0][0]:
                leading_whitespace = whole_lines[i][:j]
                break

        if not leading_whitespace or not all(c.isspace() for c in leading_whitespace):
            continue

        matched = all(
            whole_lines[i + k].startswith(leading_whitespace + part_lines[k])
            for k in range(len(part_lines))
        )

        if matched:
            replace_lines = [
                leading_whitespace + rline if rline else rline for rline in replace_lines
            ]
            whole_lines = whole_lines[:i] + replace_lines + whole_lines[i + len(part_lines) :]
            return "\n".join(whole_lines) + "\n"

    return None


def replace_most_similar_chunk(whole: str, part: str, replace: str) -> Optional[str]:
    res = replace_part_with_missing_leading_whitespace(whole, part, replace)
    if res:
        return res

    if part in whole:
        return whole.replace(part, replace)

    try:
        res = try_dotdotdots(whole, part, replace)
    except ValueError:
        return

    if res:
        return res

    similarity_thresh = 0.8

    max_similarity = 0
    most_similar_chunk_start = -1
    most_similar_chunk_end = -1

    whole_lines = whole.splitlines()
    part_lines = part.splitlines()

    scale = 0.1
    min_len = math.floor(len(part_lines) * (1 - scale))
    max_len = math.ceil(len(part_lines) * (1 + scale))

    for length in range(min_len, max_len):
        for i in range(len(whole_lines) - length + 1):
            chunk = whole_lines[i : i + length]
            chunk = "\n".join(chunk)

            similarity = SequenceMatcher(None, chunk, part).ratio()

            if similarity > max_similarity and similarity:
                max_similarity = similarity
                most
