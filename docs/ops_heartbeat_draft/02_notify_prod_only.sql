-- ★本番でしか動かない部分(pg_net・Vault が要る。テスト用DBには無い)。拡張の導入と Vault の登録のあとに入れる。
-- Vault に、運営が次の3つを登録しておく(値はチャットやリポジトリに書かない):
--   resend_api_key / alert_mail_from(Vercel の MAIL_FROM と同じ) / alert_mail_to(Vercel の MAIL_ALERT_TO と同じ)
CREATE OR REPLACE FUNCTION notify_overdue_cron_heartbeats()
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_key text;
  v_from text;
  v_to text;
  v_lines text;
  v_count integer;
BEGIN
  SELECT string_agg('・' || o.name || '(最後の成功 ' || to_char(o.last_ok_at AT TIME ZONE 'Asia/Tokyo', 'MM/DD HH24:MI')
                    || '、予定より約' || o.overdue_minutes || '分の遅れ)', E'\n'),
         count(*)
    INTO v_lines, v_count
    FROM overdue_cron_heartbeats() o;
  IF v_count = 0 THEN RETURN 0; END IF;

  SELECT decrypted_secret INTO v_key  FROM vault.decrypted_secrets WHERE name = 'resend_api_key';
  SELECT decrypted_secret INTO v_from FROM vault.decrypted_secrets WHERE name = 'alert_mail_from';
  SELECT decrypted_secret INTO v_to   FROM vault.decrypted_secrets WHERE name = 'alert_mail_to';
  IF v_key IS NULL OR v_from IS NULL OR v_to IS NULL THEN
    RAISE EXCEPTION 'cron heartbeat: Vault の設定が足りません';
  END IF;

  PERFORM net.http_post(
    url := 'https://api.resend.com/emails',
    headers := jsonb_build_object('Authorization', 'Bearer ' || v_key, 'Content-Type', 'application/json'),
    body := jsonb_build_object(
      'from', v_from,
      'to', jsonb_build_array(v_to),
      'subject', '【ポッキリ.Night】定期処理が止まっている疑いがあります',
      'text', E'次の定期処理で、予定の時刻を過ぎても、成功の記録がありません。\n\n' || v_lines
              || E'\n\nVercel の本番ログ(/api/cron/…)で、動いているかを確かめてください。'
    )
  );

  UPDATE cron_heartbeats SET last_alert_at = now()
   WHERE name IN (SELECT name FROM overdue_cron_heartbeats());
  RETURN v_count;
END;
$$;

REVOKE ALL ON FUNCTION notify_overdue_cron_heartbeats() FROM PUBLIC, anon, authenticated;

-- 15分おきに見張る(拡張 pg_cron の導入後。migration ではなく、承認のあとに本番で1回だけ実行する)
-- SELECT cron.schedule('cron-heartbeat-check', '*/15 * * * *', 'SELECT public.notify_overdue_cron_heartbeats()');
