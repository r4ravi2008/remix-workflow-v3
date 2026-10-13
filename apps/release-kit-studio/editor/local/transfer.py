"""Stream exact-length loopback uploads without Bun's HTTP chunked encoding."""
import http.client
import json
import re
import sys
from urllib.parse import urlsplit

url = urlsplit(sys.argv[1])
length = int(sys.argv[2])
if url.scheme != 'http' or url.hostname != '127.0.0.1' or not re.fullmatch(r'/jobs/[a-zA-Z0-9_-]{1,80}/(?:assets|verification)/[a-zA-Z0-9_-]{1,80}', url.path) or not 0 < length <= 2147483648:
    raise ValueError('Transfer requires an exact bounded upload to the local native engine.')
connection = http.client.HTTPConnection(url.hostname, url.port, timeout=600)
try:
    connection.putrequest('PUT', url.path)
    connection.putheader('Content-Length', str(length))
    connection.endheaders()
    remaining = length
    while remaining:
        block = sys.stdin.buffer.read(min(remaining, 256 * 1024))
        if not block:
            raise ValueError('Native input stream was truncated.')
        connection.send(block)
        remaining -= len(block)
    if sys.stdin.buffer.read(1):
        raise ValueError('Native input exceeds its immutable byte count.')
    response = connection.getresponse()
    sys.stdout.buffer.write((json.dumps({'status': response.status, 'headers': dict(response.getheaders())}) + '\n').encode())
    sys.stdout.buffer.flush()
    while block := response.read(256 * 1024):
        sys.stdout.buffer.write(block)
    sys.stdout.buffer.flush()
finally:
    connection.close()
