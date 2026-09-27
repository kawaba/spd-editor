#!/usr/bin/env python3
"""
fence_spd.py  ---  SPD図を自動判定してコードフェンス(```)で囲む

Markdownでは段落内の単独改行が無視され、行頭の空白も詰められるため、
罫線文字で描いたSPD図が1行に潰れて表示される。
このスクリプトは空行で区切られた「段落」を走査し、罫線文字を含む段落を
SPD図とみなしてコードフェンスで囲む。

使い方:
    python fence_spd.py 入力.md 出力.md
    python fence_spd.py 入力.md 出力.md --keep-bom --crlf
"""

import argparse
import re
import sys

# --- SPD図の判定に使う罫線文字 ---------------------------------------------
# 〇 は「合計＝〇〇」のように本文中にも出てくるので判定には使わない
BOX_CHARS = "│├└┌┐┘┬┴┼─◇↻"
BOX_RE = re.compile("[" + BOX_CHARS + "]")

# フェンスの外に残す行（見出し・箇条書き・番号付きリスト・引用）
OUTSIDE_RE = re.compile(r"^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|>\s)")

FENCE_RE = re.compile(r"^\s*(```|~~~)")


def split_paragraphs(lines):
    """空行を区切りとして (種別, 行リスト) のリストに分割する。
    種別は 'blank' または 'para'。"""
    blocks = []
    buf = []
    for line in lines:
        if line.strip() == "":
            if buf:
                blocks.append(("para", buf))
                buf = []
            blocks.append(("blank", [line]))
        else:
            buf.append(line)
    if buf:
        blocks.append(("para", buf))
    return blocks


def is_spd(para):
    """段落がSPD図かどうかを判定する。
    罫線文字を含む行が2行以上あればSPD図とみなす。"""
    hits = sum(1 for ln in para if BOX_RE.search(ln))
    return hits >= 2


def convert(text, fence_info=""):
    lines = text.split("\n")
    out = []
    stats = {"fenced": 0, "skipped_in_fence": 0, "warn": []}

    # 既存のコードフェンス内は触らない
    in_fence = False
    segments = []          # (種別, 行リスト) : 種別は 'raw'(そのまま) / 'body'(処理対象)
    body = []
    for line in lines:
        if FENCE_RE.match(line):
            if in_fence:
                # フェンス終了行
                segments.append(("raw", [line]))
                in_fence = False
            else:
                if body:
                    segments.append(("body", body))
                    body = []
                segments.append(("raw", [line]))
                in_fence = True
            continue
        if in_fence:
            segments.append(("raw", [line]))
            stats["skipped_in_fence"] += 1
        else:
            body.append(line)
    if body:
        segments.append(("body", body))

    for kind, seg in segments:
        if kind == "raw":
            out.extend(seg)
            continue

        for btype, para in split_paragraphs(seg):
            if btype == "blank" or not is_spd(para):
                out.extend(para)
                continue

            # 段落の先頭にある見出し・箇条書き行はフェンスの外に出す
            i = 0
            while i < len(para) and OUTSIDE_RE.match(para[i]) and not BOX_RE.search(para[i]):
                out.append(para[i])
                i += 1
            diagram = para[i:]
            if not diagram:
                continue

            # 図の1行目が罫線で始まっていたら、前の図の続きが空行で
            # 分断されている可能性があるので警告を出す
            if BOX_RE.match(diagram[0].lstrip()[:1] or " "):
                stats["warn"].append(diagram[0][:40])

            out.append("```" + fence_info if fence_info else "```")
            out.extend(diagram)
            out.append("```")
            stats["fenced"] += 1

    # 後処理: フェンス同士が隣接している箇所に空行を挟む
    tidy = []
    for i, line in enumerate(out):
        tidy.append(line)
        if (line.strip() in ("```", "~~~") and i + 1 < len(out)
                and FENCE_RE.match(out[i + 1])):
            tidy.append("")
    out = tidy

    return "\n".join(out), stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--fence-info", default="",
                    help="フェンスに付ける言語名（既定は無し＝ハイライトなし）")
    ap.add_argument("--keep-bom", action="store_true", help="BOMを残す")
    ap.add_argument("--crlf", action="store_true", help="改行コードをCRLFで出力する")
    args = ap.parse_args()

    with open(args.src, "rb") as f:
        raw = f.read()

    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    converted, stats = convert(text, args.fence_info)

    if args.crlf:
        converted = converted.replace("\n", "\r\n")
    data = converted.encode("utf-8")
    if args.keep_bom and had_bom:
        data = b"\xef\xbb\xbf" + data

    with open(args.dst, "wb") as f:
        f.write(data)

    print(f"入力     : {args.src}")
    print(f"出力     : {args.dst}")
    print(f"BOM      : {'除去しました' if had_bom and not args.keep_bom else ('元から無し' if not had_bom else '残しました')}")
    print(f"改行     : {'CRLF' if args.crlf else 'LF'}")
    print(f"囲んだSPD図 : {stats['fenced']} 個")
    print(f"既存フェンス内で触らなかった行 : {stats['skipped_in_fence']} 行")
    if stats["warn"]:
        print(f"\n[要確認] 図の途中が空行で分断されている可能性のある箇所 {len(stats['warn'])} 件:")
        for w in stats["warn"]:
            print("   ", w)


if __name__ == "__main__":
    main()
