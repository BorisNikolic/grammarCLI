#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HAMMERSPOON_DIR="$HOME/.hammerspoon"
LUA_FILE="grammar.lua"

echo "==> Setting up grammarCLI hotkey (Ctrl+Shift+G)..."

# Check if Hammerspoon is installed
if [ ! -d "/Applications/Hammerspoon.app" ]; then
    echo "    Hammerspoon not found. Installing via Homebrew..."
    brew install --cask hammerspoon
    echo "    Installed. Please open Hammerspoon and grant Accessibility permissions."
    echo "    System Settings > Privacy & Security > Accessibility > Hammerspoon"
    echo ""
    echo "    After granting permissions, run this script again."
    exit 0
fi

# Create Hammerspoon config dir if needed
mkdir -p "$HAMMERSPOON_DIR"

# Copy grammar.lua
cp "$SCRIPT_DIR/$LUA_FILE" "$HAMMERSPOON_DIR/$LUA_FILE"
echo "    Copied $LUA_FILE to $HAMMERSPOON_DIR/"

# Add require to init.lua if not present
INIT_FILE="$HAMMERSPOON_DIR/init.lua"
if [ ! -f "$INIT_FILE" ]; then
    echo "require(\"grammar\")" > "$INIT_FILE"
    echo "    Created $INIT_FILE"
elif ! grep -q 'require("grammar")' "$INIT_FILE"; then
    echo "" >> "$INIT_FILE"
    echo '-- grammarCLI hotkey' >> "$INIT_FILE"
    echo 'require("grammar")' >> "$INIT_FILE"
    echo "    Added require to $INIT_FILE"
else
    echo "    require(\"grammar\") already in $INIT_FILE"
fi

# Reload Hammerspoon config
if pgrep -x "Hammerspoon" > /dev/null; then
    hs -c "hs.reload()" 2>/dev/null && echo "    Reloaded Hammerspoon config" || echo "    Please reload Hammerspoon manually (click menu bar icon > Reload Config)"
else
    echo "    Hammerspoon is not running. Please open it from Applications."
fi

echo ""
echo "==> Done! Select any text and press Ctrl+Shift+G to fix grammar."
