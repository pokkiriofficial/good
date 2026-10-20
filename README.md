# ポッキリ.Night 初期設定キット

導入時に店舗情報を集める3つの成果物を、1つの項目定義 `spec/items.yaml` から生成します。
要件は [docs/requirements.md](docs/requirements.md) を参照してください。
お酒の銘柄の一覧は `spec/drinks.yaml` が正で、`scripts/build_catalog.py` で生成します。

| 成果物 | 生成物 |
|---|---|
| ① 導入アンケート | `form/preview/index.html`(Googleフォームの見た目のプレビュー) |
| ② 記入テンプレート | `templates/line/*.txt`・`templates/excel/初期設定_記入シート.xlsx`・`templates/preview/index.html` |
| ③ 対面レクチャー資料 | `slides/lecture.md`(Marp)・`slides/checklist.md` |
| 商品カタログ(お酒の銘柄) | `menu/drinks.json`(POS に渡す一覧)・`menu/preview/index.html`(検索して追加する画面の試作)・`menu/preview/reorder.html`(長押しで並び順を変える画面の試作) |

```sh
pip install -r requirements.txt
make all && python3 -m pytest -q
```

使わない機能は、`python3 scripts/build_templates.py --skip-theme 6` や
`python3 scripts/build_slides.py --exclude 9` で外せます。
