"""One bounded local ComfyUI diagnostic; never promotes creative acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import uuid

LEASE = Path("/home/r4ravi2008/projects/remix-workflow-v3/runs/.gpu-inference-lease.json")


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def save(path, document):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".partial")
    with temporary.open("x") as stream:
        json.dump(document, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def read(path):
    return json.loads(path.read_text())


def measure_models(run, comfy):
    publisher = read(run / "h3-publisher-files-a01.json")
    records = []
    for entry in publisher["selectedFiles"]:
        path = (comfy / "models" / entry["rfilename"]).resolve()
        path.relative_to((comfy / "models").resolve())
        before = path.stat()
        began = time.monotonic()
        measured = digest(path)
        after = path.stat()
        record = {
            "path": str(path), "bytes": after.st_size, "mtimeNs": after.st_mtime_ns,
            "inode": after.st_ino, "sha256": measured,
            "publisherSha256": entry["lfs"]["sha256"],
            "hashSeconds": time.monotonic() - began,
            "pass": measured == entry["lfs"]["sha256"]
                and after.st_size == entry["size"]
                and (before.st_ino, before.st_size, before.st_mtime_ns)
                == (after.st_ino, after.st_size, after.st_mtime_ns),
        }
        records.append(record)
        save(run / "model-hash-progress.json", records)
        print("MODEL_MEASURED", path.name, record["pass"], flush=True)
    if len(records) != 5 or not all(record["pass"] for record in records):
        raise ValueError("The selected five-model set does not match the pinned publisher bytes")
    document = {
        "schema": 1, "state": "model-bytes-verified", "host": socket.gethostname(),
        "repository": publisher["repository"], "revision": publisher["revision"],
        "publisherManifestSha256": digest(run / "h3-publisher-files-a01.json"),
        "models": records, "generationSubmitted": False,
    }
    save(run / "model-bindings.json", document)


def execute(run, comfy):
    sys.path.insert(0, str(run / "helpers"))
    import asset_snapshot
    import comfy_job

    models = read(run / "model-bindings.json")
    if models["state"] != "model-bytes-verified":
        raise ValueError("Model measurement has not passed")
    for model in models["models"]:
        stat = Path(model["path"]).stat()
        if (stat.st_ino, stat.st_size, stat.st_mtime_ns) != (model["inode"], model["bytes"], model["mtimeNs"]):
            raise ValueError("Model inode changed since the full hash measurement")
    plan = read(run / "run.json")
    workflow = read(run / "prepared/workflow.json")
    bindings = read(run / "prepared/bindings.json")
    source = comfy / "input"
    snapshot = read(run / "inputs-from-mac.json")
    asset_snapshot.verify(source, snapshot)
    expected = plan["motionInputSha256"]
    if len(snapshot["files"]) != 1 or snapshot["files"][0]["sha256"] != expected:
        raise ValueError("Transferred conditioning image differs from the frozen Mac input")
    save(run / "inputs.json", snapshot)
    client = comfy_job.Client("http://127.0.0.1:8188")
    queue = client.request("/queue")
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise ValueError("ComfyUI is occupied by another job")
    owner = {"schema": 1, "owner": uuid.uuid4().hex, "pid": os.getpid(),
        "host": socket.gethostname(), "goal": plan["goal"], "run": str(run),
        "job": plan["attempt"], "workflowSha256": asset_snapshot.fingerprint(workflow),
        "startedEpoch": time.time()}
    with LEASE.open("x") as stream:
        json.dump(owner, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    save(run / "resource-owner.json", owner)
    directory = comfy_job.job_directory(run / "jobs", plan["attempt"])
    terminal = False
    deadline = time.time() + plan["runtimeDeadlineSeconds"]
    try:
        try:
            if (directory / "intent.json").exists():
                observation = comfy_job.reconcile(client, directory)
            else:
                observation = comfy_job.submit(client, directory, workflow, snapshot, bindings,
                    source, deadline, 300)
        except Exception:
            if not (directory / "intent.json").exists():
                terminal = True
                raise
            observation = comfy_job.reconcile(client, directory)
        save(run / "progress.json", observation)
        print("MOTION_STATE", json.dumps(observation), flush=True)
        last = observation["state"]
        while True:
            observation = comfy_job.status(client, directory)
            save(run / "progress.json", observation)
            if observation["state"] != last:
                print("MOTION_STATE", json.dumps(observation), flush=True)
                last = observation["state"]
            if last in ("generated-unreviewed", "failed"):
                terminal = True
                break
            if last == "unknown-do-not-resubmit":
                raise ValueError("Owned submission is unresolved; lease retained for reconciliation")
            if time.time() >= deadline:
                prompt = observation["prompt_id"]
                queue = client.request("/queue")
                if any(entry[1] == prompt for entry in queue.get("queue_running", [])):
                    client.request("/interrupt", {})
                elif any(entry[1] == prompt for entry in queue.get("queue_pending", [])):
                    client.request("/queue", {"delete": [prompt]})
                save(run / "deadline.json", {"promptId": prompt, "epoch": time.time(), "queue": queue})
                for _ in range(36):
                    time.sleep(5)
                    observation = comfy_job.status(client, directory)
                    if observation["state"] in ("failed", "generated-unreviewed"):
                        terminal = True
                        break
                raise TimeoutError("Owned motion diagnostic exceeded its deadline")
            time.sleep(5)
        if last == "failed":
            raise ValueError("ComfyUI saved a terminal generation failure")
        result = comfy_job.collect(client, directory, comfy / "output", run / "originals", "17")
        save(run / "result.json", result)
        print("MOTION_COLLECTED", result["sha256"], result["bytes"], flush=True)
    except Exception as error:
        save(run / "error.json", {"error": str(error), "terminalOwnedJob": terminal,
            "automaticResubmission": False, "creativeAccepted": False})
        raise
    finally:
        closeout = {"schema": 1, "terminalOwnedJob": terminal, "owner": owner,
            "watched": False, "heard": False,
            "creativeAccepted": False, "leaseReleased": False}
        if terminal and LEASE.exists() and read(LEASE).get("owner") == owner["owner"]:
            LEASE.unlink()
            closeout["leaseReleased"] = True
        try:
            closeout["queue"] = client.request("/queue")
        except Exception as error:
            closeout["queueReadError"] = str(error)
        save(run / "closeout.json", closeout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("measure-models", "execute"))
    parser.add_argument("run", type=Path)
    parser.add_argument("comfy", type=Path)
    args = parser.parse_args()
    if os.environ.get("HERDR_ENV") != "1":
        raise ValueError("Run this adapter inside the actual Herdr-managed pane")
    run, comfy = args.run.resolve(), args.comfy.resolve()
    if args.operation == "measure-models":
        measure_models(run, comfy)
    else:
        execute(run, comfy)


if __name__ == "__main__":
    main()
