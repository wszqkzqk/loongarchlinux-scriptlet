#!/usr/bin/env python3

import argparse
import pyalpm
import urllib.request
import shutil
from typing import Optional
import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib # type: ignore
import os
import sys
from datetime import datetime, timedelta

CACHE_DIR: str = os.path.join(GLib.get_user_cache_dir(), "devtools-loong64")
LOONG64_REPOS: tuple = ("core", "extra")
LOONG64_DB_PATH: str = os.path.join(CACHE_DIR, "repo-db", "loong64")
DEFAULT_MIRROR: str = "https://loongarchlinux.lcpu.dev/loongarch/archlinux"

def download_file(source: str, dest: str) -> None:
    """
    Download a file from a given URL to a local destination.

    Args:
        source (str): The URL of the file to download
        dest (str): The local path where the file should be saved

    Raises:
        Exception: If the download fails for any reason
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    repo_path = os.path.dirname(dest)
    os.makedirs(repo_path, exist_ok=True)

    try:
        print(f"Downloading {source} to {dest}")
        req = urllib.request.Request(source, headers=headers)
        with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        print(f"Error downloading file: {e}", file=sys.stderr)
        raise

def update_loong64_repos(mirror_loong64: str) -> None:
    """
    Update the local loong64 repository databases from a specified mirror.

    Args:
        mirror_loong64 (str): The base URL of the loong64 package mirror
    """
    print("Updating loong64 repositories...")
    for repo in LOONG64_REPOS:
        db_url = f"{mirror_loong64}/{repo}/os/loong64/{repo}.db"
        db_path = os.path.join(LOONG64_DB_PATH, "sync", f"{repo}.db")
        try:
            download_file(db_url, db_path)
        except Exception:
            print(f"Failed to download {repo}.db, skipping.", file=sys.stderr)
            continue
    print("Loong64 repositories updated.")

def load_repo(dir_path: str, repo: str) -> Optional[pyalpm.DB]:
    """
    Load a package repository database.

    Args:
        dir_path (str): The directory path where the repository database is located
        repo (str): The name of the repository to load

    Returns:
        Optional[pyalpm.DB]: The loaded repository database, or None if loading fails
    """
    handle = pyalpm.Handle("/", dir_path)
    try:
        db = handle.register_syncdb(repo, 0)
        return db
    except pyalpm.error as e:
        print(f"Failed to load repo {dir_path}/{repo}: {e}", file=sys.stderr)
        return None

def main() -> None:
    """
    Main function to query package information.
    """
    parser = argparse.ArgumentParser(
        description="Query package information from LoongArch repositories.",
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-S', '--sync',
        action='store_true',
        help='Download and update the loong64 repository databases.'
    )
    parser.add_argument(
        '-d', '--days',
        type=int,
        default=7,
        help='List packages updated in the last n days (default: %(default)s).'
    )
    parser.add_argument(
        '-m', '--mirror',
        default=DEFAULT_MIRROR,
        help='Mirror URL for LoongArch repository database (default: %(default)s)',
        metavar='URL'
    )

    args = parser.parse_args()

    if args.sync:
        update_loong64_repos(args.mirror)

    repos_to_load = LOONG64_REPOS
    databases = []
    for repo_name in repos_to_load:
        db_path = os.path.join(LOONG64_DB_PATH, "sync", f"{repo_name}.db")
        if not os.path.exists(db_path):
            print(f"Database for '{repo_name}' not found. Please run with -S to download.", file=sys.stderr)
            continue
        db = load_repo(LOONG64_DB_PATH, repo_name)
        if db:
            databases.append(db)

    if not databases:
        print("No databases loaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    print(f"\nPackages updated in the last {args.days} days:")
    print("-" * 75)
    print(f"{'Package':<30} {'Version':<25} {'Build Date':<20}")
    print("-" * 75)

    cutoff_date = datetime.now() - timedelta(days=args.days)
    
    updated_packages = []

    for db in databases:
        for pkg in db.pkgcache:
            build_date = datetime.fromtimestamp(pkg.builddate)
            if build_date > cutoff_date:
                updated_packages.append(pkg)

    updated_packages.sort(key=lambda p: p.builddate)

    for pkg in updated_packages:
        build_date_str = datetime.fromtimestamp(pkg.builddate).strftime('%Y-%m-%d %H:%M')
        print(f"{pkg.name:<30} {pkg.version:<25} {build_date_str:<20}")

if __name__ == "__main__":
    main()
