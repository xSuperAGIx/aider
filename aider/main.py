import os
import sys
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional

import git
import configargparse
import openai
from openai.error import OpenAIError

from aider import __version__
from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model
from aider.models import models

def get_git_root() -> Optional[str]:
    try:
        repo = git.Repo(search_parent_directories=True)
        return repo.working_tree_dir
    except git.InvalidGitRepositoryError:
        return None

def setup_git(git_root: Optional[str], io: InputOutput) -> Optional[str]:
    if git_root:
        return git_root

    if not io.confirm_ask("No git repo found, create one to track GPT's changes (recommended)?"):
        return

    repo = git.Repo.init(Path.cwd())
    global_git_config = git.GitConfigParser([str(Path.home() / ".gitconfig")], read_only=True)
    with repo.config_writer() as git_config:
        if not global_git_config.has_option("user", "name"):
            git_config.set_value("user", "name", "Your Name")
            io.tool_error('Update git name with: git config --global user.name "Your Name"')
        if not global_git_config.has_option("user", "email"):
            git_config.set_value("user", "email", "you@example.com")
            io.tool_error('Update git email with: git config --global user.email "you@example.com"')

    io.tool_output("Git repository created in the current working directory.")
    git_root = str(Path.cwd().resolve())
    check_gitignore(git_root, io, False)
    return git_root

def check_gitignore(git_root: Optional[str], io: InputOutput, ask: bool = True) -> None:
    if not git_root:
        return

    pat = ".aider*"

    gitignore_file = Path(git_root) / ".gitignore"
    if gitignore_file.exists():
        content = io.read_text(gitignore_file)
        if pat in content.splitlines():
            return
    else:
        content = ""

    if ask and not io.confirm_ask(f"Add {pat} to .gitignore (recommended)?"):
        return

    if content and not content.endswith("\n"):
        content += "\n"
    content += pat + "\n"
    io.write_text(gitignore_file, content)

    io.tool_output(f"Added {pat} to .gitignore")

def main(args: List[str] = None, input: Any = None, output: Any = None) -> int:
    if args is None:
        args = sys.argv[1:]

    git_root = get_git_root()

    conf_fname = Path(".aider.conf.yml")

    default_config_files = [conf_fname.resolve()]  # CWD
    if git_root:
        git_conf = Path(git_root) / conf_fname  # git root
        if git_conf not in default_config_files:
            default_config_files.append(git_conf)
    default_config_files.append(Path.home() / conf_fname)  # homedir
    default_config_files = list(map(str, default_config_files))

    parser = configargparse.ArgumentParser(
        description="aider is GPT powered coding in your terminal",
        add_config_file_help=True,
        default_config_files=default_config_files,
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        auto_env_var_prefix="AIDER_",
    )

    # ... (rest of the code)

    try:
        args = parser.parse_args(args)
    except configargparse.ArgumentError as e:
        io.tool_error(e)
        return 1

    # ... (rest of the code)

    if not args.openai_api_key:
        io.tool_error(
            "No OpenAI API key provided. Use --openai-api-key or setx OPENAI_API_KEY on Windows or export OPENAI_API_KEY on Unix-based systems."
        )
        return 1

    try:
        openai.api_key = args.openai_api_key
        # ... (rest of the code)
    except OpenAIError as e:
        io.tool_error(e)
        return 1

    # ... (rest of the code)

    coder = Coder.create(
        main_model,
        args.edit_format,
        io,
        # ... (rest of the code)
    )

    # ... (rest of the code)

if __name__ == "__main__":
    status = main()
    sys.exit(status)
