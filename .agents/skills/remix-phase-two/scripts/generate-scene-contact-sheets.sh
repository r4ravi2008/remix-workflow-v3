#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <video> <resolve-scenes.json> <output-dir>" >&2
  exit 64
fi

video_path=$1
manifest_path=$2
output_dir=$3

for command_name in ffmpeg ffprobe jq magick; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Required command not found: $command_name" >&2
    exit 69
  fi
done

if [[ ! -f "$video_path" ]]; then
  echo "Video not found: $video_path" >&2
  exit 66
fi

if [[ ! -f "$manifest_path" ]]; then
  echo "Scene manifest not found: $manifest_path" >&2
  exit 66
fi

if ! jq -e '.scenes | type == "array" and length > 0 and all(.[]; (.id | type == "string") and (.start | type == "number") and (.end | type == "number") and .end > .start)' "$manifest_path" >/dev/null; then
  echo "Manifest must contain non-empty scenes with string id and numeric start/end where end > start" >&2
  exit 65
fi

video_duration=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "$video_path" | head -n 1)
if [[ -z "$video_duration" || "$video_duration" == "N/A" ]]; then
  echo "Could not read a finite video-stream duration from: $video_path" >&2
  exit 65
fi
if ! jq -en --argjson duration "$video_duration" --slurpfile manifest "$manifest_path" '
  $manifest[0].scenes as $scenes
  | ($scenes[0].start <= 0.05)
    and ($scenes[-1].end >= ($duration - 0.05))
    and all($scenes[]; .start >= 0 and .end <= ($duration + 0.05))
    and all(range(1; $scenes | length);
      ($scenes[.].start >= ($scenes[. - 1].end - 0.05))
      and ($scenes[.].start <= ($scenes[. - 1].end + 0.05))
    )
' >/dev/null; then
  echo "Scenes must be ordered, cover the full ${video_duration}s video, and contain no gap or overlap larger than 0.05s" >&2
  exit 65
fi

mkdir -p "$output_dir"
find "$output_dir" -maxdepth 1 -type f \( -name 'contact-sheet-*.jpg' -o -name 'contact-sheet-index.json' \) -delete
scratch_dir=$(mktemp -d "${TMPDIR:-/tmp}/vertical-scene-review.XXXXXX")
trap 'rm -rf "$scratch_dir"' EXIT

index_json="$output_dir/contact-sheet-index.json"
jq -n --arg source "$video_path" --arg manifest "$manifest_path" \
  '{sourceVideo: $source, sceneManifest: $manifest, samples: [], pages: []}' > "$index_json"

sample_number=0
while IFS=$'\t' read -r scene_id start end label focal_point; do
  duration=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')
  for sample_name in head middle tail; do
    case "$sample_name" in
      head) fraction=0.1 ;;
      middle) fraction=0.5 ;;
      tail) fraction=0.9 ;;
    esac
    timestamp=$(awk -v start="$start" -v duration="$duration" -v fraction="$fraction" 'BEGIN { printf "%.3f", start + duration * fraction }')
    sample_number=$((sample_number + 1))
    sample_file=$(printf '%s/sample-%04d.png' "$scratch_dir" "$sample_number")
    label_file=$(printf '%s/label-%04d.png' "$scratch_dir" "$sample_number")
    annotated_file=$(printf '%s/annotated-%04d.jpg' "$scratch_dir" "$sample_number")
    caption="${scene_id} | ${sample_name} | ${timestamp}s
${label:-unlabeled} | focal: ${focal_point:-unspecified}"

    ffmpeg -hide_banner -loglevel error -ss "$timestamp" -i "$video_path" -frames:v 1 \
      -vf 'scale=270:480:force_original_aspect_ratio=decrease,pad=270:480:(ow-iw)/2:(oh-ih)/2:black' \
      -y "$sample_file"
    magick -size 270x64 -background '#101014' -fill white -gravity center \
      -pointsize 12 caption:"$caption" "$label_file"
    magick "$sample_file" "$label_file" -append "$annotated_file"

    next_index=$(mktemp "${TMPDIR:-/tmp}/scene-index.XXXXXX")
    jq --arg sceneId "$scene_id" --arg sample "$sample_name" --argjson timestamp "$timestamp" \
      --arg label "$label" --arg focalPoint "$focal_point" --argjson sampleNumber "$sample_number" \
      '.samples += [{sampleNumber: $sampleNumber, sceneId: $sceneId, sample: $sample, timestamp: $timestamp, label: $label, focalPoint: $focalPoint}]' \
      "$index_json" > "$next_index"
    mv "$next_index" "$index_json"
  done
done < <(jq -r '.scenes[] | [.id, (.start|tostring), (.end|tostring), (.label // "" | gsub("[\\t\\r\\n]"; " ")), (.focalPoint // "" | gsub("[\\t\\r\\n]"; " "))] | @tsv' "$manifest_path")

mapfile_compat=()
while IFS= read -r image_path; do
  mapfile_compat+=("$image_path")
done < <(find "$scratch_dir" -name 'annotated-*.jpg' -print | sort)

page_size=12
page_number=0
for ((offset = 0; offset < ${#mapfile_compat[@]}; offset += page_size)); do
  page_number=$((page_number + 1))
  page_file=$(printf '%s/contact-sheet-%02d.jpg' "$output_dir" "$page_number")
  page_images=("${mapfile_compat[@]:offset:page_size}")
  magick montage "${page_images[@]}" -tile 3x4 -geometry +12+12 -background '#08080b' "$page_file"

  next_index=$(mktemp "${TMPDIR:-/tmp}/scene-index.XXXXXX")
  jq --arg file "$(basename "$page_file")" --argjson firstSample "$((offset + 1))" \
    --argjson lastSample "$((offset + ${#page_images[@]}))" \
    '.pages += [{file: $file, firstSample: $firstSample, lastSample: $lastSample}]' \
    "$index_json" > "$next_index"
  mv "$next_index" "$index_json"
done

next_index=$(mktemp "${TMPDIR:-/tmp}/scene-index.XXXXXX")
jq '.samples |= map(. + {page: ((((.sampleNumber - 1) / 12) | floor) + 1), cell: (((.sampleNumber - 1) % 12) + 1)})' \
  "$index_json" > "$next_index"
mv "$next_index" "$index_json"

echo "Generated ${page_number} contact sheet page(s) covering $((sample_number / 3)) scene(s) in $output_dir"
