"""商品(お酒)カタログ spec/drinks.yaml と、その生成物の検証。"""

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_catalog  # noqa: E402

# 夜のお店で必ず聞かれる銘柄(検索の言い方 → 当たるべき商品名)
MUST_FIND = {
    "ドンペリ": "ドン・ペリニヨン 白", "アルマンド": "アルマン・ド・ブリニャック ゴールド", "ソウメイ": "ソウメイ ブリュット",
    "エンジェル": "エンジェル ブリュット", "ヴーヴ": "ヴーヴ・クリコ イエローラベル", "モエ": "モエ・エ・シャンドン ブリュット アンペリアル",
    "クリスタル": "ルイ・ロデレール クリスタル", "山崎": "サントリー 山崎", "響": "サントリー 響 ジャパニーズハーモニー",
    "マッカラン": "ザ・マッカラン 12年 シェリーオーク", "ジョニ黒": "ジョニーウォーカー ブラックラベル 12年",
    "ヘネシー": "ヘネシー VS", "レミー": "レミーマルタン VSOP", "鏡月": "鏡月 グリーン", "黒霧島": "黒霧島",
    "いいちこ": "いいちこ", "獺祭": "獺祭 純米大吟醸 45", "パトロン": "パトロン シルバー", "イエガー": "イエーガーマイスター",
    "コカレロ": "コカレロ", "カシオレ": "カシスオレンジ", "レモンサワー": "レモンサワー", "ハイボール": "ハイボール",
    "ウーロンハイ": "ウーロンハイ", "テキーラ": "テキーラ ショット", "ウーロン茶": "ウーロン茶", "レッドブル": "レッドブル",
    "コロナ": "コロナ エキストラ", "氷": "氷 (アイス)", "どんぺり": "ドン・ペリニヨン 白", "はいぼーる": "ハイボール",
}


@pytest.fixture(scope="module")
def cat():
    return build_catalog.load_catalog()


@pytest.fixture(scope="module")
def data(cat):
    return build_catalog.catalog_data(cat)


def test_catalog_is_consistent(cat):
    assert build_catalog.check(cat) == []


def test_catalog_covers_night_genres(data):
    labels = {c["label"] for c in data["categories"]}
    for want in ["シャンパン", "ウイスキー", "ブランデー", "焼酎", "日本酒", "テキーラ", "リキュール", "ビール",
                 "サワー・酎ハイ", "ハイボール・割りもの", "カクテル", "ショット", "ソフトドリンク", "ワイン"]:
        assert want in labels, want
    assert len(data["items"]) >= 800
    for c in data["categories"]:
        assert c["count"] >= 5, c["label"]


def test_catalog_has_no_prices(data):
    # 価格は店舗が入力する。カタログには持たない
    for it in data["items"]:
        assert "price" not in it and "priceYen" not in it, it["name"]
        assert not re.search(r"\d{3,}円|¥", it["name"]), it["name"]


def test_catalog_kinds_match_pos(data):
    assert [k["code"] for k in data["kinds"]] == ["drink", "bottle", "food", "other"]
    for it in data["items"]:
        assert it["kind"] in {"drink", "bottle", "food", "other"}, it["name"]
    bottles = [it for it in data["items"] if it["category"] == "champagne"]
    assert all(it["kind"] == "bottle" for it in bottles if "グラス" not in it["name"])
    assert all(it["kind"] == "drink" for it in data["items"] if it["category"] == "sour")


def test_search_finds_common_names(data):
    def hits(q):
        nq = build_catalog.normalize(q)
        return [it["name"] for it in data["items"] if any(nq in s for s in it["search"])]
    for q, want in MUST_FIND.items():
        assert want in hits(q), (q, want)


def test_generated_files_are_current(data):
    html = (ROOT / "menu" / "preview" / "index.html").read_text(encoding="utf-8")
    assert "/*__CATALOG_JSON__*/null" not in html
    assert "商品を検索して追加" in html and "入力" in html and "追加済み" in html
    assert "商品価格" in html and "保存する" in html
    saved = json.loads((ROOT / "menu" / "drinks.json").read_text(encoding="utf-8"))
    assert saved == data


def test_no_sensitive_items(data):
    for word in ["本名", "生年月日", "口座", "パスワード", "ログイン", "時給"]:
        assert not any(word in it["name"] for it in data["items"]), word
