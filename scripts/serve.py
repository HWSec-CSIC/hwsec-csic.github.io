#!/usr/bin/env python3
"""Preview the site and rebuild whenever its JSON or templates change."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]


def fingerprint():
    paths = [*list((ROOT / 'scripts').glob('*.py')), *list((ROOT / 'templates').glob('*'))]
    paths.extend((ROOT / 'assets' / 'docs').glob('*.json'))
    paths.extend((ROOT / 'assets' / 'images').rglob('*'))
    paths.extend((ROOT / 'assets' / 'icons').glob('*.svg'))
    return tuple((str(path), path.stat().st_mtime_ns, path.stat().st_size)
                 for path in sorted(paths) if path.is_file())


def rebuild():
    result = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build.py')], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout.strip() + ' Refresh your browser.', flush=True)
    else:
        print(result.stderr.strip() + ' Keeping the last successful build.', flush=True)


def watch(stop):
    previous = fingerprint()
    while not stop.wait(1):
        current = fingerprint()
        if current != previous:
            previous = current
            rebuild()


class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, format, *args):
        if args[1] != '200':
            super().log_message(format, *args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    rebuild()
    stop = threading.Event()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(PreviewHandler, directory=str(ROOT)))
    watcher = threading.Thread(target=watch, args=(stop,), daemon=True)
    watcher.start()
    print(f'Preview: http://localhost:{args.port} — Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
        watcher.join(timeout=2)


if __name__ == '__main__':
    main()
