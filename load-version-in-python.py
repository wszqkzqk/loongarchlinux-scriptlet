#!/usr/bin/env python3

import subprocess
import shlex
import os
import argparse
import sys

def get_package_version(file_path: str) -> str:
    """
    Get formatted package version string by sourcing the shell configuration file.
    - If 'epoch' is defined: returns "$epoch:$pkgver-$pkgrel"
    - If 'epoch' is not defined: returns "$pkgver-$pkgrel"
    
    Uses shell execution to properly handle all shell syntax features including
    variable substitution, functions, and conditional logic.
    
    Args:
        file_path: Path to the shell configuration file (e.g., PKGBUILD)
    
    Returns:
        Formatted version string
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        ValueError: If required variables are missing or parsing fails
    """
    # Verify configuration file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    # Construct safe shell command using multi-line string
    # Properly uses single curly braces for bash parameter expansion
    command = f"""
    source {shlex.quote(file_path)}
    # Check if pkgver and pkgrel are defined
    if [ -z "${{pkgver+x}}" ] || [ -z "${{pkgrel+x}}" ]; then
        echo 'Error: pkgver or pkgrel is not defined' >&2
        exit 1
    fi
    # Check if epoch is defined and output appropriate format
    if [ -n "${{epoch+x}}" ]; then
        echo "${{epoch}}:${{pkgver}}-${{pkgrel}}"
    else
        echo "${{pkgver}}-${{pkgrel}}"
    fi
    """
    
    try:
        # Execute command in bash shell with error handling
        result = subprocess.run(
            ["bash", "-c", command],
            check=True,
            text=True,
            capture_output=True,
            env=os.environ,
            # Remove extra whitespace from command
            input=command.strip()
        )
        return result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        # Extract meaningful error message from stderr/stdout
        error_msg = e.stderr.strip() or e.stdout.strip() or "Unknown error occurred"
        raise ValueError(
            f"Failed to parse configuration: {error_msg}\n"
            f"Command executed:\n{command.strip()}"
        ) from None

def main():
    """Parse command-line arguments and execute version parsing."""
    parser = argparse.ArgumentParser(
        description="Parse PKGBUILD file to generate formatted package version string"
    )
    parser.add_argument(
        "pkgbuild_path",
        type=str,
        help="Path to the PKGBUILD configuration file"
    )
    
    args = parser.parse_args()
    
    try:
        version = get_package_version(args.pkgbuild_path)
        print(version)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
