#!/bin/bash
# Remove macOS extended attribute files recursively that can interfere with Docker builds

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Cleaning macOS extended attribute files recursively..."
find . -name "._*" -type f -print -delete
echo "Done!"
