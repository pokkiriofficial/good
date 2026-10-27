-- 定期処理の合図(ハートビート)を、Supabase の中で見張る(下書き。migration にする前の案)。
-- 運営側の記録で、テナントのデータではない。書き込みは service role のみ(error_alerts と同じ形)。

CREATE TABLE IF NOT EXISTS cron_heartbeats (
  -- 定期処理の名前(vercel.json の path の最後。例: noon-check)
  name text PRIMARY KEY,
  -- 最後に成功した時刻。アプリが、処理の最後に更新する
  last_ok_at timestamptz NOT NULL DEFAULT now(),
  -- ふだん何分おきに動くか(毎時=60、毎日=1440)
  expected_every_minutes integer NOT NULL CHECK (expected_every_minutes > 0),
  -- 予定を過ぎても、この分数までは遅れとみなさない(Vercel の定期実行の時刻のずれ用)
  grace_minutes integer NOT NULL CHECK (grace_minutes >= 0),
  -- 最後に「止まっている」と知らせた時刻
  last_alert_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);--> statement-breakpoint

ALTER TABLE cron_heartbeats ENABLE ROW LEVEL SECURITY;--> statement-breakpoint

-- 最初の合図の前に誤報を出さないよう、last_ok_at は作成時刻(既定の now())から始める
INSERT INTO cron_heartbeats (name, expected_every_minutes, grace_minutes) VALUES
  ('printer-silent-check', 60, 90),
  ('auto-close-attendance', 60, 90),
  ('daily-health', 1440, 180),
  ('noon-check', 1440, 180)
ON CONFLICT (name) DO NOTHING;--> statement-breakpoint

-- 「止まっている」処理の一覧。判定だけを持つ(メールは送らない)ので、テスト用DB(PGlite)で検査できる。
-- 同じ遅れでは p_realert_hours 時間に1通まで。合図が戻ったあと(last_ok_at が last_alert_at より新しい)に
-- また止まれば、すぐ知らせる。
CREATE OR REPLACE FUNCTION overdue_cron_heartbeats(
  p_now timestamptz DEFAULT now(),
  p_realert_hours integer DEFAULT 6
)
RETURNS TABLE (name text, last_ok_at timestamptz, overdue_minutes integer)
LANGUAGE sql
STABLE
SET search_path = public, pg_temp
AS $$
  SELECT h.name,
         h.last_ok_at,
         floor(extract(epoch FROM (p_now - h.last_ok_at)) / 60)::integer
           - h.expected_every_minutes - h.grace_minutes AS overdue_minutes
    FROM cron_heartbeats h
   WHERE p_now > h.last_ok_at + make_interval(mins => h.expected_every_minutes + h.grace_minutes)
     AND (h.last_alert_at IS NULL
          OR h.last_alert_at < h.last_ok_at
          OR h.last_alert_at < p_now - make_interval(hours => p_realert_hours))
   ORDER BY h.name;
$$;--> statement-breakpoint

-- 画面(API)から呼べないようにする。Supabase は public の関数を API として公開するため、
-- 何もしないと、誰でも呼べてしまう。
REVOKE ALL ON FUNCTION overdue_cron_heartbeats(timestamptz, integer) FROM PUBLIC, anon, authenticated;
