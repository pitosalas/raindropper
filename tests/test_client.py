import os
import unittest
from unittest.mock import patch, MagicMock

from raindropper.client import RaindropClient


class TestRaindropClient(unittest.TestCase):

    @patch.dict(os.environ, {"RAINDROP_TOKEN": "test-token"})
    @patch("raindropper.client.time.sleep")
    @patch("raindropper.client.requests.request")
    def test_fetch_tags_returns_items(self, mock_request, mock_sleep):
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": [{"_id": "python", "count": 1}]}
        mock_request.return_value = mock_response

        client = RaindropClient()
        tags = client.fetch_tags()

        self.assertEqual(tags, [{"_id": "python", "count": 1}])
        mock_response.raise_for_status.assert_called_once()
        mock_sleep.assert_called_once_with(0.5)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_token_raises(self):
        os.environ.pop("RAINDROP_TOKEN", None)
        with self.assertRaises(KeyError):
            RaindropClient()

    @patch.dict(os.environ, {"RAINDROP_TOKEN": "test-token"})
    @patch("raindropper.client.time.sleep")
    @patch("raindropper.client.requests.request")
    def test_fetch_tags_empty_items(self, mock_request, mock_sleep):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client = RaindropClient()
        tags = client.fetch_tags()

        self.assertEqual(tags, [])


    @patch.dict(os.environ, {"RAINDROP_TOKEN": "test-token"})
    @patch("raindropper.client.time.sleep")
    @patch("raindropper.client.requests.request")
    def test_fetch_bookmarks_interrupt_returns_partial(self, mock_request, mock_sleep):
        page1 = MagicMock()
        page1.json.return_value = {"items": [{"_id": 1}] * 50}
        # Second page raises KeyboardInterrupt
        mock_request.side_effect = [page1, KeyboardInterrupt()]
        client = RaindropClient()
        with patch("builtins.print") as mock_print:
            result = client.fetch_bookmarks()
        assert len(result) == 50
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        assert "Interrupted" in printed
        assert "50" in printed


if __name__ == "__main__":
    unittest.main()
