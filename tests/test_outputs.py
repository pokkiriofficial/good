"""フェーズ2〜4: 生成物の検証(要件定義書 8章)。"""

import json
import re
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_form  # noqa: E402
import build_slides  # noqa: E402
import build_templates  # noqa: E402
from validate_items import load_spec  # noqa: E402

UNKNOWN = "未定"
# 「未定」を付けない選択式(領収書のデザインは見本から必ず選ぶ)
NO_UNKNOWN = {"receipt_design"}
# 個人ごとの個人情報・給与・ログイン情報(6章)
SENSITIVE = ["本名", "生年月日", "口座", "緊急連絡先", "身分証", "パスワード", "ログインID"]


@pytest.fixture(scope="module")
def spec():
    return load_spec()


# ── ① 導入アンケート ─────────────────────────────


def test_form_has_9_sections_with_questions(spec):
    fs = build_form.form_spec(spec)
    assert len(fs["sections"]) == 9
    assert all(sec["items"] for sec in fs["sections"])
    assert "レジ" not in [sec["title"] for sec in fs["sections"]]


def test_form_choices_offer_unknown(spec):
    # 全項目が必須。まだ決まっていない選択式は「未定」を選べる
    form = build_form.form_spec(spec)
    for sec in form["sections"]:
        for it in sec["items"]:
            if it["type"] in ("radio", "checkbox", "dropdown", "time", "dial"):
                assert it.get("unknown_option") or it["id"] in NO_UNKNOWN, it["id"]
            assert UNKNOWN not in [str(o) for o in it.get("options", [])], it["id"]
            assert "任意" not in it["label"], it["id"]
    assert any(UNKNOWN in f for f in form["form"]["facts"])


def test_form_removed_questions(spec):
    # レジ・伝票番号の採番・福利厚生費は聞かない。時給の丸めは「勤務時間の丸め」
    labels = [it["label"] for s in build_form.form_spec(spec)["sections"] for it in s["items"]]
    for word in ["レジ金", "過不足", "採番", "伝票番号", "福利厚生", "丸め", "領収書に刷る内容", "税率"]:
        assert not any(word in label for label in labels), word
    for label in ["勤務時間(単位)", "勤務時間(方法)", "バック端数", "バック端数(単位)"]:
        assert label in labels, label


def test_form_asks_yes_no_first(spec):
    # 有無を先に選び、「あり」のときだけ記入欄を出す
    by_id = {it["id"]: it for s in build_form.form_spec(spec)["sections"] for it in s["items"]}
    gates = {
        "price_sets": "price_sets_use", "set_back_mode": "price_sets_use",
        "extension_menu": "extension_use", "extension_back_use": "extension_use",
        "extension_back_mode": "extension_back_use", "food_back_mode": "food_back_use",
        "nomination_types": "nomination_use", "nomination_back_mode": "nomination_use",
        "sales_split": "nomination_use",
        "card_fee": "card_fee_use", "commute_min_hours": "commute_use",
        "commute_full_day_hours": "commute_use", "pay_ratio_alert": "pay_ratio_alert_use",
        "send_areas": "send_areas_use",
    }
    # ハウスチャージは全卓に付き、個室料とは別
    assert "すべての卓" in by_id["house_charge"]["hint"] and "個室料とは別" in by_id["house_charge"]["hint"]
    # ハウスチャージの説明は、ヘルプを押したときに出す(いつも出る説明の欄は置かない)
    assert "house_charge_about" not in by_id
    assert by_id["house_charge"]["help"][0]["title"] == "ハウスチャージ"
    # 個室料・VIP席料は卓の一覧の列、ボトルキープの期限とお知らせ(2026-09-30)
    # 個室料は「個室料の有無=あり」のときだけ卓の一覧に列を出し、空欄でもよい
    t = by_id["tables"]
    c = t["columns"].index("個室料(円)")
    assert t["column_show_if"][str(c)] == {"item": "room_charge_use", "equals": "あり"}
    assert c in t["optional_columns"]
    assert not any("VIP席料" in col for col in t["columns"])
    for gone in ["room_charges", "payment_timing"]:
        assert gone not in by_id, gone
    assert "期限なし" in by_id["bottle_keep_period"]["options"]
    cond = by_id["bottle_keep_alert"]["show_if"]
    assert cond["item"] == "bottle_keep_period" and "期限なし" not in cond["in"] and "3か月" in cond["in"]
    # サービス料は「なし/率で指定(%)/金額で指定(円)/未定」
    sc = by_id["service_charge"]
    assert sc["options"] == ["なし", "率で指定", "金額で指定"] and sc["unknown_option"]
    assert sc["option_inputs"]["率で指定"]["unit"] == "%" and sc["option_inputs"]["金額で指定"]["unit"] == "円"
    # 遅刻控除は「何分ごとに・いくら」。時間はダイヤルで選ぶ
    assert by_id["late_deduction_unit"]["type"] == "dial" and "15分" in by_id["late_deduction_unit"]["options"]
    assert by_id["late_grace_minutes"]["type"] == "dial"
    assert "late_deduction_per_minute" not in by_id
    assert by_id["referral_tags"]["label"] == "お客様の流入経路"
    # プリンターが「ある」ときだけ、機器名を書いてもらう
    assert by_id["printer_device"]["type"] == "short"
    assert by_id["printer_device"]["show_if"] == {"item": "receipt_printer", "equals": "ある"}
    for child, parent in gates.items():
        assert by_id[child]["show_if"] == {"item": parent, "equals": "あり"}, child
        assert by_id[parent]["options"] == ["なし", "あり"], parent
    assert "料金から原価を引いた額" in by_id["bottle_back_base"]["options"]


def test_form_sends_by_copy_only(spec):
    # 回答は「文章をコピー」してLINEに貼ってもらう。アンケートはLINEの中で開くため「LINEで送る」ボタンは置かない
    html = build_form.build(spec)
    assert "文章をコピー" in html
    assert "line.me" not in html
    assert "line://" not in html
    assert '"LINEで送る"' not in html
    assert "管理画面・フロア画面(iPad)" in spec["form"]["changeable"]


def test_receipt_serial_question(spec):
    # 領収書の通し番号は、有無だけを聞く(プリンター・伝票の章、領収書のデザインの次)
    by_id = {it["id"]: (s["title"], it) for s in build_form.form_spec(spec)["sections"] for it in s["items"]}
    title, it = by_id["receipt_serial"]
    assert title == "プリンター・伝票"
    assert it["label"] == "領収書の通し番号の有無"
    assert it["options"] == ["なし", "あり"] and it["unknown_option"]


def test_answer_heading_is_one_line(spec):
    # 回答の文章は「■質問名」を1行にする(ラベルの2行目の補足は入れない)
    html = build_form.build(spec)
    assert '`■${it.label.split("\\n")[0]}`' in html


def test_form_validation_rules_present(spec):
    rules = {it["id"]: it.get("validation") for s in build_form.form_spec(spec)["sections"] for it in s["items"]}
    assert rules["invoice_number"]["pattern"] == r"^T\d{13}$"
    assert rules["house_charge_amount"]["kind"] == "integer"
    assert rules["card_fee"]["max"] == 100


def test_form_html_embeds_spec(spec):
    html = build_form.build(spec)
    assert "/*__SPEC_JSON__*/" not in html
    data = json.loads(re.search(r"const SPEC = (\{.*?\});\n", html).group(1).replace("<\\/", "</"))
    assert data["form"]["title"] == spec["form"]["title"]


def test_form_has_no_sensitive_questions(spec):
    text = json.dumps(build_form.form_spec(spec), ensure_ascii=False)
    for w in SENSITIVE:
        assert w not in text, w


# ── ② 記入テンプレート ─────────────────────────────


def test_line_has_guide_themes_and_closing(spec):
    names = [n for n, _ in build_templates.line_messages(spec)]
    assert names[0] == "00_案内" and names[-1] == "99_最後に"
    assert len(names) == 4


def test_line_lines_fit_phone_width(spec):
    for name, body in build_templates.line_messages(spec):
        for line in body.splitlines():
            assert len(line) <= 35, f"{name}: {line}"


def test_line_roster_warns_against_personal_info(spec):
    body = dict(build_templates.line_messages(spec))["05_キャスト・スタッフ名簿"]
    assert "個人情報は送らないでください" in body


def test_line_asks_no_sensitive_data(spec):
    for name, body in build_templates.line_messages(spec):
        asked = [l for l in body.splitlines() if not l.startswith("※")]
        for w in SENSITIVE + ["時給"]:
            assert not any(w in l and "時給を上げる" not in l for l in asked), (name, w)


def test_line_skip_theme(spec):
    names = [n for n, _ in build_templates.line_messages(spec, skip={5})]
    assert not any(n.startswith("05_") for n in names)


@pytest.fixture(scope="module")
def workbook(spec) -> Workbook:
    return build_templates.build_workbook(spec)


def test_excel_has_six_sheets(workbook, spec):
    assert workbook.sheetnames == [t["sheet"] for t in spec["themes"]]


def test_excel_examples_are_gray(workbook, spec):
    for t in spec["themes"]:
        ws = workbook[t["sheet"]]
        rows = build_templates.sheet_rows(spec, t)
        for n, row in enumerate(rows, start=1):
            if row["kind"] == "example":
                cell = next(ws.cell(row=n, column=c) for c in range(1, 9) if ws.cell(row=n, column=c).value is not None)
                assert cell.font.color.rgb.endswith("9AA0A6")


def test_excel_has_validations(workbook, spec):
    for t in spec["themes"]:
        ws = workbook[t["sheet"]]
        types = {dv.type for dv in ws.data_validations.dataValidation}
        cells = [c for it in build_templates.template_items(spec, t["id"]) for c in it["cells"]]
        if any(isinstance(c, list) for c in cells):
            assert "list" in types, t["sheet"]
        if any(c in ("int", "num") for c in cells):
            assert types & {"whole", "decimal"}, t["sheet"]


def test_excel_has_no_sensitive_columns(workbook):
    for ws in workbook:
        for row in ws.iter_rows(values_only=True):
            for v in row:
                if isinstance(v, str) and not v.startswith("※"):
                    assert not any(w in v for w in SENSITIVE + ["時給"]) or "時給を上げる" in v, v


# ── ③ 対面レクチャー資料 ─────────────────────────────


@pytest.fixture(scope="module")
def lecture(spec):
    return build_slides.load_lecture(spec)


def test_slides_cover_13_chapters(lecture):
    assert [c["id"] for c in lecture["chapters"]] == list(range(14))
    covered = {c for part in lecture["parts"] for sl in part["slides"] for c in build_slides.slide_chapters(sl)}
    assert covered == set(range(1, 14))


def test_slides_total_time_within_visit(spec):
    # 5章の章立ての目安を足すと、全章で123分。キッチン伝票(使う店舗のみ)を除いた標準で90〜120分に収める
    standard = build_slides.load_lecture(spec, exclude={9})["chapters"]
    assert 90 <= build_slides.total_minutes(standard) <= 120


def test_deck_is_15_to_20_slides(lecture):
    _, files = build_slides.deck(lecture)
    assert 15 <= len(files) <= 20


def test_each_part_is_two_or_three_slides(lecture):
    for part in lecture["parts"][:-1]:
        assert 2 <= len(part["slides"]) <= 3, part["title"]


def test_operations_have_three_parts(lecture):
    for part in lecture["parts"]:
        for sl in part["slides"]:
            if sl["kind"] == "ops":
                assert 1 <= len(sl["ops"]) <= 2, sl["title"]
                for op in sl["ops"]:
                    assert 3 <= len(op["steps"]) <= 5, op["title"]
                    assert op["screen"].endswith(".png") and op["try"], op["title"]


def test_slides_exclude_chapter(spec):
    lec = build_slides.load_lecture(spec, exclude={9})
    assert "キッチン伝票" not in build_slides.marp(lec)
    assert len(build_slides.deck(lec)[1]) == len(build_slides.deck(build_slides.load_lecture(spec))[1]) - 1


def test_every_chapter_check_is_shown(lecture):
    _, files = build_slides.deck(lecture)
    html = "".join(files.values())
    for items in lecture["checks"].values():
        for c in items:
            assert c in html, c


def test_deck_ids_and_order(lecture):
    index, files = build_slides.deck(lecture)
    assert index["order"] == list(files)
    assert all(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", i) for i in index["order"])
    for sid, html in files.items():
        assert html.startswith(f'<section id="{sid}"') and html.endswith("</section>")
        assert "<span style" not in html


def test_checklist_fits_one_page(lecture):
    text = build_slides.checklist(lecture)
    assert len(text.splitlines()) <= 40
    for c in build_slides.FINAL_CHECKS:
        assert f"□ {c}" in text


def test_form_options_are_not_split_by_commas(spec):
    # YAML のフロー記法でカンマを含む選択肢が分割されないこと
    by_id = {it["id"]: it for it in spec["items"]}
    assert "ホステス源泉(日額5,000円控除)" in by_id["main_withholding_type"]["options"]
    for it in spec["items"]:
        for o in it.get("options", []):
            s = str(o)
            assert s.count("(") == s.count(")"), (it["id"], s)


def test_workbook_has_all_kinds_with_store_name(spec):
    wb = build_templates.build_workbook(spec, standalone=True)
    assert wb.sheetnames == [t["sheet"] for t in spec["themes"]]
    for ws in wb:
        assert ws["A2"].value == "店舗名"
        assert any("LINEで送って" in str(c.value) for row in ws.iter_rows(max_row=8) for c in row if c.value)



def test_tables_and_send_rules_are_in_form(spec):
    by_id = {it["id"]: it for s in build_form.form_spec(spec)["sections"] for it in s["items"]}
    for i in ["tables", "send_areas", "busy_hours", "nomination_types", "price_sets", "extension_menu"]:
        assert by_id[i]["type"] == "table" and by_id[i]["columns"] and by_id[i]["cells"]
    assert by_id["send_areas"]["show_if"] == {"item": "send_areas_use", "equals": "あり"}
    assert by_id["send_areas"]["columns"][0] == "源氏名"   # 送り代はキャストごとに書く
    names = [n for n, _ in build_templates.line_messages(spec)]
    assert not any("卓" in n or "送り" in n or "指名" in n for n in names)


def test_every_question_has_hint_and_help(spec):
    # 記入する方が迷わないよう、全質問にタイトル下の説明と、具体例つきのヘルプを付ける
    for sec in build_form.form_spec(spec)["sections"]:
        for it in sec["items"]:
            if it["type"] == "note":
                continue
            assert it.get("hint"), it["id"]
            assert it.get("help"), it["id"]
            assert any("例" in h["text"] for h in it["help"]), it["id"]
            for h in it["help"]:
                for line in h["text"].split("\n"):
                    assert len(line) <= 35, (it["id"], line)


def test_line_menu_asks_bottle_cost(spec):
    # ボトルバックを原価を引いた額で計算するお店のため、LINEの文章でボトルの原価を聞く(Excelには足さない)
    body = dict(build_templates.line_messages(spec))["03_商品メニュー"]
    assert "■ボトルキープできる商品と原価" in body
    assert "・例)鏡月/3000" in body
    wb = build_templates.build_workbook(spec, standalone=True)
    assert not any("原価" in str(c.value) for ws in wb for row in ws.iter_rows() for c in row if c.value)


def test_xlsx_bytes_do_not_depend_on_build_time(spec, monkeypatch):
    """記入シートは、いつ作っても同じバイト列になる(差分が毎回出ない)。"""
    import datetime as dt
    import time

    first = build_templates._xlsx_bytes(build_templates.build_workbook(spec, standalone=True))
    real = time.time()
    monkeypatch.setattr(time, "time", lambda: real + 3600)
    monkeypatch.setattr(time, "localtime", lambda *a: dt.datetime.fromtimestamp(real + 3600).timetuple())
    second = build_templates._xlsx_bytes(build_templates.build_workbook(spec, standalone=True))
    assert first == second


def test_xlsx_core_dates_are_fixed(spec):
    import io
    import zipfile

    data = build_templates._xlsx_bytes(build_templates.build_workbook(spec, standalone=True))
    core = zipfile.ZipFile(io.BytesIO(data)).read("docProps/core.xml").decode()
    assert core.count("2026-01-01T00:00:00Z") == 2
