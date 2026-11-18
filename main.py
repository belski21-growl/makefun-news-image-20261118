#!/usr/bin/env python3
"""news-image-20261118 entrypoint.

Copies the entry image (entry.png, JPEG bytes) sitting beside this file
to the output directory as entry.png, verifying it before and after the
copy. Standard library only, no network, fully deterministic: the output
is byte-identical to the source on every run.

The copy streams in fixed-size chunks and hashes incrementally, so memory
use stays flat no matter the image size.

Usage (outside the grader container):
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import sys

CHUNK_SIZE = 65536
JPEG_SOI = b"\xff\xd8"  # JPEG start-of-image marker
JPEG_EOI = b"\xff\xd9"  # JPEG end-of-image marker
SOURCE_NAME = "entry.png"


def fail(message):
    """Print a clear error to stderr and exit non-zero."""
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def check_image(first_bytes, last_bytes, size, sha256, label):
    """Verify the image looks like a whole JPEG of a sane size."""
    if size > 1048576:
        fail(label + " is " + str(size) + " bytes, over the 1 MiB limit")
    if size < 2 or first_bytes != JPEG_SOI:
        fail(label + " does not start with the JPEG SOI marker")
    if size < 2 or last_bytes != JPEG_EOI:
        fail(label + " does not end with the JPEG EOI marker")
    return sha256


def hash_and_copy(source_path, dest_path):
    """Stream-copy source_path to dest_path; return (size, sha256)."""
    hasher = hashlib.sha256()
    size = 0
    first_bytes = None
    last_bytes = None
    try:
        with open(source_path, "rb") as source_file, \
                open(dest_path, "wb") as dest_file:
            while True:
                chunk = source_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                if first_bytes is None:
                    first_bytes = chunk[:2]
                last_bytes = chunk[-2:]
                hasher.update(chunk)
                dest_file.write(chunk)
                size += len(chunk)
    except OSError as exc:
        fail("copy failed (" + source_path + " -> " + dest_path + "): "
             + str(exc))
    return size, hasher.hexdigest(), first_bytes, last_bytes


def hash_file(path):
    """Return (size, sha256, first 2 bytes, last 2 bytes) of a file."""
    hasher = hashlib.sha256()
    size = 0
    first_bytes = None
    last_bytes = None
    try:
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(CHUNK_SIZE)
                if not chunk:
                    break
                if first_bytes is None:
                    first_bytes = chunk[:2]
                last_bytes = chunk[-2:]
                hasher.update(chunk)
                size += len(chunk)
    except OSError as exc:
        fail("cannot read " + path + ": " + str(exc))
    return size, hasher.hexdigest(), first_bytes, last_bytes


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, SOURCE_NAME)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    dest_path = os.path.join(out_dir, SOURCE_NAME)

    if not os.path.isfile(source_path):
        fail("source image not found: " + source_path)

    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        fail("cannot create output directory " + out_dir + ": " + str(exc))

    size, sha256, first, last = hash_and_copy(source_path, dest_path)
    check_image(first, last, size, sha256, "output " + SOURCE_NAME)

    back_size, back_sha256, back_first, back_last = hash_file(dest_path)
    check_image(back_first, back_last, back_size, back_sha256,
                "read-back " + SOURCE_NAME)
    if back_size != size:
        fail("read-back size " + str(back_size) + " != copied size "
             + str(size))
    if back_sha256 != sha256:
        fail("read-back sha256 " + back_sha256 + " != copied sha256 "
             + sha256)

    print("wrote " + dest_path + " (" + str(size) + " bytes, "
          "sha256 " + sha256 + ")")


if __name__ == "__main__":
    main()
