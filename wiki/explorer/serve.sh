#!/usr/bin/env bash
# Serve the explorer locally. fetch() needs http(s), file:// will not work.
# Binds to localhost only — not accessible from the network.
set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root
PORT="${1:-8765}"
echo ""
echo "Open http://localhost:${PORT}/wiki/explorer/  to use the wiki + map viewer."
echo ""
exec python3 -m http.server --bind 127.0.0.1 "${PORT}"
