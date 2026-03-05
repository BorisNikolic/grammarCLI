# grammarCLI

Terminal grammar checker with Grammarly-like UX. Colored inline annotations, category scores, interactive accept/reject, and diff view — all in your terminal.

## Features

- **Grammarly-style categories**: Correctness (red), Clarity (yellow), Engagement (blue), Delivery (green)
- **Overall score**: 0–100 with per-category breakdown and visual score bars
- **Multiple input modes**: File, stdin/pipe, clipboard
- **Interactive mode**: Step through suggestions one by one — accept, skip, or accept all
- **Auto-fix**: Output corrected text or fix files in place
- **Diff view**: Side-by-side original vs corrected
- **JSON output**: Machine-readable results for tool integration
- **Protocol-oriented**: Swappable grammar engines (LanguageTool, mock, bring your own)

## Requirements

- Python 3.11+
- Internet connection (for LanguageTool API — free, no API key needed)

## Installation

```bash
git clone https://github.com/BorisNikolic/grammarCLI.git
cd grammarCLI
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify it works:

```bash
echo "me and him went to the store" | grammarCLI check
```

## Usage

### Basic check

```bash
# Check a file
grammarCLI check myfile.txt

# Pipe text
echo "me and him went to the store, it were great" | grammarCLI check

# From clipboard
grammarCLI check --clipboard
```

### Auto-fix

```bash
# Print corrected text to stdout
grammarCLI check myfile.txt --fix

# Fix file in place
grammarCLI check myfile.txt --fix --in-place

# Pipe and fix
echo "it were bad" | grammarCLI check --fix
```

### Interactive mode

Step through each suggestion with keyboard controls:

```bash
grammarCLI check myfile.txt --interactive
```

Controls:
- `Enter` — Accept first suggestion
- `1-5` — Pick a specific replacement
- `s` — Skip
- `a` — Accept all remaining
- `q` — Quit

### Diff view

```bash
grammarCLI check myfile.txt --diff
```

### JSON output

```bash
grammarCLI check myfile.txt --json
```

Example output:

```json
{
  "text": "me and him went",
  "language": "en-US",
  "overall_score": 85,
  "scores": {
    "correctness": 85,
    "clarity": 100,
    "engagement": 100,
    "delivery": 100
  },
  "suggestions": [
    {
      "offset": 0,
      "length": 10,
      "message": "Use subject pronouns for sentence subjects",
      "replacements": ["he and I"],
      "category": "correctness",
      "severity": "error"
    }
  ]
}
```

### Options

```
grammarCLI check [FILE] [OPTIONS]

Options:
  -l, --language TEXT   Language code (e.g. en-US, de-DE, auto)
  --clipboard           Read text from clipboard
  --fix                 Output corrected text
  --in-place            Fix file in place (requires --fix)
  -i, --interactive     Step through suggestions interactively
  --deep                Enable AI-powered deep analysis
  --diff                Show diff of original vs corrected
  --json                Output results as JSON
```

### Configuration

Create `~/.grammarrc.toml` to set defaults:

```toml
language = "en-US"
level = "picky"           # "default" or "picky"
disabled_rules = []
disabled_categories = []
```

## Running Tests

```bash
source .venv/bin/activate
pip install pytest
pytest tests/ -v
```

## Architecture

grammarCLI is protocol-oriented — all grammar engines implement a common `GrammarEngine` protocol, making it easy to swap or combine backends:

```
grammar_cli/
  protocols.py        # GrammarEngine Protocol
  models.py           # Suggestion, CheckResult, Category, Severity
  checker.py          # Orchestrates engines, merges & deduplicates results
  engines/
    languagetool.py   # LanguageTool free API (no key needed)
    mock_engine.py    # Offline testing engine
  renderer.py         # Rich-based terminal output
  interactive.py      # Interactive accept/reject mode
  main.py             # Click CLI entry point
  config.py           # ~/.grammarrc.toml loader
  clipboard.py        # Clipboard read/write
```

Adding a new engine (Claude, Gemini, Ollama, etc.) is a single file that implements `check()`, `name`, and `supports_deep_analysis`.

## License

MIT
