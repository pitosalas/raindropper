# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch
from raindropper.actions import assign_bookmarks_to_collections
from raindropper.selection_set import SelectionSet

class AssignBookmarksTest(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.selection_set = SelectionSet()

        # Define a standard set of collections for all tests
        self.collections = [
            {"_id": 1, "title": "AI/ML"},
            {"_id": 2, "title": "Productivity"},
            {"_id": 3, "title": "Engineering"},
            {"_id": 99, "title": "Unsorted"},
        ]
        self.client.fetch_collections.return_value = self.collections

    @patch("builtins.input", side_effect=[""]) # User presses Enter to assign all
    def test_assign_all_in_batch(self, mock_input):
        """Test that all bookmarks in a batch are assigned when user hits Enter."""
        bookmarks = [
            {"_id": 101, "title": "Intro to Machine Learning", "tags": ["ai"], "body": ""},
            {"_id": 102, "title": "How to be Productive", "tags": ["focus"], "body": ""},
        ]
        self.client.fetch_bookmarks.side_effect = [bookmarks, []] # First call returns bookmarks, second ends loop

        with patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(self.client, self.selection_set)

        # Verify that update_bookmark_collection was called for each bookmark
        self.assertEqual(self.client.update_bookmark_collection.call_count, 2)

        # Check that the correct assignments were made
        self.client.update_bookmark_collection.assert_any_call(101, 1) # Bookmark 101 -> AI/ML (ID 1)
        self.client.update_bookmark_collection.assert_any_call(102, 2) # Bookmark 102 -> Productivity (ID 2)

        # Check confirmation message
        mock_print.assert_any_call("Assigned 2 bookmark(s) in this batch.")

    @patch("builtins.input", side_effect=["s"]) # User presses 's' to skip
    def test_skip_batch(self, mock_input):
        """Test that no bookmarks are assigned when the user skips a batch."""
        bookmarks_page1 = [{"_id": 101, "title": "A bookmark", "tags": [], "body": ""}]
        bookmarks_page2 = [] # End of bookmarks
        self.client.fetch_bookmarks.side_effect = [bookmarks_page1, bookmarks_page2]

        with patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(self.client, self.selection_set)

        # Verify that no assignments were made
        self.client.update_bookmark_collection.assert_not_called()
        mock_print.assert_any_call("Skipped batch.")

    @patch("builtins.input", side_effect=["2"]) # User selects the 2nd bookmark
    def test_assign_partial_batch(self, mock_input):
        """Test that only selected bookmarks in a batch are assigned."""
        bookmarks = [
            {"_id": 101, "title": "About AI", "tags": ["ai"], "body": ""},
            {"_id": 102, "title": "About Productivity", "tags": ["focus"], "body": ""},
            {"_id": 103, "title": "Something else", "tags": [], "body": ""},
        ]
        self.client.fetch_bookmarks.side_effect = [bookmarks, []]

        with patch("builtins.print"):
            assign_bookmarks_to_collections(self.client, self.selection_set)

        # Verify that update was called only once
        self.assertEqual(self.client.update_bookmark_collection.call_count, 1)

        # Check that the correct bookmark was assigned
        self.client.update_bookmark_collection.assert_called_once_with(102, 2) # Bookmark 102 -> Productivity (ID 2)

    @patch("builtins.input", side_effect=["q"]) # User presses 'q' to quit
    def test_quit_stops_processing(self, mock_input):
        """Test that the process stops when the user quits."""
        bookmarks = [{"_id": 101, "title": "A bookmark", "tags": [], "body": ""}]
        self.client.fetch_bookmarks.side_effect = [bookmarks, []]

        with patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(self.client, self.selection_set)

        # Verify no assignments were made
        self.client.update_bookmark_collection.assert_not_called()
        mock_print.assert_any_call("Stopping.")

    @patch("builtins.input", side_effect=[""])
    def test_no_match_defaults_to_unsorted(self, mock_input):
        """Test that a bookmark with no keyword matches defaults to 'Unsorted'."""
        bookmarks = [{"_id": 101, "title": "Some random topic", "tags": ["xyz"], "body": ""}]
        self.client.fetch_bookmarks.side_effect = [bookmarks, []]

        with patch("builtins.print"):
            assign_bookmarks_to_collections(self.client, self.selection_set)

        # Verify it was assigned to the 'Unsorted' collection (ID 99)
        self.client.update_bookmark_collection.assert_called_once_with(101, 99)

if __name__ == "__main__":
    unittest.main()
