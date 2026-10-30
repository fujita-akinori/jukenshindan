# 受験診断ドットコム（jukenshindan.com）

現役京大生が一人で運営する参考書診断・受験情報サイト。GitHub Pagesの静的サイトで `main` へのpushがそのまま本番に反映される。当面の目標はAdSense承認（2026年10月に「有用性の低いコンテンツ」で不承認→改善して再申請予定）と、Amazon・楽天・A8.netのアフィリエイト収益化。

運営者は匿名で「受験診断ドットコム運営者（現役京大生）」として執筆している。本名・寮・個人を特定できる情報はサイトにもこのリポジトリにも書かない。

記事の根拠に使う運営者の受験実績は @author.md にまとめてある。

## ファイル構成

- `index.html` ホーム（診断一覧→記事→ツール→備忘録 の順に並べる）
- `*-shindan.html` 参考書診断（数学・化学・生物・英単語帳・英文解釈）。本のデータは各HTML内のJS配列にある
- `shindan-ichiran.html` 診断一覧 / `norma-keisan.html` 1日ノルマ計算機 / `kyoutsuu-countdown.html` 共通テストカウントダウン
- `articles/` 記事。メタデータは `articles/articles-data.js`、タグ別一覧は `articles/tag-*.html`
- `biboroku/` 京大生の備忘録（解説コーナー）。メタデータと再生リストは `biboroku/biboroku-data.js`
- `data/highlights.json` 記事ごとに太字マーカーにする1文 / `data/rakuten-cache.json` 楽天の表紙・リンクのキャッシュ
- `scripts/build_site.py` サイト生成（下記）。`affbox.py` 表紙とアフィリエイト枠 / `highlight.py` マーカー / `rakuten.py` 楽天API
- `style.css` 全ページ共通のCSS / `nav.js` ナビ / `sitemap.xml` は自動生成

## ビルド

記事・備忘録・診断を追加または修正したら必ずリポジトリのルートで実行してからコミットする。

```
python3 scripts/build_site.py
```

`<!-- 名前:BEGIN -->`〜`<!-- 名前:END -->` の内側（GA4・SEO・CRUMBS・BYLINE・NAVBIBO・NAVSEARCH など）はスクリプトが書き換える。手で編集しない。GA4タグ・canonical・OGP・構造化データ・パンくず・記事一覧・ホームの新着・検索インデックス・sitemap はすべてここで付くので新規ページで手書きしなくてよい。

実行後は「強調する文が見つからない」の警告が出ていないか確認する。楽天APIキーは `~/.rakuten.env` にありリポジトリには置かない（キーがなくてもキャッシュ済みの本だけでビルドは通る）。

新しい固定ページ（診断・ツール）を作ったら `scripts/build_site.py` の `STATIC_PAGES` にも追加する。

## 記事を追加するとき

1. 既存記事（例 `articles/kyoutsuu-mochimono.html`）をひな形にして `articles/<ローマ字のslug>.html` を作る。head・ヘッダー・フッター・`diag-cta`・`related` の構成はそろえる
2. `articles/articles-data.js` に1件追加する（slug・title・description・tag・date・order・subject）。tag は「参考書比較・勉強法・受験戦略・予備校」のどれか。subject は数学・英語・国語・化学・生物・物理・社会・情報のどれか（科目に関係なければ省略）
3. 「あわせて読みたい」（`related`）には関連記事を3本手で選んで入れる
4. 各章の大事な1文を `data/highlights.json` に登録する（本文と一字一句同じ文にする）
5. 共通テストに関する記事なら言われなくても `kyoutsuu-countdown.html` の「共通テスト対策の記事」の一覧にも追加する
6. ビルドしてからコミット

### 記事の書き方

- 題名はSEO的に最も好ましい形に許可なく変えてよい。変えたら必ず元の題名と新しい題名を報告する
- 原稿は音声入力のことが多い。言い回しの崩れや運営者独自の呼び方（例：セミナー生物の「A問題・B問題」）は確認せず正式名に直して書く
- 固有名詞（参考書名・著者名・YouTubeチャンネル名など）は既存の記事に書いたものと表記をそろえる。迷ったら `articles/` を grep する
- 参考書の正式名は出版社サイトなどの一次情報で確かめる。「標準問題精講特別編」と言ったら池田洋介『方程式・図形・関数からとらえる数学の基礎（分野別標準問題精講）』を指す
- 本文中に参考書が出てきたらなるべく表紙を載せる。記事末尾の `aff-box` に本を並べておけばビルド時に楽天の表紙が本文の見出し直後と枠内に自動で入る。Amazonリンクは必ず `tag=jukenshindan-22` を付ける
- アフィリエイトリンクを含む記事には `pr-note`（PR表記）と `aff-disclosure` を入れる（既存記事と同じ形）
- AdSense再審査を意識し、運営者自身の経験・得点・具体的な手順など他サイトにない一次情報を厚くする。一般論の水増しはしない

## 京大生の備忘録（biboroku/）

- 1テーマ1ページで「結論→なぜそうなるか→例題→よくある間違い→参考書」の形
- YouTubeの再生リストのように投稿順とシリーズ別の両方で見せる。`biboroku/biboroku-data.js` の PLAYLISTS と POSTS に追加する（カテゴリは 受験数学・受験化学・受験生物・参考書の使い方・京大のリアル）
- 参考書は `<div class="book-link" data-book="書名" data-amz="AmazonのURL">` で入れるとビルド時に表紙が付く

## デザイン

- 新しいページやセクションは既存のデザイン・配色にそろえる。目立たせるための別配色（方眼ノート風の紙色など）は使わない
- CSSは `style.css` に追記し、ページごとのインラインスタイルは最小限にする

## 外部サービス

- GA4：G-2WNQN0ZF8D（ビルドで全ページに入る）
- AdSense：ca-pub-6837829466798350
- Amazonアソシエイト：トラッキングID `jukenshindan-22`
- 楽天アフィリエイト：`scripts/rakuten.py` 経由
- A8.net：東進（ナガセ）とリクルートの広告が提携済み
