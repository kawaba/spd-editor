# Markdown → HTML 変換 指示文

Markdownファイル（`.md`）をHTMLに変換するときの共通ルールです。
SPD記法の設計図やJavaコードを含む技術文書を、画面でも紙でも読みやすい1枚のHTMLにすることを目的とします。

## 1. 成果物

- 入力：`.md` ファイル（アップロードされたもの）
- 出力：同名の `.html` ファイル1つ（外部CSS・外部JS・画像を参照しない、単体で完結したファイル）
- 文字コードはUTF-8。ダウンロードできる形で提示すること。

## 2. head部（この通りに出力する）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>（md先頭のH1見出しをタイトルにする）</title>
<style>
/* ---- フォント指定 ----
   本文＝BIZ UDPゴシック（プロポーショナル）／見出し＝游ゴシック体（太字）／
   SPD・Javaコード＝BIZ UDゴシック（等幅）
   フォント名は環境ごとに登録名が異なるため、日本語名・英語名を併記する。 */
body, table, th, td, blockquote {
   font-family: "BIZ UDPゴシック", "BIZ UDPGothic", "Meiryo", "メイリオ",
                "Yu Gothic UI", "Hiragino Sans", sans-serif;
}

/* SPD・Javaコードは等幅のBIZ UDゴシック（Pなし＝等幅。半角＝全角の1/2幅で罫線が揃う） */
pre, code {
   font-family: "BIZ UDゴシック", "BIZ UDGothic",
                "MS ゴシック", "MS Gothic", monospace;
}

/* 見出しは游ゴシック体の太字 */
h1, h2, h3, h4, h5, h6 {
   font-family: "游ゴシック体", "YuGothic", "游ゴシック Medium", "Yu Gothic Medium",
                "游ゴシック", "Yu Gothic", sans-serif;
   font-weight: bold;
}

body {
   color: black;
   font-size: 14pt;
   line-height: 1.5em;
   margin-left: 60pt;
}

/* ---- 見出し ---- */
h1 { font-size: 20pt; border-bottom: 2px solid #555; padding-bottom: 4pt; margin-top: 24pt; }
h2 { font-size: 17pt; border-bottom: 1px solid #ddd; padding-bottom: 3pt; margin-top: 24pt; }
h3 { font-size: 15pt; margin-top: 18pt; }
h4 { font-size: 14pt; margin-top: 14pt; }
h5, h6 { font-size: 13pt; margin-top: 12pt; }

/* ---- 本文・リスト ---- */
p  { margin: 6pt 0; }
ul, ol { margin: 6pt 0; padding-left: 22pt; }
li { margin: 2pt 0; }

/* ---- コードブロック（SPD・Java共通） ---- */
pre {
   font-size: 12pt;
   line-height: 1.4em;
   white-space: pre;
   overflow-x: auto;
   background-color: #fafafa;
   border: 1px solid #e8e8e8;
   border-left: 4px solid #cbd8cb;   /* SPD・その他 */
   padding: 8pt 10pt;
   margin: 8pt 0;
   tab-size: 4;
   -moz-tab-size: 4;
}
pre code {
   font-size: inherit;
   background: none;
   border: none;
   padding: 0;
   white-space: pre;
}
.small {
    font-size: 12px;
    line-height: 1.2;
}
.med {
    font-size: 16px;
    line-height: 1.4;
}
/* Javaコードは左罫の色を変えて区別する */
pre.java { border-left-color: #b9cbe2; background-color: #f8fafd; }

/* ---- インラインコード ---- */
code {
   font-size: 95%;
   background-color: #f2f2f2;
   border-radius: 3px;
   padding: 0 3px;
}

/* ---- 表 ---- */
table {
   border-collapse: collapse;
   font-size: 12pt;
   line-height: 1.4em;
   margin: 8pt 0;
}
th, td {
   border: 1px solid #d5d5d5;
   padding: 4pt 8pt;
   text-align: left;
   vertical-align: top;
}
th { background-color: #f2f4f6; }

/* ---- 引用・区切り線 ---- */
blockquote {
   margin: 8pt 0 8pt 0;
   padding: 4pt 12pt;
   border-left: 4px solid #ddd;
   background-color: #fcfcfa;
   color: #333;
}
hr { border: none; border-top: 1px solid #bbb; margin: 20pt 0; }

/* ---- チェックリスト ---- */
ul.checklist { list-style: none; padding-left: 4pt; }
ul.checklist li { text-indent: -1.4em; padding-left: 1.4em; }
</style>
</head>
<body>
```

## 3. 変換ルール

### 3.1 パーサ

- **CommonMark準拠のパーサを使うこと**（Pythonなら `markdown-it-py`。`markdown`（Python-Markdown）は不可）。
  - 理由：本文のmdは**半角2文字**でリストを入れ子にしており、Python-Markdownでは入れ子が潰れて同階層になる。
  - 同じ理由で、リスト項目の中に2字下げで書かれたコードフェンス（<code>```java</code>）もPython-Markdownでは認識されず、そのまま文字として出てしまう。
- 表（GFMのテーブル）を有効化すること。
- 生HTMLの通過を許可すること（`html: True`）。mdに書かれた `<!-- ... -->` のコメントは、HTMLコメントとしてそのまま残す。

### 3.2 コードブロック（SPD・Javaの表示）

- フェンス（<code>```</code>）は `<pre><code>` に変換し、`<` `>` `"` `&` は必ずエスケープする。
  例：`ArrayList<String>`、`for (int i = 0; i < n; i++)` がそのまま表示されること。
- 言語指定つきのフェンスは `<code class="language-XXX">` とする。
- <code>```java</code> のブロックは、`<pre>` 側にも `class="java"` を付ける
  （`<pre class="java"><code class="language-java">`）。左罫線の色でSPDと区別するため。
  `:has()` セレクタは使わず、クラスで指定すること（古いブラウザ対策）。
- SPDの罫線（`│ ├─ └─ ↻ ◇ 〇`）や全角スペースは、**1文字も加工せずそのまま**出力する。
  インデントの揺れも直さない。

### 3.3 CJK特有の補正

- **強調の補正**：CommonMarkの規則では、`**「インスタンスメソッド」**` のように鉤括弧や句読点が隣接すると
  `**` が強調として認識されず、そのまま文字として残る。
  変換後、`<pre>` の外側に限って残った `**…**` を `<strong>…</strong>` に置換すること。
  変換後に `**` が0個になることを必ず確認する。

### 3.4 チェックリスト

- `- [ ]` → `☐`、`- [x]` → `☑` に置換する。
- ☐☑ を含む `<ul>` には `class="checklist"` を付け、行頭記号（・）を消してぶら下げインデントにする。

## 4. フォントを変えたい場合の指針

| 用途 | 採用フォント | 条件 |
|---|---|---|
| 本文 | BIZ UDPゴシック | プロポーショナル。太めで可読性が高いUD書体 |
| 見出し | 游ゴシック体（太字） | 本文と書体を変えて見出しを立たせる |
| SPD・コード | BIZ UDゴシック | **等幅**で、罫線素片を**全角**で持ち、**半角：全角＝1：2**であること |

- SPD用フォントの必須条件は「等幅・罫線が全角・半角：全角＝1：2」。
  Windows標準でこれを満たすのは **BIZ UDゴシック／BIZ UD明朝／MSゴシック／MS明朝／UDデジタル教科書体N** のみ。
- Consolas・Cascadia Code などの欧文等幅は、罫線を半角幅で描くためSPDが崩れる。使わないこと。
- UDデジタル教科書体は紙では読みやすいが、画面では線が細く見にくいため、Web用途では採用しない。
- メイリオ・游ゴシック・BIZ UDPゴシックはプロポーショナルなので、コードブロックには使わない。

## 5. 仕上げの確認項目

- [ ] 変換後のHTMLに、未変換の `**`・`|`（表の行）・`#`（見出し）・<code>```</code> が残っていないか
- [ ] `<ul>` `<li>` `<table>` の開始タグと終了タグの数が一致しているか
- [ ] リストの入れ子が元のmdと同じ階層になっているか
- [ ] SPDの罫線が桁ずれせず、階層が読み取れるか
- [ ] Javaコード内の `<` `>` が正しく表示されているか
- [ ] 表・引用・チェックリスト・区切り線がすべて反映されているか
- [ ] mdのHTMLコメントが残っているか
