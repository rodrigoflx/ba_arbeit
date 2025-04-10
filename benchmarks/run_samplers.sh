#!/bin/bash

# Path to your Python virtual environment
VENV_PATH="/home/rodff/Dokumente/TUM/WS2425/ba_arbeit/benchmarks/.venv"

# List of generator options
generators=("fio")

# List of sample sizes
samples=(10000 100000 1000000 10000000 100000000)

# List of support sizes
support=(1000000 10000000 100000000)

skew=0.8

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Loop through each generator option
for generator in "${generators[@]}"; do
    for N in "${support[@]}"; do
        for sample in "${samples[@]}"; do
            echo "Running with generator: $generator"
            echo "Running with support size: $N"
            echo "Running with sample size: $sample"

            if [ "$N" == "10000" ]; then
                BUCKETS=100
            elif [ "$N" == "100000" ]; then
                BUCKETS=1000
            elif [ "$N" == "1000000" ]; then
                BUCKETS=10000
            elif [ "$N" == "10000000" ]; then
                BUCKETS=100000
            elif [ "$N" == "100000000" ]; then
                BUCKETS=1000000
            fi

            # Run the command and capture the exit code
            sample_zipf --generator "$generator" --skew "$skew" --n "$N" --samples "$sample" --buckets "$BUCKETS"
            sleep 1 
            
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
    done
done

# Deactivate the virtual environment
deactivate

echo "All runs completed."