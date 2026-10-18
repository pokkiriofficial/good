"""契約フロー(契約〜導入日)の資料を templates/contract/flow.yaml から生成する。

社内と代理店が読む資料。簡潔でシンプルに、図解で流れがわかるようにする。

使い方: python scripts/build_contract.py
  → docs/contract_flow.md          説明ドキュメント(Markdown)
  → docs/images/contract/*.svg     図解(ドキュメントとスライドで共用)
  → slides/contract.md             スライド(Marp。PDF・PPTXは Marp CLI で出力)
  → slides/contract.html           ブラウザで開けるスライド(印刷でPDFにできる)
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "templates" / "contract" / "flow.yaml"
OUT_DOC = ROOT / "docs" / "contract_flow.md"
OUT_IMG = ROOT / "docs" / "images" / "contract"
OUT_MARP = ROOT / "slides" / "contract.md"
OUT_HTML = ROOT / "slides" / "contract.html"

# 配色は③レクチャー資料(build_slides.py)と同じ
INK, LIGHT, SOFT, ACCENT, DARK, MUTED, LINE = "#1c2433", "#f3f6fb", "#e3eaf5", "#1f3a6b", "#14213b", "#5b6678", "#cfd8e6"
CARD = "#ffffff"
STORE = "#2e7d5b"       # 店舗がやること
FREE_BG = "#e6f4ea"     # 無料の期間
FONT = "'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', sans-serif"

FIGURES = {
    "01_overview": "全体の流れ",
    "02_billing": "請求の例(10月に導入した場合)",
    "03_schedule": "契約日から導入日までのスケジュール",
    "04_install": "導入日の流れ",
}


def load_flow() -> dict:
    return yaml.safe_load(SRC.read_text(encoding="utf-8"))


# ── 文章の道具 ────────────────────────────────────


def yen(amount: int) -> str:
    return f"{amount:,}円"


def price(entry: dict, tax_rate: int) -> str:
    """金額に税の区分を添える。税別なら税込の参考額も添える。"""
    if entry["amount"] == 0:
        return "0円"
    s = f"{yen(entry['amount'])}({entry['tax']})"
    if entry["tax"] == "税別":
        s += f" = {yen(entry['amount'] * (100 + tax_rate) // 100)}(税込)"
    return s


def wrap(text: str, width: int) -> list[str]:
    """図の中の文を width 文字以内の行に分ける。読点や括弧の後で切り、英単語(iPad など)は途中で切らない。"""
    units: list[str] = []
    for ch in text:
        if ch.isascii() and ch.isalnum() and units and units[-1][-1].isascii() and units[-1][-1].isalnum():
            units[-1] += ch
        else:
            units.append(ch)
    lines, cur, last_break = [], "", -1
    for u in units:
        if cur and len(cur) + len(u) > width:
            if last_break > width // 2:
                lines.append(cur[:last_break])
                cur = cur[last_break:]
            else:
                lines.append(cur)
                cur = ""
            last_break = -1
        cur += u
        if u in "、。)・":
            last_break = len(cur)
    if cur:
        lines.append(cur)
    return lines


# ── SVG の道具 ─────────────────────────────────────


def _t(x: float, y: float, s: str, size: int = 20, weight: int = 400, fill: str = INK, anchor: str = "start") -> str:
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{escape(s)}</text>')


def _lines(x: float, y: float, lines: list[str], size: int = 20, fill: str = INK, anchor: str = "start",
           lh: float = 1.5) -> str:
    return "".join(_t(x, y + i * size * lh, s, size, 400, fill, anchor) for i, s in enumerate(lines))


def _rect(x: float, y: float, w: float, h: float, fill: str = CARD, stroke: str = LINE, r: int = 12, sw: int = 2) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def _arrow(x1: float, y: float, x2: float, color: str = MUTED) -> str:
    return (f'<line x1="{x1}" y1="{y}" x2="{x2 - 10}" y2="{y}" stroke="{color}" stroke-width="3"/>'
            f'<polygon points="{x2 - 14},{y - 8} {x2},{y} {x2 - 14},{y + 8}" fill="{color}"/>')


def _badge(x: float, y: float, s: str, color: str, size: int = 16) -> str:
    w = len(s) * size + 20
    return (f'<rect x="{x}" y="{y - size - 4}" width="{w}" height="{size + 12}" rx="{(size + 12) // 2}" fill="{color}"/>'
            + _t(x + w / 2, y + 2, s, size, 700, "#ffffff", "middle"))


def _svg(w: int, h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title><rect width="{w}" height="{h}" fill="{LIGHT}" rx="16"/>{body}</svg>')


def who_color(who: str) -> str:
    return STORE if who.startswith("店舗") and "KOKU" not in who else ACCENT


# ── 図解 ─────────────────────────────────────────


def fig_overview(flow: dict) -> str:
    steps, w, h = flow["overview"], 1200, 300
    gap, bw = 40, (w - 80 - 40 * 3) // 4
    body = ""
    for i, st in enumerate(steps):
        x = 40 + i * (bw + gap)
        body += _rect(x, 50, bw, 210)
        body += f'<circle cx="{x + 34}" cy="84" r="20" fill="{ACCENT}"/>' + _t(x + 34, 92, str(i + 1), 22, 700, "#fff", "middle")
        body += _t(x + 66, 93, st["title"], 28, 700, ACCENT)
        body += _t(x + 20, 134, st["day"], 18, 400, MUTED)
        body += _badge(x + 20, 172, st["who"], who_color(st["who"]))
        body += _lines(x + 20, 212, wrap(st["summary"], 12), 18)
        if i < len(steps) - 1:
            body += _arrow(x + bw + 6, 155, x + bw + gap - 6)
    return _svg(w, h, body, FIGURES["01_overview"])


def fig_billing(flow: dict) -> str:
    ex, w, h = flow["billing_example"], 1200, 440
    months = ex["months"] + [ex["months"][-1] % 12 + 1]
    x0, mw, rows_y = 250, 220, [230, 350]
    body = ""
    # 無料の月の帯
    fx = x0 + months.index(ex["free_month"]) * mw
    body += f'<rect x="{fx}" y="70" width="{mw}" height="{h - 110}" rx="12" fill="{FREE_BG}"/>'
    body += _t(fx + mw / 2, 100, "この月の月額は無料", 18, 700, STORE, "middle")
    body += _t(fx + mw / 2, 124, "(実質1か月無料)", 18, 400, STORE, "middle")
    # 月の目盛り
    for i, m in enumerate(months):
        x = x0 + i * mw
        body += f'<line x1="{x}" y1="150" x2="{x}" y2="{h - 50}" stroke="{LINE}" stroke-width="2"/>'
        label = f"{m}月(導入月)" if m == ex["install_month"] else f"{m}月"
        body += _t(x + mw / 2, 178, label, 24 if m != ex["install_month"] else 20, 700, INK, "middle")
    body += _t(x0 + 50, 70 - 10, "▼ 導入日(月初でも月末でも同じ)", 16, 400, MUTED)
    body += f'<line x1="{x0 + 50}" y1="70" x2="{x0 + 50}" y2="{h - 50}" stroke="{STORE}" stroke-width="2" stroke-dasharray="6 6"/>'
    for case, y in zip(ex["cases"], rows_y):
        body += _lines(30, y - 6, case["label"].replace("(", "\n(").split("\n"), 20, INK)
        body += f'<line x1="{x0}" y1="{y}" x2="{x0 + mw * len(ex["months"])}" y2="{y}" stroke="{MUTED}" stroke-width="2"/>'
        for i, ch in enumerate(case["charges"]):
            x = x0 + (i + 1) * mw
            if ch["items"]:
                body += f'<circle cx="{x}" cy="{y}" r="11" fill="{ACCENT}"/>'
                body += _t(x, y - 20, ch["when"], 16, 700, ACCENT, "middle")
                body += _lines(x, y + 32, ch["items"], 16, INK, "middle", 1.35)
            else:
                body += f'<circle cx="{x}" cy="{y}" r="10" fill="{LIGHT}" stroke="{MUTED}" stroke-width="2"/>'
                body += _t(x, y - 20, ch["when"], 16, 400, MUTED, "middle")
                body += _t(x, y + 32, "請求なし", 16, 400, MUTED, "middle")
    body += _t(w / 2, h - 14, ex["point"], 20, 700, STORE, "middle")
    return _svg(w, h, body, FIGURES["02_billing"])


def fig_schedule(flow: dict) -> str:
    days, w, h = flow["schedule"]["days"], 1200, 330
    gap, bw = 16, (w - 60 - 16 * 5) // 6
    body = _t(30, 40, flow["schedule"]["ideal"], 20, 400, MUTED)
    for i, d in enumerate(days):
        x = 30 + i * (bw + gap)
        last = i == len(days) - 1
        body += _rect(x, 60, bw, 230, SOFT if last else CARD, ACCENT if last or i == 0 else LINE)
        body += _t(x + bw / 2, 100, d["label"], 24, 700, ACCENT, "middle")
        body += _badge(x + 14, 140, d["who"], who_color(d["who"]))
        body += _lines(x + 14, 178, wrap(d["task"], 9), 17)
    return _svg(w, h, body, FIGURES["03_schedule"])


def fig_install(flow: dict) -> str:
    steps, w, h = flow["install"]["steps"], 1200, 300
    gap, bw = 22, (w - 60 - 22 * 4) // 5
    body = _t(30, 40, f"所要時間 {flow['install']['duration']}", 20, 700, ACCENT)
    for i, st in enumerate(steps):
        x = 30 + i * (bw + gap)
        body += _rect(x, 60, bw, 220)
        body += f'<circle cx="{x + 32}" cy="94" r="20" fill="{ACCENT}"/>' + _t(x + 32, 102, str(i + 1), 22, 700, "#fff", "middle")
        body += _t(x + 16, 150, st["title"], 20, 700, ACCENT)
        body += _lines(x + 16, 190, wrap(st["detail"], 11), 16, INK)
        if i < len(steps) - 1:
            body += _arrow(x + bw + 3, 170, x + bw + gap - 3)
    return _svg(w, h, body, FIGURES["04_install"])


def figures(flow: dict) -> dict[str, str]:
    return {"01_overview": fig_overview(flow), "02_billing": fig_billing(flow),
            "03_schedule": fig_schedule(flow), "04_install": fig_install(flow)}


# ── 資料に共通の部品 ───────────────────────────────


def pricing_rows(flow: dict) -> tuple[list[list[str]], list[list[str]]]:
    p, rate = flow["pricing"], flow["pricing"]["tax_rate"]
    initial = [[v["label"], price(v, rate)] for v in (p["initial"]["new"], p["initial"]["switch"])]
    monthly = [[m["name"], price(m, rate)] for m in p["monthly"]]
    return initial, monthly


def billing_rows(flow: dict) -> list[list[str]]:
    ex = flow["billing_example"]
    out = []
    for i, ch in enumerate(ex["cases"][0]["charges"]):
        out.append([ch["when"]] + ["・".join(c["charges"][i]["items"]) or "請求なし" for c in ex["cases"]])
    return out


def contract_info_text(flow: dict) -> str:
    """LINEグループに書いてもらう項目。コピーして貼れる形。"""
    ci = flow["contract_info"]
    lines = [ci["heading"]] + [f"・{c}:" for c in ci["company"]] + ["ーーーーーーーーーー"] + [f"・{s}:" for s in ci["store"]]
    for b in ci["billing"]:
        if "options" in b:
            lines.append(f"・{b['label']}: 『{' or '.join(b['options'])}』")
        else:
            lines.append(f"・{b['label']}: ({b['note']})")
    return "\n".join(lines)


def md_table(columns: list[str], rows: list[list[str]]) -> list[str]:
    return ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)] + ["| " + " | ".join(r) + " |" for r in rows]


# ── ドキュメント(Markdown) ─────────────────────────


def doc(flow: dict) -> str:
    initial, monthly = pricing_rows(flow)
    img = "images/contract"
    out = [f"# {flow['title']}", "", f"{flow['subtitle']}({flow['audience']})", "",
           "この資料は、契約から導入日までに", "誰が・いつ・何をするかをまとめたものです。", "",
           "元データは `templates/contract/flow.yaml`。", "直すときはYAMLを直し、再生成してください。", "",
           "## 1. 全体の流れ", "", f"![{FIGURES['01_overview']}]({img}/01_overview.svg)", ""]
    out += md_table(["段階", "誰が", "いつ", "すること"],
                    [[s["title"], s["who"], s["day"], s["summary"]] for s in flow["overview"]])
    out += ["", "## 2. 料金", "", "### 初期費用", ""]
    out += md_table(["区分", "金額"], initial)
    out += ["", flow["pricing"]["initial"]["note"], "", "### 月額(先払い)", ""]
    out += md_table(["プラン", "月額"], monthly)
    out += ["", "## 3. 請求のルール", ""]
    out += [f"- {r}" for r in flow["billing_rules"]]
    out += ["", f"### 例: {flow['billing_example']['install_month']}月に導入した場合", "",
            f"![{FIGURES['02_billing']}]({img}/02_billing.svg)", ""]
    out += md_table(["請求日"] + [c["label"] for c in flow["billing_example"]["cases"]], billing_rows(flow))
    out += ["", f"**{flow['billing_example']['point']}**", "",
            "## 4. 契約時にやること(その場で)", ""]
    for i, st in enumerate(flow["contract_steps"], 1):
        out.append(f"{i}. **{st['title']}**  ")
        out.append(f"   {st['detail']}")
        if "members" in st:
            out.append(f"   KOKU側の招待: {'・'.join(st['members'])}")
    out += ["", "### LINEグループに書いてもらう項目", "",
            "会社とお店の連絡先だけを書いてもらいます。", "キャストの個人情報は含めません。", "",
            "```", contract_info_text(flow), "```", "",
            "## 5. 契約日から導入日までのスケジュール", "", f"![{FIGURES['03_schedule']}]({img}/03_schedule.svg)", ""]
    out += md_table(["日", "誰が", "すること"], [[d["label"], d["who"], d["task"]] for d in flow["schedule"]["days"]])
    out += [""] + [f"- {t}" for t in flow["schedule"]["tips"]]
    out += ["", "## 6. 契約後にKOKU側がやること", ""]
    for i, st in enumerate(flow["after_contract_steps"], 1):
        out.append(f"{i}. **{st['title']}**  ")
        out.append(f"   {st['detail']}")
        if "url" in st:
            out.append(f"   {st['url']}")
        out += [f"   - {n}" for n in st.get("notes", [])]
    out += ["", f"## 7. 導入日にやること({flow['install']['duration']})", "",
            f"![{FIGURES['04_install']}]({img}/04_install.svg)", ""]
    for i, st in enumerate(flow["install"]["steps"], 1):
        out.append(f"{i}. **{st['title']}**  ")
        out.append(f"   {st['detail']}")
        out += [f"   - {n}" for n in st.get("notes", [])]
    out += ["", "## 8. チェックリスト", ""]
    for phase, items in flow["checklist"].items():
        out += [f"### {phase}", ""] + [f"- [ ] {c}" for c in items] + [""]
    out += ["## 9. 未決事項", ""] + [f"- {o}" for o in flow["open_issues"]]
    return "\n".join(out) + "\n"


# ── スライド(Marp) ─────────────────────────────────


def slides(flow: dict) -> list[dict]:
    """スライドの中身。Marp と HTML で共用する。

    kind: cover / figure / table / bullets / steps / checklist
    """
    initial, monthly = pricing_rows(flow)
    ex = flow["billing_example"]
    return [
        {"kind": "cover", "title": flow["title"], "sub": flow["subtitle"], "note": flow["audience"]},
        {"kind": "figure", "title": "全体の流れ", "figure": "01_overview",
         "bullets": [f"{s['title']}: {s['summary']}" for s in flow["overview"]]},
        {"kind": "tables", "title": "料金", "tables": [
            ("初期費用", ["区分", "金額"], initial), ("月額(先払い)", ["プラン", "月額"], monthly)],
         "note": flow["pricing"]["initial"]["note"]},
        {"kind": "bullets", "title": "請求のルール", "bullets": flow["billing_rules"]},
        {"kind": "figure", "title": f"請求の例: {ex['install_month']}月に導入した場合", "figure": "02_billing",
         "table": (["請求日"] + [c["label"] for c in ex["cases"]], billing_rows(flow)), "point": ex["point"]},
        {"kind": "steps", "title": "契約時にやること(その場で)",
         "steps": [(st["title"], st["detail"] + (f"(招待: {'・'.join(st['members'])})" if "members" in st else ""))
                   for st in flow["contract_steps"]],
         "code": contract_info_text(flow)},
        {"kind": "figure", "title": "契約日から導入日まで", "figure": "03_schedule", "bullets": flow["schedule"]["tips"]},
        {"kind": "steps", "title": "契約後にKOKU側がやること",
         "steps": [(st["title"], st["detail"] + (f"  {st['url']}" if "url" in st else ""), st.get("notes", []))
                   for st in flow["after_contract_steps"]]},
        {"kind": "figure", "title": f"導入日にやること({flow['install']['duration']})", "figure": "04_install",
         "bullets": [n for st in flow["install"]["steps"] for n in st.get("notes", [])]},
        {"kind": "checklist", "title": "チェックリスト", "groups": flow["checklist"]},
    ]


def marp(flow: dict) -> str:
    img = "../docs/images/contract"
    out = ["---", "marp: true", "size: 16:9", "paginate: true",
           "style: |",
           f"  section {{ font-family: {FONT}; background: {LIGHT}; color: {INK}; font-size: 24px; }}",
           f"  h1, h2 {{ color: {ACCENT}; }}",
           "  img { max-height: 400px; width: auto; }",
           "  .cols { display: flex; gap: 40px; align-items: flex-start; }",
           "  .cols > * { flex: 1; }",
           "  pre { font-size: 16px; line-height: 1.35; }",
           f"  .note {{ color: {MUTED}; font-size: 20px; }}",
           "---", ""]
    first = True
    for sl in slides(flow):
        if not first:
            out += ["", "---", ""]
        first = False
        if sl["kind"] == "cover":
            out += [f"# {sl['title']}", "", sl["sub"], "", f"{sl['note']} / {flow['company']}"]
            continue
        out += [f"## {sl['title']}", ""]
        if sl["kind"] == "figure":
            out += [f"![{FIGURES[sl['figure']]}]({img}/{sl['figure']}.svg)", ""]
            if "table" in sl:
                out += md_table(*sl["table"]) + [""]
            if "point" in sl:
                out += [f"**{sl['point']}**", ""]
            out += [f"- {b}" for b in sl.get("bullets", [])]
        elif sl["kind"] == "tables":
            out.append('<div class="cols">')
            for name, cols, rows in sl["tables"]:
                out += ["", "<div>", "", f"### {name}", ""] + md_table(cols, rows) + ["", "</div>"]
            out += ["", "</div>", "", f'<p class="note">{sl["note"]}</p>']
        elif sl["kind"] == "bullets":
            out += [f"- {b}" for b in sl["bullets"]]
        elif sl["kind"] == "steps":
            if "code" in sl:
                out.append('<div class="cols">')
                out += ["", "<div>", ""]
            for i, st in enumerate(sl["steps"], 1):
                title, detail, notes = (st + ([],))[:3]
                out += [f"{i}. **{title}**  ", f"   {detail}"]
                out += [f"   - {n}" for n in notes]
            if "code" in sl:
                out += ["", "</div>", "", "<div>", "", "```", sl["code"], "```", "", "</div>", "", "</div>"]
        elif sl["kind"] == "checklist":
            out.append('<div class="cols">')
            for phase, items in sl["groups"].items():
                out += ["", "<div>", "", f"### {phase}", ""] + [f"- [ ] {c}" for c in items] + ["", "</div>"]
            out += ["", "</div>"]
    return "\n".join(out) + "\n"


# ── スライド(HTML) ─────────────────────────────────


def _h_table(cols: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _h_list(items: list[str], check: bool = False) -> str:
    cls = ' class="check"' if check else ""
    return f"<ul{cls}>" + "".join(f"<li>{escape(i)}</li>" for i in items) + "</ul>"


def _h_steps(steps: list[tuple]) -> str:
    out = "<ol>"
    for st in steps:
        title, detail, notes = (tuple(st) + ([],))[:3]
        out += f"<li><b>{escape(title)}</b><br>{escape(detail)}"
        if notes:
            out += _h_list(notes)
        out += "</li>"
    return out + "</ol>"


def html(flow: dict, figs: dict[str, str]) -> str:
    sections = []
    total = len(slides(flow))
    for n, sl in enumerate(slides(flow), 1):
        if sl["kind"] == "cover":
            sections.append(
                f'<section class="cover"><div><h1>{escape(sl["title"])}</h1><p class="sub">{escape(sl["sub"])}</p>'
                f'<p class="meta">{escape(sl["note"])} / {escape(flow["company"])}</p></div></section>')
            continue
        body = ""
        if sl["kind"] == "figure":
            cls = "fig compact" if "table" in sl else "fig"
            body += f'<div class="{cls}">{figs[sl["figure"]]}</div>'
            if "table" in sl:
                body += _h_table(*sl["table"])
            if "point" in sl:
                body += f'<p class="point">{escape(sl["point"])}</p>'
            if sl.get("bullets"):
                body += _h_list(sl["bullets"])
        elif sl["kind"] == "tables":
            body += '<div class="cols">' + "".join(
                f"<div><h3>{escape(name)}</h3>{_h_table(cols, rows)}</div>" for name, cols, rows in sl["tables"]) + "</div>"
            body += f'<p class="note">{escape(sl["note"])}</p>'
        elif sl["kind"] == "bullets":
            body += _h_list(sl["bullets"])
        elif sl["kind"] == "steps":
            if "code" in sl:
                body += f'<div class="cols"><div>{_h_steps(sl["steps"])}</div><div><pre>{escape(sl["code"])}</pre></div></div>'
            else:
                body += _h_steps(sl["steps"])
        elif sl["kind"] == "checklist":
            body += '<div class="cols">' + "".join(
                f"<div><h3>{escape(phase)}</h3>{_h_list(items, check=True)}</div>"
                for phase, items in sl["groups"].items()) + "</div>"
        sections.append(f'<section><h2>{escape(sl["title"])}</h2>{body}'
                        f'<footer><span>{escape(flow["title"])}</span><span>{n} / {total}</span></footer></section>')
    css = f"""
:root {{ --ink:{INK}; --light:{LIGHT}; --soft:{SOFT}; --accent:{ACCENT}; --dark:{DARK}; --muted:{MUTED}; --line:{LINE}; --store:{STORE}; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #d9dee8; font-family: {FONT}; color: var(--ink); }}
main {{ display: flex; flex-direction: column; gap: 16px; padding: 16px; align-items: center; }}
section {{ container-type: inline-size; width: min(100%, 1280px); aspect-ratio: 16 / 9; background: var(--light);
  border-radius: 12px; padding: 3cqw 4cqw 4.5cqw; position: relative; overflow: hidden; font-size: 1.6cqw; line-height: 1.45;
  display: flex; flex-direction: column; gap: 1.2cqw; }}
section.cover {{ background: var(--dark); color: var(--light); justify-content: flex-end; }}
section.cover h1 {{ font-size: 4.5cqw; margin: 0 0 1cqw; color: #fff; }}
section.cover .sub {{ font-size: 2.4cqw; margin: 0; }}
section.cover .meta {{ color: #b8c2d6; margin: 1cqw 0 0; }}
h2 {{ font-size: 2.8cqw; color: var(--accent); margin: 0; }}
h3 {{ font-size: 1.9cqw; color: var(--accent); margin: 0 0 0.6cqw; }}
.fig svg {{ width: 100%; height: auto; max-height: 36cqw; display: block; }}
.fig.compact svg {{ max-height: 26cqw; }}
.cols {{ display: flex; gap: 3cqw; align-items: flex-start; }}
.cols > * {{ flex: 1; min-width: 0; }}
table {{ border-collapse: collapse; width: 100%; background: #fff; font-size: 1.6cqw; }}
th, td {{ border: 1px solid var(--line); padding: 0.5cqw 1cqw; text-align: left; }}
th {{ background: var(--soft); }}
ul, ol {{ margin: 0; padding-left: 2.2cqw; }}
li {{ margin: 0.25cqw 0; }}
li ul {{ font-size: 0.92em; color: var(--muted); }}
ul.check {{ list-style: none; padding-left: 0; }}
ul.check li::before {{ content: "□ "; color: var(--accent); font-weight: 700; }}
pre {{ background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 1cqw 1.4cqw; font-size: 1.35cqw;
  line-height: 1.4; margin: 0; font-family: {FONT}; white-space: pre-wrap; }}
.point {{ font-weight: 700; color: var(--store); margin: 0; }}
.note {{ color: var(--muted); margin: 0; }}
footer {{ position: absolute; left: 4cqw; right: 4cqw; bottom: 1.4cqw; display: flex; justify-content: space-between;
  font-size: 1.2cqw; color: var(--muted); }}
@media print {{
  @page {{ size: 1280px 720px; margin: 0; }}
  body {{ background: #fff; }}
  main {{ padding: 0; gap: 0; }}
  section {{ width: 1280px; border-radius: 0; page-break-after: always; break-after: page; }}
}}
"""
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{escape(flow["title"])}</title><style>{css}</style></head>'
            f'<body><main>{"".join(sections)}</main></body></html>\n')


# ── 書き出し ──────────────────────────────────────


def main() -> None:
    flow = load_flow()
    figs = figures(flow)
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    for name, svg in figs.items():
        (OUT_IMG / f"{name}.svg").write_text(svg + "\n", encoding="utf-8")
    OUT_DOC.write_text(doc(flow), encoding="utf-8")
    OUT_MARP.write_text(marp(flow), encoding="utf-8")
    OUT_HTML.write_text(html(flow, figs), encoding="utf-8")
    print(f"{OUT_DOC.relative_to(ROOT)}, {OUT_MARP.relative_to(ROOT)}, {OUT_HTML.relative_to(ROOT)}, "
          f"{len(figs)} figures in {OUT_IMG.relative_to(ROOT)}/ ({len(slides(flow))} slides)")


if __name__ == "__main__":
    main()
