# strip_tags

A simple, powerful utility to strip HTML tags from files or standard input.

## Features

- Remove HTML tags while preserving text content
- Selectively allow specific tags with `--allow` option
- Intelligent whitespace handling with automatic "squeezing" of empty lines
- Process files or piped input from stdin
- Auto-managed Python virtual environment
- Bash tab completion for options and HTML tags

## Installation

Clone this repository (requires Python 3.10+):

```bash
git clone https://github.com/Open-Technology-Foundation/strip_tags.git
cd strip_tags
```

The wrapper script automatically creates a virtual environment and installs dependencies on first run.

For system-wide access, symlink to your path:

```bash
sudo ln -s "$(pwd)/strip_tags" /usr/local/bin/
```

### Bash Completion

To enable tab completion, add to your `~/.bashrc`:

```bash
source /path/to/strip_tags/.bash_completion
```

## Usage

```
usage: strip_tags [-h] [-a ALLOW] [--no-squeeze] [-v] [filename]

Strip HTML tags from a file or stdin.

positional arguments:
  filename             Input HTML file

options:
  -h, --help           show this help message and exit
  -a, --allow ALLOW    Comma-separated list of allowed tags
  --no-squeeze         Disable squeezing of repeated empty lines
  -v, --version        show program's version and exit
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

## Testing

Run the test suite:

```bash
source .venv/bin/activate
pytest test_strip_tags.py -v
```

## Requirements

- Python 3.10+
- BeautifulSoup4

## License

GPL-3
