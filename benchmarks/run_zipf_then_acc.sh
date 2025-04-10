#!/bin/bash

# Placeholder arrays - fill these in with your values
GENERATORS=("rejection" "ycsb" "marsaglia" "sysbench" "fio" "rji" "apache")
N_VALUES=("10000" "100000" "1000000" "10000000" "100000000")
SAMPLE_COUNTS=("10000" "100000" "1000000" "10000000" "100000000" "1000000000")

# Set skew
SKEW=0.8

# Triple nested loop over generators, N_VALUES, and SAMPLE_COUNTS
for GEN in "${GENERATORS[@]}"; do
    for N in "${N_VALUES[@]}"; do
        for SAMPLES in "${SAMPLE_COUNTS[@]}"; do

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

            # Run sample_zipf command and capture returned path
            OUTPUT_PATH=$(sample_zipf --generator "$GEN" --skew "$SKEW" --n "$N" --samples "$SAMPLES" --buckets "$BUCKETS")

            sleep 1

            # Print returned path
            echo "Output saved to: $OUTPUT_PATH"

            # Run accuracy_zipf command
            accuracy_zipf --skew "$SKEW" --support_size "$N" --input_csv "$OUTPUT_PATH"
            sleep 1
        done
    done
done
