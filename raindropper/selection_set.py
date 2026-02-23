class SelectionSet:
    # In-memory accumulator of items across actions; holds tags or bookmarks, not both.

    def __init__(self):
        self._items = []
        self.kind = None  # "tags" or "bookmarks"

    def add_all(self, items, kind):
        # Clear and switch type if kind differs; then extend with new items.
        if self.kind != kind:
            self._items = []
            self.kind = kind
        self._items.extend(items)

    def items(self):
        # Return the current list of items.
        return list(self._items)

    def clear(self):
        # Reset the set to empty and clear the type.
        self._items = []
        self.kind = None
