def show_statistics(data):
    print("\n===== Statistics =====")
    print(f"  {'List':<16}{'Total':>6}{'Done':>6}{'Pending':>9}{'% Done':>8}")
    print("  " + "-" * 45)

    groups = [
        (n, [t for t in data["tasks"] if t["list"] == n])
        for n in data["lists"]
    ] + [("Total", data["tasks"])]

    for label, items in groups:
        if label == "Total":
            print("  " + "-" * 45)

        done = len([t for t in items if t["done"]])
        pct = round(done * 100 / len(items)) if items else 0

        print(f"  {label:<16}{len(items):>6}{done:>6}{len(items) - done:>9}{pct:>7}%")

def show_summary(data):
    pending = [t for t in data["tasks"] if not t["done"]]
    overdue = [t for t in pending if is_overdue(t)]
    today = [t for t in pending if days_until(t) == 0]
    soon = [
        t for t in pending
        if days_until(t) is not None
        and 1 <= days_until(t) <= 3
    ]

def export_tasks(data):
    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        f.write(
            f"MY TO DO - exported on {date.today().isoformat()}\n"
            + "=" * 40 + "\n"
        )

        for name in data["lists"]:
            tasks = [
                t for t in data["tasks"]
                if t["list"] == name
            ]

            f.write(f"\n{name} ({len(tasks)})\n")

            for t in tasks:
                tick = "x" if t["done"] else " "
                due = f" (due {t['due']})" if t["due"] else ""
                note = f"\n        note: {t['notes']}" if t["notes"] else ""

                f.write(
                    f"  [{tick}] {t['title']} - "
                    f"{t['priority']}{due}{note}\n"
                )

    print(f"Exported {len(data['tasks'])} task(s) to {EXPORT_FILE}")

def backup_data(data):
    save_data(data)
    shutil.copy(DATA_FILE, BACKUP_FILE)
    print(f"Backup saved to {BACKUP_FILE}")


shutil.copy(DATA_FILE, BACKUP_FILE)

def restore_backup(data):
    if not os.path.exists(BACKUP_FILE):
        print("There is no backup yet. Make one first.")
        return

    if not ask_yes_no(
        "This replaces your current tasks with the backup. Continue?"
    ):
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
    ("View a list", view_list),
    ("Add a task", add_task),
    ("Complete / un-complete",
     lambda d: toggle(d, "done", "Completed!", "Marked as not done.")),
    ("Star as important",
     lambda d: toggle(d, "important", "Starred ★", "Star removed.")),
    ("Add to / remove from My Day",
     lambda d: toggle(d, "my_day", "Added to My Day ☀",
                      "Removed from My Day.")),
    ("Delete a task", delete_task),
    ("Create a new list", create_list),
    ("Search tasks", search_tasks),
    ("Edit a task", edit_task),
    ("View task details", view_details),
    ("Sort and view tasks", sort_tasks),
    ("Rename a list", rename_list),
    ("Delete a list", delete_list),
    ("Clear My Day", clear_my_day),
    ("Delete completed tasks", clear_completed),
    ("Show statistics", show_statistics),
    ("Today's summary", show_summary),
    ("Export to text file", export_tasks),
    ("Back up data", backup_data),
    ("Restore from backup", restore_backup),
]

while True:
    pending = len([t for t in data["tasks"] if not t["done"]])
    print(f"\n---------------- MENU ({pending} tasks left) ----------------")

elif choice.isdigit() and 1 <= int(choice) <= len(menu):
    menu[int(choice) - 1][1](data)

if choice == "0":
    print("Your tasks are saved. Goodbye!")
    break

if __name__ == "__main__":
    main()

