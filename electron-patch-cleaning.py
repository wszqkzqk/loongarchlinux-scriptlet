#!/usr/bin/env python3

import re
import argparse

def clean_diff_file(input_file, output_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Pattern to match "diff --git a/patches"
    diff_start_pattern = re.compile(r'^diff --git a/patches')

    # Variables to store the cleaned diff
    cleaned_diff = []
    current_diff = []
    inside_relevant_diff = False

    for line in lines:
        if diff_start_pattern.match(line):
            if inside_relevant_diff:
                # Save the current diff before starting a new one
                cleaned_diff.extend(current_diff)
            # Start a new relevant diff
            current_diff = [line]
            inside_relevant_diff = True
        elif inside_relevant_diff:
            # Continue collecting lines for the current diff
            current_diff.append(line)
        else:
            # Ignore lines outside relevant diffs
            continue

    # Add the last diff if applicable
    if inside_relevant_diff:
        cleaned_diff.extend(current_diff)

    # Write the cleaned diff to the output file
    with open(output_file, 'w') as outfile:
        outfile.writelines(cleaned_diff)

    print(f"Cleaned diff saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Clean a diff file to retain only specific segments.")
    parser.add_argument("input_file", help="Path to the input diff file")
    parser.add_argument("output_file", help="Path to the output cleaned diff file")
    args = parser.parse_args()

    clean_diff_file(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
