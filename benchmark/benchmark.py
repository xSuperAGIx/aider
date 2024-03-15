#!/usr/bin/env python

import os
import sys
import json
import subprocess
import time
import re
import git
import shutil
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import openai
import lox
from typing_extensions import TypedDict
from rich.console import Console
import typer
from imgcat import imgcat
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from json.decoder import JSONDecodeError
from azure.core.exceptions import ResourceNotFoundError

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)

class ResultSummary(TypedDict):
    total_tests: int
    completed_tests: int
    duration: float
    cost: float
    error_outputs: int
    user_asks: int
    test_timeouts: int
    exhausted_context_windows: int
    pass_rate_1: float
    pass_rate_2: float

def resolve_dirname(
    dirname: Union[str, Path], use_single_prior: bool, make_new: bool

