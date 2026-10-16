# OpenCC 內建設定一覽

資料來源：OpenCC 原始碼 `README.md` 與 `data/config/*.json`（PyPI `opencc` 1.4.2），經翻譯與改寫。
OpenCC：Copyright 2010-2026 Carbo Kuo and contributors，依 Apache License 2.0 授權。

## 正式設定

| 設定 | 轉換方向 | 轉換鏈（簡述） |
|---|---|---|
| `s2t` | 簡體 → OpenCC 標準繁體 | STPhrases / STCharacters |
| `t2s` | OpenCC 標準繁體 → 簡體 | TSPhrases / TSCharacters |
| `s2tw` | 簡體 → 台灣正體 | s2t → TWVariants（異體字） |
| `tw2s` | 台灣正體 → 簡體 | TWVariantsRev → t2s |
| `s2twp` | 簡體 → 台灣正體＋台灣慣用詞 | s2t → TWPhrases（用詞）→ TWVariants |
| `tw2sp` | 台灣正體 → 簡體＋大陸慣用詞 | TWPhrasesRev / TWVariantsRev → t2s |
| `s2hk` | 簡體 → 香港繁體 | s2t → HKVariants |
| `hk2s` | 香港繁體 → 簡體 | HKVariantsRev → t2s |
| `t2tw` | 標準繁體 → 台灣正體 | TWVariants |
| `tw2t` | 台灣正體 → 標準繁體 | TWVariantsRev |
| `t2hk` | 標準繁體 → 香港繁體 | HKVariants |
| `hk2t` | 香港繁體 → 標準繁體 | HKVariantsRev |

## 開發中

| 設定 | 轉換方向 |
|---|---|
| `s2hkp` | 簡體 → 香港繁體＋香港慣用詞 |
| `hk2sp` | 香港繁體 → 簡體＋大陸慣用詞 |

## 實驗性（不建議用於正式環境）

| 設定 | 轉換方向 | 備註 |
|---|---|---|
| `t2jp` | 日文舊字體 → 新字體 | |
| `jp2t` | 日文新字體 → 舊字體 | 並轉換少量日文詞組 |
| `t2seal` / `s2seal` / `seal2t` | 繁/簡 ↔ 小篆（Unicode 18.0 篆書區塊） | PyPI 1.4.2 未收錄，需自行建置；顯示需特殊字型 |

## 範例對照

| 輸入 | `s2t` | `s2tw` | `s2twp` |
|---|---|---|---|
| 鼠标里面的硅二极管坏了 | 鼠標裏面的硅二極管壞了 | 鼠標裡面的硅二極管壞了 | 滑鼠裡面的矽二極體壞了 |

「標準繁體」與「台灣正體」差異在異體字選擇（裏/裡、爲/為、綫/線 等）；`p` 結尾者另做地區用詞轉換。
