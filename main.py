# A program that writes one image summing up the world news of
# Thursday 19 November 2026 to /output/entry.png: it copies the
# entry.png beside this file. Standard library only, no network,
# deterministic: the same bytes every run.
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")

# Sanity check: the copy must be the bundled image, byte for byte.
src = HERE / "entry.png"
dst = OUT / "entry.png"
assert src.stat().st_size == dst.stat().st_size, "entry.png copy size mismatch"
assert dst.read_bytes() == src.read_bytes(), "entry.png copy content mismatch"
