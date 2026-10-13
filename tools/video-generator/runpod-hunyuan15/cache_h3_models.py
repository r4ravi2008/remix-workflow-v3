"""Cache pinned H3 safetensors without renting GPU time; verify publisher SHA256."""
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

FILES = {
    'Comfy-Org/MiniMax-H3': [
        'diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors',
        'text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors',
        'vae/minimax_h3_video_vae_fp16.safetensors',
        'vae/minimax_h3_audio_vae_fp32.safetensors',
    ],
    'lightx2v/Minimax-h3-Turbo': [
        'minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors',
    ],
}


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def download(record, root, max_time=3600):
    target = root / record['destination']
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.stat().st_size == record['bytes'] and digest(target) == record['sha256'], target
        return {**record, 'status': 'HASH_VERIFIED', 'path': str(target)}
    partial = target.with_suffix('.partial')
    print('DOWNLOAD ' + record['destination'], flush=True)
    result = subprocess.run([
        'curl', '--fail', '--location', '--silent', '--show-error',
        '--connect-timeout', '20', '--max-time', str(max_time),
        '--continue-at', '-', '--output', str(partial), record['url'],
    ])
    if result.returncode:
        return {**record, 'status': 'PARTIAL', 'curlExit': result.returncode,
                'downloadedBytes': partial.stat().st_size if partial.exists() else 0}
    assert partial.stat().st_size == record['bytes'], target
    assert digest(partial) == record['sha256'], target
    partial.rename(target)
    print('VERIFIED ' + record['destination'], flush=True)
    return {**record, 'status': 'HASH_VERIFIED', 'path': str(target)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--max-time', type=int, default=3600)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    records = []
    for repo, names in ({} if args.manifest else FILES).items():
        with urllib.request.urlopen(f'https://huggingface.co/api/models/{repo}?blobs=true', timeout=30) as response:
            info = json.load(response)
        for name in names:
            entry = next(item for item in info['siblings'] if item['rfilename'] == name)
            lfs = entry['lfs']
            records.append({
                'repo': repo, 'revision': info['sha'], 'source': name,
                'destination': name if '/' in name else 'loras/' + name,
                'bytes': lfs['size'], 'sha256': lfs['sha256'],
                'url': f"https://huggingface.co/{repo}/resolve/{info['sha']}/{name}?download=true",
            })
    if args.manifest:
        records = json.loads(args.manifest.read_text())
    print('TOTAL_BYTES ' + str(sum(item['bytes'] for item in records)), flush=True)
    (args.cache / 'download-plan.json').write_text(json.dumps(records, indent=2))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(download, item, args.cache, args.max_time) for item in records]
        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            (args.cache / 'download-status.json').write_text(json.dumps(results, indent=2))
    if any(item['status'] != 'HASH_VERIFIED' for item in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
