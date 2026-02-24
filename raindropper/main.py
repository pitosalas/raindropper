import raindropper.actions as actions
from dotenv import load_dotenv
from raindropper.client import RaindropClient
from raindropper.selection_set import SelectionSet

load_dotenv()

MENU_OPTIONS = [
    ("Select single-use tags", "select_single_use_tags"),
    ("Select single-use tags with other tags", "select_nonsolitary_single_use_tags"),
    ("Select gibberish tags", "select_gibberish_tags"),
    ("Select multi-word tags", "select_multiword_tags"),
    ("Select bookmarks with mixed tags", "select_bookmarks_with_mixed_tags"),
    ("Remove stop words", "remove_stop_words"),
    ("Split multi-word tags on bookmarks", "split_multiword_tags"),
    ("Delete tags in selection set", "delete_selection_set_tags"),
    ("Delete singleton tags from bookmarks", "delete_singleton_tags_from_bookmarks"),
]


def print_menu():
    # Print numbered menu options plus shortcut keys.
    for i, (label, _) in enumerate(MENU_OPTIONS, start=1):
        print(f"  {i}. {label}")
    print("  p. Print selection set")
    print("  x. Quit")


def run_menu(client, selection_set):
    # Loop until user quits; dispatch numeric input or shortcut to handler.
    while True:
        print_menu()
        choice = input("Pick an option: ").strip().lower()
        if choice == "x":
            break
        if choice == "p":
            actions.print_selection_set(client, selection_set)
        elif choice.isdigit() and 1 <= int(choice) <= len(MENU_OPTIONS):
            _, handler_name = MENU_OPTIONS[int(choice) - 1]
            getattr(actions, handler_name)(client, selection_set)
        else:
            print(f"Invalid option: {choice!r}")


def main():
    client = RaindropClient()
    selection_set = SelectionSet()
    run_menu(client, selection_set)


if __name__ == "__main__":
    main()
