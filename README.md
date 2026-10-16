# opencc-skill

把 [OpenCC（Open Chinese Convert）](https://github.com/BYVoid/OpenCC) 包裝成 Claude Code 的 agent skill，
讓 Claude 以 OpenCC 官方引擎進行中文簡繁轉換與地區用詞轉換，而不是憑記憶逐字替換。

```
/opencc 鼠标里面的硅二极管坏了
→ 滑鼠裡面的矽二極體壞了（s2twp）
```

## 功能

- **詞彙級轉換**：使用 OpenCC 的分詞與詞組優先比對，正確處理「头发→頭髮」「发展→發展」等一簡對多繁的情況。
- **地區用詞**：`s2twp` 會把大陸用詞換成台灣慣用詞（软件→軟體、内存→記憶體、实时→即時）；`tw2sp` 反向轉換。
- **16 種轉換方向**：簡體、OpenCC 標準繁體、台灣正體、香港繁體互轉，以及日文新舊字體（實驗性）。
- **自訂詞彙**：用 TSV 或 JSON 詞彙表覆寫內建詞典，適合人名、品牌、內部術語。
- **免手動安裝依賴**：腳本以 [uv](https://docs.astral.sh/uv/) 執行，Python 與 `opencc` 套件都會自動下載。

## 需求

- [Claude Code](https://claude.com/claude-code)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)（第一次執行需要連網）

uv 安裝方式：

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

支援平台與 PyPI `opencc` 1.4.2 預編譯套件相同：Windows x64、macOS（Intel / Apple Silicon）、
Linux x86_64 / aarch64（glibc），Python 3.10 – 3.14。

## 安裝

先 clone 本 repo：

```bash
git clone https://github.com/jamescchuang/opencc-skill.git
```

再把 `skills/opencc` 複製到 Claude Code 的 skills 目錄，擇一即可：

```bash
# 所有專案都能使用（使用者層級）
cp -r opencc-skill/skills/opencc ~/.claude/skills/opencc
```

```bash
# 只在某個專案使用（專案層級）
cp -r opencc-skill/skills/opencc <你的專案>/.claude/skills/opencc
```

複製後開新的 Claude Code session，或在現有 session 執行 `/reload-skills`。

> 直接在本 repo 目錄開啟 Claude Code 時，`.claude/skills/opencc` 已預先安裝，可立即使用。

## 使用方式

### 斜線指令

```
/opencc [轉換方向] <文字或檔案路徑>
```

- 第一個詞若是轉換方向（如 `t2s`、`tw2sp`），就用它轉換；否則預設 `s2twp`。
- 對象若是存在的檔案，會輸出成新檔（如 `doc.md` → `doc.s2twp.md`），不覆蓋原檔。

```
/opencc 系統集成與交互            → 系統整合與互動
/opencc tw2sp 滑鼠和軟體          → 鼠标和软件
/opencc t2s docs/guide.md         → 產生 docs/guide.t2s.md
```

### 自然語言

skill 也會在對話中自動觸發，例如：

- 「把這段轉成台灣用語」
- 「把 README.md 轉成簡體」
- 「這份字幕檔簡轉繁」

### 直接執行腳本

不透過 Claude 也可以直接使用：

```bash
uv run skills/opencc/scripts/convert.py -c s2twp "鼠标里面的硅二极管坏了"
```

```bash
uv run skills/opencc/scripts/convert.py -c t2s -i input.md -o output.md
```

```bash
uv run skills/opencc/scripts/convert.py --list
```

| 參數 | 說明 |
|---|---|
| `-c, --config` | 轉換方向，預設 `s2twp` |
| `-i, --input` | 輸入檔（UTF-8，可含 BOM） |
| `-o, --output` | 輸出檔，預設輸出到 stdout；不可與輸入檔相同 |
| `-d, --dict` | 自訂詞彙檔 |
| `--list` | 列出所有轉換方向 |

未指定文字或 `-i` 時從 stdin 讀取。

## 常用轉換方向

| 需求 | 設定 |
|---|---|
| 簡體 → 台灣正體，含台灣慣用詞 | `s2twp` |
| 簡體 → 台灣正體，只換字形 | `s2tw` |
| 簡體 → OpenCC 標準繁體 | `s2t` |
| 簡體 → 香港繁體 | `s2hk` |
| 台灣正體 → 簡體，含大陸慣用詞 | `tw2sp` |
| 台灣正體 → 簡體，只換字形 | `tw2s` |
| 繁體 → 簡體 | `t2s` |

完整列表見 [skills/opencc/references/configs.md](skills/opencc/references/configs.md)。

## 自訂詞彙

TSV（每行 `來源<Tab>目標`，`#` 開頭為註解）：

```
服务器	伺服主機
麦旋风	冰炫風
```

或 JSON：

```json
{"服务器": "伺服主機", "麦旋风": "冰炫風"}
```

```bash
uv run skills/opencc/scripts/convert.py -c s2twp --dict terms.tsv -i in.md -o out.md
```

來源詞要用輸入端的文字書寫（`s2*` 寫簡體、`t2*` / `tw2*` 寫繁體）。自訂詞優先於內建詞典，
輸出仍會經過後續的地區用詞與異體字轉換。

## 限制

- OpenCC 是詞典式轉換，一簡對多繁偶有誤判，人名（如「蒂姆」與台灣慣用的「提姆」）也不會自動調整；重要文件請人工校對，或用自訂詞彙修正。
- 不轉換標點符號，例如 `“ ”` 不會變成 `「 」`。
- PyPI 版 `opencc` 1.4.2 不含小篆設定（`s2seal` / `t2seal` / `seal2t`）。
- `s2hkp`、`hk2sp` 詞庫仍在開發中；`t2jp`、`jp2t` 僅供研究。

## 專案結構

```
.claude/skills/opencc/     本 repo 的專案層級安裝（與 skills/opencc 內容相同）
skills/opencc/             skill 原始檔，安裝時複製這份
├── SKILL.md               skill 說明與 Claude 的操作規則
├── scripts/convert.py     轉換腳本（PEP 723，uv 執行）
└── references/configs.md  轉換方向完整說明
NOTICE                     第三方軟體宣告
LICENSES/                  第三方授權全文
```

## 授權與致謝

轉換引擎與詞典來自 [OpenCC](https://github.com/BYVoid/OpenCC)，Copyright 2010-2026 Carbo Kuo and contributors，
依 [Apache License 2.0](LICENSES/OpenCC-Apache-2.0.txt) 授權。本 repo 不包含 OpenCC 原始碼或詞典，
執行時自 PyPI 安裝官方 `opencc` 套件。詳見 [NOTICE](NOTICE)。

本專案與 OpenCC 專案及其作者無隸屬或背書關係。
