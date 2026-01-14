#!/usr/bin/env bash
# strip_tags.bash - Strip HTML tags from files or stdin (pure Bash)
# A pure Bash alternative to the Python strip_tags utility.
# Use when Python is not available on target systems.
set -euo pipefail
shopt -s inherit_errexit shift_verbose extglob nullglob

declare -r VERSION=1.1.0
#shellcheck disable=SC2155
declare -r SCRIPT_PATH=$(realpath -- "$0")
declare -r SCRIPT_NAME=${SCRIPT_PATH##*/}

# Global state
declare -a ALLOWED_TAGS=()
declare -i SQUEEZE=1
declare -- INPUT_FILE=''

#-----------------------------------------------------------
# Utility functions
#-----------------------------------------------------------

error() { printf '%s: %s\n' "$SCRIPT_NAME" "$*" >&2; }

die() { (($# < 2)) || error "${@:2}"; exit "${1:-0}"; }

noarg() { (($# > 1)) || die 2 "Option ${1@Q} requires an argument"; }

#-----------------------------------------------------------
# Helper functions
#-----------------------------------------------------------

is_allowed() {
  local -- tag=$1
  local -- allowed
  for allowed in "${ALLOWED_TAGS[@]}"; do
    #shellcheck disable=SC2015
    [[ $tag == "$allowed" ]] && return 0 ||:
  done
  return 1
}

parse_allowed_tags() {
  local -- IFS=','
  local -a tags=()
  read -ra tags <<< "$1"
  local -- tag
  for tag in "${tags[@]}"; do
    # Trim whitespace and lowercase
    tag="${tag#"${tag%%[![:space:]]*}"}"
    tag="${tag%"${tag##*[![:space:]]}"}"
    [[ -z $tag ]] || ALLOWED_TAGS+=("${tag,,}")
  done
}

read_input() {
  if [[ -n $INPUT_FILE ]]; then
    [[ -f $INPUT_FILE ]] || die 2 "File ${INPUT_FILE@Q} not found"
    [[ -r $INPUT_FILE ]] || die 1 "Cannot read ${INPUT_FILE@Q}"
    cat -- "$INPUT_FILE"
  else
    cat
  fi
}

remove_script_style() {
  # Remove <script>...</script> and <style>...</style> blocks entirely
  # Uses sed -z (GNU sed) for multi-line; loop removes multiple blocks
  # Pattern matches any content that isn't the closing tag
  sed -zE '
    :a; s/<script[^>]*>([^<]|<[^\/]|<\/[^s]|<\/s[^c]|<\/sc[^r]|<\/scr[^i]|<\/scri[^p]|<\/scrip[^t])*<\/script>//Ii; ta
    :b; s/<style[^>]*>([^<]|<[^\/]|<\/[^s]|<\/s[^t]|<\/st[^y]|<\/sty[^l]|<\/styl[^e])*<\/style>//Ii; tb
  '
}

#-----------------------------------------------------------
# Core business logic
#-----------------------------------------------------------

strip_tags_selective() {
  local -- content=$1
  local -- line tag_name

  # First, collapse multi-line tags by replacing newlines inside tags with spaces
  # Use null-byte swap to handle newlines, then fix tags that span lines
  content=$(printf '%s' "$content" | tr '\n' '\0' | sed -E 's/<([^>]*)\x00([^>]*)>/<\1 \2>/g' | tr '\0' '\n')

  # Normalize: put tags on separate lines for processing
  content=$(printf '%s' "$content" | sed -e 's/</\n</g' -e 's/>/>\n/g')

  while IFS= read -r line || [[ -n $line ]]; do
    if [[ $line =~ ^\</?([a-zA-Z][a-zA-Z0-9:-]*) ]]; then
      tag_name="${BASH_REMATCH[1],,}"
      if is_allowed "$tag_name"; then
        printf '%s' "$line"
      fi
    else
      printf '%s' "$line"
    fi
  done <<< "$content"
}

strip_tags() {
  local -- content=$1

  if ((${#ALLOWED_TAGS[@]} == 0)); then
    # Simple case: remove all tags (handles multi-line via null-byte swap)
    printf '%s' "$content" | tr '\n' '\0' | sed 's/<[^>]*>//g' | tr '\0' '\n'
  else
    # Complex case: preserve allowed tags
    strip_tags_selective "$content"
  fi
}

squeeze_text() {
  local -- text=$1
  # Collapse 3+ consecutive newlines to 2, then strip leading/trailing whitespace
  printf '%s' "$text" |
    sed -e ':a' -e 'N' -e '$!ba' -e 's/\n\{3,\}/\n\n/g' |
    sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

#-----------------------------------------------------------
# Interface functions
#-----------------------------------------------------------

show_help() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] [FILE]

Strip HTML tags from a file or stdin.

Pure Bash alternative to the Python strip_tags utility.
Use when Python is not available on target systems.

Options:
  -a, --allow TAGS   Comma-separated list of tags to preserve
  --no-squeeze       Disable collapsing of repeated blank lines
  -v, --version      Show version and exit
  -h, --help         Show this help and exit

Examples:
  echo "<p>Hello</p>" | $SCRIPT_NAME
  $SCRIPT_NAME input.html --allow a,p,div
  $SCRIPT_NAME input.html --no-squeeze
  curl -s https://example.com | $SCRIPT_NAME -a h1,p

Notes:
  - Script and style blocks are removed entirely (including content)
  - Multi-line tags are handled correctly
  - HTML entities (e.g., &amp;) are preserved as-is
  - Namespaced tags (e.g., svg:rect) supported in --allow
  - For complex HTML (e.g., > in attributes), use Python version
EOF
}

parse_args() {
  while (($#)); do
    case $1 in
      -a|--allow)
        noarg "$@"
        shift
        parse_allowed_tags "$1"
        ;;
      --no-squeeze)
        SQUEEZE=0
        ;;
      -v|--version)
        echo "$SCRIPT_NAME $VERSION"
        exit 0
        ;;
      -h|--help)
        show_help
        exit 0
        ;;
      --)
        shift
        INPUT_FILE=${1:-}
        break
        ;;
      -*)
        die 22 "Unknown option ${1@Q}"
        ;;
      *)
        INPUT_FILE=$1
        ;;
    esac
    shift
  done
  readonly -- ALLOWED_TAGS SQUEEZE INPUT_FILE
}

#-----------------------------------------------------------
# Main orchestration
#-----------------------------------------------------------

main() {
  parse_args "$@"

  local -- content
  content=$(read_input)
  content=$(printf '%s' "$content" | remove_script_style)
  content=$(strip_tags "$content")
  ((SQUEEZE==0)) || content=$(squeeze_text "$content")

  printf '%s\n' "$content"
}

main "$@"
#fin
