"""
Notes Manager v2.0
A command-line notes application built with Python.

Concepts used:
  - Functions
  - File handling (read / write to notes.txt)
  - Input validation

Each note is stored on its own line in this format:
    YYYY-MM-DD HH:MM|note text
"""

import os
import textwrap
from datetime import datetime

# ======== Configuration =========

FILE_NAME = "notes.txt"
WIDTH = 64            # total width of the screen layout
NOTE_WIDTH = 40       # width of the note column in the table
MAX_NOTE_LENGTH = 150

# ========= Terminal colors (ANSI codes) ========

os.system("")  # enables colors in the Windows terminal
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"


# ======== Display helpers ========

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title):
    clear_screen()
    print(CYAN + "=" * WIDTH + RESET)
    print(CYAN + BOLD + title.center(WIDTH) + RESET)
    print(CYAN + "=" * WIDTH + RESET)


def show_success(message):
    print(f"\n{GREEN}[SUCCESS]{RESET} {message}")


def show_error(message):
    print(f"\n{RED}[ERROR]{RESET} {message}")


def show_info(message):
    print(f"\n{YELLOW}[INFO]{RESET} {message}")


def pause():
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")


def display_table(rows):
    """rows = list of (number, note_dict). Prints notes as a table."""
    print()
    print(f"{BOLD}{'No.':<5}{'Date & Time':<19}{'Note'}{RESET}")
    print("-" * WIDTH)
    for number, note in rows:
        lines = textwrap.wrap(note["text"], NOTE_WIDTH) or [""]
        print(f"{number:<5}{note['date']:<19}{lines[0]}")
        for extra_line in lines[1:]:
            print(" " * 24 + extra_line)
    print("-" * WIDTH)


# ======== File handling functions ========

def load_notes():
    """Reads notes.txt and returns a list of notes (dictionaries)."""
    if not os.path.exists(FILE_NAME):
        return []
    notes = []
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if "|" in line:
                    date, text = line.split("|", 1)
                else:
                    date, text = "N/A", line
                notes.append({"date": date.strip(), "text": text.strip()})
    except OSError as error:
        show_error(f"Could not read the file: {error}")
    return notes


def save_notes(notes):
    """Writes the complete notes list to notes.txt."""
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            for note in notes:
                file.write(f"{note['date']}|{note['text']}\n")
        return True
    except OSError as error:
        show_error(f"Could not save the file: {error}")
        return False


# ======== Input validation functions ========

def get_non_empty_input(prompt, max_length=MAX_NOTE_LENGTH):
    """Keeps asking until the user enters non-empty text within max_length."""
    while True:
        text = input(f"{YELLOW}{prompt}{RESET}").strip()
        if not text:
            show_error("Input cannot be empty. Please try again.\n")
        elif len(text) > max_length:
            show_error(f"Input is too long (maximum {max_length} characters).\n")
        else:
            return text


def get_valid_number(prompt, minimum, maximum):
    """Keeps asking until the user enters a whole number in the given range."""
    while True:
        value = input(f"{YELLOW}{prompt}{RESET}").strip()
        if not value.isdigit():
            show_error("Please enter numbers only (for example: 1, 2, 3).\n")
            continue
        number = int(value)
        if minimum <= number <= maximum:
            return number
        show_error(f"Number must be between {minimum} and {maximum}.\n")


def ask_yes_no(prompt):
    """Returns True for yes and False for no. Rejects anything else."""
    while True:
        answer = input(f"{YELLOW}{prompt} (yes/no): {RESET}").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        show_error("Please type 'yes' or 'no'.\n")


# ======== Feature functions ========

def add_note():
    print_header("ADD A NEW NOTE")
    notes = load_notes()
    text = get_non_empty_input("\nWrite your note: ")
    if any(note["text"].lower() == text.lower() for note in notes):
        show_error("This note already exists.")
        return
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    notes.append({"date": date, "text": text})
    if save_notes(notes):
        show_success("Note saved successfully!")


def view_notes():
    print_header("ALL NOTES")
    notes = load_notes()
    if not notes:
        show_info("You have no notes yet. Add your first note from the menu.")
        return
    display_table(list(enumerate(notes, start=1)))
    print(f"Total notes: {len(notes)}")


def search_notes():
    print_header("SEARCH NOTES")
    notes = load_notes()
    if not notes:
        show_info("You have no notes to search.")
        return
    keyword = get_non_empty_input("\nEnter a keyword: ", 50).lower()
    rows = [
        (number, note)
        for number, note in enumerate(notes, start=1)
        if keyword in note["text"].lower()
    ]
    if not rows:
        show_info(f"No notes found for '{keyword}'.")
        return
    display_table(rows)
    print(f"Found {len(rows)} note(s).")


def edit_note():
    print_header("EDIT A NOTE")
    notes = load_notes()
    if not notes:
        show_info("You have no notes to edit.")
        return
    display_table(list(enumerate(notes, start=1)))
    number = get_valid_number(
        f"\nEnter the note number to edit (1-{len(notes)}): ", 1, len(notes)
    )
    print(f"\nCurrent text: {notes[number - 1]['text']}")
    new_text = get_non_empty_input("Enter the new text: ")
    notes[number - 1]["text"] = new_text
    notes[number - 1]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if save_notes(notes):
        show_success("Note updated successfully!")


def delete_note():
    print_header("DELETE A NOTE")
    notes = load_notes()
    if not notes:
        show_info("You have no notes to delete.")
        return
    display_table(list(enumerate(notes, start=1)))
    number = get_valid_number(
        f"\nEnter the note number to delete (1-{len(notes)}): ", 1, len(notes)
    )
    if ask_yes_no(f"Delete note {number}?"):
        removed = notes.pop(number - 1)
        if save_notes(notes):
            show_success(f"Deleted: {removed['text']}")
    else:
        show_info("Deletion cancelled.")


def clear_notes():
    print_header("CLEAR ALL NOTES")
    notes = load_notes()
    if not notes:
        show_info("There are no notes to clear.")
        return
    if ask_yes_no(f"\nThis will delete all {len(notes)} notes. Continue?"):
        if save_notes([]):
            show_success("All notes have been deleted.")
    else:
        show_info("Operation cancelled.")


# ======== Menu ========

def show_menu():
    print_header("NOTES MANAGER  |  v2.0")
    print(f"  Total notes: {len(load_notes())}")
    print("-" * WIDTH)
    print("  [1]  Add a new note")
    print("  [2]  View all notes")
    print("  [3]  Search notes")
    print("  [4]  Edit a note")
    print("  [5]  Delete a note")
    print("  [6]  Clear all notes")
    print("  [7]  Exit")
    print("-" * WIDTH)


def main():
    actions = {
        1: add_note,
        2: view_notes,
        3: search_notes,
        4: edit_note,
        5: delete_note,
        6: clear_notes,
    }
    while True:
        show_menu()
        choice = get_valid_number("Enter your choice (1-7): ", 1, 7)
        if choice == 7:
            print(f"\n{GREEN}Thank you for using Notes Manager. Goodbye!{RESET}\n")
            break
        actions[choice]()
        pause()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{GREEN}Program closed. Goodbye!{RESET}\n")