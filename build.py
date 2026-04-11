from __future__ import annotations

import argparse
from pathlib import Path

import build_backend


def _build_dist(outdir: Path, *, wheel: bool, sdist: bool) -> list[str]:
    outdir.mkdir(parents=True, exist_ok=True)
    built: list[str] = []

    if wheel:
        built.append(build_backend.build_wheel(str(outdir)))
    if sdist:
        built.append(build_backend.build_sdist(str(outdir)))

    return built


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="build", description="Build lichen distributions.")
    parser.add_argument("--wheel", action="store_true", help="Build a wheel only.")
    parser.add_argument("--sdist", action="store_true", help="Build an sdist only.")
    parser.add_argument("--outdir", default="dist", help="Output directory for artifacts.")
    args = parser.parse_args(argv)

    build_wheel = args.wheel or not args.sdist
    build_sdist = args.sdist or not args.wheel

    built = _build_dist(Path(args.outdir), wheel=build_wheel, sdist=build_sdist)
    for artifact in built:
        print(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
