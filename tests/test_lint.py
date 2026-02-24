from unittest.mock import MagicMock, patch, call

from raindropper.actions import _plural_singular_proposals, _similar_stem_proposals, lint_tags


def make_tag(name, count=1):
    return {"_id": name, "count": count}


# --- plural/singular ---

def test_plural_singular_simple_s():
    tags = [make_tag("book", 5), make_tag("books", 2)]
    props = _plural_singular_proposals(tags)
    assert len(props) == 1
    assert props[0]["source"] == "books"
    assert props[0]["target"] == "book"
    assert props[0]["kind"] == "plural"


def test_plural_singular_ies_to_y():
    tags = [make_tag("party", 3), make_tag("parties", 1)]
    props = _plural_singular_proposals(tags)
    sources = [p["source"] for p in props]
    assert "parties" in sources


def test_plural_singular_es():
    tags = [make_tag("bus", 4), make_tag("buses", 1)]
    props = _plural_singular_proposals(tags)
    sources = [p["source"] for p in props]
    assert "buses" in sources


def test_plural_singular_no_duplicate_pairs():
    tags = [make_tag("book", 5), make_tag("books", 2)]
    props = _plural_singular_proposals(tags)
    pairs = [frozenset([p["source"], p["target"]]) for p in props]
    assert len(pairs) == len(set(pairs))


def test_plural_singular_no_match():
    tags = [make_tag("python", 3), make_tag("rails", 2)]
    props = _plural_singular_proposals(tags)
    assert props == []


# --- similar stem ---

def test_similar_stem_finds_close_pair():
    tags = [make_tag("machine-learning", 3), make_tag("machinelearning", 1)]
    props = _similar_stem_proposals(tags, [])
    assert len(props) == 1
    assert props[0]["source"] == "machinelearning"
    assert props[0]["target"] == "machine-learning"


def test_similar_stem_skips_already_proposed():
    tags = [make_tag("book", 5), make_tag("books", 2)]
    existing = [{"source": "books", "target": "book"}]
    props = _similar_stem_proposals(tags, existing)
    assert all(
        not (p["source"] in ("book", "books") and p["target"] in ("book", "books"))
        for p in props
    )


def test_similar_stem_low_similarity_not_emitted():
    tags = [make_tag("python", 3), make_tag("javascript", 2)]
    props = _similar_stem_proposals(tags, [])
    assert props == []


# --- lint_tags action ---

def test_lint_tags_no_proposals():
    client = MagicMock()
    client.fetch_tags.return_value = [make_tag("python", 3), make_tag("rails", 2)]
    with patch("builtins.print") as mock_print:
        lint_tags(client, None)
    mock_print.assert_any_call("No tag lint proposals found.")
    client.merge_tag.assert_not_called()


def test_lint_tags_accept_all():
    tags = [make_tag("book", 5), make_tag("books", 2), make_tag("cat", 3), make_tag("cats", 1)]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    with patch("builtins.input", return_value="a"), patch("builtins.print"):
        lint_tags(client, None)
    assert client.merge_tag.call_count == 2


def test_lint_tags_quit_first_batch():
    tags = [make_tag("book", 5), make_tag("books", 2)]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    with patch("builtins.input", return_value="q"), patch("builtins.print"):
        lint_tags(client, None)
    client.merge_tag.assert_not_called()


def test_lint_tags_skip_batch():
    tags = [make_tag("book", 5), make_tag("books", 2)]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    with patch("builtins.input", return_value=""), patch("builtins.print"):
        lint_tags(client, None)
    client.merge_tag.assert_not_called()


def test_lint_tags_accept_by_number():
    tags = [make_tag("book", 5), make_tag("books", 2), make_tag("cat", 3), make_tag("cats", 1)]
    client = MagicMock()
    client.fetch_tags.return_value = tags
    # Accept only proposal 1
    with patch("builtins.input", return_value="1"), patch("builtins.print"):
        lint_tags(client, None)
    assert client.merge_tag.call_count == 1
