import unittest.mock
from unittest.mock import MagicMock, patch

from raindropper.actions import select_single_use_tags, print_selection_set, select_gibberish_tags, remove_stop_words, select_bookmarks_with_mixed_tags, select_multiword_tags, delete_selection_set_tags, split_multiword_tags, select_nonsolitary_single_use_tags, delete_singleton_tags_from_bookmarks, delete_tags_interactively, select_zero_bookmark_tags, rename_tag, delete_tag_by_name
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


def test_delete_tags_interactively_empty_set():
    ss = SelectionSet()
    client = MagicMock()
    with patch("builtins.print") as mock_print:
        delete_tags_interactively(client, ss)
    mock_print.assert_called_once_with("Selection set is empty.")
    client.delete_tags.assert_not_called()


def test_delete_tags_interactively_wrong_kind():
    ss = SelectionSet()
    ss.add_all([{"_id": 1, "title": "bm", "tags": []}], kind="bookmarks")
    client = MagicMock()
    with patch("builtins.print") as mock_print:
        delete_tags_interactively(client, ss)
    mock_print.assert_called_once_with("Selection set does not contain tags.")
    client.delete_tags.assert_not_called()


def test_delete_tags_interactively_all_confirmed():
    ss = SelectionSet()
    ss.add_all([{"_id": "alpha"}, {"_id": "beta"}], kind="tags")
    client = MagicMock()
    with patch("builtins.input", return_value="a"), patch("builtins.print") as mock_print:
        delete_tags_interactively(client, ss)
    assert client.delete_tag_with_cleanup.call_count == 2
    client.delete_tag_with_cleanup.assert_any_call("alpha")
    client.delete_tag_with_cleanup.assert_any_call("beta")
    assert any("Deleted 2 of 2" in str(c) for c in mock_print.call_args_list)


def test_delete_tags_interactively_all_declined():
    ss = SelectionSet()
    ss.add_all([{"_id": "alpha"}, {"_id": "beta"}], kind="tags")
    client = MagicMock()
    with patch("builtins.input", return_value=""), patch("builtins.print") as mock_print:
        delete_tags_interactively(client, ss)
    client.delete_tag_with_cleanup.assert_not_called()
    assert any("Deleted 0 of 2" in str(c) for c in mock_print.call_args_list)


def test_delete_tags_interactively_mixed():
    ss = SelectionSet()
    ss.add_all([{"_id": "alpha"}, {"_id": "beta"}, {"_id": "gamma"}], kind="tags")
    client = MagicMock()
    # "1 3" selects alpha (index 1) and gamma (index 3) from a single batch
    with patch("builtins.input", return_value="1 3"), patch("builtins.print") as mock_print:
        delete_tags_interactively(client, ss)
    assert client.delete_tag_with_cleanup.call_count == 2
    client.delete_tag_with_cleanup.assert_any_call("alpha")
    client.delete_tag_with_cleanup.assert_any_call("gamma")
    assert any("Deleted 2 of 3" in str(c) for c in mock_print.call_args_list)


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


def test_select_zero_bookmark_tags_adds_unused():
    tags = [{"_id": "unused", "count": 0}, {"_id": "used", "count": 3}]
    client = make_client(tags)
    ss = SelectionSet()
    with patch("builtins.print") as mock_print:
        select_zero_bookmark_tags(client, ss)
    assert ss.items() == [{"_id": "unused", "count": 0}]
    assert ss.kind == "tags"
    mock_print.assert_called_once_with("Added 1 tag(s) to selection set.")


def test_select_zero_bookmark_tags_none_found():
    tags = [{"_id": "used", "count": 2}]
    client = make_client(tags)
    ss = SelectionSet()
    with patch("builtins.print") as mock_print:
        select_zero_bookmark_tags(client, ss)
    assert ss.items() == []
    mock_print.assert_called_once_with("No zero-bookmark tags found.")


def test_select_zero_bookmark_tags_mixed():
    tags = [
        {"_id": "a", "count": 0},
        {"_id": "b", "count": 1},
        {"_id": "c", "count": 0},
    ]
    client = make_client(tags)
    ss = SelectionSet()
    with patch("builtins.print"):
        select_zero_bookmark_tags(client, ss)
    ids = [t["_id"] for t in ss.items()]
    assert ids == ["a", "c"]


def test_rename_tag_single():
    client = MagicMock()
    client.merge_tag.return_value = 3
    with patch("builtins.input", side_effect=["old", "new", ""]), patch("builtins.print") as mock_print:
        rename_tag(client, SelectionSet())
    client.merge_tag.assert_called_once_with("old", "new")
    assert any("old" in str(c) and "new" in str(c) and "3" in str(c) for c in mock_print.call_args_list)


def test_rename_tag_multiple():
    client = MagicMock()
    client.merge_tag.side_effect = [2, 1]
    with patch("builtins.input", side_effect=["a", "b", "c", "d", ""]), patch("builtins.print"):
        rename_tag(client, SelectionSet())
    assert client.merge_tag.call_count == 2
    client.merge_tag.assert_any_call("a", "b")
    client.merge_tag.assert_any_call("c", "d")


def test_rename_tag_blank_source_exits():
    client = MagicMock()
    with patch("builtins.input", return_value=""), patch("builtins.print"):
        rename_tag(client, SelectionSet())
    client.merge_tag.assert_not_called()


def test_delete_tag_by_name_single():
    client = MagicMock()
    client.fetch_bookmarks_by_tag.return_value = [{"_id": 1}, {"_id": 2}]
    with patch("builtins.input", side_effect=["mytag", ""]), patch("builtins.print") as mock_print:
        delete_tag_by_name(client, SelectionSet())
    client.delete_tag_with_cleanup.assert_called_once_with("mytag")
    assert any("mytag" in str(c) and "2" in str(c) for c in mock_print.call_args_list)


def test_delete_tag_by_name_multiple():
    client = MagicMock()
    client.fetch_bookmarks_by_tag.side_effect = [[{"_id": 1}], []]
    with patch("builtins.input", side_effect=["a", "b", ""]), patch("builtins.print"):
        delete_tag_by_name(client, SelectionSet())
    assert client.delete_tag_with_cleanup.call_count == 2
    client.delete_tag_with_cleanup.assert_any_call("a")
    client.delete_tag_with_cleanup.assert_any_call("b")


def test_delete_tag_by_name_blank_exits():
    client = MagicMock()
    with patch("builtins.input", return_value=""), patch("builtins.print"):
        delete_tag_by_name(client, SelectionSet())
    client.delete_tag_with_cleanup.assert_not_called()


def test_rename_tag_blank_target_skips():
    client = MagicMock()
    with patch("builtins.input", side_effect=["old", "", ""]), patch("builtins.print") as mock_print:
        rename_tag(client, SelectionSet())
    client.merge_tag.assert_not_called()
    assert any("Skipped" in str(c) for c in mock_print.call_args_list)
