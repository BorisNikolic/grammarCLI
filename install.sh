#!/bin/bash
set -e

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$INSTALL_DIR/.venv"
SHELL_RC=""

# Detect shell config file
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "$(which zsh)" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "$(which bash)" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

echo "==> Installing grammarCLI..."

# Find Python 3.11+
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" -c "import sys; print(sys.version_info[:2])")
        major=$("$candidate" -c "import sys; print(sys.version_info[0])")
        minor=$("$candidate" -c "import sys; print(sys.version_info[1])")
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: Python 3.11+ is required. Install it with: brew install python@3.13"
    exit 1
fi

echo "    Using $PYTHON ($($PYTHON --version))"

# Create venv and install
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

echo "==> Installing dependencies..."
"$VENV_DIR/bin/pip" install -q -e "$INSTALL_DIR"

# Add alias to shell config
ALIAS_LINE="alias grammarCLI='$VENV_DIR/bin/grammarCLI'"

if [ -n "$SHELL_RC" ]; then
    if grep -q "alias grammarCLI=" "$SHELL_RC" 2>/dev/null; then
        echo "==> Alias already exists in $SHELL_RC"
    else
        echo "" >> "$SHELL_RC"
        echo "# grammarCLI" >> "$SHELL_RC"
        echo "$ALIAS_LINE" >> "$SHELL_RC"
        echo "==> Added alias to $SHELL_RC"
    fi
fi

echo ""
echo "==> grammarCLI installed successfully!"
echo ""
echo "    Run: source $SHELL_RC"
echo "    Then: echo \"me and him went\" | grammarCLI check"
