# /// script
# requires-python = ">=3.10"
# dependencies = ["opencc>=1.4.2"]
# ///
"""OpenCC 簡繁轉換工具（agent skill 用）。

轉換引擎與詞典：OpenCC（https://github.com/BYVoid/OpenCC），
Copyright 2010-2026 Carbo Kuo and contributors，Apache License 2.0。
DESCRIPTIONS 中的設定說明改寫自 OpenCC README。

用法：
  uv run scripts/convert.py -c s2twp "鼠标里面的硅二极管坏了"
  uv run scripts/convert.py -c t2s -i input.txt -o output.txt
  echo 文字 | uv run scripts/convert.py -c s2t
  uv run scripts/convert.py -c s2twp --dict terms.tsv -i in.md -o out.md
  uv run scripts/convert.py --list
"""
import argparse
import json
import os
import sys
import tempfile

import opencc

DESCRIPTIONS = {
    "s2t": "簡體 → OpenCC 標準繁體",
    "t2s": "OpenCC 標準繁體 → 簡體",
    "s2tw": "簡體 → 台灣正體（僅字形）",
    "tw2s": "台灣正體 → 簡體（僅字形）",
    "s2twp": "簡體 → 台灣正體，含台灣慣用詞（如 鼠标→滑鼠）",
    "tw2sp": "台灣正體 → 簡體，含大陸慣用詞（如 滑鼠→鼠标）",
    "s2hk": "簡體 → 香港繁體",
    "hk2s": "香港繁體 → 簡體",
    "s2hkp": "簡體 → 香港繁體，含香港慣用詞（開發中）",
    "hk2sp": "香港繁體 → 簡體，含大陸慣用詞（開發中）",
    "t2tw": "OpenCC 標準繁體 → 台灣正體",
    "tw2t": "台灣正體 → OpenCC 標準繁體",
    "t2hk": "OpenCC 標準繁體 → 香港繁體",
    "hk2t": "香港繁體 → OpenCC 標準繁體",
    "t2jp": "日文舊字體 → 日文新字體（實驗性）",
    "jp2t": "日文新字體 → 日文舊字體（實驗性）",
}


def _stems():
    return sorted(c[:-5] for c in opencc.CONFIGS if c.endswith(".json"))


def _share_dir():
    return os.path.join(os.path.dirname(opencc.__file__), "clib", "share", "opencc")


def _load_entries(path):
    """讀取自訂詞彙：.json 為 {"來源": "目標"}；其他格式為每行「來源<Tab>目標」，# 開頭為註解。"""
    with open(path, encoding="utf-8-sig") as f:
        if path.lower().endswith(".json"):
            return json.load(f)
        entries = {}
        for n, line in enumerate(f, 1):
            line = line.rstrip("\r\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t") if "\t" in line else line.split(None, 1)
            if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                raise ValueError(f"{path}:{n} 格式錯誤，應為「來源<Tab>目標」")
            entries[parts[0].strip()] = parts[1].strip()
        return entries


def _build_custom_config(stem, entries):
    """複製內建設定，把自訂詞彙以 inline 字典插入第一個轉換階段的最高優先位置。"""
    share = _share_dir()
    with open(os.path.join(share, stem + ".json"), encoding="utf-8") as f:
        cfg = json.load(f)

    def absolutize(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "file" and isinstance(v, str):
                    node[k] = os.path.join(share, v)
                else:
                    absolutize(v)
        elif isinstance(node, list):
            for x in node:
                absolutize(x)

    absolutize(cfg)
    inline = {"type": "inline", "entries": entries}
    first = cfg["conversion_chain"][0]["dict"]
    if first.get("type") == "group":
        first["dicts"].insert(0, inline)
    else:
        cfg["conversion_chain"][0]["dict"] = {
            "type": "group", "match_policy": "short_circuit", "dicts": [inline, first]}
    fd, path = tempfile.mkstemp(suffix=".json", prefix="opencc_custom_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False)
    return path


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="OpenCC 簡繁轉換")
    parser.add_argument("text", nargs="*", help="要轉換的文字（省略時讀取 -i 或 stdin）")
    parser.add_argument("-c", "--config", default="s2twp", help="轉換設定（預設 s2twp）")
    parser.add_argument("-i", "--input", help="輸入檔案（UTF-8）")
    parser.add_argument("-o", "--output", help="輸出檔案（預設 stdout）")
    parser.add_argument("-d", "--dict", help="自訂詞彙檔（TSV：來源<Tab>目標，或 JSON 物件），優先於內建詞典")
    parser.add_argument("--list", action="store_true", help="列出可用的轉換設定")
    args = parser.parse_args()

    if args.list:
        print(f"OpenCC {opencc.__version__}")
        for stem in _stems():
            print(f"  {stem:<7} {DESCRIPTIONS.get(stem, '')}")
        return 0

    config = args.config[:-5] if args.config.endswith(".json") else args.config
    builtin = config in _stems()
    if not builtin and not os.path.isfile(args.config):
        print(f"錯誤：未知的設定 '{args.config}'，可用：{', '.join(_stems())}", file=sys.stderr)
        return 2

    if args.text:
        text = " ".join(args.text)
    elif args.input:
        if args.output and os.path.exists(args.output) and os.path.samefile(args.input, args.output):
            print("錯誤：輸入與輸出不可為同一檔案", file=sys.stderr)
            return 2
        with open(args.input, encoding="utf-8-sig") as f:
            text = f.read()
    else:
        sys.stdin.reconfigure(encoding="utf-8")
        text = sys.stdin.read()

    custom_path = None
    if args.dict:
        if not builtin:
            print("錯誤：--dict 只能搭配內建設定使用", file=sys.stderr)
            return 2
        try:
            entries = _load_entries(args.dict)
        except (OSError, ValueError) as e:
            print(f"錯誤：{e}", file=sys.stderr)
            return 2
        custom_path = _build_custom_config(config, entries)

    try:
        converter = opencc.OpenCC(custom_path or (config if builtin else args.config))
        result = converter.convert(text)
    finally:
        if custom_path:
            os.remove(custom_path)

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            f.write(result)
        print(f"已寫入 {args.output}（{len(result)} 字元，設定 {config}）", file=sys.stderr)
    else:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
