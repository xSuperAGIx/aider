#!/bin/bash

# Use absolute path for pwd to avoid issues with relative paths
ABS_PWD=$(realpath $(pwd))

# Set HISTFILE to a file inside the container to keep command history separate
HISTFILE=/aider/.bash_history

# Use double quotes to avoid issues with whitespaces in paths
docker run \
       -it --rm \
       -v "$ABS_PWD:/aider" \
       -v "$ABS_PWD/tmp.benchmarks:/benchmarks" \
       -e OPENAI_API_KEY="$OPENAI_API_KEY" \
       -e HISTFILE \
       -e AIDER_DOCKER=1 \
       -e AIDER_BENCHMARK_DIR=/benchmarks \
       aider-benchmark \
       bash
