# My To Do - a command line to-do app (version 2)
# Your tasks are saved in todo_data.json, in the same folder as this file.

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


def days_until(task):
    return (date.fromisoformat(task["due"]) - date.today()).days if task["due"] else None


def show_task(number, task):
    tick = "x" if task["done"] else " "
    flags = [
        "★" if task["important"] else "",
        "☀" if task["my_day"] else "",
        f"!{task['priority']}" if task["priority"] != "Medium" else "",
        f"(due {task['due']})" if task["due"] else "",
        "OVERDUE" if is_overdue(task) else "",
        "[note]" if task["notes"] else "",
    ]
    extra = "".join(f"  {f}" for f in flags if f)
    print(f"  {number}. [{tick}] {task['title']}{extra}   <{task['list']}>")


def show_tasks(tasks):
    for number, task in enumerate(tasks, start=1):
        show_task(number, task)


def tasks_in_list(data, name):
    rules = {
        "My Day": lambda t: t["my_day"] and not t["done"],
        "Important": lambda t: t["important"] and not t["done"],
        "Planned": lambda t: bool(t["due"]) and not t["done"],
        "Overdue": is_overdue,
        "Completed": lambda t: t["done"],
    }
    check = rules.get(name, lambda t: t["list"] == name)
    return [t for t in data["tasks"] if check(t)]


def choose_list(data, include_smart=True):
    all_lists = (SMART_LISTS + data["lists"]) if include_smart else data["lists"]
    print("\nYour lists:")
    for number, name in enumerate(all_lists, start=1):
        print(f"  {number}. {name} ({len(tasks_in_list(data, name))})")
    return all_lists[ask_number("Choose a list: ", 1, len(all_lists)) - 1]


def choose_task(data):
    if not data["tasks"]:
        print("You have no tasks yet.")
        return None
    print("\nAll tasks:")
    show_tasks(data["tasks"])
    return data["tasks"][ask_number("Choose a task number: ", 1, len(data["tasks"])) - 1]


def view_list(data):
    name = choose_list(data)
    tasks = tasks_in_list(data, name)
    print(f"\n===== {name} =====")
    if name == "My Day":
        print(date.today().strftime("  %A, %d %B"))
    if not tasks:
        print("  Nothing here. Enjoy your day!")
    show_tasks(tasks)
    print(f"\n  {len(tasks)} task(s), {len([t for t in tasks if t['done']])} done.")


def add_task(data):
    title = input("\nTask name: ").strip()
    if not title:
        print("A task needs a name.")
        return
    task = {
        "title": title, "list": choose_list(data, include_smart=False), "done": False,
        "important": ask_yes_no("Mark as important?"), "my_day": ask_yes_no("Add to My Day?"),
        "due": ask_date("Due date (YYYY-MM-DD) or press Enter to skip: "),
        "priority": ask_priority(), "notes": input("Note (optional): ").strip(),
        "created": date.today().isoformat(),
    }
    data["tasks"].append(task)
    save_data(data)
    print(f"Added '{title}' to {task['list']}.")


def toggle(data, field, msg_on, msg_off):
    # flips a True/False field like done, important, or my_day
    task = choose_task(data)
    if not task:
        return
    task[field] = not task[field]
    if field == "done" and task["done"]:
        task["my_day"] = False  # finished tasks leave My Day
    save_data(data)
    print(msg_on if task[field] else msg_off)


def delete_task(data):
    task = choose_task(data)
    if task and ask_yes_no(f"Delete '{task['title']}' forever?"):
        data["tasks"].remove(task)
        save_data(data)
        print("Task deleted.")


def edit_task(data):
    task = choose_task(data)
    if not task:
        return
    print(f"\nEditing: {task['title']}\n  1. Title   2. Due date   3. Priority   4. Note   5. List")
    choice = ask_number("What do you want to change? ", 1, 5)
    if choice == 1:
        task["title"] = ask_text("New title: ")
    elif choice == 2:
        task["due"] = ask_date("New due date (YYYY-MM-DD), Enter to clear: ")
    elif choice == 3:
        task["priority"] = ask_priority(task["priority"])
    elif choice == 4:
        task["notes"] = input("New note (Enter to clear): ").strip()
    else:
        task["list"] = choose_list(data, include_smart=False)
    save_data(data)
    print("Task updated.")


def view_details(data):
    task = choose_task(data)
    if not task:
        return
    print("\n----- Task details -----")
    print(f"  Title     : {task['title']}  ({task['list']})")
    print(f"  Status    : {'Done' if task['done'] else 'Not done'} | Priority: {task['priority']}")
    print(f"  Important : {'Yes' if task['important'] else 'No'} | My Day: {'Yes' if task['my_day'] else 'No'}")
    print(f"  Created   : {task['created']} | Due: {task['due'] or 'none'}")
    left = days_until(task)
    if left is not None and not task["done"]:
        status = f"overdue by {-left} day(s)" if left < 0 else ("due today" if left == 0 else f"{left} day(s)")
        print(f"  Time left : {status}")
    print(f"  Note      : {task['notes'] or 'none'}")


def sort_tasks(data):
    name = choose_list(data)
    tasks = tasks_in_list(data, name)
    if not tasks:
        print("Nothing to sort in that list.")
        return
    print("\nSort by: 1. Due date   2. Priority   3. Title (A-Z)   4. Newest first")
    choice = ask_number("Choose how to sort: ", 1, 4)
    keys = {
        1: lambda t: (t["due"] == "", t["due"]),
        2: lambda t: -PRIORITIES.index(t["priority"]),
        3: lambda t: t["title"].lower(),
    }
    tasks.sort(key=keys.get(choice, lambda t: t["created"]), reverse=(choice == 4))
    print(f"\n===== {name} (sorted) =====")
    show_tasks(tasks)


def search_tasks(data):
    word = input("\nSearch for: ").strip().lower()
    if not word:
        print("Type something to search for.")
        return
    found = [t for t in data["tasks"] if word in t["title"].lower() or word in t["notes"].lower()]
    print(f"\n{len(found)} match(es):" if found else "No matching tasks.")
    show_tasks(found)


def move_tasks(data, old_list, new_list):
    for task in data["tasks"]:
        if task["list"] == old_list:
            task["list"] = new_list


def create_list(data):
    name = input("\nNew list name: ").strip()
    if not name:
        print("A list needs a name.")
    elif name in data["lists"] or name in SMART_LISTS:
        print("A list with that name already exists.")
    else:
        data["lists"].append(name)
        save_data(data)
        print(f"List '{name}' created.")


def rename_list(data):
    old_name = choose_list(data, include_smart=False)
    new_name = ask_text("New name: ")
    if new_name in data["lists"] or new_name in SMART_LISTS:
        print("A list with that name already exists.")
        return
    data["lists"][data["lists"].index(old_name)] = new_name
    move_tasks(data, old_name, new_name)
    save_data(data)
    print(f"'{old_name}' is now called '{new_name}'.")


def delete_list(data):
    if len(data["lists"]) == 1:
        print("You need at least one list, so this one can't be deleted.")
        return
    old_name = choose_list(data, include_smart=False)
    others = [n for n in data["lists"] if n != old_name]
    count = len([t for t in data["tasks"] if t["list"] == old_name])
    new_home = others[0]
    if count > 0:
        print(f"'{old_name}' has {count} task(s). Where should they go?")
        for i, name in enumerate(others, start=1):
            print(f"  {i}. {name}")
        new_home = others[ask_number("Choose a list: ", 1, len(others)) - 1]
    if ask_yes_no(f"Delete the list '{old_name}'?"):
        move_tasks(data, old_name, new_home)
        data["lists"].remove(old_name)
        save_data(data)
        print(f"List deleted. Its tasks moved to {new_home}.")


def clear_my_day(data):
    count = len([t for t in data["tasks"] if t["my_day"]])
    if count == 0:
        print("My Day is already empty.")
    elif ask_yes_no(f"Remove {count} task(s) from My Day?"):
        for task in data["tasks"]:
            task["my_day"] = False
        save_data(data)
        print("My Day cleared. The tasks are still saved.")


def clear_completed(data):
    finished = [t for t in data["tasks"] if t["done"]]
    if not finished:
        print("There are no completed tasks.")
    elif ask_yes_no(f"Delete {len(finished)} completed task(s) forever?"):
        data["tasks"] = [t for t in data["tasks"] if not t["done"]]
        save_data(data)
        print("Completed tasks deleted.")


def show_statistics(data):
    print("\n===== Statistics =====")
    print(f"  {'List':<16}{'Total':>6}{'Done':>6}{'Pending':>9}{'% Done':>8}")
    print("  " + "-" * 45)
    groups = [(n, [t for t in data["tasks"] if t["list"] == n]) for n in data["lists"]] + [("Total", data["tasks"])]
    for label, items in groups:
        if label == "Total":
            print("  " + "-" * 45)
        done = len([t for t in items if t["done"]])
        pct = round(done * 100 / len(items)) if items else 0
        print(f"  {label:<16}{len(items):>6}{done:>6}{len(items) - done:>9}{pct:>7}%")
    pending = [t for t in data["tasks"] if not t["done"]]
    print(f"\n  Important left: {len([t for t in pending if t['important']])} | High priority: {len([t for t in pending if t['priority'] == 'High'])}")
    print(f"  Overdue tasks : {len([t for t in pending if is_overdue(t)])} | No due date  : {len([t for t in pending if not t['due']])}")


def show_summary(data):
    pending = [t for t in data["tasks"] if not t["done"]]
    overdue = [t for t in pending if is_overdue(t)]
    today = [t for t in pending if days_until(t) == 0]
    soon = [t for t in pending if days_until(t) is not None and 1 <= days_until(t) <= 3]
    print(f"\n===== Summary for {date.today().strftime('%A, %d %B')} =====")
    print(f"  Tasks left: {len(pending)}   |   In My Day: {len([t for t in pending if t['my_day']])}")
    if not (overdue or today or soon):
        print("  Nothing is due in the next 3 days. Nice!")
    for label, group in [("Overdue", overdue), ("Due today", today), ("Due in next 3 days", soon)]:
        if group:
            print(f"\n  {label} ({len(group)}):")
            show_tasks(group)


def export_tasks(data):
    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"MY TO DO - exported on {date.today().isoformat()}\n" + "=" * 40 + "\n")
        for name in data["lists"]:
            tasks = [t for t in data["tasks"] if t["list"] == name]
            f.write(f"\n{name} ({len(tasks)})\n")
            for t in tasks:
                tick = "x" if t["done"] else " "
                due = f" (due {t['due']})" if t["due"] else ""
                note = f"\n        note: {t['notes']}" if t["notes"] else ""
                f.write(f"  [{tick}] {t['title']} - {t['priority']}{due}{note}\n")
    print(f"Exported {len(data['tasks'])} task(s) to {EXPORT_FILE}")


def backup_data(data):
    save_data(data)
    shutil.copy(DATA_FILE, BACKUP_FILE)
    print(f"Backup saved to {BACKUP_FILE}")


def restore_backup(data):
    if not os.path.exists(BACKUP_FILE):
        print("There is no backup yet. Make one first.")
        return
    if not ask_yes_no("This replaces your current tasks with the backup. Continue?"):
        return
    old = load_data(BACKUP_FILE)
    if old is not None:
        data.clear()
        data.update(old)
        save_data(data)
        print(f"Backup restored: {len(data['tasks'])} task(s) loaded.")


def main():
    data = load_data()
    menu = [
        ("View a list", view_list), ("Add a task", add_task),
        ("Complete / un-complete", lambda d: toggle(d, "done", "Completed!", "Marked as not done.")),
        ("Star as important", lambda d: toggle(d, "important", "Starred ★", "Star removed.")),
        ("Add to / remove from My Day", lambda d: toggle(d, "my_day", "Added to My Day ☀", "Removed from My Day.")),
        ("Delete a task", delete_task), ("Create a new list", create_list),
        ("Search tasks", search_tasks), ("Edit a task", edit_task),
        ("View task details", view_details), ("Sort and view tasks", sort_tasks),
        ("Rename a list", rename_list), ("Delete a list", delete_list),
        ("Clear My Day", clear_my_day), ("Delete completed tasks", clear_completed),
        ("Show statistics", show_statistics), ("Today's summary", show_summary),
        ("Export to text file", export_tasks), ("Back up data", backup_data),
        ("Restore from backup", restore_backup),
    ]
    print("\n☀  Welcome to My To Do!")
    show_summary(data)
    try:
        while True:
            pending = len([t for t in data["tasks"] if not t["done"]])
            print(f"\n---------------- MENU ({pending} tasks left) ----------------")
            half = (len(menu) + 1) // 2
            for i in range(half):
                left = f"{i + 1:>2}. {menu[i][0]}".ljust(38)
                right = f"{i + half + 1:>2}. {menu[i + half][0]}" if i + half < len(menu) else ""
                print("  " + left + right)
            print("   0. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Your tasks are saved. Goodbye!")
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(menu):
                menu[int(choice) - 1][1](data)
            else:
                print("Invalid option, try again.")
    except (KeyboardInterrupt, EOFError):
        save_data(data)
        print("\nProgram closed. Your tasks are saved. Goodbye!")


if __name__ == "__main__":
    main()