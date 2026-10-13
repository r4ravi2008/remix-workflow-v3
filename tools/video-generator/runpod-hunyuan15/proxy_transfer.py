"""Copy existing files through RunPod's PTY-only SSH proxy without a public server."""
import argparse
import base64
import hashlib
import io
import shlex
import subprocess
import tarfile
import uuid
from pathlib import Path


def session(user, identity):
    proc = subprocess.Popen(
        ['ssh', '-tt', '-i', identity, '-o', 'BatchMode=yes',
         '-o', 'ConnectTimeout=15', '-o', 'ServerAliveInterval=20',
         user + '@ssh.runpod.io'], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    marker = 'READY_' + uuid.uuid4().hex
    proc.stdin.write("stty -echo; unset PROMPT_COMMAND; PS1=''; PS2=''; bind 'set enable-bracketed-paste off'; printf '\\n%s\\n' " + marker + '\n')
    proc.stdin.flush()
    for line in proc.stdout:
        if line.strip() == marker:
            return proc
    raise RuntimeError('Proxy closed before transfer handshake')


def run_command(user, identity, command):
    marker = 'STATUS_' + uuid.uuid4().hex
    proc = session(user, identity)
    output, _ = proc.communicate(command + "\ncode=$?; printf '\\n%s:%s\\n' "
                                 + marker + ' "$code"; exit "$code"\n', timeout=90)
    body, status = output.rsplit(marker + ':', 1)
    return body.strip(), int(status.splitlines()[0].strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', required=True)
    parser.add_argument('--identity', required=True)
    parser.add_argument('--root', default='/workspace/urvashi-h3')
    parser.add_argument('--file', action='append', default=[], help='existing source=relative target')
    parser.add_argument('--run', help='Run a command after copying files')
    parser.add_argument('--get', action='append', default=[], help='remote absolute file=local relative file')
    parser.add_argument('--download-dir', type=Path)
    args = parser.parse_args()
    assert args.file or args.run or args.get
    assert args.root.startswith('/workspace/')
    payload = ''
    upload = None
    if args.file:
        archive = io.BytesIO()
        names = set()
        with tarfile.open(fileobj=archive, mode='w:gz') as bundle:
            for value in args.file:
                source, name = value.rsplit('=', 1)
                assert Path(source).is_file()
                assert not Path(name).is_absolute() and '..' not in Path(name).parts
                assert name not in names
                names.add(name)
                bundle.add(source, arcname=name, recursive=False)
        upload = base64.b64encode(archive.getvalue()).decode()
    if args.run:
        payload += args.run + '\n'
    download_start = 'ARCHIVE_' + uuid.uuid4().hex
    download_end = 'END_' + uuid.uuid4().hex
    wanted = []
    if args.get:
        assert args.download_dir and not args.run
        for value in args.get:
            remote, name = value.rsplit('=', 1)
            assert remote.startswith('/workspace/') and '..' not in Path(remote).parts
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            wanted.append((remote.lstrip('/'), name))
        payload += "printf '\\n%s\\n' " + download_start + '\n'
        payload += 'tar -cz -C / ' + ' '.join(shlex.quote(r) for r, _ in wanted) + ' | base64 -w 76\n'
        payload += "printf '\\n%s\\n' " + download_end + '\n'
    end = 'RESULT_' + uuid.uuid4().hex
    payload += "code=$?; printf '\\n%s:%s\\n' " + end + ' "$code"; exit "$code"\n'
    proc = session(args.user, args.identity)
    if upload:
        marker = 'BODY_' + uuid.uuid4().hex
        program = ('import sys,base64,io,tarfile;'
                   + 'print(' + repr(marker) + ',flush=True);'
                   + 'data=sys.stdin.buffer.read(' + str(len(upload)) + ');'
                   + 'tarfile.open(fileobj=io.BytesIO(base64.b64decode(data)),mode="r:gz")'
                   + '.extractall(path=' + repr(args.root) + ',filter="data")')
        proc.stdin.write('stty -icanon -echo; python3 -c ' + shlex.quote(program) + '\n')
        proc.stdin.flush()
        for line in proc.stdout:
            if line.strip() == marker:
                break
        else:
            raise RuntimeError('Proxy closed before archive receiver was ready')
        payload = upload + payload
    output, _ = proc.communicate(payload)
    # Original file bytes travel only as a transfer payload; never log the archive.
    assert end + ':0' in output, 'Remote copy/command did not confirm success'
    if wanted:
        encoded = output.split(download_start + '\n', 1)[1].split('\n' + download_end, 1)[0]
        with tarfile.open(fileobj=io.BytesIO(base64.b64decode(encoded)), mode='r:gz') as bundle:
            for remote, name in wanted:
                stream = bundle.extractfile(remote)
                assert stream is not None
                data = stream.read()
                target = args.download_dir / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    assert target.read_bytes() == data, 'Refusing to replace an existing different original'
                else:
                    target.write_bytes(data)
                print('COPIED', name, len(data), hashlib.sha256(data).hexdigest(), flush=True)
    else:
        print(output, end='')


if __name__ == '__main__':
    main()
