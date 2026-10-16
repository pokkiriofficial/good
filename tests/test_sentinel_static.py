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
