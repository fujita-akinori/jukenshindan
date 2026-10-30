---
name: kiji
description: 音声入力などの原稿から受験診断ドットコムの記事（articles/）を作り、ビルドしてpushまで行う
argument-hint: [原稿ファイルのパス または 原稿本文]
disable-model-invocation: true
---

次の原稿から記事を1本作って公開する。

$ARGUMENTS

上の内容がファイルのパスならそのファイルを読む。本文が直接貼られていればそれを原稿として使う。原稿が空なら原稿を求めて止まる。

CLAUDE.md の「記事を追加するとき」「記事の書き方」と author.md に従う。以下はその手順を最後まで通すための段取り。

## 1. 原稿を読んで骨組みを決める

- 原稿の主張・章立て・紹介している参考書を洗い出す
- 題名：検索されやすい語を前に置き「｜」のあとに中身の具体性を足す既存記事の形にそろえる（例：「共通テスト後の過ごし方｜自己採点から二次試験までの1か月で計画を立て直す方法を京大生が解説」）。原稿に題名があっても SEO 的によりよい形にしてよい
- tag（参考書比較・勉強法・受験戦略・予備校）と subject を決める
- slug は内容を表すローマ字（既存の命名にそろえる。例 `kyoutsuu-go-sugoshikata.html`）。既存ファイルと重複しないか確かめる
- description は120字前後で記事の中身が具体的に分かる文にする

## 2. 本文を書く

- 原稿の主張と運営者の経験はそのまま生かし、話し言葉の崩れや重複だけ整える。原稿にない経験談や数字は足さない（足せるのは author.md にある事実だけ）
- 固有名詞は `articles/` を grep して既存記事の表記にそろえる。参考書の正式名・版は出版社サイトなどで確かめる
- 構成は既存記事と同じ：導入の段落→ `h2` の章→必要なら比較表（`table-scroll` と `compare-table`）→まとめ
- 紹介した参考書・商品は記事末尾の `aff-box` に並べる。Amazon リンクは `https://www.amazon.co.jp/dp/<ASIN>?tag=jukenshindan-22`（ASIN が分からなければ既存記事と同じ検索URL `https://www.amazon.co.jp/s?k=<書名>&tag=jukenshindan-22`）
- `aff-box` がある記事は `article-header` に `pr-note` を入れる
- 「あわせて読みたい」には内容が近い既存記事を3本選ぶ
- `diag-cta` は記事の科目に対応する診断ページへ誘導する（該当がなければ診断一覧）
- 日本語は CLAUDE.md の文体ルールどおり（読点を多用しない）

## 3. 登録する

- `articles/articles-data.js` の先頭に1件追加する。date は今日、order は同じ日付の既存記事より大きい数
- `data/highlights.json` に各章の大事な1文を登録する（本文と一字一句同じ文）
- 共通テストの記事なら `kyoutsuu-countdown.html` の「共通テスト対策の記事」の一覧にも追加する

## 4. ビルドして確かめる

```
python3 scripts/build_site.py
```

- エラーや「強調する文が見つからない」が出たら直して再実行する
- `git status` と `git diff --stat` で変更が今回の記事に関係するファイルだけか確かめる。無関係なファイルが変わっていたら push せず報告して止まる
- 記事の HTML を開き、表紙が本文と `aff-box` に入っているか・リンク切れがないかを確かめる

## 5. コミットして push する

```
git add -A
git commit -m "記事: <題名の「｜」より前>を公開"
git pull --rebase origin main
git push origin main
```

push が失敗したら原因を報告して止まる（force push はしない）。

## 6. 報告する

最後に次だけを短く報告する。

- 公開URL（`https://jukenshindan.com/articles/<slug>`。反映まで数分かかる）
- 題名を原稿から変えた場合は元の題名と新しい題名
- 原稿から直した固有名詞・正式名
- カウントダウンページに追加したかどうか
- 原稿だけでは判断できず仮で決めたこと（あれば）
