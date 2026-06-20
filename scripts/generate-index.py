from pathlib import Path

ROOTS = [
    "skills",
    "playbooks",
    "knowledge",
    "templates",
    "memory",
]

for root in ROOTS:
    path = Path(root)

    if not path.exists():
        continue

    index = [
        f"# Índice - {root}",
        ""
    ]

    for file in sorted(path.rglob("*.md")):
        if file.name in ("INDEX.md", "README.md"):
            continue

        index.append(f"- {file.relative_to(path)}")

    content = "\n".join(index).rstrip() + "\n"

    (path / "INDEX.md").write_text(
        content,
        encoding="utf-8"
    )
