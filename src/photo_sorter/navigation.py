"""Navigation state management for image list."""

from __future__ import annotations

from pathlib import Path


class Navigation:
    """Manages current index in image list."""

    def __init__(self, images: list[Path] | None = None) -> None:
        self._images: list[Path] = list(images) if images else []
        self._index: int = 0 if self._images else -1

    def set_images(self, images: list[Path]) -> None:
        self._images = list(images)
        self._index = 0 if self._images else -1

    def current(self) -> Path | None:
        if self._index < 0 or self._index >= len(self._images):
            return None
        return self._images[self._index]

    def image_at(self, offset: int = 0) -> Path | None:
        """Return image at current index + offset, or None if out of bounds."""
        target = self._index + offset
        if target < 0 or target >= len(self._images):
            return None
        return self._images[target]

    def count(self) -> int:
        return len(self._images)

    def index(self) -> int:
        return self._index

    def position_text(self) -> str:
        if self._index < 0 or not self._images:
            return "0 / 0"
        return f"{self._index + 1} / {len(self._images)}"

    def next(self) -> bool:
        if not self._images:
            return False
        if self._index < len(self._images) - 1:
            self._index += 1
            return True
        return False

    def prev(self) -> bool:
        if not self._images:
            return False
        if self._index > 0:
            self._index -= 1
            return True
        return False

    def remove_current(self) -> bool:
        """Remove current image from list. Returns True if removed."""
        if self._index < 0 or self._index >= len(self._images):
            return False
        del self._images[self._index]
        if not self._images:
            self._index = -1
            return True
        if self._index >= len(self._images):
            self._index = len(self._images) - 1
        return True
