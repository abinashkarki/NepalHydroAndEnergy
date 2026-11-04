#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
PORT="${1:-8765}"
echo "Open http://localhost:${PORT}/internal/dashboard/"
exec python3 -m http.server --bind 127.0.0.1 "${PORT}"
