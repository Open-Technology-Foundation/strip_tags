# strip_tags

A simple, powerful utility to strip HTML tags from files or standard input.

## Features

- Remove HTML tags while preserving text content
- Selectively allow specific tags with `--allow` option
- Intelligent whitespace handling with automatic "squeezing" of empty lines
- Process files or piped input from stdin
- Outputs plain text to stdout for easy piping to other commands

## Installation

Clone this repository and make sure you have Python 3.6+ installed:

```bash
git clone https://github.com/yourusername/strip_tags.git
cd strip_tags
pip install -r requirements.txt
```

For easier use, you can symlink the `strip_tags` script to your path:

```bash
sudo ln -s "$(pwd)/strip_tags" /usr/local/bin/
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

Examples:
  # Read from a file and allow <a>, <p>, and <div> tags
  strip_tags input.html --allow a,p,div

  # Read from stdin and allow <a> and <p> tags
  cat input.html | strip_tags -a a,p

  # Read from a file and strip all tags
  strip_tags input.html

  # Read from a file, strip all tags, and disable squeezing
  strip_tags input.html --no-squeeze
```

## Examples

### Basic usage (strip all tags)

```bash
strip_tags myfile.html > cleaned.txt
```

### Preserve specific tags

```bash
strip_tags myfile.html --allow a,p,div > cleaned.txt
```

### Process piped input

```bash
curl -s https://example.com | strip_tags --allow h1,h2,p > example.txt
```

### Combined with other commands

```bash
strip_tags myfile.html | grep "important text" > matches.txt
```

## Requirements

- Python 3.6+
- BeautifulSoup4

## License

MIT