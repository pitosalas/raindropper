Status values:
- **Status**: `not started` / `in progress` / `done`
- **Tests written**: `no` / `yes`
- **Tests passing**: `n/a` / `no` / `yes`

## F13 — Select Single-Use Tags That Are Not the Only Tag on a Bookmark
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Fetch all tags and all bookmarks. Filter to tags with count == 1. For each such tag, find the bookmark that uses it. Include the tag in the selection set only if that bookmark also has at least one other tag. Add matching tags to the selection set (kind="tags"). Print how many were added.

---

## F12 — Progress Dots for Multi-Step Operations
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: In actions that loop over multiple items (e.g. `split_multiword_tags` iterating over bookmarks, `fetch_bookmarks` paginating), print a `.` without a newline after each iteration so the user can see progress. Print a newline when the loop completes.

---
<!-- ACTIVE FEATURES ABOVE THIS LINE | COMPLETED FEATURES BELOW -->
---

## F01 — Raindrop API Client
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Authenticate with the Raindrop.io API using a token from the `RAINDROP_TOKEN` env var and provide a reusable client for fetching tags and bookmarks.

---

## F02 — Interactive CLI Menu
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Print a numbered list of available options and prompt the user to pick one by typing a number. Dispatch to the selected action.

---

## F03 — Selection Set
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Maintain an in-memory selection set that holds either tags or bookmarks (Raindrop bookmark objects), but not both at once. The set tracks its current type (`"tags"` or `"bookmarks"`). When `add_all(items, kind)` is called with a different kind than the current type, the set clears first then loads the new items. Actions pass the set through the session; it is not persisted to disk.

---

## F04 — Select Single-Use Tags into Selection Set
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Fetch all tags from Raindrop.io, filter to those used on exactly one bookmark, and add them to the selection set.

---

## F05 — Print Selection Set
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Print the current contents of the selection set as a plain numbered list. If the set is empty, print a message saying so.

---

## F06 — Select Gibberish Tags into Selection Set
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Fetch all tags from Raindrop.io, filter to those whose `_id` contains digits mixed with letters, or is 3 chars or fewer with no vowels. Add matching tags to the selection set. Print how many tags were added.

---

## F07 — Remove Stop Words from Selection Set
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Filter the selection set in-place, removing items whose `_id` matches a built-in list of common English stop words (e.g. "the", "a", "and", "of", "in"). Print how many items were removed.

---

## F08 — Select Bookmarks with Single-Use Tags and Other Tags
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Fetch all bookmarks from Raindrop.io. Filter to those that have at least one single-use tag (count == 1) AND at least one other tag (count > 1). Add the matching bookmarks to the selection set (kind="bookmarks"). Print how many bookmarks were added.

---

## F09 — Delete Tags in Selection Set
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: For each tag in the selection set (kind must be "tags"), call the Raindrop.io API to delete it. Before deleting, prompt "About to delete N tag(s). Proceed? [y/N]" and abort if the user does not confirm. Print a summary of how many were deleted. Abort with a message if the selection set is empty or not of kind "tags".

---

## F10 — Select Multi-Word Tags into Selection Set
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: Fetch all tags from Raindrop.io. Filter to those whose `_id` contains at least one space AND where none of the individual words are gibberish. Add matching tags to the selection set (kind="tags"). Print how many were added.

---

## F11 — Split Multi-Word Tags on Bookmarks
**Priority**: High
**Status**: done | Tests written: yes | Tests passing: yes
**Description**: For each multi-word tag in the selection set (kind must be "tags"), find all bookmarks that use that tag via the Raindrop API. For each such bookmark, remove the multi-word tag and add each individual word as a separate tag, but only if that word is not already a tag on the bookmark. Update the bookmark via the API. Print a summary of how many bookmarks were updated. Prompt for confirmation before making any changes.

---
