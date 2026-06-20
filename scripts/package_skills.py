"""
Empacota cada skills/<nome>/ em um .zip individual, pronto para upload
manual em claude.ai (Settings > Capabilities > Skills).

claude.ai não sincroniza skills via GitHub -- o upload do .zip é sempre
manual. Este script só automatiza a parte de "gerar o zip certo".

Uso:
    python3 scripts/package_skills.py [--output dist]
"""

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    zip_path = output_dir / f"{skill_dir.name}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in skill_dir.rglob("*"):
            if file.is_file():
                # Mantém o nome da pasta da skill como raiz dentro do zip,
                # que é o formato esperado pelo upload de Custom Skills.
                arcname = Path(skill_dir.name) / file.relative_to(skill_dir)
                zf.write(file, arcname)

    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist", help="Pasta de saída (padrão: dist/)")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    if not SKILLS_DIR.exists():
        raise SystemExit(f"Pasta {SKILLS_DIR} não existe.")

    skill_dirs = [d for d in sorted(SKILLS_DIR.iterdir()) if d.is_dir() and (d / "SKILL.md").exists()]
    if not skill_dirs:
        raise SystemExit("Nenhuma skill encontrada para empacotar.")

    print(f"Empacotando {len(skill_dirs)} skill(s) em {output_dir}/...")
    for skill_dir in skill_dirs:
        zip_path = package_skill(skill_dir, output_dir)
        size_kb = zip_path.stat().st_size / 1024
        print(f"  {zip_path.relative_to(ROOT)} ({size_kb:.1f} KB)")

    print("\nPronto. Para usar em claude.ai: Settings > Capabilities > Skills > Upload.")


if __name__ == "__main__":
    main()
