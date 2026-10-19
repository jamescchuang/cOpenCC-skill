# /// script
# requires-python = ">=3.10"
# ///
"""打包 cOpenCC skill：產生上傳用 zip，並同步 repo 內各平台的專案層級副本。

產出：
  dist/copencc.zip         上傳到 claude.ai / Claude Desktop / ChatGPT
  .claude/skills/copencc/  Claude Code 在本 repo 開啟時使用
  .agents/skills/copencc/  Codex、Antigravity 在本 repo 開啟時使用

用法：
  uv run tools/package_skill.py
  uv run tools/package_skill.py -o x.zip --no-sync
"""
import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "copencc"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
PROJECT_COPIES = [ROOT / ".claude" / "skills" / SKILL_NAME, ROOT / ".agents" / "skills" / SKILL_NAME]
EXCLUDE_DIRS = {"__pycache__", ".venv"}
EXCLUDE_SUFFIXES = {".pyc"}


def skill_files() -> list[Path]:
    return sorted(
        p for p in SKILL_DIR.rglob("*")
        if p.is_file()
        and not EXCLUDE_DIRS.intersection(p.relative_to(SKILL_DIR).parts)
        and p.suffix not in EXCLUDE_SUFFIXES
    )


def build_zip(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    # zip 內以 skill 名稱為唯一的最上層目錄：copencc/SKILL.md
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in skill_files():
            arcname = Path(SKILL_NAME) / p.relative_to(SKILL_DIR)
            zf.write(p, arcname.as_posix())
            print(f"  + {arcname.as_posix()}")
    print(f"已產生 {output}")


def sync_copies() -> None:
    for dest in PROJECT_COPIES:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(SKILL_DIR, dest, ignore=shutil.ignore_patterns(*EXCLUDE_DIRS, "*.pyc"))
        print(f"已同步 {dest.relative_to(ROOT)}")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "dist" / f"{SKILL_NAME}.zip")
    parser.add_argument("--no-sync", action="store_true", help="不同步專案層級副本")
    args = parser.parse_args()

    if not (SKILL_DIR / "SKILL.md").is_file():
        print(f"找不到 {SKILL_DIR / 'SKILL.md'}", file=sys.stderr)
        return 1

    build_zip(args.output)
    if not args.no_sync:
        sync_copies()
    return 0


if __name__ == "__main__":
    sys.exit(main())
