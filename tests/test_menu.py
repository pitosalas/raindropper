import unittest
from unittest.mock import patch, MagicMock

from raindropper.main import run_menu


class TestRunMenu(unittest.TestCase):

    @patch("raindropper.actions.list_single_use_tags")
    @patch("builtins.input", side_effect=["1", "0"])
    def test_valid_option_calls_handler(self, mock_input, mock_handler):
        client = MagicMock()
        run_menu(client)
        mock_handler.assert_called_once_with(client)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["99", "0"])
    def test_invalid_option_prints_error(self, mock_input, mock_print):
        client = MagicMock()
        run_menu(client)
        printed = [str(c) for c in mock_print.call_args_list]
        self.assertTrue(any("Invalid option" in s for s in printed))

    @patch("raindropper.actions.list_single_use_tags")
    @patch("builtins.input", side_effect=["q"])
    def test_quit_with_q(self, mock_input, mock_handler):
        client = MagicMock()
        run_menu(client)
        mock_handler.assert_not_called()


if __name__ == "__main__":
    unittest.main()
