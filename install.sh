#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# Install the requested command name.
cat > "$BIN_DIR/spotme.py" <<EOF
#!/usr/bin/env bash
cd "$ROOT"
exec python3 "$ROOT/spotme.py" "\$@"
EOF
chmod 700 "$BIN_DIR/spotme.py"

# Keep the shorter alias available too.
cat > "$BIN_DIR/spotme" <<EOF
#!/usr/bin/env bash
exec "$BIN_DIR/spotme.py" "\$@"
EOF
chmod 700 "$BIN_DIR/spotme"

# Add the user bin directory to common interactive shells once.
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$rc" ] && ! grep -Fq 'export PATH="$HOME/.local/bin:$PATH"' "$rc"; then
    printf '\n# SPOT-Me CLI\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$rc"
  fi
done

export PATH="$BIN_DIR:$PATH"

echo "SPOT-Me CLI berjaya dipasang."
echo "Tutup dan buka terminal semula, kemudian jalankan: spotme.py"
