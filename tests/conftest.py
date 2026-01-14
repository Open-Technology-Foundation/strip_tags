"""Shared pytest fixtures for strip_tags test suite."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def script_dir():
  """Return path to the scripts directory."""
  return Path(__file__).parent.parent


@pytest.fixture
def python_script(script_dir):
  """Return path to the Python strip_tags.py script."""
  return script_dir / 'strip_tags.py'


@pytest.fixture
def bash_script(script_dir):
  """Return path to the Bash html.strip-tags script."""
  return script_dir / 'html.strip-tags'


@pytest.fixture
def sample_html():
  """Common test HTML strings."""
  return {
    'simple': '<p>Hello</p>',
    'nested': '<div><p>Text</p></div>',
    'with_attrs': '<a href="http://example.com" class="link">Link</a>',
    'script': '<script>var x = 1;</script>Text',
    'style': '<style>body { color: red; }</style>Text',
    'multiline_tag': '<div\n  class="foo">\nHello\n</div>',
    'unicode': '<p>日本語 émojis 🎉</p>',
    'mixed': 'Before<p>Inside</p>After',
  }


@pytest.fixture
def run_python(python_script):
  """Fixture returning a function to run the Python script."""
  def _run(args=None, stdin_data=None):
    cmd = [sys.executable, str(python_script)]
    if args:
      cmd.extend(args)
    return subprocess.run(
      cmd,
      input=stdin_data,
      capture_output=True,
      text=True
    )
  return _run


@pytest.fixture
def run_bash(bash_script):
  """Fixture returning a function to run the Bash script."""
  def _run(args=None, stdin_data=None):
    cmd = [str(bash_script)]
    if args:
      cmd.extend(args)
    return subprocess.run(
      cmd,
      input=stdin_data,
      capture_output=True,
      text=True
    )
  return _run
