import json
import os
import time
import requests

RAINDROP_API = "https://api.raindrop.io/rest/v1"
RATE_DELAY = 0.5


class RaindropClient:
    # Reads RAINDROP_TOKEN from env; crashes if missing.

    def __init__(self):
        self.token = os.environ["RAINDROP_TOKEN"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _call(self, method, path, **kwargs):
        # Make an API request and enforce rate limiting.
        response = requests.request(method, f"{RAINDROP_API}{path}", headers=self.headers, **kwargs)
        response.raise_for_status()
        time.sleep(RATE_DELAY)
        return response

    def fetch_bookmarks(self):
        # Returns all bookmark objects from the Raindrop API using pagination.
        # A KeyboardInterrupt stops the loop early and returns what was collected.
        bookmarks = []
        page = 0
        perpage = 50
        try:
            while True:
                response = self._call("GET", "/raindrops/0", params={"perpage": perpage, "page": page})
                items = response.json().get("items", [])
                bookmarks.extend(items)
                print(".", end="", flush=True)
                if len(items) < perpage:
                    print()
                    break
                page += 1
        except KeyboardInterrupt:
            print(f"\nInterrupted — {len(bookmarks)} bookmark(s) fetched so far.")
        return bookmarks

    def fetch_bookmarks_by_tag(self, tag):
        # Returns all bookmarks that have the given tag.
        response = self._call(
            "GET", "/raindrops/0",
            params={"search": json.dumps([{"key": "tag", "val": tag}]), "perpage": 50},
        )
        return response.json().get("items", [])

    def update_bookmark_tags(self, bookmark_id, tags):
        # Replace the tags on a bookmark with the given list.
        self._call("PUT", f"/raindrop/{bookmark_id}", json={"tags": tags})

    def delete_tags(self, tag_ids):
        # Delete a list of tags by name via the Raindrop API.
        self._call("DELETE", "/tags", json={"tags": tag_ids})

    def delete_tag_with_cleanup(self, tag_name):
        # Remove tag_name from all bookmarks that use it, then delete the tag.
        bookmarks = self.fetch_bookmarks_by_tag(tag_name)
        for bookmark in bookmarks:
            current = bookmark.get("tags", [])
            new_tags = [t for t in current if t != tag_name]
            self.update_bookmark_tags(bookmark["_id"], new_tags)
            print(".", end="", flush=True)
        if bookmarks:
            print()
        self.delete_tags([tag_name])

    def merge_tag(self, source_tag, target_tag):
        # Replace source_tag with target_tag on all bookmarks that use it, then delete source_tag.
        bookmarks = self.fetch_bookmarks_by_tag(source_tag)
        updated = 0
        for bookmark in bookmarks:
            current = bookmark.get("tags", [])
            if target_tag not in current:
                new_tags = [t for t in current if t != source_tag] + [target_tag]
                self.update_bookmark_tags(bookmark["_id"], new_tags)
                updated += 1
        self.delete_tags([source_tag])
        return updated

    def fetch_tags(self):
        # Returns list of tag objects from the Raindrop API.
        response = self._call("GET", "/tags")
        return response.json().get("items", [])
