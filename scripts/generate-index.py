from pathlib import Path

ROOTS = [
    "skills",
    "playbooks",
    "knowledge",
    "templates",
]

for root in ROOTS:
    path = Path(root)

    if not path.exists():
        continue

    index = [f"# Índice - {root}\n"]

    for file in sorted(path.rglob("*.md")):
        if file.name == "INDEX.md":
            continue

        index.append(f"- {file.relative_to(path)}")

    (path / "INDEX.md").write_text(
        "\n".join(index),
        encoding="utf-8"
    )