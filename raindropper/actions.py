import re


def _is_gibberish(word):
    # Flag tags with digits mixed into letters, or short (<=3 char) tags with no vowels.
    if re.search(r"[a-z]", word.lower()) and re.search(r"\d", word):
        return True
    if len(word) <= 3 and not re.search(r"[aeiou]", word.lower()):
        return True
    return False


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at",
    "to", "for", "with", "by", "from", "is", "it", "as", "be", "this",
}


def select_single_use_tags(client, selection_set):
    # Filter tags used exactly once and add them to the selection set.
    tags = client.fetch_tags()
    single_use = [t for t in tags if t.get("count", 0) == 1]
    selection_set.add_all(single_use, kind="tags")
    print(f"Added {len(single_use)} tag(s) to selection set.")


def select_gibberish_tags(client, selection_set):
    # Fetch all tags and add those that look like gibberish to the selection set.
    tags = client.fetch_tags()
    gibberish = [t for t in tags if _is_gibberish(t["_id"])]
    selection_set.add_all(gibberish, kind="tags")
    print(f"Added {len(gibberish)} gibberish tag(s) to selection set.")


def remove_stop_words(client, selection_set):
    # Remove items from the selection set whose _id is a common stop word.
    before = selection_set.items()
    kind = selection_set.kind
    kept = [t for t in before if t["_id"].lower() not in STOP_WORDS]
    selection_set.clear()
    if kept:
        selection_set.add_all(kept, kind=kind)
    print(f"Removed {len(before) - len(kept)} stop word(s) from selection set.")


def select_bookmarks_with_mixed_tags(client, selection_set):
    # Select bookmarks that have at least one single-use tag and one non-single-use tag.
    tags = client.fetch_tags()
    single_use_names = {t["_id"] for t in tags if t.get("count", 0) == 1}
    multi_use_names = {t["_id"] for t in tags if t.get("count", 0) > 1}
    bookmarks = client.fetch_bookmarks()
    matches = [
        b for b in bookmarks
        if any(tag in single_use_names for tag in b.get("tags", []))
        and any(tag in multi_use_names for tag in b.get("tags", []))
    ]
    selection_set.add_all(matches, kind="bookmarks")
    print(f"Added {len(matches)} bookmark(s) to selection set.")


def select_multiword_tags(client, selection_set):
    # Select tags that contain spaces and where no individual word is gibberish.
    tags = client.fetch_tags()
    matches = [
        t for t in tags
        if " " in t["_id"] and not any(_is_gibberish(w) for w in t["_id"].split())
    ]
    selection_set.add_all(matches, kind="tags")
    print(f"Added {len(matches)} multi-word tag(s) to selection set.")


def split_multiword_tags(client, selection_set):
    # For each multi-word tag in the selection set, split it into words on all affected bookmarks.
    if not selection_set.items():
        print("Selection set is empty.")
        return
    if selection_set.kind != "tags":
        print("Selection set does not contain tags.")
        return
    multiword = [t for t in selection_set.items() if " " in t["_id"]]
    if not multiword:
        print("No multi-word tags in selection set.")
        return
    confirm = input(f"About to split {len(multiword)} multi-word tag(s) across their bookmarks. Proceed? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return
    updated = 0
    for tag in multiword:
        tag_name = tag["_id"]
        words = tag_name.split()
        bookmarks = client.fetch_bookmarks_by_tag(tag_name)
        for bookmark in bookmarks:
            current = bookmark.get("tags", [])
            new_tags = [t for t in current if t != tag_name]
            for word in words:
                if word not in new_tags:
                    new_tags.append(word)
            client.update_bookmark_tags(bookmark["_id"], new_tags)
            print(".", end="", flush=True)
            updated += 1
    print()
    print(f"Updated {updated} bookmark(s).")


def select_nonsolitary_single_use_tags(client, selection_set):
    # Select single-use tags that appear on bookmarks which also have other tags.
    tags = client.fetch_tags()
    single_use = {t["_id"]: t for t in tags if t.get("count", 0) == 1}
    bookmarks = client.fetch_bookmarks()
    tag_to_bookmark_tag_counts = {}
    for bookmark in bookmarks:
        for tag in bookmark.get("tags", []):
            if tag in single_use:
                tag_to_bookmark_tag_counts[tag] = len(bookmark.get("tags", []))
    matches = [
        single_use[name] for name, count in tag_to_bookmark_tag_counts.items()
        if count > 1
    ]
    selection_set.add_all(matches, kind="tags")
    print(f"Added {len(matches)} tag(s) to selection set.")


def delete_selection_set_tags(client, selection_set):
    # Delete all tags in the selection set from Raindrop after confirmation.
    if not selection_set.items():
        print("Selection set is empty.")
        return
    if selection_set.kind != "tags":
        print("Selection set does not contain tags.")
        return
    tag_ids = [t["_id"] for t in selection_set.items()]
    confirm = input(f"About to delete {len(tag_ids)} tag(s). Proceed? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return
    client.delete_tags(tag_ids)
    selection_set.clear()
    print(f"Deleted {len(tag_ids)} tag(s).")


def delete_singleton_tags_from_bookmarks(client, selection_set):
    # For each bookmark in the selection set, prompt to delete any singleton tags.
    if not selection_set.items():
        print("Selection set is empty.")
        return
    if selection_set.kind != "bookmarks":
        print("Selection set does not contain bookmarks.")
        return
    tags = client.fetch_tags()
    singleton_names = {t["_id"] for t in tags if t.get("count", 0) == 1}
    deleted_total = 0
    bookmarks_changed = 0
    for bookmark in selection_set.items():
        title = bookmark.get("title") or bookmark.get("link") or str(bookmark.get("_id", "?"))
        current_tags = bookmark.get("tags", [])
        singletons = [t for t in current_tags if t in singleton_names]
        if not singletons:
            continue
        print(f"\n{title} {current_tags}")
        tags_to_remove = []
        for tag in singletons:
            answer = input(f"  Delete singleton tag '{tag}'? [y/N] ").strip().lower()
            if answer == "y":
                tags_to_remove.append(tag)
        if tags_to_remove:
            new_tags = [t for t in current_tags if t not in tags_to_remove]
            client.update_bookmark_tags(bookmark["_id"], new_tags)
            deleted_total += len(tags_to_remove)
            bookmarks_changed += 1
    print(f"\nDeleted {deleted_total} singleton tag(s) across {bookmarks_changed} bookmark(s).")


def print_selection_set(client, selection_set):
    # Print each item in the selection set as a numbered list.
    items = selection_set.items()
    if not items:
        print("Selection set is empty.")
        return
    if selection_set.kind == "bookmarks":
        for i, item in enumerate(items, start=1):
            title = item.get("title") or item.get("link") or str(item.get("_id", "?"))
            tags = item.get("tags", [])
            print(f"{i}. {title} {tags}")
    else:
        for i, item in enumerate(items, start=1):
            print(f"{i}. {item.get('_id', str(item))}")
