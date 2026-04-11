from __future__ import annotations

import base64
import csv
import hashlib
import io
from pathlib import Path
import tarfile
import zipfile


DIST_NAME = "lichen-q"
NORMALIZED_DIST_NAME = "lichen_q"
VERSION = "0.1.0"
SUMMARY = "Blockwise hidden-memory simulator for correlated environment noise"
REQUIRES_PYTHON = ">=3.10"
REQUIRES_DIST = "numpy>=1.20"
TOP_LEVEL_PACKAGE = "lichen"

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"


def _dist_info_dir() -> str:
    return f"{NORMALIZED_DIST_NAME}-{VERSION}.dist-info"


def _wheel_name() -> str:
    return f"{NORMALIZED_DIST_NAME}-{VERSION}-py3-none-any.whl"


def _sdist_name() -> str:
    return f"{DIST_NAME}-{VERSION}.tar.gz"


def _metadata_text() -> str:
    return "\n".join(
        [
            "Metadata-Version: 2.1",
            f"Name: {DIST_NAME}",
            f"Version: {VERSION}",
            f"Summary: {SUMMARY}",
            "Description-Content-Type: text/markdown",
            f"Requires-Python: {REQUIRES_PYTHON}",
            f"Requires-Dist: {REQUIRES_DIST}",
            "License-File: LICENSE",
            "Classifier: Development Status :: 3 - Alpha",
            "Classifier: License :: OSI Approved :: MIT License",
            "Classifier: Operating System :: OS Independent",
            "Classifier: Programming Language :: Python :: 3",
            "Classifier: Programming Language :: Python :: 3.10",
            "Classifier: Programming Language :: Python :: 3.11",
            "Classifier: Programming Language :: Python :: 3.12",
            "Classifier: Programming Language :: Python :: 3.13",
            "Classifier: Programming Language :: Python :: 3.14",
            "Classifier: Topic :: Scientific/Engineering :: Physics",
            "",
            _readme_text(),
        ]
    )


def _readme_text() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8").strip()


def _wheel_text() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: build_backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def _record_row(path: str, data: bytes) -> list[str]:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
    return [path, f"sha256={digest}", str(len(data))]


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _iter_package_files() -> list[Path]:
    return sorted((SRC / TOP_LEVEL_PACKAGE).rglob("*.py"))


def _iter_sdist_files() -> list[Path]:
    files = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CHANGELOG.md",
        ROOT / "pyproject.toml",
        ROOT / "build_backend.py",
        ROOT / "build.py",
    ]
    files.extend(sorted((ROOT / "examples").rglob("*.ipynb")))
    files.extend(sorted((ROOT / "tests").rglob("*.py")))
    files.extend(sorted((ROOT / "tests").rglob("*.md")))
    files.extend(_iter_package_files())
    return [path for path in files if path.exists()]


def _write_wheel_file(wheel_directory: str, *, editable: bool) -> str:
    wheel_path = Path(wheel_directory) / _wheel_name()
    dist_info = _dist_info_dir()
    record_rows: list[list[str]] = []

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if editable:
            pth_name = f"{NORMALIZED_DIST_NAME}.pth"
            pth_data = f"{SRC.as_posix()}\n".encode("utf-8")
            zf.writestr(pth_name, pth_data)
            record_rows.append(_record_row(pth_name, pth_data))
        else:
            for file_path in _iter_package_files():
                archive_name = file_path.relative_to(SRC).as_posix()
                data = _read_bytes(file_path)
                zf.writestr(archive_name, data)
                record_rows.append(_record_row(archive_name, data))

        metadata_name = f"{dist_info}/METADATA"
        metadata_data = _metadata_text().encode("utf-8")
        zf.writestr(metadata_name, metadata_data)
        record_rows.append(_record_row(metadata_name, metadata_data))

        wheel_name = f"{dist_info}/WHEEL"
        wheel_data = _wheel_text().encode("utf-8")
        zf.writestr(wheel_name, wheel_data)
        record_rows.append(_record_row(wheel_name, wheel_data))

        top_level_name = f"{dist_info}/top_level.txt"
        top_level_data = f"{TOP_LEVEL_PACKAGE}\n".encode("utf-8")
        zf.writestr(top_level_name, top_level_data)
        record_rows.append(_record_row(top_level_name, top_level_data))

        record_name = f"{dist_info}/RECORD"
        record_buffer = io.StringIO()
        writer = csv.writer(record_buffer, lineterminator="\n")
        for row in record_rows:
            writer.writerow(row)
        writer.writerow([record_name, "", ""])
        record_data = record_buffer.getvalue().encode("utf-8")
        zf.writestr(record_name, record_data)

    return wheel_path.name


def _write_sdist_file(sdist_directory: str) -> str:
    sdist_path = Path(sdist_directory) / _sdist_name()
    base_dir = f"{DIST_NAME}-{VERSION}"
    with tarfile.open(sdist_path, "w:gz") as tf:
        pkg_info_data = _metadata_text().encode("utf-8")
        pkg_info = tarfile.TarInfo(name=f"{base_dir}/PKG-INFO")
        pkg_info.size = len(pkg_info_data)
        tf.addfile(pkg_info, io.BytesIO(pkg_info_data))
        for file_path in _iter_sdist_files():
            arcname = f"{base_dir}/{file_path.relative_to(ROOT).as_posix()}"
            tf.add(file_path, arcname=arcname)
    return sdist_path.name


def _prepare_metadata_directory(metadata_directory: str) -> str:
    dist_info = Path(metadata_directory) / _dist_info_dir()
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (dist_info / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    (dist_info / "top_level.txt").write_text(f"{TOP_LEVEL_PACKAGE}\n", encoding="utf-8")
    return dist_info.name


def get_requires_for_build_wheel(config_settings=None):
    return []


def get_requires_for_build_editable(config_settings=None):
    return []


def get_requires_for_build_sdist(config_settings=None):
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    return _prepare_metadata_directory(metadata_directory)


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    return _prepare_metadata_directory(metadata_directory)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _write_wheel_file(wheel_directory, editable=False)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _write_wheel_file(wheel_directory, editable=True)


def build_sdist(sdist_directory, config_settings=None):
    return _write_sdist_file(sdist_directory)
