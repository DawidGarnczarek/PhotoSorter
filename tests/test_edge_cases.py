import tempfile
from pathlib import Path

from photo_sorter import file_operations as fo


def test_target_same_as_source_rejected():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td).resolve()
        (d / "a.jpg").write_bytes(b"a")
        try:
            fo.safe_copy(d / "a.jpg", d, d)
            raise AssertionError()
        except fo.TargetFolderError:
            pass


def test_target_inside_source_rejected():
    with tempfile.TemporaryDirectory() as td:
        src = Path(td).resolve()
        (src / "sub").mkdir()
        tgt = src / "sub" / "target"
        tgt.mkdir()
        (src / "a.jpg").write_bytes(b"a")
        try:
            fo.safe_copy(src / "a.jpg", src, tgt)
            raise AssertionError()
        except fo.TargetFolderError:
            pass
