#!/bin/zsh

set -euo pipefail

if (( $# != 2 )); then
  print -u2 "usage: $0 <local-thumbnail> <live-thumbnail-url>"
  exit 2
fi

local_thumbnail="$1"
live_url="$2"

[[ -f "$local_thumbnail" ]] || {
  print -u2 "local thumbnail not found: $local_thumbnail"
  exit 2
}

command -v magick >/dev/null || {
  print -u2 "ImageMagick is required"
  exit 2
}

command -v compare >/dev/null || {
  print -u2 "ImageMagick compare is required"
  exit 2
}

command -v curl >/dev/null || {
  print -u2 "curl is required"
  exit 2
}

metric=$(compare -metric RMSE \
  <(magick "$local_thumbnail" -resize '320x180!' miff:-) \
  <(curl -fsSL "$live_url" | magick - miff:-) \
  null: 2>&1 || true)

normalized=$(print -r -- "$metric" | sed -E 's/.*\(([0-9.]+)\).*/\1/')

if [[ -z "$normalized" || "$normalized" == "$metric" ]]; then
  print -u2 "could not parse RMSE: $metric"
  exit 2
fi

print -r -- "RMSE $metric"

awk -v value="$normalized" 'BEGIN { exit !(value <= 0.06) }' || {
  print -u2 "thumbnail mismatch: normalized RMSE $normalized exceeds 0.06"
  exit 1
}

print -r -- "MATCH normalized_RMSE=$normalized"
