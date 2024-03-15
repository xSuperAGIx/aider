#!/usr/bin/env python

import subprocess
import sys

# from aider.dump import dump  # noqa: F401


def main():
    models = [
        "gpt-3.5-turbo-0613",
        # "gpt-3.5-turbo-16k-0613",
        # "gpt-4-0314",
        # "gpt-4-0613",
    ]
    edit_formats = [
        "whole",
        # "whole-func",
    ]

    for repeat in range(1, 10, 1):
        for model in models:
            for edit_format in edit_formats:
                if "-func" in edit_format and "-03" in model:
                    continue

                dirname = f"rungrid-{model}-{edit_format}-repeat-{repeat}"
                run(dirname, model, edit_format, repeat)


def run(dirname, model, edit_format, repeat):
    cmd = [
        "./benchmark/benchmark.py",
        dirname,
        "--model",
        model,
        "--edit-format",
        edit_format,
        "--threads",
        "10",
        "--cont",
    ]
    print(f"Repeat {repeat}: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        sys.exit(e.returncode)


if __name__ == "__main__":
    status = main()
    sys.exit(status)
