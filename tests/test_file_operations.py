import tempfile
from pathlib import Path

from photo_sorter import file_operations as fo


def test_safe_copy_preserves_structure():
    with tempfile.TemporaryDirectory() as srcd, tempfile.TemporaryDirectory() as tgtd:
        src = Path(srcd).resolve()
        tgt = Path(tgtd).resolve()
        (src / "sub").mkdir()
        (src / "sub" / "img.jpg").write_bytes(b"hello")

        res = fo.safe_copy(src / "sub" / "img.jpg", src, tgt)
        assert res == (tgt / "sub" / "img.jpg").resolve()
        assert (tgt / "sub" / "img.jpg").resolve().read_bytes() == b"hello"
