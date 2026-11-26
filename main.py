import json
import os
import shutil
from datetime import date, timedelta

FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(FOLDER, "todo_data.json")
BACKUP_FILE = os.path.join(FOLDER, "todo_backup.json")
EXPORT_FILE = os.path.join(FOLDER, "todo_export.txt")

# these lists fill themselves, so you can't add tasks to them directly
SMART_LISTS = ["My Day", "Important", "Planned", "Overdue", "Completed"]
PRIORITIES = ["Low", "Medium", "High"]


def fix_task(task):
    # tasks saved by version 1 might miss newer fields, so add defaults
    defaults = {
        "title": "Untitled", "list": "Tasks", "done": False,
        "important": False, "my_day": False, "due": "",
        "priority": "Medium", "notes": "", "created": date.today().isoformat(),
    }
    for key, val in defaults.items():
        task.setdefault(key, val)


def load_data(path=DATA_FILE):
    data = {"lists": ["Tasks"], "tasks": []}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            if path == DATA_FILE:
                # keep a copy of the broken file so nothing gets lost
                shutil.copy(DATA_FILE, DATA_FILE + ".broken")
                print("Data file couldn't be read, starting fresh (saved todo_data.json.broken).")
            else:
                print("Backup file couldn't be read.")
                return None
    data.setdefault("lists", ["Tasks"])
    data.setdefault("tasks", [])
    for task in data["tasks"]:
        fix_task(task)
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def ask_yes_no(question):
    return input(question + " (y/n): ").strip().lower() == "y"


def ask_number(question, low, high):
    # keep asking until we get a whole number in the range
    while True:
        try:
            number = int(input(question))
            if low <= number <= high:
                return number
            print(f"Please enter a number from {low} to {high}.")
        except ValueError:
            print("That is not a number. Try again.")


def ask_text(question):
    while True:
        text = input(question).strip()
        if text:
            return text
        print("This cannot be empty.")


def ask_date(question):
    # pressing Enter means "no date"
    while True:
        text = input(question).strip()
        if text == "":
            return ""
        try:
            date.fromisoformat(text)
            return text
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD, for example 2026-12-31.")


def ask_priority(current="Medium"):
    print("Priority: 1. Low   2. Medium   3. High")
    answer = input(f"Choose 1-3 or press Enter to keep {current}: ").strip()
    return PRIORITIES[int(answer) - 1] if answer in ("1", "2", "3") else current


def is_overdue(task):
    return bool(task["due"] and not task["done"] and task["due"] < date.today().isoformat())
