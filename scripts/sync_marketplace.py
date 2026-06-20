"""
Valida o frontmatter de cada skills/<nome>/SKILL.md e sincroniza
a lista de skills dentro de .claude-plugin/marketplace.json.

Uso:
    python3 scripts/sync_marketplace.py            # valida e atualiza
    python3 scripts/sync_marketplace.py --check    # só valida, não escreve (para CI)
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


class SkillError(Exception):
    pass


def parse_frontmatter(text: str, skill_path: Path) -> dict:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise SkillError(f"{skill_path}: frontmatter YAML ausente (precisa começar com '---').")

    raw = match.group(1)
    data = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise SkillError(f"{skill_path}: linha de frontmatter inválida: {line!r}")
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_skill(skill_dir: Path) -> dict:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise SkillError(f"{skill_dir}: SKILL.md não encontrado.")

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text, skill_md)

    name = fm.get("name")
    description = fm.get("description")

    if not name:
        raise SkillError(f"{skill_md}: campo 'name' ausente no frontmatter.")
    if name != skill_dir.name:
        raise SkillError(
            f"{skill_md}: 'name: {name}' não bate com o nome da pasta '{skill_dir.name}'."
        )
    if not description:
        raise SkillError(f"{skill_md}: campo 'description' ausente no frontmatter.")
    if len(description) < 30:
        raise SkillError(
            f"{skill_md}: 'description' muito curta ({len(description)} chars) — "
            "inclua o que a skill faz E quando usá-la."
        )

    line_count = len(text.splitlines())
    if line_count > 500:
        print(
            f"  aviso: {skill_md} tem {line_count} linhas (recomendado manter < 500; "
            "considere mover detalhes para references/)."
        )

    return {"name": name, "description": description, "path": f"skills/{skill_dir.name}"}


def discover_skills() -> list[dict]:
    if not SKILLS_DIR.exists():
        raise SkillError(f"Pasta {SKILLS_DIR} não existe.")

    skills = []
    errors = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        try:
            skills.append(validate_skill(entry))
        except SkillError as e:
            errors.append(str(e))

    if errors:
        print("Erros de validação encontrados:\n")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)

    if not skills:
        raise SkillError(f"Nenhuma skill válida encontrada em {SKILLS_DIR}.")

    return skills


def sync_marketplace(skills: list[dict], check_only: bool) -> bool:
    if not MARKETPLACE_PATH.exists():
        raise SkillError(f"{MARKETPLACE_PATH} não existe. Crie o manifesto base primeiro.")

    manifest = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))

    if not manifest.get("plugins"):
        raise SkillError("marketplace.json não tem nenhum plugin declarado.")

    plugin = manifest["plugins"][0]
    new_skill_paths = [s["path"] for s in skills]

    changed = plugin.get("skills") != new_skill_paths
    plugin["skills"] = new_skill_paths

    skill_names = ", ".join(s["name"] for s in skills)
    new_description = (
        f"Skills pessoais: {skill_names}."
    )
    if plugin.get("description") != new_description:
        changed = True
        plugin["description"] = new_description

    if changed and not check_only:
        MARKETPLACE_PATH.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    return changed


def main() -> None:
    check_only = "--check" in sys.argv

    print(f"Validando skills em {SKILLS_DIR}...")
    skills = discover_skills()
    for s in skills:
        print(f"  ok: {s['name']} ({s['path']})")

    changed = sync_marketplace(skills, check_only)

    if changed and check_only:
        print(
            "\nmarketplace.json está desatualizado em relação às skills atuais. "
            "Rode 'python3 scripts/sync_marketplace.py' (sem --check) para corrigir."
        )
        raise SystemExit(1)
    elif changed:
        print(f"\n{MARKETPLACE_PATH} atualizado.")
    else:
        print(f"\n{MARKETPLACE_PATH} já está sincronizado.")


if __name__ == "__main__":
    main()
