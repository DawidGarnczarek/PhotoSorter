"""Image view widget."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from .errors import ImageLoadError
from .image_loader import load_image


class ImageView(QWidget):
    """Central widget for displaying images with zoom and pan."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._label = QLabel(self._scroll)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setScaledContents(False)
        self._scroll.setWidget(self._label)

        self._layout.addWidget(self._scroll)

        self._current_path: Path | None = None
        self._image: QImage | None = None
        self._pixmap: QPixmap | None = None
        self._zoom_factor: float = 1.0
        self._base_pixmap: QPixmap | None = None  # fitted to view
        self._fitted: bool = True
        self._last_view_size: tuple[int, int] | None = None

    def clear(self) -> None:
        self._current_path = None
        self._image = None
        self._pixmap = None
        self._base_pixmap = None
        self._label.clear()
        self._zoom_factor = 1.0
        self._fitted = True

    def set_image(self, path: Path | None) -> None:
        self.clear()
        if path is None:
            self._label.setText("No images in folder")
            return
        self._current_path = path
        try:
            pil_img = load_image(path)
        except ImageLoadError as e:
            self._label.setText(f"Failed to load image:\n{e}")
            return

        # Convert PIL to QImage
        try:
            if pil_img.mode not in ("RGB", "RGBA"):
                pil_img = pil_img.convert("RGBA")
            data = pil_img.tobytes()
            if pil_img.mode == "RGBA":
                fmt = QImage.Format.Format_RGBA8888
            else:
                fmt = QImage.Format.Format_RGB888
            bytes_per_line = pil_img.width * (4 if pil_img.mode == "RGBA" else 3)
            qimg = QImage(data, pil_img.width, pil_img.height, bytes_per_line, fmt)
            if qimg.isNull():
                raise ImageLoadError("QImage conversion failed")
            self._image = qimg
        except Exception as e:
            self._label.setText(f"Failed to display image:\n{e}")
            return

        self._fit_to_view()
        self._fitted = True
        self._zoom_factor = 1.0

    def _fit_to_view(self) -> None:
        if self._image is None:
            return
        view_w = self._scroll.viewport().width() or self.width()
        view_h = self._scroll.viewport().height() or self.height()
        if view_w < 1 or view_h < 1:
            view_w, view_h = 800, 600
        self._last_view_size = (view_w, view_h)
        pm = QPixmap.fromImage(self._image)
        scaled = pm.scaled(
            view_w, view_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._base_pixmap = scaled
        self._pixmap = scaled
        self._label.setPixmap(scaled)
        self._fitted = True
        self._zoom_factor = 1.0

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self._image is not None and self._fitted:
            self._fit_to_view()

    def _apply_zoom(self) -> None:
        if self._image is None:
            return
        if not self._fitted and self._image:
            target_w = int(self._image.width() * self._zoom_factor)
            target_h = int(self._image.height() * self._zoom_factor)
            pm_orig = QPixmap.fromImage(self._image)
            scaled = pm_orig.scaled(
                target_w,
                target_h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._label.setPixmap(scaled)
            return
        if self._fitted and self._base_pixmap:
            scaled = self._base_pixmap.scaled(
                int(self._base_pixmap.width() * self._zoom_factor),
                int(self._base_pixmap.height() * self._zoom_factor),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._label.setPixmap(scaled)
            return

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if self._image is None:
            return
        delta = event.angleDelta().y()
        if delta > 0:
            self._zoom_factor *= 1.1
        else:
            self._zoom_factor *= 0.9

        # Constraints: min = fit (1.0 relative to fit base), max ~8x relative to fitted
        if self._zoom_factor < 0.1:
            self._zoom_factor = 0.1
        if self._zoom_factor > 8.0:
            self._zoom_factor = 8.0

        if self._zoom_factor <= 1.01 and delta < 0:
            # snap back to fit
            self._fit_to_view()
            event.accept()
            return

        self._fitted = False
        self._apply_zoom()
        event.accept()

    def reset_zoom(self) -> None:
        self._fit_to_view()

    def is_fitted(self) -> bool:
        return self._fitted

    def zoom_out_to_fit(self) -> None:
        self._fit_to_view()
