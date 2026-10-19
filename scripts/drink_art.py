"""銘柄ごとの商品画像(SVG)を描く。

写真の代わりに、ボトル・グラスの形と色を銘柄ごとに変えた絵を作る
(実在ブランドの写真・ロゴは許諾が要るので使わない)。
形(shape)と色は spec/drinks.yaml の styles と各商品の s で決める。
"""

from __future__ import annotations

import re

SHAPES = [
    "champagne", "wine", "bordeaux", "whisky", "square", "decanter", "cognac", "isshobin", "jar",
    "tequila", "tall", "round", "beer", "can", "mini", "tokkuri", "flute", "glass", "rocks",
    "cocktail", "shot", "mug", "soft", "water", "ice", "plate", "tower", "star",
]
COLOR_KEYS = ["glass", "label", "text", "cap", "liquid"]
BOTTLES = {"champagne", "wine", "bordeaux", "whisky", "square", "decanter", "cognac", "isshobin", "jar",
           "tequila", "tall", "round", "beer", "can", "mini", "tokkuri", "water"}
PREFIXES = ["サントリー ", "ニッカ ", "キリン ", "ホセ・クエルボ ", "クエルボ ", "ザ・", "ルイ・ロデレール ", "ペリエ・ジュエ ",
            "モエ・エ・シャンドン ", "ヴーヴ・クリコ ", "アルマン・ド・ブリニャック ", "マルス ", "ホワイトオーク ",
            "イチローズモルト ", "ブラックニッカ ", "ジョニーウォーカー ", "シーバスリーガル ", "ザ・マッカラン ",
            "ジャックダニエル ", "ジムビーム ", "ワイルドターキー ", "フォアローゼズ ", "ヘネシー ", "レミーマルタン ",
            "マーテル ", "カミュ ", "クルボアジェ ", "ふんわり", "梅乃宿 ", "チョーヤ ", "カフェ・ド・パリ", "サンテロ ",
            "ロジャー・グラート ", "ルジェ ", "シャトー・", "グラス", "ハウス"]


def mark_of(name: str) -> str:
    """ラベルに置く短い目印(商品名の先頭2文字。英字なら3文字まで)。ロゴではない。"""
    s = name
    for p in PREFIXES:
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    s = re.sub(r"[\s・()（）]", "", s)
    if re.match(r"[A-Za-z0-9&.]", s):
        return re.match(r"[A-Za-z0-9&.]{1,3}", s).group(0).upper()
    return s[:2]


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _label(c: dict, mark: str, x: int, y: int, w: int, h: int, r: int = 3, fs: int = 15) -> str:
    text = f'<text x="{x + w/2:.0f}" y="{y + h/2 + fs*0.36:.0f}" text-anchor="middle" font-size="{fs}" font-weight="700" ' \
           f'font-family="Hiragino Sans,Noto Sans JP,sans-serif" fill="{c["text"]}">{_esc(mark)}</text>' if mark else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c["label"]}"/>{text}'


def _gloss(x: int, y: int, h: int, w: int = 6) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#fff" opacity=".18"/>'


def _ice(x: int, y: int, s: int = 14) -> str:
    return f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="3" fill="#fff" opacity=".7" stroke="#9fc3d9" stroke-width="1"/>'


def shape_champagne(c, m):
    return (f'<path d="M48 12h24v38c0 10 20 14 20 32v62a8 8 0 0 1-8 8H36a8 8 0 0 1-8-8V82c0-18 20-22 20-32z" fill="{c["glass"]}"/>'
            f'<path d="M46 8h28v42c0 4 3 8 7 11H39c4-3 7-7 7-11z" fill="{c["cap"]}"/>'
            + _gloss(33, 84, 60) + _label(c, m, 38, 92, 44, 32))


def shape_wine(c, m):
    return (f'<path d="M50 8h20v48c0 8 18 12 18 28v64a6 6 0 0 1-6 6H38a6 6 0 0 1-6-6V84c0-16 18-20 18-28z" fill="{c["glass"]}"/>'
            f'<rect x="48" y="6" width="24" height="16" rx="2" fill="{c["cap"]}"/>'
            + _gloss(36, 86, 56) + _label(c, m, 40, 96, 40, 34))


def shape_bordeaux(c, m):
    return (f'<path d="M51 8h18v44c0 4 2 6 6 8h4a8 8 0 0 1 8 8v80a6 6 0 0 1-6 6H39a6 6 0 0 1-6-6V68a8 8 0 0 1 8-8h4c4-2 6-4 6-8z" fill="{c["glass"]}"/>'
            f'<rect x="49" y="6" width="22" height="18" rx="2" fill="{c["cap"]}"/>'
            + _gloss(37, 72, 70) + _label(c, m, 41, 92, 38, 36))


def shape_whisky(c, m):
    return (f'<path d="M50 10h20v30c0 6 18 8 18 22v82a6 6 0 0 1-6 6H38a6 6 0 0 1-6-6V62c0-14 18-16 18-22z" fill="{c["glass"]}"/>'
            f'<rect x="48" y="6" width="24" height="14" rx="3" fill="{c["cap"]}"/>'
            + _gloss(36, 66, 70) + _label(c, m, 40, 86, 40, 40))


def shape_square(c, m):
    return (f'<path d="M50 10h20v26c0 5 20 6 20 16v90a6 6 0 0 1-6 6H36a6 6 0 0 1-6-6V52c0-10 20-11 20-16z" fill="{c["glass"]}"/>'
            f'<rect x="48" y="6" width="24" height="14" rx="3" fill="{c["cap"]}"/>'
            + _gloss(34, 58, 80) + _label(c, m, 38, 82, 44, 44, 4, 16))


def shape_decanter(c, m):
    return (f'<path d="M52 14h16v30c0 8 26 14 26 44v48a12 12 0 0 1-12 12H38a12 12 0 0 1-12-12V88c0-30 26-36 26-44z" fill="{c["glass"]}"/>'
            f'<rect x="48" y="6" width="24" height="18" rx="5" fill="{c["cap"]}"/>'
            + _gloss(32, 80, 50) + _label(c, m, 42, 96, 36, 30, 15, 13))


def shape_cognac(c, m):
    return (f'<path d="M50 10h20v34c0 8 22 12 22 34v70a6 6 0 0 1-6 6H34a6 6 0 0 1-6-6V78c0-22 22-26 22-34z" fill="{c["glass"]}"/>'
            f'<rect x="48" y="6" width="24" height="16" rx="4" fill="{c["cap"]}"/>'
            + _gloss(32, 82, 56) + _label(c, m, 40, 92, 40, 36, 6))


def shape_isshobin(c, m):
    return (f'<path d="M52 8h16v28c0 4 18 6 18 14v96a6 6 0 0 1-6 6H40a6 6 0 0 1-6-6V50c0-8 18-10 18-14z" fill="{c["glass"]}"/>'
            f'<rect x="50" y="4" width="20" height="12" rx="2" fill="{c["cap"]}"/>'
            + _gloss(38, 56, 86) + _label(c, m, 44, 66, 32, 60, 2, 16))


def shape_jar(c, m):
    return (f'<path d="M36 38h48v6c4 0 8 4 8 10v88a8 8 0 0 1-8 8H36a8 8 0 0 1-8-8V54c0-6 4-10 8-10z" fill="{c["glass"]}"/>'
            f'<rect x="34" y="22" width="52" height="20" rx="4" fill="{c["cap"]}"/>'
            + _gloss(32, 60, 70) + _label(c, m, 40, 80, 40, 40, 6))


def shape_tequila(c, m):
    return (f'<path d="M50 20h20v32c0 8 24 10 24 28v62a8 8 0 0 1-8 8H34a8 8 0 0 1-8-8V80c0-18 24-20 24-28z" fill="{c["glass"]}"/>'
            f'<rect x="46" y="6" width="28" height="22" rx="6" fill="{c["cap"]}"/>'
            + _gloss(31, 82, 52) + _label(c, m, 40, 92, 40, 34, 4))


def shape_tall(c, m):
    return (f'<path d="M50 8h20v24c0 4 14 6 14 14v98a6 6 0 0 1-6 6H42a6 6 0 0 1-6-6V46c0-8 14-10 14-14z" fill="{c["glass"]}"/>'
            f'<rect x="48" y="4" width="24" height="14" rx="3" fill="{c["cap"]}"/>'
            + _gloss(40, 50, 90) + _label(c, m, 44, 72, 32, 48, 3, 14))


def shape_round(c, m):
    return (f'<path d="M50 10h20v38c0 10 24 16 24 42v38a22 22 0 0 1-22 22H48a22 22 0 0 1-22-22V90c0-26 24-32 24-42z" fill="{c["glass"]}"/>'
            f'<rect x="48" y="6" width="24" height="16" rx="4" fill="{c["cap"]}"/>'
            + _gloss(32, 92, 44) + _label(c, m, 42, 98, 36, 30, 8, 13))


def shape_beer(c, m):
    return (f'<path d="M52 12h16v30c0 6 14 8 14 18v84a6 6 0 0 1-6 6H44a6 6 0 0 1-6-6V60c0-10 14-12 14-18z" fill="{c["glass"]}"/>'
            f'<rect x="50" y="6" width="20" height="12" rx="2" fill="{c["cap"]}"/>'
            + _gloss(42, 64, 70) + _label(c, m, 44, 86, 32, 36, 3, 13))


def shape_can(c, m):
    return (f'<rect x="38" y="18" width="44" height="130" rx="8" fill="{c["glass"]}"/>'
            f'<rect x="38" y="18" width="44" height="12" rx="6" fill="{c["cap"]}"/>'
            f'<rect x="38" y="138" width="44" height="10" rx="5" fill="{c["cap"]}"/>'
            + _gloss(42, 34, 100) + _label(c, m, 44, 66, 32, 44, 3, 14))


def shape_mini(c, m):
    return (f'<path d="M52 44h16v16c0 4 10 6 10 12v62a6 6 0 0 1-6 6H48a6 6 0 0 1-6-6V72c0-6 10-8 10-12z" fill="{c["glass"]}"/>'
            f'<rect x="50" y="38" width="20" height="12" rx="3" fill="{c["cap"]}"/>'
            + _gloss(46, 76, 50) + _label(c, m, 48, 86, 24, 30, 3, 11))


def shape_tokkuri(c, m):
    return (f'<path d="M50 30h20v16c0 6 20 10 20 30v52a16 16 0 0 1-16 16H46a16 16 0 0 1-16-16V76c0-20 20-24 20-30z" fill="{c["glass"]}"/>'
            f'<path d="M84 118h22l-3 22a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6z" fill="{c["label"]}"/>'
            + _gloss(34, 80, 44) + _label(c, m, 44, 90, 32, 28, 6, 13))


def shape_flute(c, m):
    return (f'<path d="M46 14h28l-4 70a10 10 0 0 1-20 0z" fill="#fff" stroke="#b9c7d1" stroke-width="2"/>'
            f'<path d="M48 40h24l-2.5 44a9.5 9.5 0 0 1-19 0z" fill="{c["liquid"]}"/>'
            f'<circle cx="56" cy="56" r="1.6" fill="#fff" opacity=".8"/><circle cx="63" cy="66" r="1.4" fill="#fff" opacity=".8"/>'
            f'<rect x="57" y="92" width="6" height="40" fill="#dfe7ec"/><rect x="40" y="132" width="40" height="8" rx="4" fill="#cfd9e0"/>')


def shape_glass(c, m):
    return (f'<path d="M36 20h48l-6 118a8 8 0 0 1-8 8H50a8 8 0 0 1-8-8z" fill="#fff" stroke="#b9c7d1" stroke-width="2"/>'
            f'<path d="M39 48h42l-4.6 90a6 6 0 0 1-6 6H50a6 6 0 0 1-6-6z" fill="{c["liquid"]}"/>'
            + _ice(46, 60) + _ice(60, 78, 12) + _ice(48, 98, 12)
            + (f'<circle cx="78" cy="36" r="13" fill="{c["label"]}" stroke="#fff" stroke-width="2"/>' if c.get("garnish") else ""))


def shape_rocks(c, m):
    return (f'<path d="M30 56h60l-4 86a8 8 0 0 1-8 8H42a8 8 0 0 1-8-8z" fill="#fff" stroke="#b9c7d1" stroke-width="2"/>'
            f'<path d="M33 82h54l-3 60a6 6 0 0 1-6 6H42a6 6 0 0 1-6-6z" fill="{c["liquid"]}"/>'
            + _ice(42, 94, 18) + _ice(62, 104, 16))


def shape_cocktail(c, m):
    return (f'<path d="M22 32h76L60 96z" fill="#fff" stroke="#b9c7d1" stroke-width="2"/>'
            f'<path d="M34 50h52L60 92z" fill="{c["liquid"]}"/>'
            f'<rect x="57" y="96" width="6" height="36" fill="#dfe7ec"/><rect x="36" y="132" width="48" height="8" rx="4" fill="#cfd9e0"/>'
            f'<circle cx="84" cy="34" r="7" fill="{c["label"]}"/>')


def shape_shot(c, m):
    return (f'<path d="M40 62h40l-4 76a8 8 0 0 1-8 8H52a8 8 0 0 1-8-8z" fill="#fff" stroke="#b9c7d1" stroke-width="2"/>'
            f'<path d="M43 84h34l-3 54a6 6 0 0 1-6 6H52a6 6 0 0 1-6-6z" fill="{c["liquid"]}"/>')


def shape_mug(c, m):
    return (f'<path d="M34 50h52v88a8 8 0 0 1-8 8H42a8 8 0 0 1-8-8z" fill="{c["liquid"]}" stroke="#b9c7d1" stroke-width="2"/>'
            f'<path d="M86 66h8a10 10 0 0 1 10 10v30a10 10 0 0 1-10 10h-8" fill="none" stroke="#b9c7d1" stroke-width="6"/>'
            f'<path d="M30 40a12 12 0 0 1 12-12 14 14 0 0 1 26-2 12 12 0 0 1 22 14z" fill="#fff" stroke="#e5e7eb" stroke-width="2"/>'
            + _gloss(40, 60, 70))


def shape_soft(c, m):
    return (f'<path d="M38 26h44l-5 112a8 8 0 0 1-8 8H51a8 8 0 0 1-8-8z" fill="#fff" stroke="#b9c7d1" stroke-width="2"/>'
            f'<path d="M41 52h38l-4 84a6 6 0 0 1-6 6H51a6 6 0 0 1-6-6z" fill="{c["liquid"]}"/>'
            f'<path d="M66 26 86 6" stroke="{c["cap"]}" stroke-width="5" stroke-linecap="round"/>' + _ice(48, 62) + _ice(60, 84, 12))


def shape_water(c, m):
    return (f'<path d="M50 10h20v18c0 4 12 6 12 12v104a6 6 0 0 1-6 6H44a6 6 0 0 1-6-6V40c0-6 12-8 12-12z" fill="{c["glass"]}" stroke="#b9c7d1" stroke-width="1.5"/>'
            f'<rect x="48" y="6" width="24" height="12" rx="3" fill="{c["cap"]}"/>'
            f'<path d="M38 70h44M38 84h44M38 98h44" stroke="#fff" stroke-width="2" opacity=".6"/>' + _label(c, m, 44, 104, 32, 28, 3, 12))


def shape_ice(c, m):
    return (f'<rect x="22" y="56" width="44" height="44" rx="8" fill="#eaf4fa" stroke="#9fc3d9" stroke-width="2"/>'
            f'<rect x="54" y="80" width="44" height="44" rx="8" fill="#f3f9fc" stroke="#9fc3d9" stroke-width="2"/>'
            f'<path d="M86 24s14 15 14 24a14 14 0 0 1-28 0c0-9 14-24 14-24z" fill="{c["liquid"]}"/>')


def shape_plate(c, m):
    return (f'<ellipse cx="60" cy="100" rx="52" ry="22" fill="#fff" stroke="#cfd9e0" stroke-width="3"/>'
            f'<ellipse cx="60" cy="98" rx="34" ry="13" fill="{c["liquid"]}"/>'
            f'<circle cx="48" cy="92" r="6" fill="{c["label"]}"/><circle cx="66" cy="96" r="7" fill="{c["cap"]}"/>')


def shape_tower(c, m):
    g = '<path d="M{x} {y}h18l-2 20a7 7 0 0 1-14 0z" fill="#fff" stroke="#b9c7d1" stroke-width="2"/><path d="M{a} {b}h14l-1.6 14a5.4 5.4 0 0 1-10.8 0z" fill="{l}"/>'
    out = ""
    for row, n in enumerate([1, 2, 3]):
        y = 30 + row * 36
        for i in range(n):
            x = 60 - 9 - (n - 1) * 14 + i * 28
            out += g.format(x=x, y=y, a=x + 2, b=y + 6, l=c["liquid"])
    return out + '<rect x="14" y="140" width="92" height="6" rx="3" fill="#cfd9e0"/>'


def shape_star(c, m):
    return f'<path d="M60 24l11 23 25 3-18 17 4 25-22-12-22 12 4-25-18-17 25-3z" fill="{c["liquid"]}" stroke="{c["cap"]}" stroke-width="3" stroke-linejoin="round"/>'


RENDER = {s: globals()["shape_" + s] for s in SHAPES}


def render(item_id: str, name: str, style: dict, title: str) -> str:
    """1商品ぶんの SVG(120×160)。style は shape と色(glass/label/text/cap/liquid)。"""
    c = {k: style[k] for k in COLOR_KEYS}
    if style.get("garnish"):
        c["garnish"] = True
    shape = style["shape"]
    mark = mark_of(name) if shape in BOTTLES and style.get("mark", True) else ""
    scale = style.get("scale", 1)
    body = RENDER[shape](c, mark)
    if scale != 1:
        body = f'<g transform="translate({60 - 60*scale:.1f} {160 - 160*scale:.1f}) scale({scale})">{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 160" width="120" height="160" role="img" aria-label="{_esc(title)}" data-id="{item_id}">'
            f'<ellipse cx="60" cy="152" rx="34" ry="5" fill="#000" opacity=".08"/>{body}</svg>')
