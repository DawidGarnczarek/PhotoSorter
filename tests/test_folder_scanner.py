import tempfile
from pathlib import Path

from photo_sorter.folder_scanner import scan_folder


def test_scan_basic():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td).resolve()
        (d / "a.jpg").write_bytes(b"abc")
        (d / "b.PNG").write_bytes(b"def")
        (d / "c.txt").write_bytes(b"ghi")
        (d / ".hidden.jpg").write_bytes(b"hidden")
        (d / "sub").mkdir()
        (d / "sub" / "d.heic").write_bytes(b"heicdata")

        res = scan_folder(d)
        names = [p.name for p in res]
        assert "a.jpg" in names
        assert "b.PNG" in names
        assert "d.heic" in names
        assert ".hidden.jpg" not in names
        assert "c.txt" not in names


def test_scan_sorting():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td).resolve()
        (d / "B.jpg").write_bytes(b"b")
        (d / "a.jpg").write_bytes(b"a")
        (d / "A.JPG").write_bytes(b"A")
        res = scan_folder(d)
        rels = [p.resolve().relative_to(d).as_posix() for p in res]
        assert rels == sorted(rels, key=str.lower)
