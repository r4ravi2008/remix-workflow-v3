"""Reopen a declared native codec fixture; never promotes creative acceptance."""
import argparse
import hashlib
import json
import pathlib
import subprocess

import numpy as np
from PIL import Image, ImageOps


def digest(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=pathlib.Path)
    parser.add_argument("movie", type=pathlib.Path)
    parser.add_argument("binary", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--artifact-receipt",type=pathlib.Path)
    parser.add_argument("--encoder-binary",type=pathlib.Path)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    fixture = json.loads(args.fixture.read_text())
    observations = {}

    def run(name, command):
        result = subprocess.run(command, capture_output=True, text=True, timeout=65)
        (args.output / (name + ".stdout")).write_text(result.stdout)
        (args.output / (name + ".stderr")).write_text(result.stderr)
        observations[name + "Exit"] = result.returncode
        if result.returncode:
            raise RuntimeError(name + " failed: " + result.stdout + result.stderr)
        return json.loads(result.stdout)

    video_command=[str(args.binary), str(args.movie), str(args.output / "first.png"), str(fixture["frames"] + 1)]
    if "videoRanges" in fixture:
        video_command=[str(args.binary),"sequence",str(args.movie),str(args.output / "output-frames"),str(fixture["frames"]+1)]
    video = run("video",video_command)
    source = run("source-audio", [str(args.binary), "pcm", fixture["sourceAudio"], str(args.output / "source.f32le"), str(fixture["audioSamples"])])
    output = run("output-audio", [str(args.binary), "pcm", str(args.movie), str(args.output / "output.f32le"), str(fixture["audioSamples"] + 2000)])
    boxes = run("container", ["python3", str(pathlib.Path(__file__).with_name("inspect_mp4.py")), str(args.movie)])
    frames = video["decodedFrames"]
    checks = {
        "videoFrameCount": len(frames) == fixture["frames"],
        "everyVideoPts": all(f["pts"]["value"] * fixture["fps"] == i * f["pts"]["timescale"] for i, f in enumerate(frames)),
        "videoReaderCompleted": video["readerStatusAtStop"] == "AVAssetReaderStatus(2)",
        "dimensions": all(f["width"] == fixture["width"] and f["height"] == fixture["height"] for f in frames),
        "decodedAudioExtent": output["sampleFrames"] == fixture["audioSamples"],
        "audioReaderCompleted": output["reachedEnd"],
        "audioFormat": output["sampleRate"] == 48000 and output["channels"] == 2,
    }
    video_track = next(t for t in boxes["tracks"] if t["handler"] == "vide")
    audio_track = next(t for t in boxes["tracks"] if t["handler"] == "soun")
    checks["independentSampleTable"] = video_track["sampleCount"] == fixture["frames"] and video_track["timingTicks"] * fixture["fps"] == fixture["frames"] * video_track["timescale"]
    checks["nativeCodecProfile"] = video_track["codec"] == "avc1" and audio_track["codec"] == "mp4a"
    frame_metrics=[]
    if "videoRanges" in fixture:
        source_extent=max(r["sourceStart"]+r["length"] for r in fixture["videoRanges"])
        source_video=run("source-video",[str(args.binary),"sequence",fixture["sourceVideo"],str(args.output / "source-frames"),str(source_extent)])
        checks["sourceFrameExtent"] = len(source_video["decodedFrames"])==source_extent
        covered=[]
        for r in fixture["videoRanges"]:
            for local in range(r["length"]):
                timeline_frame=r["timelineStart"]+local
                source_frame=r["sourceStart"]+local
                covered.append(timeline_frame)
                with Image.open(args.output/"source-frames"/f"frame-{source_frame:06}.png") as a, Image.open(args.output/"output-frames"/f"frame-{timeline_frame:06}.png") as b:
                    if "framing" in r:
                        framing=r["framing"]
                        crop=framing["crop"]
                        a=a.convert("RGB").crop((crop["x"]*a.width,crop["y"]*a.height,(crop["x"]+crop["width"])*a.width,(crop["y"]+crop["height"])*a.height))
                        canvas=(fixture["width"],fixture["height"])
                        if framing["fit"]=="contain":
                            fitted=ImageOps.contain(a,canvas,Image.Resampling.BILINEAR)
                            a=Image.new("RGB",canvas)
                            a.paste(fitted,((a.width-fitted.width)//2,(a.height-fitted.height)//2))
                        elif framing["fit"]=="cover":
                            a=ImageOps.fit(a,canvas,Image.Resampling.BILINEAR)
                        elif framing["fit"]=="stretch":
                            a=a.resize(canvas,Image.Resampling.BILINEAR)
                        else:
                            raise ValueError("Unknown fixture framing")
                    x=np.asarray(a,dtype=np.float64)[:,:,:3]
                    y=np.asarray(b,dtype=np.float64)[:,:,:3]
                mse=float(np.mean((x-y)**2))
                psnr=10*float(np.log10(255*255/max(mse,1e-12)))
                frame_metrics.append({"timelineFrame":timeline_frame,"sourcePresentationOrdinal":source_frame,"psnrDb":psnr})
        checks["sourceMapCoverage"] = sorted(covered)==list(range(fixture["frames"]))
        checks["everyFrameMatchesDeclaredSource"] = all(m["psnrDb"]>=fixture["expectationsBeforeEncode"]["minimumEveryFramePsnrDb"] for m in frame_metrics)
    x = np.fromfile(args.output / "source.f32le", dtype="<f4").reshape(-1, 2).astype("float64")
    y = np.fromfile(args.output / "output.f32le", dtype="<f4").reshape(-1, 2).astype("float64")
    metrics = []
    if x.shape != y.shape:
        checks["waveformExtent"] = False
    else:
        checks["waveformExtent"] = True
        for channel in range(2):
            a, b = x[:, channel], y[:, channel]
            candidates = []
            for lag in range(-1024, 1025):
                n = len(a) - abs(lag)
                aa = a[max(0, lag):max(0, lag) + n]
                bb = b[max(0, -lag):max(0, -lag) + n]
                candidates.append(float(np.dot(aa, bb) / (np.linalg.norm(aa) * np.linalg.norm(bb))))
            best_lag = int(np.argmax(candidates)) - 1024
            correlation = float(np.corrcoef(a, b)[0, 1])
            metrics.append({"channel": channel, "bestLagSamples": best_lag, "correlationAtZero": correlation, "sourceRms": float(np.sqrt(np.mean(a * a))), "outputRms": float(np.sqrt(np.mean(b * b))), "errorRms": float(np.sqrt(np.mean((a - b) ** 2)))})
            checks["channel" + str(channel) + "Alignment"] = best_lag == fixture["expectationsBeforeEncode"]["audioLagSamples"]
            checks["channel" + str(channel) + "Correlation"] = correlation >= fixture["expectationsBeforeEncode"]["minimumAudioCorrelation"]
    link = subprocess.run(["otool", "-L", str(args.binary)], capture_output=True, text=True, timeout=10)
    (args.output / "native-links.txt").write_text(link.stdout + link.stderr)
    checks["noLibavLink"] = link.returncode == 0 and not any(v in link.stdout.lower() for v in ["libavcodec", "libavformat", "libavutil", "ffmpeg"])
    binding=None
    if args.artifact_receipt:
        response=json.loads(args.artifact_receipt.read_text())["result"]
        receipt=response["receipt"]["artifact"] if "receipt" in response else response
        checks["artifactReceiptBytes"] = receipt["output_sha256"]==digest(args.movie) and receipt["output_bytes"]==args.movie.stat().st_size and pathlib.Path(receipt["output_path"]).resolve()==args.movie.resolve()
        checks["artifactReceiptClock"] = receipt["technical"]["video_frames"]==fixture["frames"] and receipt["technical"]["audio_sample_frames"]==fixture["audioSamples"]
        checks["encoderBinaryIdentity"] = bool(args.encoder_binary) and digest(args.encoder_binary)==receipt["renderer"]["executable_sha256"]
        checks["perceptualClaimsRemainPending"] = all(k not in receipt for k in ["watched","heard","creative_accepted"]) if receipt["schema"]==2 else not any(receipt[k] for k in ["watched","heard","creative_accepted"])
        if receipt["schema"]==2:
            receipt_id=response["receipt"]["receipt_id"]
            immutable=args.movie.parent.parent / "receipts" / (receipt_id+".json")
            checks["immutableReceiptIdentity"] = immutable.is_file() and digest(immutable)==receipt_id and json.loads(immutable.read_text())==receipt
            verification_id=response["verification_id"]
            verification=args.movie.parent.parent / "receipts" / (verification_id+".json")
            checks["freshVerificationIdentity"] = verification.is_file() and digest(verification)==verification_id and response["verification"]["artifact_receipt"]==receipt_id and response["verification"]["output_sha256"]==digest(args.movie)
        binding={"project":receipt["project"],"revision":receipt["revision"],"planId":receipt["plan_id"],"receiptSha256":digest(args.artifact_receipt),"encoderBinarySha256":receipt["renderer"]["executable_sha256"]}
    report = {"state": "technical-roundtrip-pass" if all(checks.values()) else "technical-roundtrip-fail", "checks": checks, "observations": observations, "videoFrames": len(frames), "decodedAudioFrames": output["sampleFrames"], "encodedAudioTicks": audio_track["timingTicks"], "nativeReaderTrimmedTicks": audio_track["timingTicks"] - output["sampleFrames"], "waveform": metrics, "fixtureSha256": digest(args.fixture), "binarySha256": digest(args.binary), "verifierSha256": digest(__file__), "sourceVideoSha256": digest(fixture["sourceVideo"]), "sourceAudioSha256": digest(fixture["sourceAudio"]), "outputSha256": digest(args.movie), "outputBytes": args.movie.stat().st_size, "watched": False, "heard": False, "creativeAccepted": False, "productExport": bool(binding),"artifactBinding":binding}
    report["sourceFrameComparisons"]=frame_metrics
    (args.output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, allow_nan=False))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
