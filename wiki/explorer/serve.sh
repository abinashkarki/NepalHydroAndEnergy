#!/usr/bin/env bash
# Serve the explorer locally. fetch() needs http(s), file:// will not work.
set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root
PORT="${1:-8765}"
echo ""
echo "Open http://localhost:${PORT}/wiki/explorer/  to use the wiki + map viewer."
echo ""
exec python3 -m http.server "${PORT}"
