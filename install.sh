#!/usr/bin/env bash
# j2 installer
# Copies the scaffold into the current directory and validates the setup.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"

echo "j2 installer"
echo "============"

# --- Python version check ---
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install Python 3.10 or later." >&2
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED="3.10"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
  echo "ERROR: Python $REQUIRED+ required, found $PYTHON_VERSION." >&2
  exit 1
fi
echo "Python $PYTHON_VERSION ... OK"

# --- PyYAML check ---
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "Installing PyYAML..."
  pip3 install --quiet pyyaml
fi
echo "PyYAML ... OK"

# --- Create target directory ---
mkdir -p "$TARGET_DIR"

# --- Copy scaffold ---
echo "Copying scaffold to $TARGET_DIR ..."
rsync -a --ignore-existing \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  "$SCRIPT_DIR/" "$TARGET_DIR/"
echo "Scaffold copied."

# --- Copy runner.py from j2 source repo ---
RUNNER_SRC="$(dirname "$SCRIPT_DIR")/.j2/runner.py"
if [ -f "$RUNNER_SRC" ]; then
  cp "$RUNNER_SRC" "$TARGET_DIR/.j2/runner.py"
  echo "runner.py installed."
else
  echo "WARNING: runner.py not found at $RUNNER_SRC — copy it manually to $TARGET_DIR/.j2/runner.py" >&2
fi

# --- Copy templates from j2 source repo ---
TEMPLATES_SRC="$(dirname "$SCRIPT_DIR")/.j2/templates"
if [ -d "$TEMPLATES_SRC" ]; then
  rsync -a --ignore-existing "$TEMPLATES_SRC/" "$TARGET_DIR/.j2/templates/"
  echo "Templates installed."
else
  echo "WARNING: templates not found at $TEMPLATES_SRC — copy them manually to $TARGET_DIR/.j2/templates/" >&2
fi

# --- Copy config from j2 source repo ---
CONFIG_SRC="$(dirname "$SCRIPT_DIR")/.j2/config"
if [ -d "$CONFIG_SRC" ]; then
  rsync -a --ignore-existing "$CONFIG_SRC/" "$TARGET_DIR/.j2/config/"
  echo "Config installed."
else
  echo "WARNING: config not found at $CONFIG_SRC — copy it manually to $TARGET_DIR/.j2/config/" >&2
fi

# --- Validate YAML configs ---
echo "Validating config files..."
for f in "$TARGET_DIR/.j2/config/"*.yaml; do
  python3 -c "import yaml, sys; yaml.safe_load(open('$f'))" \
    && echo "  $f ... OK" \
    || { echo "  ERROR: $f is invalid YAML" >&2; exit 1; }
done

echo ""
echo "Installation complete."
echo "Next steps:"
echo "  1. Edit .j2/config/settings.yaml with your project name."
echo "  2. Edit .j2/rules.md with your project's coding principles (language, testing rules, style, etc.)."
echo "  3. Add your project spec to .j2/specs/"
echo "  4. Run /refresh in Claude Code to begin."
