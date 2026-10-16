#!/usr/bin/env python3
"""ポッキリ.Night 点検係の静的点検(読み取りだけ)。

使い方: python3 scripts/sentinel_static.py <nightwork-pos の読み取り専用クローン>

やること(どれも書き込まない):
  1. 依存パッケージの既知の穴 (npm audit --package-lock-only。lock だけを見る。install しない)
  2. 鍵・トークン・資格情報入り URL の混入、.env* の追跡
  3. cron の入口が CRON_SECRET を確かめているか / 認証の無い API の一覧
  4. migration の並び (_journal.json の idx と when が単調増加か)
  5. 本番ビルドの番人 (package.json の build に build-guard) が外れていないか
結果は Markdown で標準出力へ。終了コードは常に 0(報告専用)。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERNS = [
    (r"sk_(live|test)_[A-Za-z0-9]{10,}", "Stripe/Square 風の鍵"),
    (r"eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JWT"),
    (r"postgres(ql)?://[^:\s]+:[^@\s]+@", "パスワード入りの DB 接続 URL"),
    (r"(SUPABASE_SERVICE_ROLE_KEY|CRON_SECRET|RESEND_API_KEY)\s*=\s*['\"]?[A-Za-z0-9_-]{16,}", "環境変数の値のベタ書き"),
    (r"AKIA[0-9A-Z]{16}", "AWS アクセスキー"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "秘密鍵"),
]
SCAN_DIRS = ("src", "scripts", "docs", "public")
SCAN_EXT = {".ts", ".tsx", ".js", ".mjs", ".json", ".md", ".sh", ".sql", ".yaml", ".yml", ".html"}
KNOWN_DUMMY = ("tests/", ".env.example", "dummy", "example")


def ok(msg: str) -> str:
    return f"| ✅ | {msg} |"


def warn(msg: str) -> str:
    return f"| 🟡 | {msg} |"


def bad(msg: str) -> str:
    return f"| 🔴 | {msg} |"


def check_audit(repo: Path) -> list[str]:
    lock = repo / "package-lock.json"
    if not lock.exists():
        return [warn("package-lock.json が無い。npm audit は未実施")]
    try:
        out = subprocess.run(
            ["npm", "audit", "--package-lock-only", "--omit=dev", "--json"],
            cwd=repo, capture_output=True, text=True, timeout=180,
        ).stdout
        data = json.loads(out or "{}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        return [warn(f"npm audit を実行できない(未確認): {type(e).__name__}")]
    meta = data.get("metadata", {}).get("vulnerabilities", {})
    vulns = data.get("vulnerabilities", {})
    crit = [k for k, v in vulns.items() if v.get("severity") == "critical"]
    high = [k for k, v in vulns.items() if v.get("severity") == "high"]
    lines = []
    summary = f"npm audit(本番依存のみ): critical {meta.get('critical', 0)} / high {meta.get('high', 0)} / moderate {meta.get('moderate', 0)}"
    if crit:
        lines.append(bad(summary + " ── critical: " + ", ".join(sorted(crit))))
    elif high:
        lines.append(warn(summary + " ── high: " + ", ".join(sorted(high))))
    else:
        lines.append(ok(summary))
    for k, v in sorted(vulns.items()):
        if v.get("severity") in ("critical", "high"):
            fix = v.get("fixAvailable")
            fix_s = "fix あり" if fix else "fix なし"
            lines.append(f"|  | `{k}` {v.get('severity')} 範囲 `{v.get('range')}` {fix_s} |")
    return lines


def check_secrets(repo: Path) -> list[str]:
    hits: list[str] = []
    for d in SCAN_DIRS:
        base = repo / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix not in SCAN_EXT:
                continue
            rel = p.relative_to(repo).as_posix()
            if any(k in rel for k in KNOWN_DUMMY):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pat, label in SECRET_PATTERNS:
                for m in re.finditer(pat, text):
                    line = text.count("\n", 0, m.start()) + 1
                    hits.append(f"{rel}:{line} ({label})")
    lines = [bad(f"鍵・トークンらしき文字列: {len(hits)} 件")] if hits else [ok("鍵・トークンらしき文字列: 0 件")]
    lines += [f"|  | {h} |" for h in hits[:20]]
    tracked = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True).stdout.splitlines()
    env_tracked = [t for t in tracked if re.match(r"(.*/)?\.env(\..*)?$", t) and not t.endswith(".example")]
    lines.append(bad(f".env* がコミットされている: {', '.join(env_tracked)}") if env_tracked else ok(".env* はコミットされていない"))
    return lines


def check_api_routes(repo: Path) -> list[str]:
    lines = []
    api = repo / "src" / "app" / "api"
    if not api.exists():
        return [warn("src/app/api が無い(未確認)")]
    for route in sorted(api.rglob("route.ts")):
        rel = route.relative_to(repo).as_posix()
        text = route.read_text(encoding="utf-8", errors="ignore")
        if "/api/cron/" in rel:
            if "CRON_SECRET" in text:
                tsafe = "timingSafeEqual" in text
                lines.append(ok(f"{rel}: CRON_SECRET を確認" + ("" if tsafe else "(比較は `===`。timingSafeEqual が望ましい)")))
            else:
                lines.append(bad(f"{rel}: CRON_SECRET の確認が無い(誰でも実行できる)"))
            continue
        guards = [g for g in ("requirePlatformAdmin", "resolveCommandContext", "timingSafeEqual", "verifySignature", "verifyLineSignature", "x-line-signature", "Bearer", "sdp-token", "verifyToken", "findPrinterByToken", "requireOwnerCtx", "getUser(") if g in text]
        if guards:
            lines.append(ok(f"{rel}: 守り = {', '.join(guards)}"))
        else:
            lines.append(warn(f"{rel}: 認証らしき処理が見当たらない(中身を確認)"))
    return lines


def check_journal(repo: Path) -> list[str]:
    j = repo / "src" / "db" / "migrations" / "meta" / "_journal.json"
    if not j.exists():
        return [warn("migrations/meta/_journal.json が無い(未確認)")]
    entries = json.loads(j.read_text(encoding="utf-8")).get("entries", [])
    problems = []
    for prev, cur in zip(entries, entries[1:]):
        if cur.get("idx", 0) <= prev.get("idx", 0):
            problems.append(f"idx が戻る: {prev.get('tag')} → {cur.get('tag')}")
        if cur.get("when", 0) <= prev.get("when", 0):
            problems.append(f"when が戻る: {prev.get('tag')} → {cur.get('tag')}(本番に永久に当たらない形)")
    sql_count = len(list((repo / "src" / "db" / "migrations").glob("*.sql")))
    if problems:
        return [bad(f"migration の並び: {len(problems)} 件の逆順")] + [f"|  | {p} |" for p in problems]
    return [ok(f"migration の並び: {len(entries)} 件が単調増加(SQL ファイル {sql_count} 件)")]


def check_build_guard(repo: Path) -> list[str]:
    pkg = repo / "package.json"
    if not pkg.exists():
        return [warn("package.json が無い(未確認)")]
    build = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {}).get("build", "")
    if "build-guard" in build:
        return [ok(f"本番ビルドの番人: build = `{build}`")]
    return [bad(f"本番ビルドの番人が外れている: build = `{build}`")]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 0
    repo = Path(argv[1]).resolve()
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--short"], cwd=repo, capture_output=True, text=True).stdout.strip()
    print(f"# 静的点検 {repo.name} @ {head or '(git なし)'}\n")
    print("| 判定 | 項目 |\n|---|---|")
    print(bad("作業ツリーに変更がある(点検係は書き込まない。誰かの作業中か)") if dirty else ok("作業ツリーは clean"))
    for section, fn in (
        ("依存パッケージ", check_audit),
        ("鍵・トークンの混入", check_secrets),
        ("API の入口と cron の秘密", check_api_routes),
        ("migration の並び", check_journal),
        ("本番ビルドの番人", check_build_guard),
    ):
        print(f"| **{section}** |  |")
        for line in fn(repo):
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
