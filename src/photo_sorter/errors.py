"""Common error types for Photo Sorter."""

from __future__ import annotations


class PhotoSorterError(Exception):
    """Base exception for Photo Sorter."""


class SourceFolderError(PhotoSorterError):
    """Error related to source folder selection or access."""


class TargetFolderError(PhotoSorterError):
    """Error related to target folder selection or validation."""


class ImageLoadError(PhotoSorterError):
    """Error when loading or decoding an image."""


class FileOperationError(PhotoSorterError):
    """Error during file copy/trash operations."""


class NavigationError(PhotoSorterError):
    """Error related to image navigation state."""
