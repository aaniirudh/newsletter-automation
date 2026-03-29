def get_approved_subject(subject_lines_path: str) -> str:
    try:
        with open(subject_lines_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        lines = ["1. Weekly Newsletter", "2. This Week's Digest", "3. Your Update"]

    subjects = []
    for line in lines:
        parts = line.split(". ", 1)
        subjects.append(parts[1] if len(parts) == 2 else line)

    while True:
        print("\n============================================")
        print("  NEWSLETTER READY FOR REVIEW")
        print("============================================")
        print("Please choose a subject line or enter your own:\n")
        for i, s in enumerate(subjects, 1):
            print(f"  [{i}] {s}")
        print("  [C] Enter custom subject line")
        print()

        choice = input("Your choice: ").strip()

        if choice in [str(i) for i in range(1, len(subjects) + 1)]:
            selected = subjects[int(choice) - 1]
            print(f"\n  Selected: \"{selected}\"")
            return selected
        elif choice.lower() == "c":
            custom = input("Enter your custom subject line: ").strip()
            if custom:
                print(f"\n  Using custom subject: \"{custom}\"")
                return custom
        else:
            print("  Invalid choice. Please try again.")
