# /// script
# requires-python = ">=3.10"
# ///
"""把 cOpenCC skill 安裝到各 AI 代理工具的 skills 目錄。

用法：
  uv run tools/install.py                      # 安裝到所有支援的工具（使用者層級）
  uv run tools/install.py claude codex         # 只裝指定工具
  uv run tools/install.py --project ~/myproj   # 裝到某個專案（Claude Code + Codex/Antigravity）
  uv run tools/install.py --uninstall          # 移除

也可用 python 直接執行：python tools/install.py ...
"""
import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "copencc"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
HOME = Path.home()


def antigravity_dir() -> Path:
    # Antigravity IDE 使用 ~/.gemini/antigravity/skills；新版改為 ~/.gemini/config/skills
    legacy = HOME / ".gemini" / "antigravity"
    if legacy.is_dir():
        return legacy / "skills"
    return HOME / ".gemini" / "config" / "skills"


USER_TARGETS = {
    "claude": lambda: HOME / ".claude" / "skills",        # Claude Code
    "codex": lambda: HOME / ".agents" / "skills",         # OpenAI Codex CLI / IDE / ChatGPT 桌面版
    "antigravity": antigravity_dir,                       # Google Antigravity
}
PROJECT_SUBDIRS = [Path(".claude") / "skills", Path(".agents") / "skills"]


def install(dest_root: Path, uninstall: bool) -> None:
    dest = dest_root / SKILL_NAME
    if dest.exists():
        shutil.rmtree(dest)
    if uninstall:
        print(f"已移除 {dest}")
        return
    dest_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL_DIR, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"已安裝 {dest}")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*", metavar="TARGET",
                        help=f"{' / '.join(USER_TARGETS)}，預設全部")
    parser.add_argument("--project", type=Path, help="安裝到指定專案目錄，而非使用者層級")
    parser.add_argument("--uninstall", action="store_true", help="移除已安裝的 skill")
    args = parser.parse_args()
    unknown = [t for t in args.targets if t not in USER_TARGETS]
    if unknown:
        parser.error(f"不支援的目標：{', '.join(unknown)}（可用：{', '.join(USER_TARGETS)}）")

    if not (SKILL_DIR / "SKILL.md").is_file():
        print(f"找不到 {SKILL_DIR / 'SKILL.md'}", file=sys.stderr)
        return 1

    if args.project:
        project = args.project.expanduser().resolve()
        if not project.is_dir():
            print(f"專案目錄不存在：{project}", file=sys.stderr)
            return 1
        for sub in PROJECT_SUBDIRS:
            install(project / sub, args.uninstall)
    else:
        for name in args.targets or USER_TARGETS:
            install(USER_TARGETS[name](), args.uninstall)

    if not args.uninstall:
        print("完成。請重新啟動對應工具或開新 session 以載入 skill。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
