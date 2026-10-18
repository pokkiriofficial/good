"""契約フロー資料(社内・代理店向け)の検証。"""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_contract  # noqa: E402

# 値を資料に書かないもの(ログイン情報は訪問時に設定する)
NO_VALUES = ["パスワード:", "パスワードは「", "ID:"]


@pytest.fixture(scope="module")
def flow():
    return build_contract.load_flow()


def test_pricing_is_as_agreed(flow):
    initial, monthly = build_contract.pricing_rows(flow)
    assert initial == [["新規", "50,000円(税別) = 55,000円(税込)"], ["乗り換え", "0円"]]
    assert monthly == [["ライトプラン", "30,000円(税込)"], ["スタンダードプラン", "50,000円(税込)"]]


def test_billing_example_starts_two_months_after_install(flow):
    # 月額は先払い。導入月(10月)は新規だけ初期費用、乗り換えは請求なし。
    # 11月分は無料で、11月末に12月分から請求が始まる(新規も乗り換えも同じ)
    rows = build_contract.billing_rows(flow)
    assert rows == [["10月末", "初期費用", "請求なし"], ["11月末", "12月分の月額", "12月分の月額"],
                    ["12月末", "1月分の月額", "1月分の月額"]]
    assert not any("11月分" in c for r in rows for c in r)
    ex = flow["billing_example"]
    assert ex["free_month"] == ex["install_month"] + 1
    assert "無料" in ex["point"] and "12月分" in ex["point"]
    assert any("実質1か月無料" in r for r in flow["billing_rules"])


def test_schedule_is_five_days_and_form_due_in_two(flow):
    days = flow["schedule"]["days"]
    assert [d["day"] for d in days] == list(range(6))
    assert "導入日" in days[-1]["task"] and "2日後" in days[2]["task"]
    assert flow["after_contract_steps"][0]["url"] == "https://pokkiri-night-survey.vercel.app"


def test_contract_info_has_company_store_and_billing(flow):
    text = build_contract.contract_info_text(flow)
    for w in ["【ポッキリ.Night】お客様契約情報", "会社名", "代表者", "店舗名", "担当者", "メールアドレス",
              "クレカ or 振込 or 口座振替", "無料期間"]:
        assert w in text, w
    # 会社とお店の連絡先だけ。キャストの個人情報や給与は聞かない
    for w in ["本名", "生年月日", "口座番号", "時給", "源氏名"]:
        assert w not in text, w


def test_doc_has_all_sections_and_figures(flow):
    md = build_contract.doc(flow)
    for h in ["## 1. 全体の流れ", "## 2. 料金", "## 3. 請求のルール", "## 4. 契約時にやること",
              "## 5. 契約日から導入日まで", "## 6. 契約後にKOKU側がやること", "## 7. 導入日にやること",
              "## 8. チェックリスト", "## 9. 未決事項"]:
        assert h in md, h
    for name in build_contract.FIGURES:
        assert f"images/contract/{name}.svg" in md, name


def test_doc_lines_are_short(flow):
    # 文章の行は35文字以内(表・画像・URLは除く)
    for line in build_contract.doc(flow).splitlines():
        s = line.strip()
        if not s or s.startswith(("|", "![", "```")) or "http" in s or "`" in s:
            continue
        s = re.sub(r"^(\d+\.|-|\*|#+|\[ \])\s*", "", s).strip("* ")
        assert len(s) <= 35, line


def test_no_login_values_anywhere(flow):
    figs = build_contract.figures(flow)
    texts = [build_contract.doc(flow), build_contract.marp(flow), build_contract.html(flow, figs), *figs.values()]
    for t in texts:
        for w in NO_VALUES:
            assert w not in t, w


def test_deck_is_8_to_12_slides(flow):
    sl = build_contract.slides(flow)
    assert 8 <= len(sl) <= 12
    assert sl[0]["kind"] == "cover" and sl[-1]["kind"] == "checklist"
    assert build_contract.marp(flow).count("\n---\n") == len(sl) - 1 + 1  # 区切り + front matter の終わり


def test_figures_are_valid_svg_with_titles(flow):
    for name, svg in build_contract.figures(flow).items():
        assert svg.startswith("<svg ") and svg.endswith("</svg>")
        assert f"<title>{build_contract.FIGURES[name]}</title>" in svg
        assert "<text" in svg


def test_wrap_keeps_ascii_words_and_breaks_after_punctuation():
    assert build_contract.wrap("店舗のプリンターとiPadをつなぐ", 11) == ["店舗のプリンターと", "iPadをつなぐ"]
    assert build_contract.wrap("LINEグループを作り、契約情報を記入する", 13) == ["LINEグループを作り、", "契約情報を記入する"]
    assert all(len(l) <= 12 for l in build_contract.wrap("あ" * 30, 12))


def test_html_embeds_figures_and_prints_one_slide_per_page(flow):
    html = build_contract.html(flow, build_contract.figures(flow))
    assert html.count("<section") == len(build_contract.slides(flow))
    assert html.count("<svg ") == len(build_contract.FIGURES)
    assert "page-break-after: always" in html and 'lang="ja"' in html
