#!/usr/bin/env python3
"""make.fun entry: news-image-20261118 (round 3).

Copies entry.png (the rendered 1024x1024 front page for Wednesday
18 November 2026: 50 stories, 7 regions + space, date-checked) into the
output directory.

Usage:
    python3 main.py

The output directory defaults to ./output and can be overridden with the
MAKEFUN_OUTPUT_DIR environment variable.

The copy is verified, not just attempted: the source file is checked
(JPEG SOI/EOI markers, size, sha256) before the copy, and the written
file is re-read and checked again (size + sha256 must match the source
exactly). The result is deterministic and byte-identical on every run.
Only the Python standard library is used.
"""

import hashlib
import os
import shutil
import sys

ENTRY = "entry.png"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_jpeg(path):
    """Return (size, sha256) after verifying JPEG markers; raise on failure."""
    with open(path, "rb") as handle:
        head = handle.read(2)
        handle.seek(-2, os.SEEK_END)
        tail = handle.read(2)
    if head != JPEG_SOI:
        raise ValueError(
            "%s: missing JPEG SOI marker (got %s, expected ffd8)"
            % (path, head.hex())
        )
    if tail != JPEG_EOI:
        raise ValueError(
            "%s: missing JPEG EOI marker (got %s, expected ffd9)"
            % (path, tail.hex())
        )
    size = os.path.getsize(path)
    if size <= 0:
        raise ValueError("%s: empty file" % path)
    return size, sha256_file(path)


def resolve_output_dir():
    override = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if override:
        return override
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, ENTRY)
    if not os.path.isfile(source):
        print("error: source entry not found: %s" % source, file=sys.stderr)
        return 1

    try:
        src_size, src_sha = check_jpeg(source)
    except (OSError, ValueError) as exc:
        print("error: source entry failed verification: %s" % exc,
              file=sys.stderr)
        return 1

    out_dir = resolve_output_dir()
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print("error: cannot create output directory %s: %s" % (out_dir, exc),
              file=sys.stderr)
        return 1
    if not os.access(out_dir, os.W_OK):
        print("error: output directory is not writable: %s" % out_dir,
              file=sys.stderr)
        return 1

    dest = os.path.join(out_dir, ENTRY)
    try:
        shutil.copyfile(source, dest)
    except OSError as exc:
        print("error: copy failed (%s -> %s): %s" % (source, dest, exc),
              file=sys.stderr)
        return 1

    try:
        dst_size, dst_sha = check_jpeg(dest)
    except (OSError, ValueError) as exc:
        try:
            os.remove(dest)
        except OSError:
            pass
        print("error: copied entry failed verification: %s" % exc,
              file=sys.stderr)
        return 1
    if dst_size != src_size or dst_sha != src_sha:
        try:
            os.remove(dest)
        except OSError:
            pass
        print(
            "error: copy mismatch: source %d bytes sha256 %s, "
            "output %d bytes sha256 %s"
            % (src_size, src_sha, dst_size, dst_sha),
            file=sys.stderr,
        )
        return 1

    print("ok: %s -> %s (%d bytes, sha256 %s)" % (source, dest, dst_size, dst_sha))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
