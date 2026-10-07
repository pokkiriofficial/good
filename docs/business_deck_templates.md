# ビジネス資料テンプレート集(スライド作成の標準資産)

資料(スライド・提案書・報告書など)を作るときは、まずこの文書で用途に合うテンプレートを選び、`reference/business_deck_templates/by_industry/標準/` の実物HTMLを土台にする。

- 公開URL: https://business-deck-templates.vercel.app/
- Vercel: チーム `koku`(team_XbYXQzuiEhlmNRnobKYkWMaf)/ プロジェクト `business-deck-templates`(prj_JTzU4NCSO6noVlrcXRlfxrmjugeb)
- 取り込み日: 2026-10-07(最新デプロイ `dpl_DcXs1F1EbCUQZPq5fnzSoKn8t9AH`)
- 取り込み済み: 標準版12本のHTML全文(`reference/business_deck_templates/by_industry/標準/`)。業種版96本は構造が同じなので、必要時に取得する(3章)

## 1. 全体像

| 項目 | 内容 |
|---|---|
| 規模 | 12用途 × (標準版1 + 8業種版) = 108本、各10枚、計1,080枚 |
| 形式 | 16:9・1ファイル自己完結のHTML(CSS/JSをインライン。外部依存はGoogle Fontsのみ) |
| 思想 | 日本のビジネス文化(合意形成・稟議・根回し)に最適化。結論ファースト |
| 図解 | プレースホルダではなく**実データを焼き込んだSVG**。`{{ }}` を差し替えれば提出物になる |
| 既定デザイン | 株式会社KOKU デザインパレット v2.0(Apple的モノクロ + Dior Sauvageの紺) |
| 操作 | `←` `→` `Space` `PageUp/Down` でスライド送り。印刷/PDFは 1280×720px で1枚1ページ |
| 業種 | SaaS・IT / 製造 / 人材 / 医療介護 / 飲食小売 / 不動産建設 / 物流運輸 / 士業コンサル |

ギャラリー(`index.html`)の機能: 用途ごとに「標準版を開く」ボタンと8業種のチップ。上部の業種フィルタ(sticky)で、選んだ業種以外のチップを薄くする。noindex。

## 2. 12用途の一覧と10枚の構成

各デッキは「表紙 → 8枚の本編 → 締め(紺地・CTA)」の10枚。本編の各スライドは `eyebrow(NN / 英語ラベル)` + 主張型の見出し + subhead(2行) + 本文 + 下部の takeaway帯(1行の結論)で作る。

| No | 用途 | 目的 | 本編8枚(英語ラベル → 主な図解) |
|---|---|---|---|
| 01 | 稟議・投資決裁 | 社内の投資決裁を通す | Summary(累計収支の折れ線)/ Issue(空雨傘+工程フロー図)/ Inaction(見送り損失の累積線)/ ROI(投資と効果の内訳)/ Options(松竹梅3案)/ Budget(予算内訳+負荷バー)/ Schedule(タイムライン)/ Risk(リスク表) |
| 02 | B2B営業提案 | 初回提案〜受注 | Market(市場推移の折れ線)/ Issue(工程フロー図)/ Approach(3つの道すじ・主役カード)/ Solution(Before/After)/ Compare(競合比較表)/ Proof(実績ロゴ+声)/ Steps(導入ステップ)/ Pricing(松竹梅) |
| 03 | 課題解決ホワイトペーパー | 見込み客に配るgive型資料 | Overview(目次+統計)/ Data(調査棒グラフ)/ Cause(空雨傘+悪循環図)/ Fact(誤解vs事実)/ Framework(2軸マップ)/ Action(90日4ステップ)/ Checklist(現在地診断)/ Case(手作業時間の推移) |
| 04 | 採用ピッチ | 候補者を誠実に口説く | Mission / Business(主役カード)/ Numbers(聞きにくい数字も開示)/ Career(等級・年収レンジ)/ A Day(1日の流れ)/ Voices / Benefits(利用率つき)/ Process(選考4ステップ) |
| 05 | IR決算説明 | 投資家への決算説明 | Highlights / Trend(4期比較)/ Bridge(利益ブリッジ・ウォーターフォール)/ Segment(構成比)/ Finance(財務表)/ Guidance(通期予想の進捗)/ Returns(配当推移)/ Strategy |
| 06 | 中期経営計画 | 3か年計画で全社の目線を揃える | Review / Vision(数字の大見出し)/ Plan(実績3年+計画3年)/ Strategy(3本柱)/ Roadmap(3か年)/ Investment(投資配分)/ KPI(7指標の表)/ Governance(推進体制図)。表紙が紺地 |
| 07 | スタートアップピッチ | VCへの資金調達 | Problem(工程フロー)/ Solution(Before/After)/ Market(TAM/SAM/SOMの同心円)/ Why Now / Model(ユニットエコノミクスのフロー)/ Moat(2軸ポジショニング)/ Traction(MRR折れ線)/ Team |
| 08 | 業務改善DX提案 | 業務改善・DXの社内提案 | Current(工程別の実測フロー)/ Issue(損失の累積線)/ To-Be(Before/After)/ Impact(人件費換算−ツール費)/ Tools(3案比較表)/ Risk(対策セット)/ Roadmap(8週間)/ Team(RACI表) |
| 09 | セミナー・ウェビナー | 投影資料。学びを型で渡す | Agenda / Speaker / Why Now(空雨傘)/ Framework(3ステップ図)/ Work(15分ワーク)/ Results(受講前後比較)/ Voices / Action(3つだけ) |
| 10 | プロジェクト進捗報告 | 月次報告。意思決定を早める | Summary(結論と論点1つ)/ Schedule(ガント)/ KPI(計画・実績・差異表)/ Scope(バーンダウン)/ Issue(課題管理表)/ Recovery(空雨傘+リリース時期比較)/ Next(来月のマイルストーン)/ Request(依頼3点) |
| 11 | 製品仕様・技術カタログ | 検討中の実務者へ | Performance(応答時間の折れ線)/ Architecture(構成図+責任分界)/ Features(3機能)/ Spec(条件つき実測値)/ Security(認証)/ Ecosystem(連携図)/ Setup(10営業日)/ Pricing(ID単位の料金) |
| 12 | 顧客成功事例 | 1社の導入ストーリー | Profile(空雨傘)/ Challenge(工程フロー)/ Decision(3案比較)/ Journey(7週間)/ Results(処理時間の推移)/ ROI(回収月数)/ Voice / Analysis(成功要因3つ) |

締めスライド(10枚目)の見出し例: 稟議「ご承認いただきたい事項は、3点です。」/ 営業「まずは、2週間の無料トライアルから。」/ 採用「志望動機は、まだなくていい。」/ IR「対話を、企業価値へ。」/ 進捗「本日のご承認で、リリース {{08/28}} は守れます。」。**締めは必ず「次に取ってほしい行動」を1つに絞る**(CTAボタン or QR)。

## 3. 業種版の扱い

- ファイル名: `decks/NN_用途名_{業種}.html`。業種キーは `SaaS` `製造` `人材` `医療介護` `飲食小売` `不動産建設` `物流運輸` `士業コンサル`。標準版は接尾辞なし
- **CSSと構造は標準版と同一**(確認済み: 01製造・12医療介護で `<style>` が完全一致)
- 変わるもの: title(「…（製造業）」)、本文の言い回し(「現場」→「検査員」「施設」など)、数値(14ヶ月→15ヶ月、960万→1,200万)、図中のラベル(工程名: 受注入力→受入検査 など)、SVGの寸法・合計・割合
- 作り方の基本: **標準版を土台に、上記を業種に合わせて書き換える**。数値を変えたらバーの長さ・合計・割合・aria-labelも必ず同時に直す
- 業種版が必要な場面で既存の版に近いものがあれば、取得して読む(取得方法は4章)

## 4. 取得方法(重要)

このセッション環境では `curl` と `WebFetch` は egress 制限で `business-deck-templates.vercel.app` に届かない。**`mcp__Vercel__web_fetch_vercel_url` を使う**。

- 大きいHTMLは結果がファイルに保存される。中身はJSONで、本文は `.text` フィールド。`python3 -I` で `json.load` して書き出す
- デプロイのファイル一覧: `mcp__Vercel__list_deployment_files`(引数 `id`・`teamId`)
- 個別ファイルの中身: `mcp__Vercel__get_deployment_file_contents`(`id`・`fileId`=一覧のuid・`teamId`)。ただしbase64で長いと途中で切れるため、HTMLは上のURL取得の方が確実
- 共通アセット(ギャラリー用): `/assets/theme.css` `/assets/deck.css` `/assets/deck.js`、部品見本 `/components.html`
- 元のビルド(`_src/NN_*.html` と `_fw/build.mjs` `_fw/gallery.mjs`)はデプロイに含まれない。**HTMLを直接編集して使う**

## 5. デザインルール(新規資料でも守る)

### 配色(`:root` トークン)

| 役割 | トークン | 値 |
|---|---|---|
| アクセント(強調・CTA・表紙地) | `--navy` | `#17233E` |
| 暗地でのアクセント | `--steel` | `#4E6A9E`(hover `#24365B`) |
| 本文 | `--ink` / `--graphite` | `#1D1D1F` / `#424245` |
| キャプション | `--gray` | `#86868B`(大字・太字のみ) |
| 罫線 | `--silver` / `--line` | `#D2D2D7` / `#E3E7EE` |
| 面 | `--mist` / `--cloud` / `--white` | `#E8E8ED` / `#F5F5F7` / `#FFFFFF` |
| 良好 | `--ok`(tint `#EBF4EF`) | `#2E7D5B` |
| 損失・遅延・警告 | `--warn`(tint `#FBEEEC`) | `#C0392B` |

- 比率は **純白70 : ink 25 : アクセント5**。面は塗りでなく罫線で分け、アクセントは1画面1か所
- 機能色(良好/損失/要確認)は、ステータスと損失の可視化だけに使う。装飾には使わない
- **他社案件への横展開は `:root` の色トークンを差し替えるだけ**(全体が一括で変わる)

### タイポ

- 見出し・英字ラベル: Jost / 本文: システム日本語ゴシック(游ゴシック・Hiragino・Noto Sans JP)/ 数字: JetBrains Mono(等幅・右揃えで桁を揃える)
- サイズは `min(○vh, ○vw)` 指定で、16:9の枠(`width:100vw; height:56.25vw; max-width:177.78vh`)に合わせて拡縮する。固定pxを使わない
- 見出し(`.h2`)は **20字以内の主張型**、subhead は2行・90字以内、強調は1か所

### 構成の型

- 結論ファースト。各スライドは「見出し=主張 → subhead → 図解 → takeaway帯(`<b>`で数字を強調)」
- 空・雨・傘(`.srk`): 空=事実(中立の灰)/ 雨=解釈(`--warn`の左罫線)/ 傘=打ち手(紺ベタで強調)。1枚で完結させる
- 損失回避: 「見送るコスト」を損失色の累積線で見せる(稟議・DX)
- 価格は松竹梅(`.plans`)。中央を本命にして紺ベタ反転・一段大きく、`おすすめ` バッジ
- 比較表は自社/推奨列だけ `.col-hi`(steelの見出し+cloud地)。弱みも正直に載せる
- 1系列だけ強調(自社・最新をアクセント、他はグレー)。ステップの連結は控えめなグレーの線/三角(派手な矢印は使わない)
- 誠実さを出す: 良くない数字(残業・定着率・遅延・弱み)も先に開示する。測定条件・出所・n数を併記する

## 6. 部品(クラス)の早見表

実デッキに入っているインラインFWの部品(新規作成時はこの名前で書く)。

| 区分 | クラス | 用途 |
|---|---|---|
| 枠 | `.slide` `.slide.dark` `.slide.cover` | 16:9の1枚。`dark cover` は締め用の紺地 |
| ヘッダ | `.s-head` `.eyebrow` `.h2`(`.u`で強調語) `.subhead` `.tag`(`01 / SUMMARY`) | 左上に主張を置く(Z/F型) |
| 本文枠 | `.s-body` `.fillcenter` `.split`(1.02:1の2カラム) `.grid .g2/.g3/.g4` | 配置 |
| 下部 | `.takeaway`(`.tk`+`<b>`) `.s-foot`(`.pageno` `.brandline`) | 結論1行/ページ番号と社名 |
| カード | `.card`(`.ico` `.idx` `h3` `p` `.foot .n`) `.card.hero` | `.hero` は紺ベタで1画面1枚だけ |
| 数値 | `.kpi`(`.xl` `.sm` `.unit`) `.kpi-l` `.count[data-to][data-dec]` `.stat` | `.count` はスクロール登場でカウントアップ |
| グラフ | `.chartcard` `.dghead(.t .n)` `.csvg`(`.draw` `.area` `.dot(.key)` `.axis-t` `.val-t` `.ann-bg/.ann-t` `.lead-l`) | 折れ線・エリア。pathに `pathLength="1"` |
| 図解 | `.fsvg`(`.nd(.hot)` `.nd-t` `.ar` `.bar(.hot)` `.mn` `.an` `.tag-bg/.tag-t`) | 工程フロー・棒・同心円・2軸マップなど。`.hot` が損失の1点 |
| 論理 | `.srk`(`.band .sora/.ame/.kasa` `.k` `.v`) `.ba`(`.row` `.row.after` `.mid .badge`) | 空雨傘/Before-After |
| 流れ | `.timeline`(`.step` `.dot` `.cn` `.k` `h4` `p`) `.stepcard` `.load`(`.lr` `.ln` `.track` `.lv`) | ステップ/作業負荷バー |
| 表 | `table` `th/td.num` `.col-hi` | 紺の見出し行。数値は右揃え等幅 |
| 料金 | `.plans` `.plan(.reco)` `.badge` `.price(.u)` `.meta` | 松竹梅 |
| 証拠 | `.logos .lg` `.quote`(`cite`) `.checks`(`.ck`) `.frame`(写真枠) | 実績・声・チェックリスト・画像スロット |
| 行動 | `.btn` `.qr` | 締めの1アクション |
| 表紙 | `.cover` `.grid-bg` `.wm`(巨大な英語透かし)`.kick` `h1 .ln>span`(行ごとにせり上がる) `.sub` `.rule` | 表紙・締め共通 |
| 動き | `.reveal`(`--i`で遅延) `.in`(IntersectionObserverが付与) | フェード+ライズ+ブラー解除。登場のみ |

- 登場アニメの発火: スライドが25〜30%見えたら `.in` を付ける(デッキ内のインラインJS)。進捗バー `#progress`・カウンタ `#cur` / 総数 `10` を持つ
- `prefers-reduced-motion` ではアニメ全停止、`@media print` で 1280×720 に固定して1枚1ページ
- ギャラリーの `components.html` / `assets/deck.css` は別系統の部品見本(`.eyebrow→.headline→.rule→.lead`、`.slot.image/.chart/.logo/.qr` の点線プレースホルダ、`.ring`、`.bars`、`.lossarea`、`.pill.good/.warn/.loss`、`.cta`、`.dotnav`)。**実デッキの土台は上表のインラインFW**。見本にある `.ring`(達成率の円)・`.pill`(進捗ステータス)・`.slot`(画像/グラフ配置枠)は、必要なときだけ追加で使う

## 7. 資料作成の手順(今後の標準フロー)

1. 用途を決める(12用途から選ぶ。該当なしなら近い用途を土台にして構成だけ変える)
2. 業種を決める(8業種。なければ標準版)。必要なら4章の方法で業種版を取得する
3. `reference/business_deck_templates/by_industry/標準/` の該当HTMLを `cp` して土台にする(元ファイルは直さない)
4. `{{ }}` を実データに置換する。数値を変えたら、バーの寸法・合計・割合・`aria-label`・takeaway・「P.○」の参照・`data-to` を**全部**そろえる
5. 見出しを主張型(20字以内)に直し、締めのCTAを1つに絞る
6. 他社ブランドにするなら `:root` の色トークンのみ差し替える。アクセントは1画面1か所を守る
7. ブラウザで全10枚を確認(`←→`)。印刷は1280×720。Playwright(Chromium導入済み)でスクリーンショットを撮って崩れを確認する
8. 提出前チェック: `{{` が残っていないか(`grep -c '{{'`)、出所・時点・n数の記載、個人情報や機密の混入がないか

## 8. 差し替え項目(`{{ }}`)の傾向

- 共通: `{{社名}}` `{{自社名}}` `{{氏名}}` `{{メール}}` `{{電話}}` `{{リンク}}` `{{YYYY.MM.DD}}` `{{出所}}`
- 稟議: `{{案件名}}` `{{起案部門}}` `{{No.}}` `{{システム名}}`(11項目)
- 営業: `{{見込み顧客名}}` `{{提案サービス名}}` `{{競合A/B}}` `{{導入企業名}}`(26項目)
- スタートアップピッチ: `{{製品名}}` `{{ターゲット}}` `{{中核課題}}` `{{ラウンド}}` 他(42項目と最多)
- IR: `{{企業名}}` `{{2026年3月期}}` `{{IRサイトURL}}`(9項目)
- 進捗: `{{プロジェクト名}}`(8項目と最少)
- **サンプルの数値(例: 14ヶ月・960万円・68%・n=516)は実データではない**。必ず自社の実測値に置き換えるか、根拠のない数値は削除する

## 9. ファイル配置

```
docs/business_deck_templates.md                      ← この文書
reference/business_deck_templates/by_industry/{標準,業種}/NN_用途.html  ← 業種別フォルダ
reference/business_deck_templates/README.md           ← 取り込みの概要
```

ポッキリ.Night の初期設定キット(アンケート・LINEテキスト・Excel・スライド)は `spec/items.yaml` が唯一の正であり、本文書のテンプレートとは別系統。両者を混ぜないこと。キットの「③ スライド」(`templates/slides/lecture.yaml`)を作り直す依頼が来た場合に限り、本文書の配色・構成の型を参考にする。
