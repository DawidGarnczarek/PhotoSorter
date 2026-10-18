"""File operations: safe copy and move to trash."""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

from .errors import FileOperationError, TargetFolderError


def _validate_target(target: Path) -> None:
    if not target.exists() or not target.is_dir():
        raise TargetFolderError(f"Target folder does not exist: {target}")
    if not os.access(target, os.W_OK):
        raise TargetFolderError(f"Target folder is not writable: {target}")


def _ensure_inside(parent: Path, child: Path) -> Path:
    parent_res = parent.resolve()
    child_res = child.resolve()
    try:
        child_res.relative_to(parent_res)
    except Exception as e:
        raise TargetFolderError(
            f"Target path escapes parent folder: {child_res} not under {parent_res}"
        ) from e
    return child_res


def _validate_target_against_source(source_root: Path, target_root: Path) -> None:
    src = source_root.resolve()
    tgt = target_root.resolve()
    if tgt == src:
        raise TargetFolderError("Target folder cannot be the same as source folder")
    try:
        tgt.relative_to(src)
        raise TargetFolderError("Target folder cannot be inside source folder")
    except ValueError:
        pass
    try:
        src.relative_to(tgt)
        raise TargetFolderError("Source folder cannot be inside target folder")
    except ValueError:
        pass


def _relative_target_path(source_file: Path, source_root: Path, target_root: Path) -> Path:
    rel = source_file.resolve().relative_to(source_root.resolve())
    target_path = (target_root.resolve() / rel).resolve()
    _ensure_inside(target_root.resolve(), target_path)
    return target_path


def safe_copy(
    source_file: Path | str,
    source_root: Path | str,
    target_root: Path | str,
) -> Path:
    """Copy source_file preserving relative structure under target_root.

    - Does not overwrite if target exists (raises FileOperationError)
    - Copies atomically: write to temp file in target dir, then replace if not exists
    - Copies bytes as-is
    """
    src = Path(source_file).resolve()
    if not src.is_file():
        raise FileOperationError(f"Source file does not exist or is not a file: {src}")

    src_root = Path(source_root).resolve()
    tgt_root = Path(target_root).resolve()

    _validate_target(tgt_root)
    _validate_target_against_source(src_root, tgt_root)

    tgt_path = _relative_target_path(src, src_root, tgt_root)

    if tgt_path.exists():
        raise FileOperationError(f"Target file already exists: {tgt_path}")

    tgt_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_name = ""
    try:
        with tempfile.NamedTemporaryFile(dir=tgt_path.parent, delete=False, prefix=".photo_sorter_tmp_") as tf:
            tmp_name = tf.name
            with src.open("rb") as sf:
                while True:
                    chunk = sf.read(1024 * 1024)
                    if not chunk:
                        break
                    tf.write(chunk)
    except Exception as e:
        with contextlib.suppress(Exception):
            Path(tmp_name).unlink(missing_ok=True)
        raise FileOperationError(f"Failed to copy to temp file: {e}") from e

    tmp_path = Path(tmp_name)

    try:
        try:
            if src.stat().st_size != tmp_path.stat().st_size:
                raise FileOperationError("Copy size mismatch")
        except Exception as e:
            raise FileOperationError(f"Copy verification failed: {e}") from e

        try:
            os.replace(tmp_path, tgt_path)
        except FileExistsError as e:
            raise FileOperationError(f"Target file appeared during copy: {tgt_path}") from e
        except Exception as e:
            raise FileOperationError(f"Failed to finalize copy: {e}") from e
    except Exception as e:
        with contextlib.suppress(Exception):
            tmp_path.unlink(missing_ok=True)
        raise FileOperationError(f"Copy failed: {e}") from e

    return tgt_path


def move_to_trash(source_file: Path | str) -> Path:
    """Move file to system trash. Returns original path."""
    from send2trash import send2trash

    src = Path(source_file).resolve()
    if not src.exists() or not src.is_file():
        raise FileOperationError(f"Source file does not exist: {src}")

    try:
        send2trash(str(src))
    except Exception as e:
        raise FileOperationError(f"Failed to move to trash: {e}") from e
    return src
