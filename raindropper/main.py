import raindropper.actions as actions
from raindropper.client import RaindropClient

MENU_OPTIONS = [
    ("List single-use tags", "list_single_use_tags"),
]


def print_menu():
    # Print numbered menu options plus quit.
    for i, (label, _) in enumerate(MENU_OPTIONS, start=1):
        print(f"  {i}. {label}")
    print("  0. Quit")


def run_menu(client):
    # Loop until user quits; dispatch numeric input to handler.
    while True:
        print_menu()
        choice = input("Pick an option: ").strip()
        if choice == "0" or choice.lower() == "q":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(MENU_OPTIONS):
            _, handler_name = MENU_OPTIONS[int(choice) - 1]
            getattr(actions, handler_name)(client)
        else:
            print(f"Invalid option: {choice!r}")


def main():
    client = RaindropClient()
    run_menu(client)


if __name__ == "__main__":
    main()
