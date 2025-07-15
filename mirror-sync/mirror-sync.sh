#!/bin/bash
# Arch Linux Loong64 Tier0 Mirror Synchronization Script
# Synchronizes local repo to remote rsync server

SOURCE_DIR="/srv/http/loongarch/archlinux"
# For safety reasons DEST_URL is not included here. Please set DEST_URL yourself here.
LOCK_FILE="/var/lock/mirror-sync.lock"
PASSWD_FILE="/root/.rsync-password"
LOG_FILE="/var/log/mirror-wsyu-sync.log"

# Rsync options for mirror synchronization
RSYNC_OPTS=(
  -rlptH           # Recursive copy with link/perm/time/hardlink preservation
  --safe-links     # Ignore symlinks pointing outside source tree (security)
  --delete-delay   # Delete files after transfer completes
  --delay-updates  # Atomic update (rename after complete)
  --password-file="$PASSWD_FILE"
  --stats          # Show transfer statistics
  --exclude=".~tmp~" # Cleanup old rsync temp files
)

# Create lock file descriptor
exec 9>"$LOCK_FILE"

# Exit immediately if previous sync still running
if ! flock -n 9; then
  echo "[$(date)] Previous synchronization still running. Skipping this cycle." \
    | tee -a "$LOG_FILE"
  exit 0
fi

# Synchronization process
echo "==================================================" | tee -a "$LOG_FILE"
echo "Sync STARTED at: $(date)" | tee -a "$LOG_FILE"

rsync "${RSYNC_OPTS[@]}" "$SOURCE_DIR/" "$DEST_URL" 2>&1 | tee -a "$LOG_FILE"

# Capture rsync exit status
SYNC_EXIT=${PIPESTATUS[0]}
echo "Sync COMPLETED at: $(date) - Exit code: $SYNC_EXIT" | tee -a "$LOG_FILE"

# Error notification on failure
# if [ $SYNC_EXIT -ne 0 ]; then
#   echo "ALERT: Synchronization failed with exit code $SYNC_EXIT" \
#     | mail -s "Arch Loong64 Mirror Sync Failure" admin@example.com
# fi

# Release lock
flock -u 9
exit $SYNC_EXIT
