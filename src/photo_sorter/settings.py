"""Settings management for Photo Sorter."""

from __future__ import annotations

import json
from pathlib import Path

APP_NAME = "photo-sorter"
SETTINGS_FILE = "settings.json"


class Settings:
    """Simple settings storage for last selected folders."""

    def __init__(self, app_data_dir: Path | None = None) -> None:
        if app_data_dir is None:
            app_data_dir = Path.home() / "Library" / "Application Support" / "PhotoSorter"
        self.app_data_dir = app_data_dir
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        self.settings_path = self.app_data_dir / SETTINGS_FILE
        self._data: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if not self.settings_path.exists():
            return {}
        try:
            with self.settings_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {str(k): str(v) for k, v in data.items()}
        except Exception:
            pass
        return {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str | None) -> None:
        if value is None:
            self._data.pop(key, None)
        else:
            self._data[key] = value
        try:
            with self.settings_path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass
