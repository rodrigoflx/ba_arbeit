#!/bin/bash

# Path to your Python virtual environment
VENV_PATH="/home/rodff/Dokumente/TUM/WS2425/ba_arbeit/benchmarks/.venv"

# List of generator options
generators=("rji" "lean" "base" "pg_bench" "sysbench" "rust" "ycsb" "apache" "fio")

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Loop through each generator option
for generator in "${generators[@]}"; do
    echo "Running with generator: $generator"
    
    # Run the command and capture the exit code
    sample_zipf --generator "$generator" --skew 0.8 --n $1 --samples $2 --buckets $3
    
    # Check the exit code
    exit_code=$?
    
    # Handle the exit code
    if [ $exit_code -eq 0 ]; then
        echo "Completed successfully with generator: $generator"
    else
        echo "Failed or ran out of memory with generator: $generator (Exit code: $exit_code)"
    fi
    
    echo "Moving to the next generator..."
done

# Deactivate the virtual environment
deactivate

echo "All runs completed."