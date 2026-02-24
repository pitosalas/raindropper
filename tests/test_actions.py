import unittest.mock
from unittest.mock import MagicMock, patch

from raindropper.actions import select_single_use_tags, print_selection_set, select_gibberish_tags, remove_stop_words, select_bookmarks_with_mixed_tags, select_multiword_tags, delete_selection_set_tags, split_multiword_tags, select_nonsolitary_single_use_tags, delete_singleton_tags_from_bookmarks
from raindropper.selection_set import SelectionSet


def make_client(tags):
    client = MagicMock()
    client.fetch_tags.return_value = tags
    return client


def test_select_single_use_tags_adds_only_count_one():
    tags = [{"_id": "a", "count": 1}, {"_id": "b", "count": 3}, {"_id": "c", "count": 1}]
    client = make_client(tags)
    ss = SelectionSet()
    with patch("builtins.print") as mock_print:
        select_single_use_tags(client, ss)
    assert ss.items() == [{"_id": "a", "count": 1}, {"_id": "c", "count": 1}]
    assert ss.kind == "tags"
    mock_print.assert_called_once_with("Added 2 tag(s) to selection set.")


def test_select_single_use_tags_none_found():
    client = make_client([{"_id": "a", "count": 2}])
    ss = SelectionSet()
    with patch("builtins.print") as mock_print:
        select_single_use_tags(client, ss)
    assert ss.items() == []
    mock_print.assert_called_once_with("Added 0 tag(s) to selection set.")


def test_select_gibberish_tags_adds_gibberish():
    tags = [
        {"_id": "tag2023x"},   # letters + digits → gibberish
        {"_id": "xyz"},        # <=3 chars, no vowels → gibberish
        {"_id": "python"},     # real word → not gibberish
        {"_id": "statistics"}, # real word → not gibberish
        {"_id": "a3f"},        # letters + digits → gibberish
    ]
    client = make_client(tags)
    ss = SelectionSet()
    with patch("builtins.print"):
        select_gibberish_tags(client, ss)
    ids = [t["_id"] for t in ss.items()]
    assert "tag2023x" in ids
    assert "xyz" in ids
    assert "a3f" in ids
    assert "python" not in ids
    assert "statistics" not in ids


def test_remove_stop_words_removes_matches():
    ss = SelectionSet()
    ss.add_all([{"_id": "the"}, {"_id": "python"}, {"_id": "and"}], kind="tags")
    with patch("builtins.print") as mock_print:
        remove_stop_words(None, ss)
    assert ss.items() == [{"_id": "python"}]
    mock_print.assert_called_once_with("Removed 2 stop word(s) from selection set.")


def test_remove_stop_words_none_removed():
    ss = SelectionSet()
    ss.add_all([{"_id": "python"}, {"_id": "rails"}], kind="tags")
    with patch("builtins.print") as mock_print:
        remove_stop_words(None, ss)
    assert len(ss.items()) == 2
    mock_print.assert_called_once_with("Removed 0 stop word(s) from selection set.")


def test_select_bookmarks_with_mixed_tags():
    tags = [{"_id": "rare", "count": 1}, {"_id": "common", "count": 10}]
    bookmarks = [
        {"_id": 1, "title": "both", "tags": ["rare", "common"]},
        {"_id": 2, "title": "only rare", "tags": ["rare"]},
        {"_id": 3, "title": "only common", "tags": ["common"]},
        {"_id": 4, "title": "no tags", "tags": []},
    ]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    client.fetch_bookmarks.return_value = bookmarks
    ss = SelectionSet()
    with patch("builtins.print") as mock_print:
        select_bookmarks_with_mixed_tags(client, ss)
    assert len(ss.items()) == 1
    assert ss.items()[0]["_id"] == 1
    assert ss.kind == "bookmarks"
    mock_print.assert_called_once_with("Added 1 bookmark(s) to selection set.")


def test_select_multiword_tags():
    tags = [
        {"_id": "machine learning"},   # two real words → match
        {"_id": "Elections Weather"},  # two real words → match
        {"_id": "python"},             # no space → no match
        {"_id": "tag2023x foo"},       # one gibberish word → no match
    ]
    client = make_client(tags)
    ss = SelectionSet()
    with patch("builtins.print"):
        select_multiword_tags(client, ss)
    ids = [t["_id"] for t in ss.items()]
    assert "machine learning" in ids
    assert "Elections Weather" in ids
    assert "python" not in ids
    assert "tag2023x foo" not in ids


def test_delete_selection_set_tags_confirmed():
    ss = SelectionSet()
    ss.add_all([{"_id": "foo"}, {"_id": "bar"}], kind="tags")
    client = MagicMock()
    with patch("builtins.input", return_value="y"), patch("builtins.print") as mock_print:
        delete_selection_set_tags(client, ss)
    client.delete_tags.assert_called_once_with(["foo", "bar"])
    assert ss.items() == []
    assert any("Deleted 2" in str(c) for c in mock_print.call_args_list)


def test_delete_selection_set_tags_aborted():
    ss = SelectionSet()
    ss.add_all([{"_id": "foo"}], kind="tags")
    client = MagicMock()
    with patch("builtins.input", return_value="n"), patch("builtins.print") as mock_print:
        delete_selection_set_tags(client, ss)
    client.delete_tags.assert_not_called()
    assert len(ss.items()) == 1
    mock_print.assert_called_once_with("Aborted.")


def test_delete_selection_set_tags_empty():
    ss = SelectionSet()
    client = MagicMock()
    with patch("builtins.print") as mock_print:
        delete_selection_set_tags(client, ss)
    client.delete_tags.assert_not_called()
    mock_print.assert_called_once_with("Selection set is empty.")


def test_delete_selection_set_tags_wrong_kind():
    ss = SelectionSet()
    ss.add_all([{"_id": 1, "title": "a bookmark"}], kind="bookmarks")
    client = MagicMock()
    with patch("builtins.print") as mock_print:
        delete_selection_set_tags(client, ss)
    client.delete_tags.assert_not_called()
    mock_print.assert_called_once_with("Selection set does not contain tags.")


def test_split_multiword_tags_updates_bookmarks():
    ss = SelectionSet()
    ss.add_all([{"_id": "machine learning"}], kind="tags")
    client = MagicMock()
    client.fetch_bookmarks_by_tag.return_value = [
        {"_id": 1, "tags": ["machine learning", "python"]},
    ]
    with patch("builtins.input", return_value="y"), patch("builtins.print") as mock_print:
        split_multiword_tags(client, ss)
    client.update_bookmark_tags.assert_called_once_with(1, ["python", "machine", "learning"])
    assert any("Updated 1" in str(c) for c in mock_print.call_args_list)


def test_split_multiword_tags_skips_existing_words():
    ss = SelectionSet()
    ss.add_all([{"_id": "machine learning"}], kind="tags")
    client = MagicMock()
    client.fetch_bookmarks_by_tag.return_value = [
        {"_id": 1, "tags": ["machine learning", "machine"]},  # "machine" already exists
    ]
    with patch("builtins.input", return_value="y"), patch("builtins.print"):
        split_multiword_tags(client, ss)
    client.update_bookmark_tags.assert_called_once_with(1, ["machine", "learning"])


def test_split_multiword_tags_aborted():
    ss = SelectionSet()
    ss.add_all([{"_id": "machine learning"}], kind="tags")
    client = MagicMock()
    with patch("builtins.input", return_value="n"), patch("builtins.print") as mock_print:
        split_multiword_tags(client, ss)
    client.fetch_bookmarks_by_tag.assert_not_called()
    mock_print.assert_called_once_with("Aborted.")


def test_split_multiword_tags_empty_set():
    ss = SelectionSet()
    client = MagicMock()
    with patch("builtins.print") as mock_print:
        split_multiword_tags(client, ss)
    client.fetch_bookmarks_by_tag.assert_not_called()
    mock_print.assert_called_once_with("Selection set is empty.")


def test_split_multiword_tags_prints_progress_dots():
    ss = SelectionSet()
    ss.add_all([{"_id": "machine learning"}], kind="tags")
    client = MagicMock()
    client.fetch_bookmarks_by_tag.return_value = [
        {"_id": 1, "tags": ["machine learning"]},
        {"_id": 2, "tags": ["machine learning"]},
    ]
    with patch("builtins.input", return_value="y"), patch("builtins.print") as mock_print:
        split_multiword_tags(client, ss)
    dot_calls = [c for c in mock_print.call_args_list if c == unittest.mock.call(".", end="", flush=True)]
    assert len(dot_calls) == 2


def test_select_nonsolitary_single_use_tags_includes_tag_with_companions():
    tags = [{"_id": "rare", "count": 1}, {"_id": "common", "count": 5}]
    bookmarks = [{"_id": 1, "tags": ["rare", "common"]}]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    client.fetch_bookmarks.return_value = bookmarks
    ss = SelectionSet()
    with patch("builtins.print"):
        select_nonsolitary_single_use_tags(client, ss)
    assert any(t["_id"] == "rare" for t in ss.items())


def test_select_nonsolitary_single_use_tags_excludes_sole_tag():
    tags = [{"_id": "rare", "count": 1}]
    bookmarks = [{"_id": 1, "tags": ["rare"]}]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    client.fetch_bookmarks.return_value = bookmarks
    ss = SelectionSet()
    with patch("builtins.print") as mock_print:
        select_nonsolitary_single_use_tags(client, ss)
    assert ss.items() == []
    mock_print.assert_called_once_with("Added 0 tag(s) to selection set.")


def test_select_nonsolitary_single_use_tags_no_single_use():
    tags = [{"_id": "common", "count": 5}]
    bookmarks = [{"_id": 1, "tags": ["common"]}]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    client.fetch_bookmarks.return_value = bookmarks
    ss = SelectionSet()
    with patch("builtins.print"):
        select_nonsolitary_single_use_tags(client, ss)
    assert ss.items() == []


def test_print_selection_set_empty():
    ss = SelectionSet()
    with patch("builtins.print") as mock_print:
        print_selection_set(None, ss)
    mock_print.assert_called_once_with("Selection set is empty.")


def test_print_selection_set_with_items():
    ss = SelectionSet()
    ss.add_all([{"_id": "foo"}, {"_id": "bar"}], kind="tags")
    with patch("builtins.print") as mock_print:
        print_selection_set(None, ss)
    calls = [str(c) for c in mock_print.call_args_list]
    assert any("foo" in s for s in calls)
    assert any("bar" in s for s in calls)


def test_print_selection_set_bookmarks_shows_title_and_tags():
    ss = SelectionSet()
    ss.add_all([{"_id": 1, "title": "My Bookmark", "tags": ["alpha", "beta"]}], kind="bookmarks")
    with patch("builtins.print") as mock_print:
        print_selection_set(None, ss)
    output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "My Bookmark" in output
    assert "alpha" in output
    assert "beta" in output


def test_print_selection_set_bookmarks_no_title_falls_back_to_link():
    ss = SelectionSet()
    ss.add_all([{"_id": 2, "link": "https://example.com", "tags": []}], kind="bookmarks")
    with patch("builtins.print") as mock_print:
        print_selection_set(None, ss)
    output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "https://example.com" in output


def test_delete_singleton_tags_confirmed():
    ss = SelectionSet()
    ss.add_all([{"_id": 1, "title": "My Page", "tags": ["rare", "common"]}], kind="bookmarks")
    client = MagicMock()
    client.fetch_tags.return_value = [{"_id": "rare", "count": 1}, {"_id": "common", "count": 5}]
    with patch("builtins.input", return_value="y"), patch("builtins.print"):
        delete_singleton_tags_from_bookmarks(client, ss)
    client.update_bookmark_tags.assert_called_once_with(1, ["common"])


def test_delete_singleton_tags_declined():
    ss = SelectionSet()
    ss.add_all([{"_id": 1, "title": "My Page", "tags": ["rare", "common"]}], kind="bookmarks")
    client = MagicMock()
    client.fetch_tags.return_value = [{"_id": "rare", "count": 1}, {"_id": "common", "count": 5}]
    with patch("builtins.input", return_value="n"), patch("builtins.print"):
        delete_singleton_tags_from_bookmarks(client, ss)
    client.update_bookmark_tags.assert_not_called()


def test_delete_singleton_tags_no_singletons_skips():
    ss = SelectionSet()
    ss.add_all([{"_id": 1, "title": "My Page", "tags": ["common"]}], kind="bookmarks")
    client = MagicMock()
    client.fetch_tags.return_value = [{"_id": "common", "count": 5}]
    with patch("builtins.input") as mock_input, patch("builtins.print"):
        delete_singleton_tags_from_bookmarks(client, ss)
    mock_input.assert_not_called()
    client.update_bookmark_tags.assert_not_called()


def test_delete_singleton_tags_multiple_singletons_per_bookmark():
    ss = SelectionSet()
    ss.add_all([{"_id": 1, "title": "My Page", "tags": ["r1", "r2", "common"]}], kind="bookmarks")
    client = MagicMock()
    client.fetch_tags.return_value = [
        {"_id": "r1", "count": 1}, {"_id": "r2", "count": 1}, {"_id": "common", "count": 5}
    ]
    with patch("builtins.input", side_effect=["y", "n"]), patch("builtins.print"):
        delete_singleton_tags_from_bookmarks(client, ss)
    client.update_bookmark_tags.assert_called_once_with(1, ["r2", "common"])


def test_delete_singleton_tags_empty_set():
    ss = SelectionSet()
    client = MagicMock()
    with patch("builtins.print") as mock_print:
        delete_singleton_tags_from_bookmarks(client, ss)
    mock_print.assert_called_once_with("Selection set is empty.")
    client.update_bookmark_tags.assert_not_called()


def test_delete_singleton_tags_wrong_kind():
    ss = SelectionSet()
    ss.add_all([{"_id": "foo"}], kind="tags")
    client = MagicMock()
    with patch("builtins.print") as mock_print:
        delete_singleton_tags_from_bookmarks(client, ss)
    mock_print.assert_called_once_with("Selection set does not contain bookmarks.")
    client.update_bookmark_tags.assert_not_called()


def test_print_selection_set_bookmarks_no_tags_shows_empty_list():
    ss = SelectionSet()
    ss.add_all([{"_id": 3, "title": "No Tags Here", "tags": []}], kind="bookmarks")
    with patch("builtins.print") as mock_print:
        print_selection_set(None, ss)
    output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "No Tags Here" in output
    assert "[]" in output
