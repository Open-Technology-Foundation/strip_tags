#!/usr/bin/env python3
"""
strip_tags - A utility to remove HTML tags from files or stdin.

This script processes HTML content from a file or standard input,
removing HTML tags based on user-specified options, and outputs
the resulting plain text.
"""
import sys
import re
import os
import argparse
from typing import List, Optional, Union
from bs4 import BeautifulSoup


def strip_tags(html: str, allowed_tags: Optional[List[str]] = None) -> str:
  """
  Strip HTML tags from the provided HTML content.
  
  Args:
      html: HTML content to process
      allowed_tags: List of HTML tags to preserve in the output (optional)
      
  Returns:
      Processed text with HTML tags removed (except allowed tags)
  """
  # Remove the <!DOCTYPE...> tag
  html = re.sub(r'<!DOCTYPE.*?>', '', html, flags=re.IGNORECASE | re.DOTALL)
  
  try:
    soup = BeautifulSoup(html, 'html.parser')
    
    if allowed_tags:
      allowed_tags = [tag.lower() for tag in allowed_tags]
      for tag in soup.find_all(True):
        if tag.name.lower() not in allowed_tags:
          tag.unwrap()
    else:
      for tag in soup.find_all(True):
        tag.unwrap()
        
    return str(soup)
  except Exception as e:
    sys.stderr.write(f"Error processing HTML: {e}\n")
    return html  # Return original content on error


def squeeze_text(string: str) -> str:
  """
  Remove excessive empty lines, preserving at most one empty line between text blocks.
  
  Args:
      string: Text to process
      
  Returns:
      Text with excessive empty lines removed
  """
  lines = string.split('\n')
  result = []
  prev_line_empty = False
  start_non_empty = False
  
  for line in lines:
    if line.strip():
      result.append(line)
      prev_line_empty = False
      start_non_empty = True
    else:
      if start_non_empty and not prev_line_empty:
        result.append('')
        prev_line_empty = True
        
  return '\n'.join(result)


def read_input(filename: Optional[str]) -> str:
  """
  Read HTML content from a file or stdin.
  
  Args:
      filename: Path to the input file (None for stdin)
      
  Returns:
      HTML content as string
      
  Raises:
      FileNotFoundError: If the specified file doesn't exist
      PermissionError: If the file cannot be read due to permissions
  """
  if filename:
    if not os.path.exists(filename):
      sys.stderr.write(f"Error: File '{filename}' not found\n")
      sys.exit(1)
      
    try:
      with open(filename, 'r', encoding='utf-8') as file:
        return file.read()
    except (PermissionError, UnicodeDecodeError) as e:
      sys.stderr.write(f"Error reading file '{filename}': {e}\n")
      sys.exit(1)
  else:
    # Read from stdin
    return sys.stdin.read()


def main() -> None:
  """Parse arguments and process HTML content."""
  parser = argparse.ArgumentParser(
    prog='strip_tags',
    description='Strip HTML tags from a file or stdin.',
    epilog='''
Examples:
  # Read from a file and allow <a>, <p>, and <div> tags
  strip_tags input.html --allow a,p,div

  # Read from stdin and allow <a> and <p> tags
  cat input.html | strip_tags -a a,p

  # Read from a file and strip all tags
  strip_tags input.html

  # Read from a file, strip all tags, and disable squeezing
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

  allowed_tags = args.allow.split(',') if args.allow else None
  
  try:
    html_content = read_input(args.filename)
    plain_text = strip_tags(html_content, allowed_tags)
    
    if args.squeeze:
      plain_text = squeeze_text(plain_text)
      
    print(plain_text)
  except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    sys.stderr.write("\nOperation cancelled\n")
    sys.exit(130)


if __name__ == '__main__':
  main()
