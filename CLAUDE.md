# ポッキリ.Night 初期設定キット

POS「ポッキリ.Night」の導入時に店舗情報を集めるキット。要件は `docs/requirements.md`、既存見本は `reference/survey_sample.html`。

## ルール

- `spec/items.yaml` が唯一の正。成果物のファイルを手で直さず、YAMLかテンプレートを直して再生成する
- 個人情報・給与・ログイン情報の項目は、どの成果物にも作らない(要件定義書 6章)
- 文章は要件定義書 6章のルールに従う(1行20〜35文字、読点は1文に1〜2個、用語は「キャスト」「スタッフ」「卓」「伝票」「バック」)
- 変更後は `make all && pytest` を実行して結果を報告する

## 資料作成(スライド・提案書・報告書)

- 資料を作るときは、先に `docs/business_deck_templates.md` を読み、12用途から選んで `reference/business_deck_templates/decks/` の標準版を土台にする(原本は直さずコピーして使う)
- 配色・部品・構成の型・作成手順は同文書に従う。業種版の取得方法も同文書の4章
- 上の「ルール」(`spec/items.yaml` が唯一の正、文章ルール)は初期設定キットの成果物用。ビジネス資料テンプレートとは別系統

## 構成

- `spec/items.yaml` / `spec/items.schema.json` … 項目定義とスキーマ
- `scripts/sample_sections.py` … 既存見本の SECTIONS から質問を抽出
- `scripts/validate_items.py` … items.yaml の検証と route 別件数の報告
- `scripts/build_form.py` … ① アンケートのHTMLプレビュー(`templates/form/preview.html` → `form/preview/index.html`)
  - `--site form/site` で店舗に配る公開用ページも書き出す。Vercel(チーム koku・プロジェクト pokkiri-night-survey、rootDirectory `form/site`)で https://pokkiri-night-survey.vercel.app に公開している。変更後は push してから再デプロイする
- `scripts/build_templates.py` … ② LINEテキスト・Excel・確認ページ(`templates/line/`・`templates/excel/`・`templates/preview/`)
- `scripts/build_slides.py` … ③ スライド(`templates/slides/lecture.yaml` → `slides/lecture.md`・`slides/checklist.md`)。`--exclude 9` で章を除外
- `tests/` … pytest

## POS への反映

- 回答は、店舗が「文章をコピー」して LINE で送り、運営コンソールで貼り付けて取り込む。外部からの送信経路は作らない
- POS 本体は `pokkiriofficial/nightwork-pos`。POS 側でやること・回答の書式・質問の一覧は `docs/pos_handoff.md`
