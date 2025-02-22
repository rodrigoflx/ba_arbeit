#!/bin/bash
# generate_accuracy_table.sh
# Extracts accuracy metrics from JSON files, splitting samplers into smaller tables.
export LC_NUMERIC="C"


set -e

# Directory where JSON files are stored
bench_dir="results/benchmarks/acc"

# Define `n` values
n_values=(10000 100000)

# Define sample sizes relative to `n`
multipliers=(1 5 10)

# Extract sampler names dynamically
first_json=$(find "$bench_dir" -type f -name "*.json" | head -n 1)
if [ -z "$first_json" ]; then
    echo "No JSON files found in $bench_dir!"
    exit 1
fi
sampler_keys=($(jq -r '.results | keys_unsorted[]' "$first_json"))

# Define metrics
metrics=("kl_divergence" "tvd" "ks_test")

# Define chunk size (number of samplers per table)
# Define chunk size (number of samplers per table)
chunk_size=5  # Adjust this based on the number of samplers that fit

num_samplers=${#sampler_keys[@]}
num_chunks=$(( (num_samplers + chunk_size - 1) / chunk_size ))  # Ceiling division

# Loop through chunks of samplers to create separate tables
for ((chunk=0; chunk<num_chunks; chunk++)); do
    start=$((chunk * chunk_size))
    end=$((start + chunk_size))
    if [ $end -gt $num_samplers ]; then
        end=$num_samplers
    fi

    sampler_subset=("${sampler_keys[@]:start:end-start}")

    # Print table header
    echo "\begin{table}[h!]"
    echo "  \centering"
    echo "  \caption{Accuracy Metrics (Part $((chunk + 1)))}"
    echo "  \resizebox{\textwidth}{!}{%"
    echo "  \begin{tabular}{l l$(printf ' ccc' $(seq 1 ${#sampler_subset[@]}))}"
    echo "    \toprule"
    
    # Print the main header row, aligning "n" and "Samples" properly
    echo -n "    n & Samples"
    for sampler in "${sampler_subset[@]}"; do
        echo -n " & \multicolumn{3}{c}{$sampler}"
    done
    echo " \\\\"

    # Print the rule below the sampler names, aligning correctly
    echo "    \cmidrule(lr){3-$((${#sampler_subset[@]} * 3 + 2))}"

    # Print sub-header row (KL, TVD, KS)
    echo -n "    & "  # Keeps `n` and `Samples` centered
    for sampler in "${sampler_subset[@]}"; do
        echo -n " KL & TVD & KS"
    done
    echo " \\\\"
    echo "    \midrule"

    # Print table data
    for n in "${n_values[@]}"; do
        for multiplier in "${multipliers[@]}"; do
            samples=$((n * multiplier))

            json_file=$(find "$bench_dir" -maxdepth 1 -type f -name "*.json" | while read -r f; do
                file_n=$(jq '.metadata.n' "$f")
                file_samples=$(jq '.metadata.samples' "$f")
                if [ "$file_n" -eq "$n" ] && [ "$file_samples" -eq "$samples" ]; then
                    echo "$f"
                    break
                fi
            done)

            row="$n & $samples"
            if [ -z "$json_file" ]; then
                for sampler in "${sampler_subset[@]}"; do
                    row="$row & - & - & -"
                done
            else
                for sampler in "${sampler_subset[@]}"; do
                    for metric in "${metrics[@]}"; do
                        value=$(jq -r ".results[\"$sampler\"].$metric // \"-\"" "$json_file")
                        value=$(printf "%.3f" "$value")
                        row="$row & $value"
                    done
                done
            fi
            echo "    $row \\\\"
        done
    done

    echo "    \bottomrule"
    echo "  \end{tabular}"
    echo "  }"  
    echo "\end{table}"
    echo ""
done

