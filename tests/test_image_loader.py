import tempfile
from pathlib import Path

from PIL import Image

from photo_sorter import image_loader as il


def test_load_basic():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "img.png"
        img = Image.new("RGB", (100, 50), color="red")
        img.save(p)
        loaded = il.load_image(p)
        assert loaded.size == (100, 50)
