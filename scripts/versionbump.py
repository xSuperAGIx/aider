import argparse
import re
import subprocess
from packaging import version
from typing import Match
from typing import Optional


def main(new_version: str, dry_run: bool) -> None:
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        raise ValueError(f"Invalid version format, must be x.y.z: {new_version}")

    new_version_obj = version.parse(new_version)

    with open("aider/__init__.py", "r") as f:
        content = f.read()

    match: Optional[Match[str]] = re.search(r'__version__ = "(.+?)"', content)
    if not match:
        raise ValueError("Version not found in aider/__init__.py")

    current_version_str = match.group(1).split("-dev")[0]
    current_version = version.parse(current_version_str)
    if new_version_obj <= current_version:
        raise ValueError(
            f"New version {new_version} must be greater than the current version {current_version_str}"
        )

    updated_content = re.sub(r'__version__ = ".+?"', f'__version__ = "{new_version}"', content)

    print("Updating aider/__init__.py with new version:")
    print(updated_content)
    if not dry_run:
        with open("aider/__init__.py", "w") as f:
            f.write(updated_content)

    git_commands = [
        ["git", "add", "aider/__init__.py"],
        ["git", "commit", "-m", f"version bump to {new_version}"],
        ["git", "tag", f"v{new_version}"],
        ["git", "push", "origin"],
        ["git", "push", "origin", f"v{new_version}"],
    ]

    for cmd in git_commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, check=True)
        print(result.stdout.decode())

    updated_dev_content = re.sub(
        r'__version__ = ".+?"', f'__version__ = "{new_version}-dev"', content
    )

    print()
    print("Updating aider/__init__.py with new dev version:")
    print(updated_dev_content)
    if not dry_run:
        with open("aider/__init__.py", "w") as f:
            f.write(updated_dev_content)

    git_commands_dev = [
        ["git", "add", "aider/__init__.py"],
        ["git", "commit", "-m", f"set version to {new_version}-dev"],
        ["git", "push", "origin"],
    ]

    for cmd in git_commands_dev:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, check=True)
        print(result.stdout.decode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bump version")
    parser.add_argument("new_version", help="New version in x.y.z format")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print each step without actually executing them"
    )
    args = parser.parse_args()
    main(args.new_version, args
