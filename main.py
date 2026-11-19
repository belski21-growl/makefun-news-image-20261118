"""main.py -- entrypoint for news-image-20261118 (round 3 resubmit).

Renders the front page of Wednesday 18 November 2026 with the bundled
PIL renderer and writes it to entry.png in the output directory.

Output directory: $MAKEFUN_OUTPUT_DIR when set, otherwise /output
(the grader's writable directory). No network, no clock, no randomness:
two runs write byte-identical output.

Run locally:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def output_dir():
    """Resolve the writable output directory (env first, /output next)."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        return env_dir
    return "/output"


def main():
    out_dir = output_dir()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    # The renderer lives beside this file; the grader runs main.py from a
    # read-only copy of the repository, so import it from here explicitly.
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import render_frontpage18_r3

    render_frontpage18_r3.save_entry(out_path)
    size = os.path.getsize(out_path)
    if size > 1048576:
        raise SystemExit("entry.png is %d bytes, over the 1 MiB limit" % size)
    print("wrote %s (%d bytes)" % (out_path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
