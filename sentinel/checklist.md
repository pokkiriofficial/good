# 毎日の点検手順(pos-sentinel)

読み取りだけで行う。所要 10〜15 分。順番どおりに進め、結果を `report_template.md` に埋める。
ID は `.claude/agents/pos-sentinel.md` の表。

## 0. 本番作業とぶつからない確認

- `mcp__github__list_pull_requests`(nightwork-pos, open)で開いている PR を数える。点検係は PR にコメントしない
- 🔴 を直す前に、**同じ不具合の PR が無いか先に探す**(`list_pull_requests` の open を題名で見る。2026-10-15 に cron 修正の PR が 2 本並んだ #558・#559)。あれば自分では出さず、報告に「PR #N で対応中」と書く
- nightwork-pos の作業ツリーに変更が無いこと: `git -C /home/user/nightwork-pos status --short` が空。空でなければ点検を止めて報告
- クローンは `git fetch --depth 1 origin main && git checkout -q origin/main` で最新にする(push しない)

## 1. エラー(止まらず動き続けていないか)

| 手順 | 使うもの | 🔴 | 🟡 |
|---|---|---|---|
| 本番の runtime errors を 24h と 7d で取る | `get_runtime_errors`(since 24h / 7d) | 会計・注文・ログイン(`/floor`・`/dashboard`・`/login`・`/api/cloudprnt`・`/api/epson`)で新しいエラー群 | cron・帳票・運営画面の新しいエラー群 |
| エラーの件数をパス別に見る | `get_runtime_logs`(production, level error+fatal, group_by requestPath, since 24h) | 同じパスで 50 件超 | 同じパスで 10 件超 |
| cron 3 本の実行結果 | `get_runtime_logs`(query `[cron/`, since 24h) | 1 本でも 24h 全失敗 | 散発の失敗 |
| 本番デプロイ | `list_deployments`(production, limit 5) | 最新が ERROR / BUILDING のまま 30 分超 | build-guard で止まった(直前の版が動いている) |
| 手で出した本番デプロイ | `list_deployments` で `meta` が空(Git 連携でない)のもの | その版が出ていた時間帯に `/floor` のエラーがある | 1 件でもあれば 🟡。手元の Mac で作った版は印刷の部品(Linux 版)が入らず、フロア画面ごと落ちた(2026-10-24 の事故。約 3 時間)。10/21 の手動 2 回も同じ作り方だった。本番は main のマージで自動で出るので、手で出す理由を聞く |
| CI | `actions_list`(ci.yml, 40 件) | main の push が failure | PR の failure が同日 3 件以上。main の push が cancelled(並行マージで検証されずに本番へ出た) |
| 画面側のエラー | `get_runtime_logs`(query `client`, since 24h) | 同じ画面で 20 件超 | 新しい種類 |
| **描画で落ちるエラー**(`ReferenceError`・`TypeError` が `digest` 付きで、`/floor`・`/dashboard`・`/platform` などの画面のパスに出る) | `get_runtime_errors` のサンプル | **1 回でも 🔴**。開けば必ず落ちる不具合なので、回数は「開いた人の数」でしかない(2026-10-15〜18、運営画面が 4 日開けなかった。`incidents/2026-10-19_…md`) | - |

判定のコツ: 「エラー 0 件」と「誰も使っていない」は区別できない。深夜 0〜5 時(JST)が営業の山なので、
その時間帯の info ログが 0 なら「利用なし」と書く。

昼の点検メール(POS の `noon-check`、12:00 JST)が届いた日は、次を見てから書く。
- メールの回数は「前回のエラーメールを送ってからの回数」(`error_alerts.occurrences`)で、累計ではない。「0 回」は「メールを 1 通送った後、再発なし」の意味
- 各エラーの**最終発生時刻**(`get_runtime_errors` の `last`)と、**最新の本番デプロイの時刻**(`list_deployments`)を見比べる。最終発生がデプロイより前で、デプロイに修正の PR が含まれていれば「修正済み(PR #N、デプロイ時刻)」と書く
- 修正済みでも、**修正後にその画面が開かれた記録**(同じパスの info ログ)が無ければ「解消」にしない(手順 4)

## 2. セキュリティ(外から攻められていないか)

| 手順 | 使うもの | 🔴 | 🟡 |
|---|---|---|---|
| 依存パッケージ | `python3 scripts/sentinel_static.py <clone>`(npm audit) | critical かつ fix あり(特に `next`) | high |
| 鍵・トークンの混入 | 同上(secrets grep、`.env*` の追跡) | 1 件でも | - |
| cron の秘密、認証の無い API | 同上(cron route に `CRON_SECRET`、`partner/login-ids` の有無) | 認証無しの書き込み API | 固定の共有鍵だけの API |
| migration の並び | 同上(`_journal.json` の idx/when が単調増加) | 逆順(本番に永久に当たらない) | - |
| 本番ビルドの番人 | 同上(`package.json` の build に `build-guard`) | 外れている | - |
| 再発防止の番人テスト | 同上(`tests/no-use-before-declare-in-render.test.ts`・`tests/printer-silent-check.test.ts`・`tests/create-tenant-button-render.test.ts` の有無、`ALLOWED` の件数) | 1 本でも無くなっている | `ALLOWED` が前日より増えた(理由を報告に書く) |
| 不審アクセス | `get_runtime_logs`(production, query `401` / `403` / `404`, group_by requestPath, since 24h) | `/api/*` へ同一パスで 100 件超の 401/403 | 50 件超 |
| ログインの失敗 | `get_runtime_logs`(query `login`, level error/warning) | 同一店舗で短時間に多数 | - |
| WAF・攻撃の状況 | `get_firewall_config`(active)・`get_active_attack_status` | 攻撃検知あり | 404(設定なし)は「未設定」と記録 |
| 新しい協力者・ブランチ | `list_commits`(main, 24h)の作者が既知(pokkiri-official / tomoking11423 / nanzetianling-beep / Claude)か | 知らない作者 | - |

Supabase 側(Auth の失敗一覧・RLS)は見られない。報告の「未確認」に毎回書く。

## 3. 操作感(重くないか)

| 手順 | 使うもの | 🔴 | 🟡 |
|---|---|---|---|
| API の応答 | `web_fetch_vercel_url` で `https://nightwork-pos.vercel.app/api/time` を 2 回(1 回目はコールドスタート) | 2 回目が 3 秒超、または 5xx | 2 回目が 1 秒超 |
| ログイン画面 | 同 `/login` | 5xx / 空のページ | 3 秒超 |
| アンケートサイト | 同 `https://pokkiri-night-survey.vercel.app/` | 200 以外 | 3 秒超 |
| 実機の申告 | 前日の引き継ぎ文書・PR 本文に「固まる」「押せない」「崩れる」が無いか(`list_commits` のメッセージ) | - | あれば記録 |

時間は `web_fetch_vercel_url` を呼ぶ前後の時刻差で測る(ツールに所要時間は出ない)。

## 4. 前日との比較

`sentinel/reports/` の前日の報告(無ければ最新)を読み、同じ指摘は「継続(初出 月/日)」、消えた指摘は「解消」と書く。
3 日続けて同じ 🔴 なら、報告の 1 行目に「3 日放置」と書く。
**「再発なし」は、その画面が開かれた記録があって初めて「解消」にする。** 利用の痕跡が無い日の「再発なし」は「未確認(利用なし)」と書く(2026-10-18、運営画面の ReferenceError を 2 日「再発なし」で解消扱いにしたが、誰も開いていなかっただけで、開いた途端に 7 回出た。直したのは #588)。

## 5. 報告を書く・届ける

- `sentinel/reports/YYYY-MM-DD.md` に `report_template.md` の形で書く(日本時間の日付)
- 最後のメッセージの 1 行目を結論(🔴/🟡/🟢 + 一言)にする。通知にはこの 1 行目が載る
- 🔴 があれば「依頼文」を必ず付ける。直す人が迷わない粒度(ファイル:行、直し方、確かめ方)
