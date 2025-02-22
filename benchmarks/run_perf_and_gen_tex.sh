#!/bin/bash
# run_and_generate.sh
#
# This script runs the command:
#   perf_benchmark --skew <float> --samples <int> --n <int>
# for different combinations of samples and n.
#
# It assumes that each run produces a JSON file in the benchmarks/
# directory with a filename like: perf_timestamp.json
#
# Later, the script reads the JSON files and produces LaTeX tables.
# Each table corresponds to one value of "n" and has rows indexed
# by the "samples" parameter and columns for each sampler type.
#
# Requirements: jq must be installed.

set -e

# ---- Configuration ----

skew=0.8

n_values=(10 100 500)

samples_values=(1 10 100 1000)

bench_dir="results/benchmarks/perf_bench"

sampler_keys=(BaseSampler RustSampler PgBenchSampler SysbenchSampler RJISampler FIOSampler LeanStoreSampler ApacheSampler YCSBSampler)

column_format="l$(printf ' c%.0s' $(seq 1 ${#sampler_keys[@]}))"

# ---- Part 1: Run the benchmarks ----

# echo "Running benchmarks..."
# for n in "${n_values[@]}"; do
#   for samples in "${samples_values[@]}"; do
#     echo "Running: perf_benchmark --skew $skew --samples $samples --n $n"
#     perf_benchmark --skew "$skew" --samples "$samples" --n "$n"
#     sleep 1
#   done
# done

echo "Benchmarks completed."

# ---- Part 2: Generate LaTeX tables ----

echo "Generating LaTeX tables..."

for n in "${n_values[@]}"; do
    n_million=$((n * 1000000))
    echo "%-------------------------------------------------------"
    echo "% LaTeX table for n = ${n}M"
    echo "\begin{table}[h!]"
    echo "  \centering"
    echo "  \caption{Benchmark results for n = ${n}M}"
    echo "  \begin{tabular}{$column_format}"
    echo "    \toprule"
    # Print header row: first column is "Samples", then sampler names.
    header="Samples (M)"
    for key in "${sampler_keys[@]}"; do
        header="$header & $key"
    done
    echo "    $header \\\\"
    echo "    \midrule"
    
    # For each sample value (row), find the JSON file with matching metadata.
    for samples in "${samples_values[@]}"; do
        samples_million=$((samples * 1000000))
        # Try to find a JSON file that has metadata.n equal to $n_million and metadata.samples equal to $samples_million.
        # (We assume one such file exists for each combination.)
        json_file=$(find "$bench_dir" -maxdepth 1 -type f -name "*.json" | while read -r f; do
            file_n=$(jq '.metadata.n' "$f")
            file_samples=$(jq '.metadata.samples' "$f")
            if [ "$file_n" -eq "$n_million" ] && [ "$file_samples" -eq "$samples_million" ]; then
                echo "$f"
                break
            fi
        done)
        
        row="${samples}M"
        if [ -z "$json_file" ]; then
            for key in "${sampler_keys[@]}"; do
                row="$row & -"
            done
        else
            for key in "${sampler_keys[@]}"; do
                value=$(jq ".results.${key}" "$json_file")
                row="$row & $value"
            done
        fi
        echo "    $row \\\\"
    done
    
    echo "    \bottomrule"
    echo "  \end{tabular}"
    echo "\end{table}"
    echo ""
done

echo "LaTeX table generation complete."
