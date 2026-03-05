#!/bin/bash
set -e

HAMMERSPOON_DIR="$HOME/.hammerspoon"

echo "==> Removing grammarCLI hotkey..."

# Remove grammar.lua
if [ -f "$HAMMERSPOON_DIR/grammar.lua" ]; then
    rm "$HAMMERSPOON_DIR/grammar.lua"
    echo "    Removed grammar.lua"
fi

# Remove require line from init.lua
INIT_FILE="$HAMMERSPOON_DIR/init.lua"
if [ -f "$INIT_FILE" ] && grep -q 'require("grammar")' "$INIT_FILE"; then
    sed -i '' '/-- grammarCLI hotkey/d' "$INIT_FILE"
    sed -i '' '/require("grammar")/d' "$INIT_FILE"
    # Remove trailing blank lines
    sed -i '' -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$INIT_FILE"
    echo "    Removed require from init.lua"
fi

# Reload Hammerspoon
if pgrep -x "Hammerspoon" > /dev/null; then
    hs -c "hs.reload()" 2>/dev/null || true
    echo "    Reloaded Hammerspoon config"
fi

echo ""
echo "==> Done! Ctrl+Shift+G hotkey removed."
echo "    Hammerspoon itself was not uninstalled. To remove it:"
echo "    brew uninstall --cask hammerspoon"
