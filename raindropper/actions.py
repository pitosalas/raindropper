import re
import difflib

# ...existing code...

# -*- coding: utf-8 -*-
import re
from raindropper.client import RaindropClient
from raindropper.selection_set import SelectionSet

# Table mapping collection names to keywords (update as needed)
collection_keywords = {
    "productivity": {
        "productivity", "focus", "time", "management", "efficiency", "workflow", "habit", "goal", "task", "calendar", "organize", "self-improvement", "motivation", "routine", "planning", "skills"
    },
    "entrepreneurship": {
        "business", "startup", "entrepreneur", "pivot", "lean", "venture", "capital", "funding", "ipo", "profit", "earnings", "marketing", "buy", "sell", "scale", "scaling", "customer", "market", "successful", "launch", "MVP", "Viable", "salary", "raise", "stripe", "improv", "microsoft", "lotus", "oracle"
    }, 
    "ai/ml": {
        "ai", "ml", "artificial", "intelligence", "machine", "learning", "deep", "neural", "network", "openai", "anthropic", "claude", "llm", "chatgpt", "transformer", "nlp", "vision", "model", "data", "copilot", "training", "inference", "prompt", "RAG", "llama"
    },
    "engineering": {
        "engineering", "engineer", "bridge", "canal", "construction", "infrastructure", "mechanical", "civil", "electrical", "system", "project", "process"
    },
    "design": {
        "design", "designer", "graphics", "graphic", "layout", "ui", "ux", "interface", "visual", "typography", "color", "aesthetics", "sketch", "figma", "adobe", "photoshop", "tinkercad", "fusion", "illustrator", "ui", "ux", "uis", "html", "css", "bootstrap"
    },
    "robotics": {
        "robotics", "robot", "automation", "autonomous", "mechatronics", "servo", "actuator", "sensor", "robotic", "manipulator", "drone", "ros", "navigation", "control", "hardware", "motor", "robotshop", "embedded", "ros2", "topics", "urdf", "arduino", "raspberry", "raspi", "lidar", "teensy", "sparkfun", "adafruit", "waveshare", "sensors", "foxglove", "kalman"
    },
    "how to": {
        "how", "tutorial", "guide", "step", "instruction", "manual", "walkthrough", "tips", "tricks", "faq", "help", "learn", "learning", "explained", "fix", "repair", "explain", "explainer", "hack", "hacks", "diy", "handmade", "buy", "shop", "artisanal"
    },
    "hobbies": {
        "watches", "photography", "photo", "photograph", "hiking", "movies", "television", "cable", "netflix", "jewish", "smithsonian", "arlington", "shir", "vilna"
    }, 
    "software engineering": {
        "automation", "pip", "package", "library", "async", "concurrency", "unittest", "virtualenv", "venv", "import", "module", "pandas", "numpy", "matplotlib", "scipy", "flask", "django", "fastapi", "cli", "shell", "terminal", "repl", "algorithm", "datastructure", "debug", "test", "devops", "REST", "typing", "git", "github", "database", "databases",  "dbms", "programmer", "coder", "developer", "markdown", "docker", "linux", "unix", "mock", "mocking", "tdd", "software", "hardware", "architecture", "object-oriented", "object", "pattern", "ACM", "http", "tcp", "udp", "tdd", "rails", "django", "flask", "fastapi", "php", "coroutines", "co-routines", "heroku", "fly.io", "environment", "applicatoin", "system", "rss", "dotfiles", "volume", "plugins", "server", "aws", "serverless", "plug-ins", "vscode", "authentication", "oauth", "SQL", "jquery", "torrent", "graphql", "ssl", "node", "npm", "bytes", "SOA", "CLI", "refactor", "refactoring", "debugger", "debugging", "postgres", "regexp", "regexpr", "regexper", "sinatra", "rack", "stack", "stacks", "queues", "agile", "scrum", "streamlit", "monitor", "API", "domain", "algorithms", "computer", "monolith", "QR"
    }, 
    "programming": {
        "programming", "code", "coding", "scripting", "script", "interpreter", "function", "class", "variable", "loop", "list", "dict", "set", "tuple", "comprehension", "decorator", "unittest", "virtualenv", "venv", "numpy", "matplotlib", "scipy", "datastructure", "debug", "ruby", "python", "rust", "go", "hash", "programmer", "programmers", "coders", "developers", "coder", "developer", "python3", "function", "method", "variable"
    },
    "academia": {
        "academic", "academics", "teaching", "learning", "brandeis", "university", "grading", "research", "olin", "ashe", "cosi"
    }
}
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at",
    "to", "for", "with", "by", "from", "is", "it", "as", "be", "this",
    "we", "are", "that", "about", "what", "which", "was", "were", "so", "if", "then", "than", "also", "into", "out", "up", "down", "off", "not", "do", "does", "did", "has", "have", "had", "will", "would", "can", "could", "should", "may", "might", "must"
}

def extract_top_words(text, n=3):
    words = re.findall(r"\b\w+\b", text.lower())
    filtered = [w for w in words if w not in STOP_WORDS]
    counts = {}
    for w in filtered:
        counts[w] = counts.get(w, 0) + 1
    return [w for w, _ in sorted(counts.items(), key=lambda x: -x[1])[:n]]

def assign_bookmarks_to_collections(client, selection_set):
    """
    Interactively assign bookmarks from a chosen collection to other collections.
    """
    collections = client.fetch_collections()
    
    # Display available collections
    print("\nAvailable collections:")
    for idx, col in enumerate(collections, start=1):
        print(f"  {idx}. {col.get('title', 'Untitled')} (ID: {col.get('_id')})")
    
    # Prompt user to select a collection
    while True:
        choice = input("\nWhich collection do you want to reorganize? (Enter number or 'x' to cancel): ").strip()
        if choice.lower() == 'x':
            print("Cancelled.")
            return
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(collections):
                source_collection = collections[choice_idx]
                break
            else:
                print(f"Please enter a number between 1 and {len(collections)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    print(f"\nReorganizing collection: {source_collection.get('title', 'Untitled')}")

    unsorted_collection = next((c for c in collections if c.get('title', '').lower() == 'unsorted'), None)

    # All collections are valid targets (bookmarks can stay in the source collection)
    target_collections = collections

    batch_num = 0
    batch_size = 500
    api_limit = 50  # Raindrop API max per request
    
    while True:
        # Fetch enough pages to reach batch_size
        bookmarks = []
        pages_to_fetch = (batch_size + api_limit - 1) // api_limit  # Ceiling division
        
        for i in range(pages_to_fetch):
            page = batch_num * pages_to_fetch + i
            page_bookmarks = client.fetch_bookmarks(
                collection_id=source_collection.get('_id'), 
                page=page, 
                perpage=api_limit
            )
            if not page_bookmarks:
                break
            bookmarks.extend(page_bookmarks)
            if len(bookmarks) >= batch_size:
                bookmarks = bookmarks[:batch_size]
                break
        
        if not bookmarks:
            print(f"No more bookmarks to process in the '{source_collection.get('title', 'selected')}' collection.")
            break

        print(f"\n--- Processing Batch {batch_num + 1} from '{source_collection.get('title', 'selected')}' ({len(bookmarks)} bookmarks) ---")
        proposals = []
        for bookmark in bookmarks:
            title = bookmark.get("title", "")
            body = bookmark.get("body", "")
            tags = " ".join(bookmark.get("tags", []))
            text = f"{title} {body} {tags}".strip()
            top_words = [w.lower() for w in extract_top_words(text, n=5)]

            best_collections = []
            best_score = -1
            
            for collection in target_collections:  # Only consider non-source collections
                cname = collection.get("title", "").lower()
                keywords = set(k.lower() for k in collection_keywords.get(cname, set()))
                score = sum(1 for w in top_words if w in keywords)
                if score > best_score:
                    best_score = score
                    best_collections = [collection]
                elif score == best_score:
                    best_collections.append(collection)

            matched_collection = None
            if len(best_collections) > 1:
                for c in best_collections:
                    cname_parts = c.get("title", "").lower().split('/')
                    if any(part in top_words for part in cname_parts):
                        matched_collection = c
                        break
            
            if not matched_collection and best_collections:
                matched_collection = best_collections[0]
            elif not best_collections:
                # No keyword matches - default to Unsorted or first available collection
                matched_collection = unsorted_collection if unsorted_collection else (target_collections[0] if target_collections else None)
            
            proposals.append({
                "bookmark": bookmark,
                "proposed_collection": matched_collection,
            })

        for idx, proposal in enumerate(proposals, start=1):
            bookmark = proposal["bookmark"]
            collection = proposal["proposed_collection"]
            collection_name = collection.get("title", str(collection.get("_id"))) if collection else "(none)"
            print(f"  {idx}. {bookmark.get('title', str(bookmark.get('_id')))} → {collection_name}")

        user_input = input("Assign (Enter=all, s=skip, nums=partial, q/x=stop): ").strip().lower()

        if user_input in ['q', 'x']:
            print("Stopping.")
            break
        
        if user_input == 's':
            print("Skipped batch.")
            page += 1
            continue

        to_assign_indices = []
        if user_input == "":  # Enter accepts all
            to_assign_indices = list(range(len(proposals)))
        else:
            try:
                parts = re.split(r'[\s,]+', user_input)
                indices = [int(i)-1 for i in parts if i.isdigit() and 0 < int(i) <= len(proposals)]
                if not indices and user_input:
                     raise ValueError("Invalid input")
                to_assign_indices = indices
            except ValueError:
                print("Invalid input. Skipping batch.")
                batch_num += 1
                continue
        
        assigned_count = 0
        skipped_count = 0
        if to_assign_indices:
            for idx in to_assign_indices:
                proposal = proposals[idx]
                bookmark = proposal["bookmark"]
                collection = proposal["proposed_collection"]
                if collection:
                    # Check if bookmark is already in the target collection
                    current_collection_id = bookmark.get("collection", {}).get("$id")
                    target_collection_id = collection["_id"]
                    
                    if current_collection_id == target_collection_id:
                        # Already in the right collection, no need to update
                        skipped_count += 1
                        print(f"Skipped '{bookmark.get('title', '')}' (already in '{collection.get('title', '')}').")
                    else:
                        try:
                            client.update_bookmark_collection(bookmark["_id"], target_collection_id)
                            assigned_count += 1
                            print(f"Assigned '{bookmark.get('title', '')}' to collection '{collection.get('title', '')}.'")
                        except Exception as e:
                            print(f"ERROR: Could not assign bookmark: {e}")
            print(f"Assigned {assigned_count} bookmark(s), skipped {skipped_count} (already in correct collection) in this batch.")
        else:
            if user_input:
                 print("No valid assignments made for this batch.")

        batch_num += 1



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


def select_zero_bookmark_tags(client, selection_set):
    # Select tags that exist but are not used on any bookmark (count == 0).
    tags = client.fetch_tags()
    unused = [t for t in tags if t.get("count", 0) == 0]
    if not unused:
        print("No zero-bookmark tags found.")
        return
    selection_set.add_all(unused, kind="tags")
    print(f"Added {len(unused)} tag(s) to selection set.")


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


def delete_tags_interactively(client, selection_set):
    # Prompt to delete tags in the selection set in groups of 10.
    if not selection_set.items():
        print("Selection set is empty.")
        return
    if selection_set.kind != "tags":
        print("Selection set does not contain tags.")
        return
    tags = selection_set.items()
    deleted = 0
    batch_size = 10
    for batch_start in range(0, len(tags), batch_size):
        batch = tags[batch_start:batch_start + batch_size]
        print(f"\nTags {batch_start + 1}–{batch_start + len(batch)} of {len(tags)}:")
        for i, tag in enumerate(batch, start=1):
            print(f"  {i}. {tag['_id']}")
        raw = input("Delete (numbers, 'a'=all, Enter=skip, 'q'=quit): ").strip().lower()
        if raw == "q":
            break
        if raw == "":
            continue
        if raw == "a":
            to_delete = batch
        else:
            indices = []
            for tok in raw.split():
                if tok.isdigit() and 1 <= int(tok) <= len(batch):
                    indices.append(int(tok) - 1)
            to_delete = [batch[i] for i in indices]
        if to_delete:
            for t in to_delete:
                client.delete_tag_with_cleanup(t["_id"])
            deleted += len(to_delete)
            print(f"Deleted {len(to_delete)} tag(s). ({deleted} total so far)")
    print(f"Deleted {deleted} of {len(tags)} tag(s).")


def _plural_singular_proposals(tags):
    # Return proposals where one tag is a simple plural of another.
    tag_map = {t["_id"]: t.get("count", 0) for t in tags}
    tag_names = set(tag_map)
    proposals = []
    seen = set()
    for name in tag_names:
        candidates = []
        if name.endswith("ies") and len(name) > 3:
            candidates.append(name[:-3] + "y")
        if name.endswith("es") and len(name) > 2:
            candidates.append(name[:-2])
        if name.endswith("s") and len(name) > 2:
            candidates.append(name[:-1])
        for singular in candidates:
            if singular in tag_names and singular != name:
                pair = frozenset([name, singular])
                if pair not in seen:
                    seen.add(pair)
                    proposals.append({
                        "kind": "plural",
                        "source": name,
                        "target": singular,
                        "source_count": tag_map[name],
                        "target_count": tag_map[singular],
                    })
                break
    return proposals


def _similar_stem_proposals(tags, existing_proposals):
    # Return proposals for tag pairs with high string similarity not already proposed.
    existing_pairs = {frozenset([p["source"], p["target"]]) for p in existing_proposals}
    tag_list = [t for t in tags if len(t["_id"]) >= 3]
    proposals = []
    seen = set()
    for i, a in enumerate(tag_list):
        for b in tag_list[i + 1:]:
            pair = frozenset([a["_id"], b["_id"]])
            if pair in existing_pairs or pair in seen:
                continue
            ratio = difflib.SequenceMatcher(None, a["_id"], b["_id"]).ratio()
            if ratio >= 0.85:
                seen.add(pair)
                a_count = a.get("count", 0)
                b_count = b.get("count", 0)
                if a_count >= b_count:
                    source, target = b["_id"], a["_id"]
                    source_count, target_count = b_count, a_count
                else:
                    source, target = a["_id"], b["_id"]
                    source_count, target_count = a_count, b_count
                proposals.append({
                    "kind": "similar",
                    "source": source,
                    "target": target,
                    "source_count": source_count,
                    "target_count": target_count,
                })
    return proposals


def lint_tags(client, selection_set):
    # Fetch all tags, generate plural/similar proposals, present in batches of 10 for user to accept.
    tags = client.fetch_tags()
    plural_props = _plural_singular_proposals(tags)
    similar_props = _similar_stem_proposals(tags, plural_props)
    proposals = plural_props + similar_props
    if not proposals:
        print("No tag lint proposals found.")
        return
    total_merged = 0
    batch_size = 10
    for batch_start in range(0, len(proposals), batch_size):
        batch = proposals[batch_start:batch_start + batch_size]
        print(f"\nProposals {batch_start + 1}–{batch_start + len(batch)} of {len(proposals)}:")
        for i, p in enumerate(batch, start=1):
            print(f"  {i}. [{p['kind']}] MERGE '{p['source']}' → '{p['target']}'  (source: {p['source_count']} uses, target: {p['target_count']} uses)")
        raw = input("Accept (numbers, 'a'=all, Enter=skip, 'q'=quit): ").strip().lower()
        if raw == "q":
            break
        if raw == "":
            continue
        if raw == "a":
            accepted = batch
        else:
            indices = []
            for tok in raw.split():
                if tok.isdigit() and 1 <= int(tok) <= len(batch):
                    indices.append(int(tok) - 1)
            accepted = [batch[i] for i in indices]
        for p in accepted:
            client.merge_tag(p["source"], p["target"])
            total_merged += 1
        print(f"Merged {total_merged} tag(s) so far.")
    print(f"Done. Merged {total_merged} tag(s) total.")


def delete_tag_by_name(client, selection_set):
    # Repeatedly prompt for a tag name; remove it from all bookmarks then delete it.
    while True:
        tag = input("Tag to delete (blank to stop): ").strip()
        if not tag:
            break
        bookmarks = client.fetch_bookmarks_by_tag(tag)
        count = len(bookmarks)
        client.delete_tag_with_cleanup(tag)
        print(f"Deleted '{tag}' from {count} bookmark(s).")


def rename_tag(client, selection_set):
    # Repeatedly prompt for source/target pairs; blank source exits the loop.
    while True:
        source = input("Source tag (blank to stop): ").strip()
        if not source:
            break
        target = input(f"Rename '{source}' to: ").strip()
        if not target:
            print("Skipped: target tag name was blank.")
            continue
        updated = client.merge_tag(source, target)
        print(f"Renamed '{source}' → '{target}': {updated} bookmark(s) updated.")


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
