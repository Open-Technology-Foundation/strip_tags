# strip_tags

Strip HTML tags from files or stdin while preserving text content.

Available in two versions with identical CLI interfaces:
- **`strip_tags`** - Python + BeautifulSoup (robust, handles edge cases)
- **`strip_tags.bash`** - Pure Bash + sed (fast, portable, no dependencies)

## Quick Start

```bash
# Strip all HTML tags
echo "<p>Hello <b>world</b></p>" | strip_tags
# Output: Hello world

# Preserve specific tags
echo "<p>Hello <b>world</b></p>" | strip_tags -a b
# Output: Hello <b>world</b>

# Process a file
strip_tags index.html > clean.txt

# Pipe from curl
curl -s https://example.com | strip_tags -a h1,p
```

## Features

- Remove HTML tags while preserving text content
- Selectively preserve tags with `-a/--allow`
- Automatic whitespace normalization (collapse multiple blank lines)
- Process files or piped stdin
- Bash tab completion for options and common HTML tags
- Full Unicode support

## Installation

```bash
git clone https://github.com/Open-Technology-Foundation/strip_tags.git
cd strip_tags
```

### Requirements

- **Python version**: Python 3.10+ and BeautifulSoup4
- **Bash version**: Bash 5.2+ and GNU sed (no other dependencies)

### User Install (Recommended)

Installs to `~/.local/`:

```bash
make install
make install-venv    # Optional: pre-build Python venv
```

### System Install

Installs to `/usr/local/`:

```bash
sudo make install PREFIX=/usr/local
sudo make install-venv PREFIX=/usr/local
```

### Development (Symlink Only)

For development, create symlinks without copying files:

```bash
make link
# Or for system-wide: sudo make link BINDIR=/usr/local/bin
```

### Update

Pull latest changes and refresh symlinks:

```bash
make update
```

### Uninstall

```bash
make uninstall
# Or: sudo make uninstall PREFIX=/usr/local
```

### Tab Completion

Add to `~/.bashrc`:

```bash
source ~/.local/share/yatti/strip_tags/.bash_completion
# Or for system install: source /usr/local/share/yatti/strip_tags/.bash_completion
```

## Usage

```
strip_tags [OPTIONS] [FILE]

Options:
  -a, --allow TAGS   Comma-separated list of tags to preserve
  --no-squeeze       Disable collapsing of repeated blank lines
  -v, --version      Show version and exit
  -h, --help         Show this help and exit
```

## Examples

### Basic Tag Stripping

```bash
# From stdin
echo "<div><p>Text</p></div>" | strip_tags

# From file
strip_tags document.html

# Save output
strip_tags document.html > clean.txt
```

### Preserve Specific Tags

```bash
# Keep bold tags
strip_tags -a b < input.html

# Keep multiple tags (comma-separated)
strip_tags --allow "a,p,h1,h2,h3" page.html

# Spaces allowed around commas
strip_tags -a "p, div, span" page.html

# Namespaced tags (SVG, etc.)
strip_tags -a "svg:rect,svg:circle" drawing.svg
```

### Pipeline Usage

```bash
# Fetch and clean a webpage
curl -s https://example.com | strip_tags -a p,h1

# Extract text from HTML email
cat email.html | strip_tags | less

# Clean multiple files
for f in *.html; do strip_tags "$f" > "${f%.html}.txt"; done
```

### Whitespace Control

```bash
# Default: collapse 3+ blank lines to 2
strip_tags document.html

# Preserve all whitespace
strip_tags --no-squeeze document.html
```

## Performance

Tested on 33KB real-world HTML (averaged over 5 runs):

| Scenario | Python | Bash | Speedup |
|----------|--------|------|---------|
| Simple tags | 57 ms | 10 ms | **5.5x** |
| With `--allow` | 58 ms | 13 ms | **4.5x** |
| 33KB HTML | 68 ms | 18 ms | **3.8x** |
| 33KB + allow | 66 ms | 59 ms | **1.1x** |

Bash is **4-5x faster** for typical use cases due to lower startup overhead.

## Accuracy

| Feature | Python | Bash | Notes |
|---------|--------|------|-------|
| Basic HTML | 100% | 100% | Identical output |
| Nested tags | 100% | 100% | Both handle correctly |
| Multi-line tags | Yes | Yes | Tags spanning lines |
| Self-closing | Yes | Yes | `<br/>`, `<hr/>` |
| Namespaced tags | Yes | Yes | `svg:rect`, `xlink:href` |
| Script blocks | Preserves content | **Removes entirely** | Different by design |
| Style blocks | Preserves content | **Removes entirely** | Different by design |
| HTML comments | Preserves | **Removes** | |
| DOCTYPE | Preserves | **Removes** | |
| `>` in attributes | Handles | Breaks | Known Bash limitation |
| Malformed HTML | Robust recovery | Best-effort | Python more forgiving |
| HTML entities | Decodes some | Preserves as-is | |

## When to Use Which

### Use Python (`strip_tags`) when:

- Processing malformed or complex HTML
- You need script/style content preserved (not removed)
- Accuracy is more important than speed
- HTML contains `>` inside attribute values

### Use Bash (`strip_tags.bash`) when:

- Speed is priority (4-5x faster)
- You want script/style blocks fully removed
- Running on minimal systems without Python
- Processing clean, well-formed HTML
- In containers or constrained environments

## Testing

Run the full test suite (111 tests):

```bash
source .venv/bin/activate
pytest tests/ -v
```

Run specific test modules:

```bash
# Python tests only (65 tests)
pytest tests/test_python_strip_tags.py -v

# Bash tests only (46 tests)
pytest tests/test_bash_strip_tags.py -v
```

Run performance comparison:

```bash
python tests/performance_matrix.py
```

## License

GPL-3.0
