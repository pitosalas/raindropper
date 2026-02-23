from raindropper.selection_set import SelectionSet


def test_add_all_and_items():
    ss = SelectionSet()
    ss.add_all([{"_id": "a"}, {"_id": "b"}], kind="tags")
    assert ss.items() == [{"_id": "a"}, {"_id": "b"}]


def test_add_all_accumulates_same_kind():
    ss = SelectionSet()
    ss.add_all([{"_id": "a"}], kind="tags")
    ss.add_all([{"_id": "b"}], kind="tags")
    assert len(ss.items()) == 2


def test_add_all_clears_on_kind_switch():
    ss = SelectionSet()
    ss.add_all([{"_id": "a"}], kind="tags")
    ss.add_all([{"title": "x"}], kind="bookmarks")
    assert ss.items() == [{"title": "x"}]
    assert ss.kind == "bookmarks"


def test_kind_is_set():
    ss = SelectionSet()
    assert ss.kind is None
    ss.add_all([{"_id": "a"}], kind="tags")
    assert ss.kind == "tags"


def test_clear():
    ss = SelectionSet()
    ss.add_all([{"_id": "a"}], kind="tags")
    ss.clear()
    assert ss.items() == []
    assert ss.kind is None


def test_items_returns_copy():
    ss = SelectionSet()
    ss.add_all([{"_id": "a"}], kind="tags")
    result = ss.items()
    result.append({"_id": "b"})
    assert len(ss.items()) == 1
