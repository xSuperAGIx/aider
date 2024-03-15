#!/bin/bash

# exit when any command fails
set -e

benchmark_names=(
  "2023-06-29-11-04-31--gpt-3.5-turbo-0301"
  "2023-06-29-11-17-32--gpt-3.5-turbo-0613"
  "2023-06-29-22-18-10--diff-func-string-accept-lists"
  "2023-06-29-22-33-14--whole-func"
  "2023-06-29-22-33-21--whole-func-string"
  # Add more benchmark names here...
)

./benchmark/benchmark.py --stats "${benchmark_names[@]}"
