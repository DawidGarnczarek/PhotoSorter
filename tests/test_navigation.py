from pathlib import Path

from photo_sorter.navigation import Navigation


def test_navigation_basic():
    imgs = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]
    nav = Navigation(imgs)
    assert nav.count() == 3
    assert nav.position_text() == "1 / 3"
    assert nav.current() == Path("a.jpg")
    assert nav.next()
    assert nav.position_text() == "2 / 3"
    assert nav.current() == Path("b.jpg")
    assert nav.prev()
    assert nav.position_text() == "1 / 3"


def test_navigation_bounds():
    imgs = [Path("a.jpg")]
    nav = Navigation(imgs)
    assert not nav.prev()
    assert nav.position_text() == "1 / 1"
    assert not nav.next()


def test_remove_current():
    imgs = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]
    nav = Navigation(imgs)
    nav.next()  # at b
    assert nav.current() == Path("b.jpg")
    assert nav.remove_current()
    assert nav.count() == 2
    assert nav.current() == Path("c.jpg")
