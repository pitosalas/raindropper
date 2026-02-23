import os
import unittest
from unittest.mock import patch, MagicMock

from raindropper.client import RaindropClient


class TestRaindropClient(unittest.TestCase):

    @patch.dict(os.environ, {"RAINDROP_TOKEN": "test-token"})
    @patch("raindropper.client.requests.get")
    def test_fetch_tags_returns_items(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": [{"tag": "python", "count": 1}]}
        mock_get.return_value = mock_response

        client = RaindropClient()
        tags = client.fetch_tags()

        self.assertEqual(tags, [{"tag": "python", "count": 1}])
        mock_response.raise_for_status.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_token_raises(self):
        os.environ.pop("RAINDROP_TOKEN", None)
        with self.assertRaises(KeyError):
            RaindropClient()

    @patch.dict(os.environ, {"RAINDROP_TOKEN": "test-token"})
    @patch("raindropper.client.requests.get")
    def test_fetch_tags_empty_items(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = RaindropClient()
        tags = client.fetch_tags()

        self.assertEqual(tags, [])


if __name__ == "__main__":
    unittest.main()
