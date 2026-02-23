import unittest
from unittest.mock import patch, MagicMock

from raindropper.main import run_menu
from raindropper.selection_set import SelectionSet


class TestRunMenu(unittest.TestCase):

    @patch("raindropper.actions.select_single_use_tags")
    @patch("builtins.input", side_effect=["1", "0"])
    def test_valid_option_calls_handler(self, mock_input, mock_handler):
        client = MagicMock()
        ss = SelectionSet()
        run_menu(client, ss)
        mock_handler.assert_called_once_with(client, ss)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["99", "0"])
    def test_invalid_option_prints_error(self, mock_input, mock_print):
        client = MagicMock()
        ss = SelectionSet()
        run_menu(client, ss)
        printed = [str(c) for c in mock_print.call_args_list]
        self.assertTrue(any("Invalid option" in s for s in printed))

    @patch("raindropper.actions.select_single_use_tags")
    @patch("builtins.input", side_effect=["q"])
    def test_quit_with_q(self, mock_input, mock_handler):
        client = MagicMock()
        ss = SelectionSet()
        run_menu(client, ss)
        mock_handler.assert_not_called()


if __name__ == "__main__":
    unittest.main()
