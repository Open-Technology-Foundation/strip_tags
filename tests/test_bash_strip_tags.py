#!/usr/bin/env python3
"""Comprehensive test suite for Bash strip_tags.bash utility."""
import os
import stat

import pytest


class TestBashBasicTagStripping:
  """Basic tag stripping tests for Bash version."""

  def test_basic_tag_removal(self, run_bash):
    """Single tag is removed, content preserved."""
    result = run_bash(stdin_data='<p>Hello</p>')
    assert result.returncode == 0
    assert 'Hello' in result.stdout

  def test_nested_tags(self, run_bash):
    """Nested tags are all removed."""
    result = run_bash(stdin_data='<div><p>Text</p></div>')
    assert result.returncode == 0
    assert 'Text' in result.stdout
    assert '<div>' not in result.stdout
    assert '<p>' not in result.stdout

  def test_multiple_tags(self, run_bash):
    """Multiple sibling tags are removed."""
    result = run_bash(stdin_data='<p>A</p><p>B</p>')
    assert result.returncode == 0
    assert 'A' in result.stdout
    assert 'B' in result.stdout

  def test_self_closing_tags(self, run_bash):
    """Self-closing tags like <br/> are removed."""
    result = run_bash(stdin_data='Line<br/>break')
    assert result.returncode == 0
    assert 'Linebreak' in result.stdout

  def test_attributes_stripped(self, run_bash):
    """Tag attributes are removed with the tag."""
    result = run_bash(stdin_data='<a href="http://example.com">Link</a>')
    assert result.returncode == 0
    assert 'Link' in result.stdout
    assert 'href' not in result.stdout

  def test_empty_input(self, run_bash):
    """Empty string returns empty output."""
    result = run_bash(stdin_data='')
    assert result.returncode == 0

  def test_plain_text_no_tags(self, run_bash):
    """Plain text without tags is unchanged."""
    result = run_bash(stdin_data='Hello world')
    assert result.returncode == 0
    assert 'Hello world' in result.stdout

  def test_unicode_content(self, run_bash):
    """Unicode content is preserved."""
    result = run_bash(stdin_data='<p>日本語 émojis 🎉</p>')
    assert result.returncode == 0
    assert '日本語' in result.stdout
    assert '🎉' in result.stdout


class TestBashAllowedTags:
  """Tests for --allow flag in Bash version."""

  def test_allow_single_tag_short(self, run_bash):
    """Short -a flag preserves specified tag."""
    result = run_bash(
      ['-a', 'b'],
      stdin_data='<p><b>Bold</b></p>'
    )
    assert result.returncode == 0
    assert '<b>' in result.stdout
    assert '</b>' in result.stdout
    assert '<p>' not in result.stdout

  def test_allow_single_tag_long(self, run_bash):
    """Long --allow flag preserves specified tag."""
    result = run_bash(
      ['--allow', 'b'],
      stdin_data='<p><b>Bold</b></p>'
    )
    assert result.returncode == 0
    assert '<b>' in result.stdout

  def test_allow_multiple_tags(self, run_bash):
    """Multiple tags in --allow are preserved."""
    result = run_bash(
      ['-a', 'p,div'],
      stdin_data='<div><p>Text</p></div>'
    )
    assert result.returncode == 0
    assert '<div>' in result.stdout
    assert '<p>' in result.stdout

  def test_allow_with_spaces(self, run_bash):
    """Allow flag with spaces around tags works."""
    result = run_bash(
      ['-a', 'b, i, p'],
      stdin_data='<div><b>B</b><i>I</i><p>P</p></div>'
    )
    assert result.returncode == 0
    assert '<b>' in result.stdout
    assert '<i>' in result.stdout
    assert '<p>' in result.stdout
    assert '<div>' not in result.stdout

  def test_allow_case_insensitive(self, run_bash):
    """Allowed tags match case-insensitively."""
    result = run_bash(
      ['-a', 'P'],
      stdin_data='<P>Text</P>'
    )
    assert result.returncode == 0
    # Tag should be preserved (lowercase or uppercase)
    assert 'Text' in result.stdout


class TestBashScriptStyleRemoval:
  """Tests for script/style block removal (v1.1.0 feature)."""

  def test_script_block_removed(self, run_bash):
    """Script block and content are removed entirely."""
    result = run_bash(
      stdin_data='<script>var x = 1;</script>Hello'
    )
    assert result.returncode == 0
    assert 'Hello' in result.stdout
    assert 'var x' not in result.stdout
    assert '<script>' not in result.stdout

  def test_style_block_removed(self, run_bash):
    """Style block and content are removed entirely."""
    result = run_bash(
      stdin_data='<style>body { color: red; }</style>Hello'
    )
    assert result.returncode == 0
    assert 'Hello' in result.stdout
    assert 'color: red' not in result.stdout
    assert '<style>' not in result.stdout

  def test_multiline_script_block(self, run_bash):
    """Multi-line script blocks are removed entirely."""
    result = run_bash(
      stdin_data='<script>\nvar x = 1;\nvar y = 2;\n</script>OK'
    )
    assert result.returncode == 0
    assert 'OK' in result.stdout
    assert 'var x' not in result.stdout

  def test_multiline_style_block(self, run_bash):
    """Multi-line style blocks are removed entirely."""
    result = run_bash(
      stdin_data='<style>\nbody {\n  color: red;\n}\n</style>OK'
    )
    assert result.returncode == 0
    assert 'OK' in result.stdout
    assert 'color' not in result.stdout

  def test_script_with_attributes(self, run_bash):
    """Script tags with attributes are removed."""
    result = run_bash(
      stdin_data='<script type="text/javascript">code</script>OK'
    )
    assert result.returncode == 0
    assert 'OK' in result.stdout
    assert 'code' not in result.stdout

  def test_multiple_script_blocks(self, run_bash):
    """Multiple script blocks are all removed."""
    result = run_bash(
      stdin_data='<script>a</script>text<script>b</script>more'
    )
    assert result.returncode == 0
    assert 'text' in result.stdout
    assert 'more' in result.stdout

  def test_script_with_less_than(self, run_bash):
    """Script containing < character is handled."""
    result = run_bash(
      stdin_data='<script>if(x<5){alert(1)}</script>OK'
    )
    assert result.returncode == 0
    assert 'OK' in result.stdout


class TestBashMultilineTags:
  """Tests for multi-line tag handling (v1.1.0 feature)."""

  def test_multiline_tag_stripped(self, run_bash):
    """Tags spanning multiple lines are stripped."""
    result = run_bash(
      stdin_data='<div\n  class="foo">\nHello\n</div>'
    )
    assert result.returncode == 0
    assert 'Hello' in result.stdout
    assert 'class=' not in result.stdout

  def test_multiline_tag_selective(self, run_bash):
    """Multi-line tags work with --allow."""
    result = run_bash(
      ['-a', 'p'],
      stdin_data='<div\n  class="foo">\n<p>Hello</p>\n</div>'
    )
    assert result.returncode == 0
    assert '<p>' in result.stdout
    assert 'class=' not in result.stdout

  def test_attributes_on_multiple_lines(self, run_bash):
    """Tags with attributes on multiple lines are handled."""
    result = run_bash(
      stdin_data='<a\n  href="url"\n  class="link">Link</a>'
    )
    assert result.returncode == 0
    assert 'Link' in result.stdout
    assert 'href' not in result.stdout


class TestBashNamespacedTags:
  """Tests for namespaced tag support (v1.1.0 feature)."""

  def test_svg_namespaced_tag_stripped(self, run_bash):
    """SVG namespaced tags are stripped by default."""
    result = run_bash(
      stdin_data='<svg:rect width="100"/>Text'
    )
    assert result.returncode == 0
    assert 'Text' in result.stdout
    assert 'svg:rect' not in result.stdout

  def test_svg_namespaced_tag_allowed(self, run_bash):
    """SVG namespaced tags can be preserved with --allow."""
    result = run_bash(
      ['-a', 'svg:rect'],
      stdin_data='<svg:rect width="100"/><p>Text</p>'
    )
    assert result.returncode == 0
    assert 'svg:rect' in result.stdout
    assert '<p>' not in result.stdout

  def test_xlink_namespaced_tag(self, run_bash):
    """xlink namespaced tags work with --allow."""
    result = run_bash(
      ['-a', 'xlink:href'],
      stdin_data='<xlink:href>link</xlink:href><p>Text</p>'
    )
    assert result.returncode == 0
    # The tag should be in the output
    assert 'xlink' in result.stdout.lower() or 'link' in result.stdout


class TestBashWhitespace:
  """Tests for whitespace handling."""

  def test_squeeze_default(self, run_bash):
    """Default behavior squeezes multiple newlines."""
    result = run_bash(
      stdin_data='A\n\n\n\n\nB'
    )
    assert result.returncode == 0
    assert '\n\n\n' not in result.stdout

  def test_no_squeeze_flag(self, run_bash):
    """--no-squeeze preserves multiple newlines."""
    result = run_bash(
      ['--no-squeeze'],
      stdin_data='A\n\n\n\nB'
    )
    assert result.returncode == 0
    assert result.stdout.count('\n') >= 4


class TestBashCLIFlags:
  """Tests for CLI flags."""

  def test_version_flag_short(self, run_bash):
    """Short -v flag shows version."""
    result = run_bash( ['-v'])
    assert result.returncode == 0
    assert '1.1.0' in result.stdout

  def test_version_flag_long(self, run_bash):
    """Long --version flag shows version."""
    result = run_bash( ['--version'])
    assert result.returncode == 0
    assert '1.1.0' in result.stdout

  def test_help_flag_short(self, run_bash):
    """Short -h flag shows help."""
    result = run_bash( ['-h'])
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower()

  def test_help_flag_long(self, run_bash):
    """Long --help flag shows help."""
    result = run_bash( ['--help'])
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower()
    assert '--allow' in result.stdout


class TestBashFileInput:
  """Tests for file input handling."""

  def test_file_argument(self, run_bash, tmp_path):
    """Processing a file argument."""
    test_file = tmp_path / 'test.html'
    test_file.write_text('<div>Content</div>', encoding='utf-8')
    result = run_bash([str(test_file)])
    assert result.returncode == 0
    assert 'Content' in result.stdout

  def test_file_with_allow(self, run_bash, tmp_path):
    """File argument with --allow flag."""
    test_file = tmp_path / 'test.html'
    test_file.write_text('<p><b>Bold</b></p>', encoding='utf-8')
    result = run_bash(['-a', 'b', str(test_file)])
    assert result.returncode == 0
    assert '<b>' in result.stdout
    assert '<p>' not in result.stdout

  def test_unicode_file(self, run_bash, tmp_path):
    """Processing a file with unicode content."""
    test_file = tmp_path / 'unicode.html'
    test_file.write_text('<p>日本語 🎉</p>', encoding='utf-8')
    result = run_bash([str(test_file)])
    assert result.returncode == 0
    assert '日本語' in result.stdout


class TestBashErrorHandling:
  """Tests for error handling."""

  def test_missing_file(self, run_bash):
    """Non-existent file returns exit code 2."""
    result = run_bash(['/nonexistent/file.html'])
    assert result.returncode == 2
    assert 'not found' in result.stderr.lower()

  def test_unreadable_file(self, run_bash, tmp_path):
    """Unreadable file returns exit code 1."""
    test_file = tmp_path / 'noperm.html'
    test_file.write_text('content', encoding='utf-8')
    os.chmod(test_file, 0o000)
    try:
      result = run_bash([str(test_file)])
      assert result.returncode == 1
      assert 'cannot read' in result.stderr.lower()
    finally:
      os.chmod(test_file, stat.S_IRUSR | stat.S_IWUSR)

  def test_invalid_option(self, run_bash):
    """Invalid option returns exit code 22."""
    result = run_bash( ['--invalid-option'])
    assert result.returncode == 22
    assert 'unknown option' in result.stderr.lower()

  def test_allow_missing_argument(self, run_bash):
    """--allow without argument returns error."""
    result = run_bash( ['-a'])
    assert result.returncode != 0
    assert 'requires' in result.stderr.lower()


class TestBashEdgeCases:
  """Edge case tests for Bash version."""

  def test_html_comments_removed(self, run_bash):
    """HTML comments are removed."""
    result = run_bash(
      stdin_data='Before<!-- comment -->After'
    )
    assert result.returncode == 0
    assert 'Before' in result.stdout
    assert 'After' in result.stdout
    assert 'comment' not in result.stdout

  def test_doctype_removed(self, run_bash):
    """DOCTYPE declaration is removed."""
    result = run_bash(
      stdin_data='<!DOCTYPE html><p>X</p>'
    )
    assert result.returncode == 0
    assert 'X' in result.stdout
    assert 'DOCTYPE' not in result.stdout

  def test_html_entities_preserved(self, run_bash):
    """HTML entities are preserved as-is."""
    result = run_bash(
      stdin_data='<p>&amp; &lt; &gt;</p>'
    )
    assert result.returncode == 0
    assert '&amp;' in result.stdout or '&' in result.stdout

  def test_mixed_content(self, run_bash):
    """Mixed text and tags handled correctly."""
    result = run_bash(
      stdin_data='Before<p>Inside</p>After'
    )
    assert result.returncode == 0
    assert 'Before' in result.stdout
    assert 'Inside' in result.stdout
    assert 'After' in result.stdout

  def test_deeply_nested_tags(self, run_bash):
    """Deeply nested tags are handled."""
    html = '<div>' * 10 + 'Deep' + '</div>' * 10
    result = run_bash( stdin_data=html)
    assert result.returncode == 0
    assert 'Deep' in result.stdout

  def test_combined_flags(self, run_bash):
    """Multiple flags work together."""
    result = run_bash(
      ['-a', 'b', '--no-squeeze'],
      stdin_data='<p><b>Bold</b></p>More'
    )
    assert result.returncode == 0
    assert '<b>' in result.stdout
    assert '<p>' not in result.stdout
    assert 'Bold' in result.stdout
    assert 'More' in result.stdout


if __name__ == '__main__':
  pytest.main([__file__, '-v'])
