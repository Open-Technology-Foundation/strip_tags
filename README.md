# strip_tags

A simple, powerful utility to strip HTML tags from files or standard input.

Available in two versions:
- **`strip_tags`** - Python version (robust, handles edge cases)
- **`html.strip-tags`** - Pure Bash version (no dependencies, portable)

## Features

- Remove HTML tags while preserving text content
- Selectively allow specific tags with `--allow` option
- Intelligent whitespace handling with automatic "squeezing" of empty lines
- Process files or piped input from stdin
- Bash tab completion for options and HTML tags

## Installation

Clone this repository:

```bash
git clone https://github.com/Open-Technology-Foundation/strip_tags.git
cd strip_tags
```

### Python Version (strip_tags)

Requires Python 3.10+. The wrapper script automatically creates a virtual environment and installs dependencies on first run.

```bash
sudo ln -s "$(pwd)/strip_tags" /usr/local/bin/
```

### Bash Version (html.strip-tags)

Pure Bash 5.2+, no dependencies. Use on systems without Python.

```bash
sudo ln -s "$(pwd)/html.strip-tags" /usr/local/bin/
```

### Bash Completion

To enable tab completion, add to your `~/.bashrc`:

```bash
source /path/to/strip_tags/.bash_completion
```

## Usage

Both versions share the same interface:

```
Usage: strip_tags [OPTIONS] [FILE]

Strip HTML tags from a file or stdin.

Options:
  -a, --allow TAGS   Comma-separated list of tags to preserve
  --no-squeeze       Disable collapsing of repeated blank lines
  -v, --version      Show version and exit
  -h, --help         Show this help and exit
```

## Examples

### Basic usage (strip all tags)

```bash
echo "<p>Hello <b>world</b></p>" | strip_tags
# Output: Hello world
```

### Preserve specific tags

```bash
echo "<p>Hello <b>world</b></p>" | strip_tags -a b
# Output: Hello <b>world</b>
```

### Process a file

```bash
strip_tags myfile.html > cleaned.txt
```

### Preserve multiple tags (spaces allowed)

```bash
strip_tags myfile.html --allow "a, p, div" > cleaned.txt
```

### Process piped input

```bash
curl -s https://example.com | strip_tags --allow h1,h2,p
```

### Disable whitespace squeezing

```bash
strip_tags myfile.html --no-squeeze
```

## Which Version to Use?

| Feature | Python (`strip_tags`) | Bash (`html.strip-tags`) |
|---------|----------------------|--------------------------|
| Dependencies | Python 3.10+, BeautifulSoup4 | Bash 5.2+, GNU sed |
| Script/style removal | Full block removal | Full block removal |
| Multi-line tags | Handled | Handled |
| Namespaced tags | Supported | Supported (v1.1.0+) |
| `>` in attributes | Handled | Not supported |
| Malformed HTML | Robust | Basic |
| Performance | ~200ms startup | ~10ms startup |
| Portability | Needs Python | Any Linux/Unix |

**Use Python version** for production HTML processing, especially with complex or malformed HTML.

**Use Bash version** on minimal systems, containers, or when Python is unavailable. Handles most common HTML correctly.

## Testing

Run the Python test suite:

```bash
source .venv/bin/activate
pytest test_strip_tags.py -v
```

## License

GPL-3
