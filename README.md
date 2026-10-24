# Photo Sorter

A simple desktop app for manual photo selection. Browse images in a source folder, copy selected ones to one of up to 9 target folders (keys 1–9), move unwanted ones to Trash with Backspace. Navigate with arrow keys. Fullscreen with F. Mouse wheel to zoom.

## Setup (development)

```bash
pip install -e .
```

## Run

```bash
photo-sorter
```

### Shortcuts

| Key | Action |
|-----|--------|
| ← / → | Previous / next image |
| 1–9 | Copy current image to target folder N |
| Space | Copy current image to target folder 1 |
| Backspace | Move current image to Trash |
| F | Toggle fullscreen |
| Esc | Exit fullscreen / reset zoom to fit |

## Build standalone `.exe` (Windows)

1. Zainstaluj PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Zbuduj aplikację:
   ```bash
   pyinstaller photo_sorter.spec
   ```
3. Gotowy plik `.exe` znajduje się w katalogu `dist/photo-sorter.exe`.

Użytkownik końcowy nie potrzebuje zainstalowanego Pythona — wystarczy uruchomić `photo-sorter.exe`.

## Requirements

- Python 3.12+
- PySide6
- Pillow
- pillow-heif
- send2trash
