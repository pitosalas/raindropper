import unittest
from unittest.mock import MagicMock
from raindropper.actions import assign_bookmarks_to_collections

class TestAssignBookmarksByKeywords(unittest.TestCase):
    def test_engineering_keyword(self):
        client = MagicMock()
        # Simulate collections
        client.fetch_collections.return_value = [
            {"_id": 1, "title": "engineering"},
            {"_id": 2, "title": "design"},
        ]
        # Simulate bookmarks
        client.fetch_bookmarks.return_value = [
            {"_id": 101, "title": "Panama Canal"},
            {"_id": 102, "title": "Modern Architecture"},
        ]
        # Patch input to skip user interaction
        with unittest.mock.patch("builtins.input", return_value="yes"), unittest.mock.patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(client, None)
        # Check that Panama Canal goes to engineering
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Panama Canal" in s and "engineering" in s for s in calls)
        assert any("Modern Architecture" in s and "design" in s for s in calls)

    def test_ai_and_robotics_keywords(self):
        client = MagicMock()
        client.fetch_collections.return_value = [
            {"_id": 1, "title": "ai"},
            {"_id": 2, "title": "robotics"},
        ]
        client.fetch_bookmarks.return_value = [
            {"_id": 201, "title": "OpenAI GPT-4"},
            {"_id": 202, "title": "ROS Navigation Stack"},
        ]
        with unittest.mock.patch("builtins.input", return_value="yes"), unittest.mock.patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(client, None)
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("OpenAI GPT-4" in s and "ai" in s for s in calls)
        assert any("ROS Navigation Stack" in s and "robotics" in s for s in calls)

    def test_programming_python_keyword(self):
        client = MagicMock()
        client.fetch_collections.return_value = [
            {"_id": 1, "title": "programming/python"},
            {"_id": 2, "title": "library"},
        ]
        client.fetch_bookmarks.return_value = [
            {"_id": 301, "title": "Python Decorators"},
            {"_id": 302, "title": "Reference Archive"},
        ]
        with unittest.mock.patch("builtins.input", return_value="yes"), unittest.mock.patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(client, None)
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Python Decorators" in s and "programming/python" in s for s in calls)
        assert any("Reference Archive" in s and "library" in s for s in calls)

    def test_skip_batch(self):
        client = MagicMock()
        client.fetch_collections.return_value = [
            {"_id": 1, "title": "engineering"},
        ]
        client.fetch_bookmarks.return_value = [
            {"_id": 401, "title": "Bridge Design"},
        ]
        with unittest.mock.patch("builtins.input", return_value=""), unittest.mock.patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(client, None)
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Skipped batch." in s for s in calls)

    def test_partial_assignment(self):
        client = MagicMock()
        client.fetch_collections.return_value = [
            {"_id": 1, "title": "engineering"},
            {"_id": 2, "title": "design"},
        ]
        client.fetch_bookmarks.return_value = [
            {"_id": 501, "title": "Bridge Design"},
            {"_id": 502, "title": "UI Layout"},
        ]
        # Only assign the first bookmark
        with unittest.mock.patch("builtins.input", return_value="1"), unittest.mock.patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(client, None)
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Assigned 'Bridge Design'" in s for s in calls)
        assert not any("Assigned 'UI Layout'" in s for s in calls)

    def test_fallback_to_first_collection(self):
        client = MagicMock()
        client.fetch_collections.return_value = [
            {"_id": 1, "title": "misc"},
        ]
        client.fetch_bookmarks.return_value = [
            {"_id": 601, "title": "Unmatched Bookmark"},
        ]
        with unittest.mock.patch("builtins.input", return_value="yes"), unittest.mock.patch("builtins.print") as mock_print:
            assign_bookmarks_to_collections(client, None)
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Unmatched Bookmark" in s and "misc" in s for s in calls)

if __name__ == "__main__":
    unittest.main()
