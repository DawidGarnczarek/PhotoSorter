"""Main application window."""

from __future__ import annotations

import contextlib
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from .errors import FileOperationError, SourceFolderError, TargetFolderError
from .file_operations import move_to_trash, safe_copy
from .folder_scanner import scan_folder
from .image_view import ImageView
from .navigation import Navigation
from .settings import Settings


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Photo Sorter")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self.settings = Settings()
        self.nav = Navigation()
        self.source_root: Path | None = None
        self.target_root: Path | None = None
        self._copying_or_trashing = False

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        src_bar = QHBoxLayout()
        self.btn_source = QPushButton("Select source folder...")
        self.lbl_source = QLabel("(none)")
        self.lbl_source.setWordWrap(True)
        src_bar.addWidget(self.btn_source)
        src_bar.addWidget(self.lbl_source, 1)
        layout.addLayout(src_bar)

        tgt_bar = QHBoxLayout()
        self.btn_target = QPushButton("Select target folder...")
        self.lbl_target = QLabel("(none)")
        self.lbl_target.setWordWrap(True)
        tgt_bar.addWidget(self.btn_target)
        tgt_bar.addWidget(self.lbl_target, 1)
        layout.addLayout(tgt_bar)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)

        self.image_view = ImageView(self)
        layout.addWidget(self.image_view, 1)

        self.lbl_filename = QLabel("")
        self.lbl_filename.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_counter = QLabel("0 / 0")
        self.lbl_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_filename)
        layout.addWidget(self.lbl_counter)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        shortcuts = QHBoxLayout()
        shortcuts.addStretch()
        shortcuts.addWidget(
            QLabel("← Prev  → Next  Space: Copy  ⌫: Trash  F: Fullscreen  Esc: Zoom/Exit")
        )
        shortcuts.addStretch()
        layout.addLayout(shortcuts)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.btn_source.clicked.connect(self.select_source)
        self.btn_target.clicked.connect(self.select_target)

        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.on_prev)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.on_next)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.on_copy)
        QShortcut(QKeySequence(Qt.Key.Key_Backspace), self, self.on_trash)
        QShortcut(QKeySequence(Qt.Key.Key_F), self, self.on_toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.on_escape)

        self._restore_saved_folders()

    def _restore_saved_folders(self) -> None:
        saved_src = self.settings.get("source")
        saved_tgt = self.settings.get("target")
        if saved_src:
            p = Path(saved_src)
            if p.exists() and p.is_dir():
                with contextlib.suppress(Exception):
                    self._set_source(p)
        if saved_tgt:
            p = Path(saved_tgt)
            if p.exists() and p.is_dir():
                self.target_root = p
                self.lbl_target.setText(str(p))
                self.settings.set("target", str(p))

    def _set_source(self, source_path: Path) -> None:
        try:
            imgs = scan_folder(source_path)
        except SourceFolderError as e:
            QMessageBox.critical(self, "Error", str(e))
            raise
        self.source_root = source_path.resolve()
        self.lbl_source.setText(str(self.source_root))
        self.settings.set("source", str(self.source_root))
        self.nav.set_images(imgs)
        self._update_view()

    def select_source(self) -> None:
        start = str(Path.home())
        if self.source_root:
            start = str(self.source_root)
        path = QFileDialog.getExistingDirectory(self, "Select source folder", start)
        if not path:
            return
        try:
            self._set_source(Path(path))
            self.status_bar.showMessage("Source folder selected")
        except Exception:
            pass

    def select_target(self) -> None:
        start = str(Path.home())
        if self.target_root:
            start = str(self.target_root)
        path = QFileDialog.getExistingDirectory(self, "Select target folder", start)
        if not path:
            return
        try:
            tgt = Path(path).resolve()
            src = self.source_root.resolve() if self.source_root else None
            from .file_operations import _validate_target_against_source
            if src:
                _validate_target_against_source(src, tgt)
            from .file_operations import _validate_target
            _validate_target(tgt)
            self.target_root = tgt
            self.lbl_target.setText(str(tgt))
            self.settings.set("target", str(tgt))
            self.status_bar.showMessage("Target folder selected")
        except (TargetFolderError, SourceFolderError) as e:
            QMessageBox.warning(self, "Invalid target", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _update_view(self) -> None:
        cur = self.nav.current()
        self.lbl_counter.setText(self.nav.position_text())
        if cur is None:
            self.lbl_filename.setText("")
            self.image_view.set_image(None)
            return
        self.lbl_filename.setText(cur.name)
        self.image_view.set_image(cur)

    def on_prev(self) -> None:
        if self._copying_or_trashing:
            return
        self.nav.prev()
        self.image_view.reset_zoom()
        self._update_view()

    def on_next(self) -> None:
        if self._copying_or_trashing:
            return
        self.nav.next()
        self.image_view.reset_zoom()
        self._update_view()

    def on_copy(self) -> None:
        if self._copying_or_trashing:
            return
        cur = self.nav.current()
        if cur is None:
            self.status_bar.showMessage("No image to copy")
            return
        if self.target_root is None:
            QMessageBox.warning(self, "Missing target", "Select target folder first")
            return
        self._copying_or_trashing = True
        self.status_bar.showMessage("Copying...")
        try:
            safe_copy(cur, self.source_root if self.source_root else cur.parent, self.target_root)
            self.status_bar.showMessage("Copied successfully")
            self.nav.next()
            self.image_view.reset_zoom()
            self._update_view()
        except (FileOperationError, TargetFolderError) as e:
            QMessageBox.warning(self, "Copy failed", str(e))
            self.status_bar.showMessage("Copy failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_bar.showMessage("Copy failed")
        finally:
            self._copying_or_trashing = False

    def on_trash(self) -> None:
        if self._copying_or_trashing:
            return
        cur = self.nav.current()
        if cur is None:
            self.status_bar.showMessage("No image to trash")
            return
        self._copying_or_trashing = True
        self.status_bar.showMessage("Moving to trash...")
        try:
            move_to_trash(cur)
            self.status_bar.showMessage("Moved to trash")
            self.nav.remove_current()
            self.image_view.reset_zoom()
            self._update_view()
        except FileOperationError as e:
            QMessageBox.warning(self, "Trash failed", str(e))
            self.status_bar.showMessage("Trash failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_bar.showMessage("Trash failed")
        finally:
            self._copying_or_trashing = False

    def on_toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def on_escape(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            return
        # if zoomed out from fit? image_view handles reset on change; reset if not fitted
        if hasattr(self.image_view, "is_fitted") and not self.image_view.is_fitted():
            self.image_view.reset_zoom()

