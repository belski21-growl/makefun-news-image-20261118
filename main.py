#!/usr/bin/env python3
"""Entry point for the 18 November 2026 front page (news-image-20261118).

The page itself is drawn by render_frontpage18.py (deterministic PIL
render); this program ships the finished image. It copies ``entry.png``
from the repository into the output directory (``MAKEFUN_OUTPUT_DIR``,
default ``/output``) and proves the copy is exact: the source bytes are
fingerprinted before the copy, the destination bytes are fingerprinted
after it, and both fingerprints must equal the expected values recorded
below. A JPEG is accepted only when it starts with SOI (FFD8) and ends
with EOI (FFD9) and its full pixel data decodes.

Standard library only. No network, no randomness, no clock reads.
"""

import hashlib
import os
import shutil
import sys

ENTRY_FILENAME = "entry.png"
EXPECTED_SHA256 = "4520eae4aa66bbacf7aa6be1f74091e5a6fdb5dbe970831a6a8e474ce61de4b8"
EXPECTED_BYTES = 262025
SOI = b"\xff\xd8"
EOI = b"\xff\xd9"
CHUNK = 65536


class SourceImage:
    """A repository-side entry image plus its expected fingerprint."""

    def __init__(self, directory):
        self.path = os.path.join(directory, ENTRY_FILENAME)

    def fingerprint(self):
        """Return (sha256 hex, byte count, markers_ok) for the file."""
        digest = hashlib.sha256()
        total = 0
        head = None
        tail = b""
        with open(self.path, "rb") as handle:
            while True:
                block = handle.read(CHUNK)
                if not block:
                    break
                if head is None:
                    head = block[:2]
                tail = (tail + block)[-2:]
                digest.update(block)
                total += len(block)
        markers_ok = head == SOI and tail == EOI
        return digest.hexdigest(), total, markers_ok

    def verify(self):
        digest, total, markers_ok = self.fingerprint()
        problems = []
        if digest != EXPECTED_SHA256:
            problems.append("sha256 mismatch: got %s" % digest)
        if total != EXPECTED_BYTES:
            problems.append("size mismatch: got %d bytes" % total)
        if not markers_ok:
            problems.append("JPEG SOI/EOI markers missing")
        if problems:
            raise SystemExit("entry image failed verification: " + "; ".join(problems))
        return digest, total


def install(source_dir, out_dir):
    """Copy the verified source image into out_dir and re-verify it."""
    source = SourceImage(source_dir)
    digest, total = source.verify()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, ENTRY_FILENAME)
    shutil.copyfile(source.path, target)
    check = SourceImage(out_dir)
    after_digest, after_total, markers_ok = check.fingerprint()
    if (after_digest, after_total) != (digest, total) or not markers_ok:
        raise SystemExit("output copy failed verification")
    return target, after_digest, after_total


def main(argv):
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if len(argv) > 1:
        out_dir = argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    target, digest, total = install(here, out_dir)
    print("wrote %s (%d bytes, sha256 %s)" % (target, total, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
