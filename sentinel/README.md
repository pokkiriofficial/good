# ポッキリ.Night 毎日点検係(pos-sentinel)

本番の POS(`pokkiriofficial/nightwork-pos`)と導入アンケートサイト(このリポジトリ)を、
毎日 1 回、読み取りだけで点検して報告する係。2026-10-15 に新設。

## 何を見るか(3 つの問い)

| 問い | 見るもの |
|---|---|
| 外から攻められていないか | ログインまわりの失敗の山、API への不審なアクセス、依存パッケージの既知の穴、鍵の混入、認証の無い入口 |
| エラーが起きたまま動き続けていないか | Vercel の本番エラー(24h/7d)、cron の失敗、デプロイの失敗、CI の失敗・取り消し、本番ビルドの番人の停止 |
| 操作の重さは大丈夫か | 本番の応答時間(ログイン画面・API)、コールドスタート、アンケートサイトの応答 |

詳しい手順と判定の基準は `checklist.md`。報告の形は `report_template.md`。
過去の報告は `reports/YYYY-MM-DD.md`。

## 本番作業とぶつけないための決めごと

- 点検係は **nightwork-pos に一切書き込まない**(commit・push・PR・Issue・ブランチを作らない)
- 直すべき点は「依頼文」として報告に書く。実際に直す人(沢田さん・山中さん・本番作業中のセッション)が判断する
- Vercel の設定・デプロイ・本番 DB に触らない。再デプロイもしない
- 点検係のファイルは、すべてこのリポジトリ(`good`)の `sentinel/`・`scripts/sentinel_static.py`・`.claude/agents/pos-sentinel.md` に置く。POS 本体のファイルは変えない
- 本番作業が落ち着いたら、`.claude/agents/pos-sentinel.md` と `checklist.md` を nightwork-pos 側へ移してもよい(その時はこの README を直す)

## 動かし方

1. **自動(毎日)**: Claude の「スケジュールされたタスク」(名前「ポッキリ.Night 毎日点検」)が毎朝 08:46(日本時間)に、
   点検係を作ったセッションを起こして `checklist.md` を実行する。報告は `reports/YYYY-MM-DD.md` に書いて
   このリポジトリのブランチ `claude/eloquent-dirac-26mc74` に push し、結論の 1 行を push 通知で知らせる。
   止めるときは Claude の画面の「スケジュールされたタスク」から無効にする(削除してもコードは消えない)。
   新しいセッションで動かす形(メール通知つき)にするには、Vercel と GitHub の連携を付けたタスクを
   claude.ai の画面から作り直す(この組織では API から連携を付けられない)
2. **手で**: Claude Code のセッションで「今日の点検をして」と言うと `pos-sentinel` エージェントが動く
3. **静的な点検だけ**: `python3 scripts/sentinel_static.py /path/to/nightwork-pos`

## 点検係が見られないもの(人に頼む)

- Supabase の管理画面(Auth のログイン失敗の一覧、DB の容量、RLS の実態)。接続情報が無い
- Vercel の WAF(ファイアウォール)の画面。API では「設定なし(404)」としか分からない
- 実機 iPad の操作感(固まる・押せない)。店舗からの申告を待つしかない
- 運営宛てのエラーメール(pokkiri_official@pokkiri.jp)が実際に届いているか
