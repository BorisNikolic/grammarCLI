-- grammarCLI Hammerspoon integration
-- Hotkey: Ctrl+Shift+G — fixes grammar of selected text in any app

local GRAMMAR_CLI = os.getenv("HOME") .. "/WORK/grammarCLI/.venv/bin/grammarCLI"

local function grammarFix()
    -- Save current clipboard
    local originalClipboard = hs.pasteboard.getContents()

    -- Copy selected text
    hs.eventtap.keyStroke({"cmd"}, "c")

    -- Wait for clipboard to propagate, then process
    hs.timer.doAfter(0.2, function()
        local selectedText = hs.pasteboard.getContents()

        if not selectedText or selectedText == "" then
            hs.notify.new({title = "grammarCLI", informativeText = "No text selected"}):send()
            return
        end

        -- Write selected text to a temp file to avoid shell escaping issues
        local tmpFile = os.tmpname()
        local f = io.open(tmpFile, "w")
        f:write(selectedText)
        f:close()

        -- Run grammarCLI
        local cmd = GRAMMAR_CLI .. " check " .. tmpFile .. " --fix"
        local output, status = hs.execute(cmd)
        os.remove(tmpFile)

        if not status then
            hs.notify.new({title = "grammarCLI", informativeText = "Check failed"}):send()
            -- Restore clipboard
            if originalClipboard then
                hs.pasteboard.setContents(originalClipboard)
            end
            return
        end

        -- Trim trailing newline
        local corrected = output:gsub("%s+$", "")

        if corrected == selectedText or corrected == "" then
            hs.notify.new({title = "grammarCLI", informativeText = "No issues found"}):send()
            -- Restore clipboard
            if originalClipboard then
                hs.pasteboard.setContents(originalClipboard)
            end
            return
        end

        -- Paste corrected text
        hs.pasteboard.setContents(corrected)
        hs.eventtap.keyStroke({"cmd"}, "v")

        -- Restore original clipboard after paste propagates
        hs.timer.doAfter(0.3, function()
            if originalClipboard then
                hs.pasteboard.setContents(originalClipboard)
            end
        end)

        hs.notify.new({title = "grammarCLI", informativeText = "Text corrected"}):send()
    end)
end

hs.hotkey.bind({"ctrl", "shift"}, "g", grammarFix)
