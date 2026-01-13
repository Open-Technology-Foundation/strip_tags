#!/usr/bin/env python3
"""
strip_tags - Remove HTML tags from files or stdin.

Processes HTML content, removing tags based on options,
and outputs the resulting plain text.
"""
import sys
import re
import argparse
from bs4 import BeautifulSoup


def strip_tags(html: str, allowed_tags: set[str] | None = None) -> str:
  """
  Strip HTML tags from content.

  Args:
      html: HTML content to process
      allowed_tags: Set of lowercase tag names to preserve (optional)

  Returns:
      Text with HTML tags removed (except allowed tags)
  """
  soup = BeautifulSoup(html, 'html.parser')

  for tag in soup.find_all(True):
    if allowed_tags is None or tag.name not in allowed_tags:
      tag.unwrap()

  return str(soup)


def squeeze_text(text: str) -> str:
  """
  Remove excessive empty lines, preserving at most one between blocks.

  Args:
      text: Text to process

  Returns:
      Text with excessive empty lines collapsed
  """
  return re.sub(r'\n{3,}', '\n\n', text).strip()


def read_input(filename: str | None) -> str:
  """
  Read content from file or stdin.

  Args:
      filename: Path to input file (None for stdin)

  Returns:
      Content as string
  """
  if not filename:
    return sys.stdin.read()

  try:
    with open(filename, encoding='utf-8') as f:
      return f.read()
  except FileNotFoundError:
    sys.stderr.write(f"Error: File '{filename}' not found\n")
    sys.exit(1)
  except (PermissionError, UnicodeDecodeError) as e:
    sys.stderr.write(f"Error reading '{filename}': {e}\n")
    sys.exit(1)


def main() -> None:
  """Parse arguments and process HTML content."""
  parser = argparse.ArgumentParser(
    prog='strip_tags',
    description='Strip HTML tags from a file or stdin.',
    epilog='''
Examples:
  strip_tags input.html --allow a,p,div
  cat input.html | strip_tags -a a,p
  strip_tags input.html
  strip_tags input.html --no-squeeze
    ''',
    formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument('filename', nargs='?', help='Input HTML file')
  parser.add_argument('-a', '--allow', help='Comma-separated list of allowed tags')
  parser.add_argument('--no-squeeze', action='store_false', dest='squeeze',
                      help='Disable squeezing of repeated empty lines')
  parser.add_argument('-v', '--version', action='version', version='strip_tags 1.0.0')

  args = parser.parse_args()

  # Pre-process allowed_tags: strip whitespace, lowercase, convert to set
  allowed_tags = None
  if args.allow:
    allowed_tags = {tag.strip().lower() for tag in args.allow.split(',')}

  try:
    text = strip_tags(read_input(args.filename), allowed_tags)
    if args.squeeze:
      text = squeeze_text(text)
    print(text)
  except KeyboardInterrupt:
    sys.exit(130)


if __name__ == '__main__':
  main()
