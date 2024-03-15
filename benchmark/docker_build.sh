#!/bin/bash

# Exit immediately if any command exits with a non-zero status.
set -e

# Build the Docker image using the benchmark/Dockerfile and tag it as aider-benchmark.
docker build \
       --file benchmark/Dockerfile \
       --tag aider-benchmark \
       .

