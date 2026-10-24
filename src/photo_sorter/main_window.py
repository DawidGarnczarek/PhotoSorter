"""Main application window."""

from __future__ import annotations

import contextlib
from PIL import Image
from datetime import datetime
from functools import partial
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
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
from .file_operations import _validate_target, _validate_target_against_source, move_to_trash, safe_copy
from .folder_scanner import scan_folder
from .image_view import ImageView
from .navigation import Navigation
from .settings import Settings

MAX_TARGETS = 9


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Photo Sorter")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self.settings = Settings()
        self.nav = Navigation()
        self.source_root: Path | None = None
        self.target_roots: dict[int, Path] = {}
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

        self.target_group = QGroupBox("Target folders (1-9)")
        self.target_group.setCheckable(True)
        self.target_group.setChecked(True)
        self.target_group.toggled.connect(self._toggle_targets)
        tgt_layout = QVBoxLayout(self.target_group)

        grid = QGridLayout()
        grid.setSpacing(8)
        self.target_buttons: list[QPushButton] = []
        self.target_labels: list[QLabel] = []
        self.target_cells: list[QWidget] = []
        for n in range(1, MAX_TARGETS + 1):
            cell = QVBoxLayout()
            cell.setSpacing(2)
            btn = QPushButton(f"Target {n}...")
            lbl = QLabel(f"{n}: (none)")
            lbl.setWordWrap(True)
            cell.addWidget(btn)
            cell.addWidget(lbl)
            wrapper = QWidget()
            wrapper.setLayout(cell)
            row = (n - 1) // 3
            col = (n - 1) % 3
            grid.addWidget(wrapper, row, col)
            self.target_buttons.append(btn)
            self.target_labels.append(lbl)
            self.target_cells.append(wrapper)
            btn.clicked.connect(partial(self.select_target, n))
        tgt_layout.addLayout(grid)
        layout.addWidget(self.target_group)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)

        self.lbl_map = QLabel("")
        self.lbl_map.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_map)

        # Middle section: main image + side preview panel
        self.image_view = ImageView(self)
        middle = QHBoxLayout()
        middle.setSpacing(6)
        middle.addWidget(self.image_view, 1)

        preview_panel = QWidget()
        preview_panel.setMinimumWidth(400)
        preview_panel.setMaximumWidth(700)
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(4, 4, 4, 4)
        preview_layout.setSpacing(8)

        preview_title = QLabel("Next 3:")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_title)

        self.preview_views: list[ImageView] = []
        for _ in range(3):
            pv = ImageView(self)
            pv.setMaximumHeight(300)
            pv.setMinimumHeight(220)
            self.preview_views.append(pv)
            preview_layout.addWidget(pv)

        preview_layout.addStretch()
        middle.addWidget(preview_panel)

        layout.addLayout(middle, 1)

        self.lbl_filename = QLabel("")
        self.lbl_filename.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_counter = QLabel("0 / 0")
        self.lbl_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_created = QLabel("")
        self.lbl_created.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_filename)
        layout.addWidget(self.lbl_counter)
        layout.addWidget(self.lbl_created)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        shortcuts = QHBoxLayout()
        shortcuts.addStretch()
        shortcuts.addWidget(
            QLabel("← Prev  → Next  1-9: Copy to target N  Space: Copy to target 1  ⌫: Trash  F: Fullscreen  Esc: Zoom/Exit")
        )
        shortcuts.addStretch()
        layout.addLayout(shortcuts)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.btn_source.clicked.connect(self.select_source)

        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.on_prev)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.on_next)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.on_copy)
        QShortcut(QKeySequence(Qt.Key.Key_Backspace), self, self.on_trash)
        QShortcut(QKeySequence(Qt.Key.Key_F), self, self.on_toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.on_escape)
        for n in range(1, MAX_TARGETS + 1):
            QShortcut(QKeySequence(getattr(Qt.Key, f"Key_{n}")), self, partial(self.on_copy_to, n))

        self._restore_saved_folders()
        self._refresh_target_map()

    def _restore_saved_folders(self) -> None:
        saved_src = self.settings.get("source")
        if saved_src:
            p = Path(saved_src)
            if p.exists() and p.is_dir():
                with contextlib.suppress(Exception):
                    self._set_source(p)
        for n in range(1, MAX_TARGETS + 1):
            saved = self.settings.get(f"target_{n}")
            if saved:
                p = Path(saved)
                if p.exists() and p.is_dir():
                    resolved = p.resolve()
                    self.target_roots[n] = resolved
                    self.target_labels[n - 1].setText(f"{n}: {resolved}")

    def _set_source(self, source_path: Path) -> None:
        imgs = scan_folder(source_path)
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
        except SourceFolderError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception:
            pass

    def select_target(self, n: int) -> None:
        start = str(Path.home())
        if n in self.target_roots:
            start = str(self.target_roots[n])
        path = QFileDialog.getExistingDirectory(self, f"Select target folder {n}", start)
        if not path:
            return
        try:
            tgt = Path(path).resolve()
            src = self.source_root.resolve() if self.source_root else None
            if src:
                _validate_target_against_source(src, tgt)
            _validate_target(tgt)
            for m, existing in self.target_roots.items():
                if m != n and existing == tgt:
                    raise TargetFolderError(f"Target folder {n} is the same as target {m}")
            self.target_roots[n] = tgt
            self.target_labels[n - 1].setText(f"{n}: {tgt}")
            self.settings.set(f"target_{n}", str(tgt))
            self._refresh_target_map()
            self.status_bar.showMessage(f"Target folder {n} selected")
        except (TargetFolderError, SourceFolderError) as e:
            QMessageBox.warning(self, "Invalid target", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _refresh_target_map(self) -> None:
        parts = [f"{n}: {p}" for n, p in sorted(self.target_roots.items())]
        self.lbl_map.setText("  ".join(parts) if parts else "No target folders set")

    def _toggle_targets(self, checked: bool) -> None:
        for cell in self.target_cells:
            cell.setVisible(checked)

    def _update_view(self) -> None:
        cur = self.nav.current()
        self.lbl_counter.setText(self.nav.position_text())
        if cur is None:
            self.lbl_filename.setText("")
            self.lbl_created.setText("")
            self.lbl_created.setStyleSheet("")
            self.image_view.set_image(None)
            for pv in self.preview_views:
                pv.set_image(None)
            return
        self.lbl_filename.setText(cur.name)
        info, is_hd = self._get_image_info(cur)
        self.lbl_created.setText(info if info else "")
        self.lbl_created.setStyleSheet(
            f"color: {'green' if is_hd else 'red'}" if info else ""
        )
        self.image_view.set_image(cur)
        for i, pv in enumerate(self.preview_views):
            pv.set_image(self.nav.image_at(i + 1))

    @staticmethod
    def _get_image_info(path: Path) -> tuple[str, bool]:
        parts: list[str] = []
        is_hd = False
        created = MainWindow._get_creation_date(path)
        if created:
            parts.append(created)
        try:
            with Image.open(path) as img:
                width, height = img.size
            parts.append(f"{width}x{height}")
            if width >= 1280 and height >= 720:
                is_hd = True
        except Exception:
            pass
        return "  ".join(parts), is_hd

    @staticmethod
    def _get_creation_date(path: Path) -> str | None:
        try:
            st = path.stat()
        except Exception:
            return None
        ts = getattr(st, "st_birthtime", None) or st.st_ctime
        try:
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return None

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
        self.on_copy_to(1)

    def on_copy_to(self, n: int) -> None:
        if self._copying_or_trashing:
            return
        cur = self.nav.current()
        if cur is None:
            self.status_bar.showMessage("No image to copy")
            return
        tgt = self.target_roots.get(n)
        if tgt is None:
            QMessageBox.warning(self, "Missing target", f"Select target folder {n} first")
            return
        self._copying_or_trashing = True
        self.status_bar.showMessage(f"Copying to target {n}...")
        try:
            safe_copy(cur, self.source_root if self.source_root else cur.parent, tgt)
            self.status_bar.showMessage(f"Copied to target {n}")
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
        if hasattr(self.image_view, "is_fitted") and not self.image_view.is_fitted():
            self.image_view.reset_zoom()
