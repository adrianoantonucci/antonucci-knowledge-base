from pathlib import Path

areas = [
    "skills",
    "playbooks",
    "knowledge",
    "templates",
    "branding",
    "memory",
]

content = [
    "# Estatísticas",
    ""
]

for area in areas:
    path = Path(area)

    if not path.exists():
        continue

    total = len(list(path.rglob("*.md")))

    content.append(
        f"- {area}: {total} arquivos"
    )

Path("STATS.md").write_text(
    "\n".join(content).rstrip() + "\n",
    encoding="utf-8"
)
