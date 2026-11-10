#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/spotme" <<EOF
#!/usr/bin/env bash
cd "$ROOT"
exec python3 "$ROOT/spotme.py" "\$@"
EOF
chmod 700 "$BIN_DIR/spotme"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "Tambah $BIN_DIR ke PATH: export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac
echo "SPOT-Me CLI dipasang."
echo "Jalankan: spotme"
