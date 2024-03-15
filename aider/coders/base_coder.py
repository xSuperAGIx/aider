#!/usr/bin/env python

import hashlib
import json
import os
import sys
import traceback
from json.decoder import JSONDecodeError
from pathlib import Path, PurePosixPath

import backoff
import git
import openai
import requests
from jsonschema import Draft7Validator
from openai.error import APIError, RateLimitError, ServiceUnavailableError, Timeout
from rich.console import Console, Text
from rich.live import Live
from rich.markdown import Markdown

from aider import models, prompts, utils
from aider.commands import Commands
from aider.repomap import RepoMap

from ..dump import dump  # noqa: F401

class MissingAPIKeyError(ValueError):
    pass

class ExhaustedContextWindow(Exception):
    pass

def wrap_fence(name):
    return f"<{name}>", f"</{name}>"

class Coder:
    abs_fnames = None
    repo = None
    last_aider_commit_hash = None
    last_asked_for_commit_time = 0
    repo_map = None
    functions = None
    total_cost = 0.0
    num_exhausted_context_windows = 0

    @classmethod
    def create(cls, main_model, edit_format, io, **kwargs):
        if not main_model:
            main_model = models.GPT35_1
