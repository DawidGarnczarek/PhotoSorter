"""Folder scanning and image file discovery."""

from __future__ import annotations

from pathlib import Path

from .errors import SourceFolderError

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff"}


def _is_hidden(path: Path) -> bool:
    try:
        name = path.name
    except Exception:
        return True
    if name.startswith("."):
        return True
    # macOS special files
    return name in {
        ".DS_Store",
        ".Spotlight-V100",
        ".Trashes",
        "._.Trashes",
        ".fseventsd",
        ".TemporaryItems",
    }


def _is_valid_image_path(path: Path) -> bool:
    try:
        ext = path.suffix.lower()
    except Exception:
        return False
    if ext not in SUPPORTED_EXTS:
        return False
    try:
        # Quick check: can we stat and is it a regular file?
        st = path.stat()
        if not path.is_file() or st.st_size == 0:
            return False
    except Exception:
        return False
    return True


def scan_folder(source: Path | str) -> list[Path]:
    """Recursively scan source folder for supported image files.

    Returns list of image paths sorted case-insensitively by relative path from source.
    """
    src = Path(source).resolve()

    if not src.exists() or not src.is_dir():
        raise SourceFolderError(f"Source folder does not exist or is not a directory: {src}")

    # Gather candidates
    candidates: list[Path] = []
    try:
        for p in src.rglob("*"):
            if _is_hidden(p):
                continue
            if p.is_file() and _is_valid_image_path(p):
                candidates.append(p)
    except Exception as e:
        raise SourceFolderError(f"Failed to scan folder {src}: {e}") from e

    # Sort by case-insensitive relative path string
    def key(p: Path) -> str:
        try:
            rel = p.relative_to(src).as_posix()
        except Exception:
            rel = p.as_posix()
        return rel.lower()

    candidates.sort(key=key)
    return candidates
