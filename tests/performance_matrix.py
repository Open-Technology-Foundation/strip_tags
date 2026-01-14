#!/usr/bin/env python3
"""Performance matrix comparing Python and Bash strip_tags utilities."""
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple


class TestCase(NamedTuple):
  name: str
  html: str
  args: list[str] = []
  category: str = ""


class Result(NamedTuple):
  time_ms: float
  output: str
  exit_code: int


SCRIPT_DIR = Path(__file__).parent.parent
PYTHON_SCRIPT = SCRIPT_DIR / 'strip_tags.py'
BASH_SCRIPT = SCRIPT_DIR / 'html.strip-tags'
REAL_HTML_PATH = Path('/tmp/test_page.html')

# Number of iterations for timing
ITERATIONS = 5


def load_real_html() -> str:
  """Load the real-world HTML from okusiassociates.com."""
  if REAL_HTML_PATH.exists():
    return REAL_HTML_PATH.read_text(encoding='utf-8')
  return "<p>Real HTML not available</p>"


def create_test_cases() -> list[TestCase]:
  """Create comprehensive test cases."""
  real_html = load_real_html()

  return [
    # Category 1: Basic HTML
    TestCase("simple_tag", "<p>Hello</p>", category="Basic"),
    TestCase("nested_tags", "<div><p><span>Text</span></p></div>", category="Basic"),
    TestCase("self_closing", "Text<br/>more<hr/>end", category="Basic"),
    TestCase("with_attrs", '<a href="url" class="link" data-id="1">Link</a>', category="Basic"),

    # Category 2: Script/Style Blocks
    TestCase("inline_script", "<script>var x=1;</script>Text", category="Script/Style"),
    TestCase("script_with_lt", "<script>if(x<5){alert(1)}</script>OK", category="Script/Style"),
    TestCase("style_block", "<style>body{color:red}</style>Text", category="Script/Style"),
    TestCase("multi_script", "<script>a</script>X<script>b</script>Y", category="Script/Style"),

    # Category 3: Complex Structures
    TestCase("multiline_tag", "<div\n  class=\"foo\">\nHello\n</div>", category="Complex"),
    TestCase("deeply_nested", "<div>" * 15 + "Deep" + "</div>" * 15, category="Complex"),
    TestCase("mixed_content", "Before<p>Inside</p>After", category="Complex"),
    TestCase("unicode", "<p>日本語 🎉 émojis</p>", category="Complex"),

    # Category 4: Edge Cases
    TestCase("html_comment", "Before<!-- comment -->After", category="Edge"),
    TestCase("doctype", "<!DOCTYPE html><html><body>X</body></html>", category="Edge"),
    TestCase("malformed", "<p>Unclosed<div>mixed</p></div>", category="Edge"),
    TestCase("entities", "<p>&amp; &lt; &gt; &nbsp;</p>", category="Edge"),

    # Category 5: Allowed Tags Mode
    TestCase("allow_single", "<p><b>Bold</b></p>", ["-a", "b"], category="Allow"),
    TestCase("allow_multi", "<div><p>Text</p><span>More</span></div>", ["-a", "p,div"], category="Allow"),
    TestCase("allow_namespace", "<svg:rect width=\"100\"/><p>Text</p>", ["-a", "svg:rect"], category="Allow"),

    # Category 6: Real-World
    TestCase("real_full", real_html, category="Real-World"),
    TestCase("real_allow", real_html, ["-a", "p,h1,h2,h3,a"], category="Real-World"),
  ]


def run_python(html: str, args: list[str]) -> Result:
  """Run Python strip_tags and measure time."""
  cmd = [sys.executable, str(PYTHON_SCRIPT)] + args

  start = time.perf_counter()
  for _ in range(ITERATIONS):
    result = subprocess.run(
      cmd,
      input=html,
      capture_output=True,
      text=True
    )
  elapsed = (time.perf_counter() - start) / ITERATIONS * 1000

  return Result(elapsed, result.stdout, result.returncode)


def run_bash(html: str, args: list[str]) -> Result:
  """Run Bash html.strip-tags and measure time."""
  cmd = [str(BASH_SCRIPT)] + args

  start = time.perf_counter()
  for _ in range(ITERATIONS):
    result = subprocess.run(
      cmd,
      input=html,
      capture_output=True,
      text=True
    )
  elapsed = (time.perf_counter() - start) / ITERATIONS * 1000

  return Result(elapsed, result.stdout, result.returncode)


def compare_outputs(py_out: str, bash_out: str) -> tuple[bool, str]:
  """Compare outputs and return match status and notes."""
  py_clean = py_out.strip()
  bash_clean = bash_out.strip()

  if py_clean == bash_clean:
    return True, ""

  # Known differences
  notes = []

  # Check if difference is script/style content
  if "var " in py_clean and "var " not in bash_clean:
    notes.append("Bash removes script content")
  if "color:" in py_clean and "color:" not in bash_clean:
    notes.append("Bash removes style content")

  # Check comment handling
  if "<!--" in py_clean and "<!--" not in bash_clean:
    notes.append("Bash removes comments")

  # Check DOCTYPE
  if "DOCTYPE" in py_clean and "DOCTYPE" not in bash_clean:
    notes.append("Bash removes DOCTYPE")

  if notes:
    return False, "; ".join(notes)

  # Length difference
  len_diff = len(py_clean) - len(bash_clean)
  if abs(len_diff) > 10:
    return False, f"Length diff: {len_diff:+d}"

  return False, "Minor diff"


def format_size(size: int) -> str:
  """Format byte size."""
  if size >= 1024:
    return f"{size/1024:.1f}K"
  return str(size)


def run_performance_matrix():
  """Run all tests and generate performance matrix."""
  test_cases = create_test_cases()

  print("# Performance Matrix: Python vs Bash strip_tags\n")
  print(f"Test iterations: {ITERATIONS}")
  print(f"Real HTML size: {format_size(len(load_real_html()))} bytes")
  print()

  # Results by category
  categories: dict[str, list] = {}

  for tc in test_cases:
    py_result = run_python(tc.html, tc.args)
    bash_result = run_bash(tc.html, tc.args)

    match, notes = compare_outputs(py_result.output, bash_result.output)
    speedup = py_result.time_ms / bash_result.time_ms if bash_result.time_ms > 0 else 0

    row = {
      'name': tc.name,
      'py_ms': py_result.time_ms,
      'bash_ms': bash_result.time_ms,
      'speedup': speedup,
      'match': match,
      'notes': notes,
      'py_size': len(py_result.output),
      'bash_size': len(bash_result.output),
    }

    if tc.category not in categories:
      categories[tc.category] = []
    categories[tc.category].append(row)

  # Print results by category
  for category, rows in categories.items():
    print(f"## {category}\n")
    print("| Test Case | Python (ms) | Bash (ms) | Speedup | Match | Py Size | Bash Size | Notes |")
    print("|-----------|-------------|-----------|---------|-------|---------|-----------|-------|")

    for r in rows:
      match_str = "Yes" if r['match'] else "No"
      print(f"| {r['name']:<17} | {r['py_ms']:>11.1f} | {r['bash_ms']:>9.1f} | {r['speedup']:>6.1f}x | {match_str:<5} | {format_size(r['py_size']):>7} | {format_size(r['bash_size']):>9} | {r['notes']} |")

    print()

  # Summary statistics
  all_rows = [r for rows in categories.values() for r in rows]
  avg_py = sum(r['py_ms'] for r in all_rows) / len(all_rows)
  avg_bash = sum(r['bash_ms'] for r in all_rows) / len(all_rows)
  avg_speedup = avg_py / avg_bash if avg_bash > 0 else 0
  match_count = sum(1 for r in all_rows if r['match'])

  print("## Summary\n")
  print(f"- **Total tests**: {len(all_rows)}")
  print(f"- **Average Python time**: {avg_py:.1f} ms")
  print(f"- **Average Bash time**: {avg_bash:.1f} ms")
  print(f"- **Average speedup**: {avg_speedup:.1f}x (Bash faster)")
  print(f"- **Output matches**: {match_count}/{len(all_rows)} ({100*match_count/len(all_rows):.0f}%)")
  print()

  print("## Notes\n")
  print("- **Speedup**: How many times faster Bash is compared to Python")
  print("- **Match**: Whether outputs are identical after stripping whitespace")
  print("- Python preserves script/style content, comments, DOCTYPE")
  print("- Bash removes script/style blocks entirely (more aggressive)")
  print("- Both handle basic HTML tag stripping identically")


if __name__ == '__main__':
  run_performance_matrix()
