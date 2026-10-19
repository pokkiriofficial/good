"""scripts/sentinel_static.py の判定が、偽のリポジトリで期待どおりに出ることを確かめる。"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sentinel_static as ss  # noqa: E402


def _fake_repo(tmp_path: Path, *, journal_ok=True, guard=True, cron_secret=True) -> Path:
    repo = tmp_path / "pos"
    (repo / "src/db/migrations/meta").mkdir(parents=True)
    (repo / "src/app/api/cron/x").mkdir(parents=True)
    (repo / "src/app/api/time").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    entries = [{"idx": 0, "when": 100, "tag": "0000_a"}, {"idx": 1, "when": 200 if journal_ok else 50, "tag": "0001_b"}]
    (repo / "src/db/migrations/meta/_journal.json").write_text(json.dumps({"entries": entries}))
    (repo / "src/db/migrations/0000_a.sql").write_text("select 1;")
    (repo / "package.json").write_text(json.dumps({"scripts": {"build": "tsx scripts/build-guard.ts && next build" if guard else "next build"}}))
    (repo / "src/app/api/cron/x/route.ts").write_text(
        'export async function GET(req){ if (req.headers.get("authorization") !== `Bearer ${process.env.CRON_SECRET}`) return;}' if cron_secret else "export async function GET(){}"
    )
    (repo / "src/app/api/time/route.ts").write_text("export async function GET(){ return Response.json({now: 1}); }")
    return repo


def test_journal_and_guard_ok(tmp_path):
    repo = _fake_repo(tmp_path)
    assert ss.check_journal(repo)[0].startswith("| ✅")
    assert ss.check_build_guard(repo)[0].startswith("| ✅")


def test_journal_reversed_is_red(tmp_path):
    repo = _fake_repo(tmp_path, journal_ok=False)
    out = ss.check_journal(repo)
    assert out[0].startswith("| 🔴")
    assert any("when が戻る" in line for line in out)


def test_build_guard_missing_is_red(tmp_path):
    repo = _fake_repo(tmp_path, guard=False)
    assert ss.check_build_guard(repo)[0].startswith("| 🔴")


def test_cron_without_secret_is_red_and_open_route_is_yellow(tmp_path):
    repo = _fake_repo(tmp_path, cron_secret=False)
    out = ss.check_api_routes(repo)
    assert any(line.startswith("| 🔴") and "cron" in line for line in out)
    assert any(line.startswith("| 🟡") and "api/time" in line for line in out)


def test_secret_pattern_detected(tmp_path):
    repo = _fake_repo(tmp_path)
    (repo / "src/leak.ts").write_text('const u = "postgresql://user:pass@db.example.com/x";')
    out = ss.check_secrets(repo)
    assert out[0].startswith("| 🔴")
    assert any("src/leak.ts:1" in line for line in out)


def _add_guard_tests(repo: Path, *, allowed_entries=0, drop=None):
    (repo / "tests").mkdir(exist_ok=True)
    entries = ",".join('{ file: "a.tsx", name: "x", reason: "r" }' for _ in range(allowed_entries))
    bodies = {
        "tests/no-use-before-declare-in-render.test.ts": f"const ALLOWED: {{ file: string; name: string; reason: string }}[] = [{entries}];\n",
        "tests/create-tenant-button-render.test.ts": "it('renders', () => {});\n",
        "tests/printer-silent-check.test.ts": "it('no Date', () => {});\n",
    }
    for rel, body in bodies.items():
        if rel != drop:
            (repo / rel).write_text(body)


def test_guard_tests_all_present_is_green(tmp_path):
    repo = _fake_repo(tmp_path)
    _add_guard_tests(repo)
    out = ss.check_guard_tests(repo)
    assert all(line.startswith("| ✅") for line in out)
    assert any("ALLOWED): 0 件" in line for line in out)


def test_guard_test_missing_is_red(tmp_path):
    repo = _fake_repo(tmp_path)
    _add_guard_tests(repo, drop="tests/no-use-before-declare-in-render.test.ts")
    out = ss.check_guard_tests(repo)
    assert any(line.startswith("| 🔴") and "no-use-before-declare" in line for line in out)


def test_guard_allowed_entries_are_yellow(tmp_path):
    repo = _fake_repo(tmp_path)
    _add_guard_tests(repo, allowed_entries=2)
    out = ss.check_guard_tests(repo)
    assert any(line.startswith("| 🟡") and "2 件" in line for line in out)
