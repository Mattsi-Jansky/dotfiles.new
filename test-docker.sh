#!/bin/bash
set -e

IMAGE_NAME="dotfiles-test"
CONTAINER_NAME="dotfiles-test-run"

echo "Building test image..."
docker build -f Dockerfile.test -t "$IMAGE_NAME" .

echo ""
echo "Running dotfiles setup in fresh Ubuntu container..."
echo "──────────────────────────────────────────────────────"

output_file=$(mktemp)
docker run --rm \
    --name "$CONTAINER_NAME" \
    -v "$(pwd):/home/testuser/dotfiles:ro" \
    "$IMAGE_NAME" 2>&1 | tee "$output_file" || true

echo "──────────────────────────────────────────────────────"

failures=$(grep '\[!!\]' "$output_file" || true)
rm -f "$output_file"

if [ -z "$failures" ]; then
    echo "PASS: No failures."
    exit 0
else
    echo "FAIL: Unexpected failures:"
    echo "$failures"
    exit 1
fi
