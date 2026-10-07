"""フェーズ1: spec/items.yaml の検証(要件定義書 8章「共通」の自動項目)。"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from sample_sections import load_sample_sections  # noqa: E402
from validate_items import check, load_spec  # noqa: E402


@pytest.fixture(scope="module")
def spec():
    return load_spec()


def test_sample_has_13_sections():
    assert len(load_sample_sections()) == 13


def test_spec_is_consistent(spec):
    assert check(spec) == []


def test_every_item_has_route(spec):
    assert all(it.get("route") for it in spec["items"])


def test_form_has_9_sections(spec):
    used = {it["section"] for it in spec["items"] if it["route"] == "form"}
    assert used == {s["id"] for s in spec["sections"]}
    assert len(used) == 9


def test_template_themes(spec):
    used = {it["theme"] for it in spec["items"] if it["route"] == "template"}
    assert used == {3, 5, 7}  # 7=キャスト別バック(任意)


def test_only_store_name_is_required(spec):
    # どの店舗の回答か分かるよう、店舗名だけは必須にする
    assert [it["id"] for it in spec["items"] if it.get("required")] == ["store_name"]


def test_excluded_store_info_is_not_asked(spec):
    # 店舗の情報として①②で聞かない(店舗名だけは聞く。③のキャスト個人情報・交通費は別物)
    labels = [it["label"] for it in spec["items"] if it["route"] in ("form", "template") and it["id"] != "store_name"]
    for word in ["店舗名", "業態", "郵便番号", "電話番号", "住所", "事業者名", "最寄り駅"]:
        assert not any(word in label for label in labels), word


# 6章: 個人情報・給与・ログイン情報の項目は ①② に作らない
FORBIDDEN = ["時給", "本名", "生年月日", "口座", "緊急連絡先", "身分証", "源泉区分", "ログイン", "パスワード", "交通費"]


@pytest.mark.parametrize("word", FORBIDDEN)
def test_no_sensitive_items_in_form_or_template(spec, word):
    # 店舗全体のルール(交通費の条件・主に使う源泉区分・繁忙時間帯の時給)は対象外
    allowed = {
        "commute_use", "commute_min_hours", "main_withholding_type", "busy_hours", "busy_hours_use",
    }
    offenders = [
        it["id"]
        for it in spec["items"]
        if it["route"] in ("form", "template")
        and it["id"] not in allowed
        and (word in it["label"] or any(word in c for c in it.get("columns", [])))
    ]
    assert offenders == []


def test_tax_rates_are_fixed(spec):
    by_id = {it["id"]: it for it in spec["items"]}
    assert by_id["tax_rate_standard"]["route"] == "fixed"
    assert by_id["tax_rate_standard"]["default"] == 10
    assert by_id["tax_rate_reduced"]["default"] == 8
