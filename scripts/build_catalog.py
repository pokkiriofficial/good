"""商品(お酒)カタログを spec/drinks.yaml から生成する。

使い方: python scripts/build_catalog.py
  → menu/drinks.json            POS に渡す一覧(ジャンル・銘柄・かな・別名・種別・初期値)
  → menu/preview/index.html     「商品を検索して追加」画面の試作(1枚で開ける)
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec" / "drinks.yaml"
TEMPLATE = ROOT / "templates" / "catalog" / "preview.html"
OUT_JSON = ROOT / "menu" / "drinks.json"
OUT_HTML = ROOT / "menu" / "preview" / "index.html"

KINDS = ["ドリンク", "ボトル", "フード", "その他"]
# POS(nightwork-pos)の product_category_kind に合わせる
KIND_CODE = {"ドリンク": "drink", "ボトル": "bottle", "フード": "food", "その他": "other"}
ITEM_KEYS = {"c", "g", "n", "k", "a", "kind", "keep", "cast"}


def load_catalog() -> dict:
    return yaml.safe_load(SPEC.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    """検索用に、全角半角・大文字小文字・カタカナひらがな・区切り記号の違いをなくす。"""
    s = unicodedata.normalize("NFKC", str(text)).lower()
    s = "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in s)
    return re.sub(r"[\s・･\-‐−–—_/()（）.,'’&]", "", s)


def check(cat: dict) -> list[str]:
    """整合性の問題を文字列のリストで返す(空なら合格)。"""
    errors: list[str] = []
    cats = cat.get("categories", [])
    items = cat.get("items", [])
    if cat.get("kinds") != KINDS:
        errors.append(f"kinds は {KINDS} にする")
    cat_ids = [c["id"] for c in cats]
    for dup in sorted(k for k, v in Counter(cat_ids).items() if v > 1):
        errors.append(f"category id が重複しています: {dup}")
    for c in cats:
        for key in ("id", "label", "kind", "keep", "cast", "icon", "color"):
            if key not in c:
                errors.append(f"category {c.get('id')}: {key} がありません")
        if c.get("kind") not in KINDS:
            errors.append(f"category {c.get('id')}: kind {c.get('kind')} は {KINDS} のどれかにする")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(c.get("color", ""))):
            errors.append(f"category {c.get('id')}: color は #rrggbb の形にする")
    names = Counter(it.get("n") for it in items)
    for dup in sorted(k for k, v in names.items() if v > 1):
        errors.append(f"商品名が重複しています: {dup}")
    for it in items:
        label = it.get("n", "?")
        extra = set(it) - ITEM_KEYS
        if extra:
            errors.append(f"{label}: 使えないキー {sorted(extra)}")
        for key in ("c", "g", "n", "k", "a"):
            if key not in it:
                errors.append(f"{label}: {key} がありません")
        if it.get("c") not in cat_ids:
            errors.append(f"{label}: 未定義の category {it.get('c')}")
        if not isinstance(it.get("a", []), list):
            errors.append(f"{label}: a(別名)はリストにする")
        if "kind" in it and it["kind"] not in KINDS:
            errors.append(f"{label}: kind {it['kind']} は {KINDS} のどれかにする")
        kana = str(it.get("k", ""))
        if kana and not re.fullmatch(r"[ぁ-ゖー゛゜ 〆]+", kana):
            errors.append(f"{label}: k(かな)はひらがなにする: {kana}")
        if "¥" in label or re.search(r"\d{3,}円", label):
            errors.append(f"{label}: 商品名に価格を入れない(店舗が入力する)")
    return errors


def catalog_data(cat: dict) -> dict:
    """POS に渡す形(menu/drinks.json)。"""
    by_cat = {c["id"]: c for c in cat["categories"]}
    counter: Counter = Counter()
    items = []
    for it in cat["items"]:
        c = by_cat[it["c"]]
        counter[it["c"]] += 1
        kind = it.get("kind", c["kind"])
        aliases = [str(a) for a in it.get("a", [])]
        search = sorted({normalize(x) for x in [it["n"], it["k"], it["g"], c["label"], *aliases] if x})
        items.append({
            "id": f"{it['c']}-{counter[it['c']]:03d}",
            "category": it["c"],
            "categoryLabel": c["label"],
            "group": it["g"],
            "name": it["n"],
            "kana": it["k"],
            "aliases": aliases,
            "kind": KIND_CODE[kind],
            "kindLabel": kind,
            "bottleKeep": bool(it.get("keep", c["keep"])),
            "castDrink": bool(it.get("cast", c["cast"])),
            "search": search,
        })
    categories = [{
        "id": c["id"], "label": c["label"], "kind": KIND_CODE[c["kind"]], "kindLabel": c["kind"],
        "bottleKeep": bool(c["keep"]), "castDrink": bool(c["cast"]),
        "icon": c["icon"], "color": c["color"], "count": counter[c["id"]],
    } for c in cat["categories"]]
    return {
        "version": str(cat["version"]),
        "note": "価格と写真は持たない。価格は店舗が商品を追加するときに入力し、写真は店舗が登録する",
        "kinds": [{"code": KIND_CODE[k], "label": k} for k in KINDS],
        "categories": categories,
        "items": items,
    }


def build_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return TEMPLATE.read_text(encoding="utf-8").replace("/*__CATALOG_JSON__*/null", payload)


def main() -> int:
    cat = load_catalog()
    errors = check(cat)
    if errors:
        print("\n".join(errors))
        return 1
    data = catalog_data(cat)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_html(data), encoding="utf-8")
    print(f"catalog: {len(data['categories'])} categories / {len(data['items'])} items")
    for c in data["categories"]:
        print(f"  {c['label']}: {c['count']}")
    print(f"-> {OUT_JSON.relative_to(ROOT)}, {OUT_HTML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
