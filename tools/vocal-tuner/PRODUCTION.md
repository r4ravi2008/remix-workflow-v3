# Production Readiness

This tool is production-ready for the repository's offline acapella pitch-correction workflow when the verification gate below passes and the input is a clean monophonic vocal.

It is not a legal or technical clone of Antares Auto-Tune, and it does not replace commercial DAW tooling for manual note editing. The supported production target is deterministic CLI rendering for remix pipeline vocals.

## Release Gate

Run this before using a build in the pipeline:

```bash
cd tools/vocal-tuner
./verify.sh
```

The gate runs:

- `cargo fmt --check`
- `cargo test`
- `cargo clippy -- -D warnings`
- `cargo run -- --help`

## Runtime Gate

For automated renders, use:

```bash
vocal-tuner \
  --input vocal.wav \
  --output vocal-tuned.wav \
  --key A \
  --scale minor \
  --preset pop \
  --report vocal-tuned-report.json \
  --fail-on-warnings
```

Review the JSON report before release. Important fields:

- `voiced_frames`: frames confidently corrected as pitched vocal
- `protected_frames`: attacks, consonants, or noisy phonemes intentionally left alone
- `low_confidence_frames`: frames rejected by pitch confidence gating
- `average_correction_cents` and `max_correction_cents`: correction intensity
- `peak`, `rms`, and `clipped_samples`: output level safety
- `warnings`: machine-readable quality concerns

## Input Contract

Best results require:

- isolated monophonic vocal or acapella
- minimal bleed, reverb, and backing vocals
- a known target key and scale
- manual listening review for release candidates

Use `--mix`, `--humanize`, `--retune-speed`, `--transient-protection`, and `--consonant-protection` to reduce artifacts on expressive or noisy recordings.

