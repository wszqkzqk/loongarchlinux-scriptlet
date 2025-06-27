#!/usr/bin/env python3

import sys
import os

def process_patch(patch_path):
    if not os.path.exists(patch_path):
        print(f"Error: File {patch_path} does not exist")
        return

    output_path = os.path.join(os.path.dirname(patch_path), 'loong-addition.config')

    with open(patch_path, 'r') as patch_file:
        lines = patch_file.readlines()

    # Process lines
    filtered_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('+CONFIG_') and (not line.endswith('=n')):
            # Remove leading + character
            filtered_lines.append(line[1:] + '\n')

    # Sort lines
    filtered_lines.sort()

    # Write to output file
    with open(output_path, 'w') as output_file:
        output_file.writelines(filtered_lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 cleanpatch.py <patch_file>")
        sys.exit(1)

    process_patch(sys.argv[1])
