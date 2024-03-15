import colorsys
import json
import os
import random
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import tiktoken
from diskcache import Cache
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound

try:
    from aider import models  # type: ignore
except ImportError:
    pass

from .dump import dump  # noqa: F402,E402


def to_tree(tags: List[Tuple[str, ...]]) -> str:
    if not tags:
        return ""

    tags = sorted(tags)

    output = ""
    last = [None] * len(tags[0])
    tab = "\t"
    for tag in tags:
        tag = list(tag)

        for i in range(len(last) + 1):
            if i == len(last):
                break
            if last[i] != tag[i]:
              
