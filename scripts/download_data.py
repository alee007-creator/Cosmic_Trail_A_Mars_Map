"""Download COSMIC TRAIL's data from Hugging Face into data/.

The data is too large for Git, so it lives in the Hugging Face dataset
https://huggingface.co/datasets/irhabatool/cosmic-trail-data (about 9.7 GB in total).
The app only reads the processed files (about 236 MB):

    data/
      hirise_gale/          real HiRISE terrain of Gale Crater
        analysis.npz          elevation/slope grid used for routing (52 MB)
        ortho_mosaic.tif      HiRISE photo mosaic, the "HiRISE photo" layer (145 MB)
        elevation.png  slope.png  hillshade.png  fill_overlay.png  thumbnail.png
        metadata.json         provenance + checksums
      synthetic_demo/       synthetic terrain (fallback / tests)
      terrain_context.npz   MOLA heights around the study area for the 3D globe (10 MB)
      minerals/aqueous_minerals.json
      usgs_geologic_units.geojson  hazard_zones.geojson  curiosity_official_route.geojson

Everything under hirise_gale/raw/ (the original HiRISE DTMs, orthoimages, USGS and MOLA
mosaics, ~9.5 GB) is only an input to scripts/prepare_data.py and the build_* scripts and
is skipped unless you pass --include-raw.

Usage (from the repository root, with the virtual environment active):
    python scripts/download_data.py                # processed files only (~236 MB)
    python scripts/download_data.py --include-raw  # everything (~9.7 GB)

Running it again only downloads what is missing or changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ID = "irhabatool/cosmic-trail-data"
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEST = ROOT / "data"
ALWAYS_SKIP = ["README.md", ".gitattributes"]
RAW_PATTERN = "hirise_gale/raw/*"


def human(n: float) -> str:
    """Decimal units (1 MB = 1,000,000 bytes), as Hugging Face shows file sizes."""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1000 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1000
    return f"{n:.1f} GB"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def find_key(obj, key: str):
    """First value stored under `key` anywhere in a nested JSON object."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            found = find_key(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = find_key(v, key)
            if found is not None:
                return found
    return None


def verify(dest: Path) -> bool:
    """Check each dataset's analysis.npz against the SHA-256 in its metadata.json."""
    ok = True
    for meta_path in sorted(dest.glob("*/metadata.json")):
        npz = meta_path.parent / "analysis.npz"
        expected = find_key(json.loads(meta_path.read_text(encoding="utf-8")), "analysis_npz_sha256")
        if not npz.exists() or not expected:
            continue
        actual = sha256(npz)
        status = "OK" if actual == expected else "MISMATCH"
        ok &= actual == expected
        print(f"  checksum {status:8} {npz.relative_to(dest.parent).as_posix()}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--include-raw", action="store_true",
                    help="also download hirise_gale/raw/ (~9.5 GB of source files)")
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST,
                    help=f"target folder (default: {DEFAULT_DEST})")
    ap.add_argument("--revision", default="main", help="dataset branch, tag or commit")
    args = ap.parse_args()

    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError:
        print("huggingface_hub is not installed. Run:  pip install -r requirements.txt", file=sys.stderr)
        return 1

    ignore = ALWAYS_SKIP + ([] if args.include_raw else [RAW_PATTERN])
    files = [f for f in HfApi().list_repo_tree(REPO_ID, repo_type="dataset", recursive=True,
                                               revision=args.revision)
             if getattr(f, "size", None) is not None]
    wanted = [f for f in files
              if f.path not in ALWAYS_SKIP and (args.include_raw or not f.path.startswith("hirise_gale/raw/"))]
    total = sum(f.size for f in wanted)
    print(f"Hugging Face dataset {REPO_ID} ({args.revision})")
    print(f"Downloading {len(wanted)} files, {human(total)} -> {args.dest}")
    if not args.include_raw:
        skipped = sum(f.size for f in files if f.path.startswith("hirise_gale/raw/"))
        print(f"(skipping hirise_gale/raw/, {human(skipped)} of source files; use --include-raw to get them)")

    args.dest.mkdir(parents=True, exist_ok=True)
    snapshot_download(REPO_ID, repo_type="dataset", revision=args.revision,
                      local_dir=str(args.dest), ignore_patterns=ignore)

    missing = [f.path for f in wanted if not (args.dest / f.path).exists()]
    if missing:
        print("Missing after download:", *missing, sep="\n  ", file=sys.stderr)
        return 1
    print("Verifying ...")
    if not verify(args.dest):
        print("A checksum does not match. Delete that file and run this script again.", file=sys.stderr)
        return 1
    print("Done. Start the backend with:  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
