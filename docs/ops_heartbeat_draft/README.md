# 定期処理の合図を Supabase で見張る — 沢田さん向けの依頼と下書き(2026-10-27)

目的: POS の定期処理(昼の点検・容量の見回り・プリンター点検・勤怠の自動締め)が止まったとき、Gmail に知らせる。背景と決定の経緯は `docs/ops_monitoring_notes.md` の 7章。

決定済み: 見張りは Supabase の中(`pg_cron`)。メールは `pg_net` から Resend を直接呼ぶ(方式 A)。宛先は `MAIL_ALERT_TO` と同じ。

## 沢田さんにお願いしたいこと(migration と本番への適用)
AGENTS.md のルールで、migration の作成と本番DBへの適用は、沢田さんだけが行う。このフォルダの SQL は、**下書き**。番号の振り直しと、`meta/_journal.json` への登録は、沢田さんに任せる。

| ファイル | 中身 | migration にするか |
|---|---|---|
| `01_migration_draft.sql` | 表 `cron_heartbeats`(RLS 有効・ポリシー無し)、最初の4行、判定の関数 `overdue_cron_heartbeats()`、API から呼べないようにする `REVOKE` | する(migration にできる形) |
| `02_notify_prod_only.sql` | メールを送る関数 `notify_overdue_cron_heartbeats()`。`pg_net` と Vault が要る。末尾に、15分おきの `cron.schedule`(コメントアウト) | しない。テスト用DB(PGlite)に `pg_net`・Vault が無いため。拡張の導入と Vault の登録のあと、承認を得て、本番で1回だけ実行する |

## 確認済み(2026-10-27、PGlite で下書きを実行)
- `01` を適用でき、4行が入る。RLS は有効。`anon` に関数の実行権が無い。
- 判定の関数: 毎時は150分(周期60+猶予90)ちょうどでは出ず、151分で出る。毎日は1620分(1440+180)。知らせ済みは、6時間は出さない。合図が戻ったあとの再停止は、すぐ出る。
- **未確認**: `02` は、本番でしか動かない。構文も、実際のテストは、まだ。

## 本番に入れる順番(「先にDB → あとからコード」)
1. 運営が、Supabase の管理画面で、拡張 `pg_cron` と `pg_net` を有効にする(承認を得てから)。
2. 運営が、Vault に3つ登録する(値は、チャットやリポジトリに書かない): `resend_api_key`(Vercel の `RESEND_API_KEY` と同じ)、`alert_mail_from`(`MAIL_FROM` と同じ)、`alert_mail_to`(`MAIL_ALERT_TO` と同じ)。
3. 沢田さんが `01` を migration にして、本番へ適用する。`npm run db:check` の ✅ を確認する。
4. 沢田さんが `02` の関数を、本番に入れる。
5. POS 側のコード(下の「アプリ側」)をマージする。
6. `cron.schedule` を、本番で1回だけ実行する。
7. 「止めて試す」: `cron_heartbeats` の1行の `last_ok_at` を一時的に古くし、15分以内に Gmail へメールが届くことを確かめる。届いたら、`last_ok_at` と `last_alert_at` を戻す。**`net._http_response` の状態コード(200番台か)も見る。** Resend が断った場合、送った扱いになったまま、メールが届かない恐れがある。

## アプリ側(POS のコード。表ができたあとに書く。私が担当)
- `src/db/schema/platform.ts` に `cronHeartbeats` を足す。
- 4つの定期処理が、**最後まで成功したあと**に、`last_ok_at = now()` で更新する(`pingHeartbeat` と同じ位置・同じ作法。失敗しても処理を落とさない、例外を投げない)。書き込みは `src/db/service-role/` の中だけ。
- `sql` に `Date` を入れない(AGENTS.md 18)。時刻は `now()` で書く。
- 既存の `HEARTBEAT_URL_*`(外部サービス向け)は、使わないので、残すか外すかを、沢田さんと決める。
- 新しい定期処理を足したときは、`cron_heartbeats` に行を足す(足し忘れの検査テストを書く)。

## 注意
- 関数は、すべて `REVOKE ... FROM PUBLIC, anon, authenticated` する。Supabase は `public` の関数を API として公開するため、しないと、誰でもメール送信を起こせる。
- Vault が足りないと、`02` の関数は例外になり、`pg_cron` の実行記録(`cron.job_run_details`)にだけ残る。気づきにくいので、「止めて試す」で必ず確かめる。
- Supabase 自体が止まると、見張りも止まる(外部サービスなら拾える)。
