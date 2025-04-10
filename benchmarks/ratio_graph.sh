#!/bin/bash

# Usage: ./script.sh <directory> <X_value>
# Example: ./script.sh data_csv 1000000

dir="$1"
x_arg="$2"
sampler="marsaglia"

# Validate arguments
if [ $# -ne 2 ]; then
    echo "Error: Missing arguments"
    echo "Usage: $0 <input_directory> <X_value>"
    exit 1
fi

if [ ! -d "$dir" ]; then
    echo "Error: Directory $dir does not exist"
    exit 1
fi

# Process CSV files
for file in "$dir"/*.csv; do
    # Extract X and Y values from filename
    filename=$(basename "$file" .csv)
    
    # Split on first occurrence of - or _
    x_raw=$(echo "$filename" | sed -E 's/[-_]([0-9]+[KM]?)[-_]?.*$//')
    y_raw=$(echo "$filename" | sed -E 's/.*[-_]([0-9]+[KM]?)(\..*)?$/\1/')

    # Convert raw values to numbers
    x_value=$(echo "$x_raw" | sed -e 's/K/*1000/' -e 's/M/*1000000/' | bc)
    y_value=$(echo "$y_raw" | sed -e 's/K/*1000/' -e 's/M/*1000000/' | bc)

    # Only process if converted X matches argument X
    if [ "$x_value" -eq "$x_arg" ]; then
        # Calculate bucket size
        bucket_size=$(echo "$y_value / 100" | bc)
        
        # Build output path
        output_file="graphs/ratio/${sampler}/${x_arg}_${y_value}.png"

        echo "Processing $filename: X=$x_value Y=$y_value"
        Rscript r_scripts/normalized_graph.r \
            --n "$x_arg" \
            --samples "$y_value" \
            --skew 0.8 \
            -o "$output_file" \
            -b "$bucket_size" \
            "$file"
    else
        echo "Skipping $filename: Extracted X=$x_value != argument X=$x_arg"
    fi
done

echo "Processing complete!"