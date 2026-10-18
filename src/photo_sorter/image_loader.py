"""Image loading with EXIF orientation and scaling."""

from __future__ import annotations

import contextlib
from pathlib import Path

from PIL import Image, ImageOps
from PIL.Image import Image as PILImage
from pillow_heif import register_heif_opener

from .errors import ImageLoadError

# Register HEIC/HEIF support
register_heif_opener()


def _get_exif_oriented(img: PILImage) -> PILImage:
    try:
        return ImageOps.exif_transpose(img)
    except Exception:
        return img


def load_image(path: Path | str) -> PILImage:
    """Load image from path. Returns PIL Image (not scaled)."""
    p = Path(path)
    try:
        with Image.open(p) as img:
            img.load()
            img = _get_exif_oriented(img)
            return img.copy()
    except Exception as e:
        raise ImageLoadError(f"Failed to load image {p}: {e}") from e


def load_scaled_for_view(path: Path | str, view_size: tuple[int, int]) -> PILImage:
    """Load and scale image to fit inside view_size while preserving aspect ratio.

    view_size is (width, height) of target view area.
    """
    if view_size[0] <= 0 or view_size[1] <= 0:
        return load_image(path)

    img = load_image(path)
    try:
        img.thumbnail(view_size, Image.Resampling.LANCZOS)
    except Exception:
        with contextlib.suppress(Exception):
            img.thumbnail(view_size)
    return img
