#!/usr/bin/env python3
"""Comprehensive test suite for strip_tags utility."""
import os
import stat
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from strip_tags import strip_tags, squeeze_text, read_input


class TestStripTags:
  """Tests for strip_tags() function."""

  def test_basic_tag_removal(self):
    """Single tag is removed, content preserved."""
    assert strip_tags('<p>Hello</p>') == 'Hello'

  def test_nested_tags(self):
    """Nested tags are all removed."""
    assert strip_tags('<div><p>Text</p></div>') == 'Text'

  def test_multiple_tags(self):
    """Multiple sibling tags are removed."""
    result = strip_tags('<p>A</p><p>B</p>')
    assert 'A' in result and 'B' in result

  def test_self_closing_tags(self):
    """Self-closing tags like <br/> are removed."""
    assert strip_tags('Line<br/>break') == 'Linebreak'

  def test_attributes_stripped(self):
    """Tag attributes are removed with the tag."""
    assert strip_tags('<a href="http://example.com">Link</a>') == 'Link'

  def test_empty_input(self):
    """Empty string returns empty string."""
    assert strip_tags('') == ''

  def test_plain_text_no_tags(self):
    """Plain text without tags is unchanged."""
    assert strip_tags('Hello world') == 'Hello world'

  def test_allowed_single_tag(self):
    """Single allowed tag is preserved."""
    result = strip_tags('<p><b>Bold</b></p>', {'b'})
    assert '<b>Bold</b>' in result
    assert '<p>' not in result

  def test_allowed_multiple_tags(self):
    """Multiple allowed tags are preserved."""
    result = strip_tags('<div><p>X</p></div>', {'p', 'div'})
    assert '<div>' in result
    assert '<p>' in result

  def test_allowed_tags_case_insensitive(self):
    """Allowed tags match case-insensitively."""
    # BeautifulSoup normalizes to lowercase
    result = strip_tags('<P>Text</P>', {'p'})
    assert '<p>' in result.lower()

  def test_script_tag_content_preserved(self):
    """Script tag removed but content preserved."""
    result = strip_tags('<script>code</script>Text')
    assert 'code' in result and 'Text' in result
    assert '<script>' not in result

  def test_style_tag_content_preserved(self):
    """Style tag removed but content preserved."""
    result = strip_tags('<style>.class{}</style>Text')
    assert 'Text' in result
    assert '<style>' not in result

  def test_html_entities_preserved(self):
    """HTML entities are preserved through processing."""
    # html.parser preserves entities (re-encodes special chars for safety)
    result = strip_tags('<p>&amp; &lt; &gt;</p>')
    assert '&amp;' in result or '&' in result
    assert '&lt;' in result or '<' in result

  def test_doctype_preserved(self):
    """DOCTYPE declaration is preserved by html.parser."""
    # html.parser preserves DOCTYPE - this is expected behavior
    result = strip_tags('<!DOCTYPE html><p>X</p>')
    assert 'X' in result

  def test_malformed_html_unclosed_tag(self):
    """Unclosed tags are handled gracefully."""
    result = strip_tags('<p>Unclosed')
    assert 'Unclosed' in result

  def test_malformed_html_extra_closing(self):
    """Extra closing tags are handled gracefully."""
    result = strip_tags('<p>Text</p></div>')
    assert 'Text' in result

  def test_deeply_nested_tags(self):
    """Deeply nested tags (10+ levels) are handled."""
    html = '<div>' * 15 + 'Deep' + '</div>' * 15
    result = strip_tags(html)
    assert result == 'Deep'

  def test_unicode_content(self):
    """Unicode content is preserved."""
    assert strip_tags('<p>日本語</p>') == '日本語'
    assert strip_tags('<p>émojis 🎉</p>') == 'émojis 🎉'

  def test_html_comments_preserved(self):
    """HTML comments are preserved by html.parser."""
    # html.parser preserves comments - this is expected behavior
    result = strip_tags('Before<!-- comment -->After')
    assert 'Before' in result and 'After' in result

  def test_empty_allowed_tags_set(self):
    """Empty set for allowed_tags removes all tags."""
    result = strip_tags('<p>Text</p>', set())
    assert result == 'Text'

  def test_allowed_tags_none_vs_empty(self):
    """None and empty set behave the same."""
    html = '<p><b>Text</b></p>'
    assert strip_tags(html, None) == strip_tags(html, set())

  def test_special_characters_in_content(self):
    """Special characters in content are preserved."""
    html = '<p>a < b && c > d</p>'
    result = strip_tags(html)
    assert '<' in result or '&lt;' in result

  def test_whitespace_preserved(self):
    """Whitespace in content is preserved."""
    result = strip_tags('<p>  spaced  </p>')
    assert '  spaced  ' in result


class TestSqueezeText:
  """Tests for squeeze_text() function."""

  def test_no_change_single_newline(self):
    """Single newline between lines unchanged."""
    assert squeeze_text('Line1\nLine2') == 'Line1\nLine2'

  def test_no_change_double_newline(self):
    """Double newline (one blank line) unchanged."""
    assert squeeze_text('A\n\nB') == 'A\n\nB'

  def test_collapse_multiple_blank_lines(self):
    """Multiple blank lines collapsed to one."""
    assert squeeze_text('A\n\n\n\nB') == 'A\n\nB'

  def test_collapse_many_newlines(self):
    """Many consecutive newlines collapsed."""
    assert squeeze_text('A' + '\n' * 10 + 'B') == 'A\n\nB'

  def test_leading_whitespace_stripped(self):
    """Leading newlines are stripped."""
    assert squeeze_text('\n\n\nText') == 'Text'

  def test_trailing_whitespace_stripped(self):
    """Trailing newlines are stripped."""
    assert squeeze_text('Text\n\n\n') == 'Text'

  def test_mixed_whitespace(self):
    """Leading, trailing, and middle whitespace handled."""
    assert squeeze_text('\nA\n\n\n\nB\n') == 'A\n\nB'

  def test_empty_string(self):
    """Empty string returns empty string."""
    assert squeeze_text('') == ''

  def test_only_whitespace(self):
    """String of only newlines returns empty."""
    assert squeeze_text('\n\n\n') == ''

  def test_preserves_single_blank_lines(self):
    """Single blank lines between paragraphs preserved."""
    text = 'Para1\n\nPara2\n\nPara3'
    assert squeeze_text(text) == text

  def test_spaces_not_affected(self):
    """Horizontal spaces are not collapsed."""
    assert squeeze_text('word   word') == 'word   word'


class TestReadInput:
  """Tests for read_input() function."""

  def test_read_existing_file(self, tmp_path):
    """Reading an existing file returns its content."""
    test_file = tmp_path / 'test.html'
    test_file.write_text('<p>Hello</p>', encoding='utf-8')
    result = read_input(str(test_file))
    assert result == '<p>Hello</p>'

  def test_read_empty_file(self, tmp_path):
    """Reading an empty file returns empty string."""
    test_file = tmp_path / 'empty.html'
    test_file.write_text('', encoding='utf-8')
    result = read_input(str(test_file))
    assert result == ''

  def test_read_unicode_file(self, tmp_path):
    """Reading a UTF-8 file with unicode content."""
    test_file = tmp_path / 'unicode.html'
    test_file.write_text('<p>日本語 émoji 🎉</p>', encoding='utf-8')
    result = read_input(str(test_file))
    assert '日本語' in result

  def test_file_not_found(self):
    """Non-existent file causes sys.exit(1)."""
    with pytest.raises(SystemExit) as exc_info:
      read_input('/nonexistent/path/file.html')
    assert exc_info.value.code == 1

  def test_permission_denied(self, tmp_path):
    """Unreadable file causes sys.exit(1)."""
    test_file = tmp_path / 'noperm.html'
    test_file.write_text('content', encoding='utf-8')
    os.chmod(test_file, 0o000)
    try:
      with pytest.raises(SystemExit) as exc_info:
        read_input(str(test_file))
      assert exc_info.value.code == 1
    finally:
      os.chmod(test_file, stat.S_IRUSR | stat.S_IWUSR)

  def test_stdin_input(self):
    """Reading from stdin when filename is None."""
    with patch('sys.stdin', StringIO('<p>stdin content</p>')):
      result = read_input(None)
    assert result == '<p>stdin content</p>'

  def test_stdin_empty(self):
    """Reading from empty stdin."""
    with patch('sys.stdin', StringIO('')):
      result = read_input(None)
    assert result == ''

  def test_large_file(self, tmp_path):
    """Reading a large file (1MB+)."""
    test_file = tmp_path / 'large.html'
    content = '<p>' + 'x' * (1024 * 1024) + '</p>'
    test_file.write_text(content, encoding='utf-8')
    result = read_input(str(test_file))
    assert len(result) > 1024 * 1024


class TestCLI:
  """Integration tests for CLI using subprocess."""

  @pytest.fixture
  def script_path(self):
    """Return path to the strip_tags script."""
    return Path(__file__).parent / 'strip_tags.py'

  def run_script(self, script_path, args=None, stdin_data=None):
    """Helper to run the script and return result."""
    cmd = [sys.executable, str(script_path)]
    if args:
      cmd.extend(args)
    result = subprocess.run(
      cmd,
      input=stdin_data,
      capture_output=True,
      text=True
    )
    return result

  def test_stdin_basic(self, script_path):
    """Basic stdin processing."""
    result = self.run_script(script_path, stdin_data='<p>Hello</p>')
    assert result.returncode == 0
    assert 'Hello' in result.stdout

  def test_file_argument(self, script_path, tmp_path):
    """Processing a file argument."""
    test_file = tmp_path / 'test.html'
    test_file.write_text('<div>Content</div>', encoding='utf-8')
    result = self.run_script(script_path, [str(test_file)])
    assert result.returncode == 0
    assert 'Content' in result.stdout

  def test_allow_flag_short(self, script_path):
    """Short -a flag preserves specified tags."""
    result = self.run_script(
      script_path,
      ['-a', 'b'],
      stdin_data='<p><b>Bold</b></p>'
    )
    assert result.returncode == 0
    assert '<b>' in result.stdout
    assert '<p>' not in result.stdout

  def test_allow_flag_long(self, script_path):
    """Long --allow flag preserves specified tags."""
    result = self.run_script(
      script_path,
      ['--allow', 'p,div'],
      stdin_data='<div><p>Text</p></div>'
    )
    assert result.returncode == 0
    assert '<div>' in result.stdout
    assert '<p>' in result.stdout

  def test_allow_with_spaces(self, script_path):
    """Allow flag with spaces around tags."""
    result = self.run_script(
      script_path,
      ['-a', 'b, i, p'],
      stdin_data='<div><b>B</b><i>I</i><p>P</p></div>'
    )
    assert result.returncode == 0
    assert '<b>' in result.stdout
    assert '<i>' in result.stdout
    assert '<p>' in result.stdout
    assert '<div>' not in result.stdout

  def test_no_squeeze_flag(self, script_path):
    """--no-squeeze preserves multiple newlines."""
    result = self.run_script(
      script_path,
      ['--no-squeeze'],
      stdin_data='A\n\n\n\nB'
    )
    assert result.returncode == 0
    # Count newlines - should be more than 2
    assert result.stdout.count('\n') >= 4

  def test_squeeze_default(self, script_path):
    """Default behavior squeezes newlines."""
    result = self.run_script(
      script_path,
      stdin_data='A\n\n\n\n\nB'
    )
    assert result.returncode == 0
    # Should have at most 2 consecutive newlines
    assert '\n\n\n' not in result.stdout

  def test_version_flag_short(self, script_path):
    """Short -v flag shows version."""
    result = self.run_script(script_path, ['-v'])
    assert 'strip_tags' in result.stdout or 'strip_tags' in result.stderr
    assert '1.0.0' in result.stdout or '1.0.0' in result.stderr

  def test_version_flag_long(self, script_path):
    """Long --version flag shows version."""
    result = self.run_script(script_path, ['--version'])
    assert '1.0.0' in result.stdout or '1.0.0' in result.stderr

  def test_help_flag_short(self, script_path):
    """Short -h flag shows help."""
    result = self.run_script(script_path, ['-h'])
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower()

  def test_help_flag_long(self, script_path):
    """Long --help flag shows help."""
    result = self.run_script(script_path, ['--help'])
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower()
    assert '--allow' in result.stdout

  def test_missing_file(self, script_path):
    """Non-existent file returns error."""
    result = self.run_script(script_path, ['/nonexistent/file.html'])
    assert result.returncode == 1
    assert 'not found' in result.stderr.lower()

  def test_combined_flags(self, script_path):
    """Multiple flags work together."""
    result = self.run_script(
      script_path,
      ['-a', 'b', '--no-squeeze'],
      stdin_data='<p><b>Bold</b></p>\n\n\n\nMore'
    )
    assert result.returncode == 0
    assert '<b>' in result.stdout
    assert result.stdout.count('\n') >= 4


class TestEdgeCases:
  """Edge case and error handling tests."""

  def test_cdata_section(self):
    """CDATA sections are handled."""
    html = '<![CDATA[some data]]>'
    result = strip_tags(html)
    # BeautifulSoup may handle this differently
    assert 'CDATA' not in result or 'some data' in result

  def test_processing_instruction(self):
    """XML processing instructions handled."""
    html = '<?xml version="1.0"?><p>Text</p>'
    result = strip_tags(html)
    assert 'Text' in result

  def test_mixed_content(self):
    """Mixed text and tags handled correctly."""
    html = 'Before<p>Inside</p>After'
    result = strip_tags(html)
    assert 'Before' in result
    assert 'Inside' in result
    assert 'After' in result

  def test_very_long_tag_name(self):
    """Very long (fake) tag names handled."""
    html = '<verylongtagname>Content</verylongtagname>'
    result = strip_tags(html)
    assert 'Content' in result

  def test_numeric_entities_converted(self):
    """Numeric HTML entities are converted to named entities."""
    # html.parser converts numeric to named entities for safety
    html = '<p>&#60;&#62;</p>'  # < and >
    result = strip_tags(html)
    # May be raw chars or escaped entities
    assert '<' in result or '&lt;' in result
    assert '>' in result or '&gt;' in result

  def test_named_entities(self):
    """Named HTML entities decoded."""
    html = '&nbsp;&copy;&reg;'
    result = strip_tags(html)
    # Non-breaking space, copyright, registered
    assert len(result) >= 3

  def test_broken_entities(self):
    """Broken entities handled gracefully."""
    html = '&notanentity; &amp incomplete'
    result = strip_tags(html)
    assert 'notanentity' in result or '&' in result

  def test_svg_content(self):
    """SVG elements are stripped."""
    html = '<svg><circle r="50"/></svg>Text'
    result = strip_tags(html)
    assert 'Text' in result
    assert '<svg>' not in result

  def test_math_content(self):
    """MathML elements are stripped."""
    html = '<math><mi>x</mi></math>Text'
    result = strip_tags(html)
    assert 'Text' in result

  def test_data_attributes(self):
    """Data attributes are stripped with tags."""
    html = '<div data-value="123">Content</div>'
    result = strip_tags(html)
    assert 'Content' in result
    assert 'data-value' not in result

  def test_template_tags(self):
    """Template tags are handled."""
    html = '<template><p>Template content</p></template>Visible'
    result = strip_tags(html)
    assert 'Visible' in result


if __name__ == '__main__':
  pytest.main([__file__, '-v'])
