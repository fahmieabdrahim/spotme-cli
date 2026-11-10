#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cp "$ROOT/spotme.py" "$BIN_DIR/spotme"
chmod 700 "$BIN_DIR/spotme"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "Tambah $BIN_DIR ke PATH: export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac
echo "Dipasang di $BIN_DIR/spotme"
echo "Jalankan: spotme"
