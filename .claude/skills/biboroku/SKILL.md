---
name: biboroku
description: 原稿から「京大生の備忘録」（biboroku/）の解説ページを作り、再生リストに登録してビルドしpushまで行う
argument-hint: [原稿ファイルのパス または 原稿本文]
disable-model-invocation: true
---

次の原稿から京大生の備忘録のページを1本作って公開する。

$ARGUMENTS

上の内容がファイルのパスならそのファイルを読む。本文が直接貼られていればそれを原稿として使う。原稿が空なら原稿を求めて止まる。

CLAUDE.md の「京大生の備忘録」と文体ルール、author.md に従う。

## 1. 骨組みを決める

- どの再生リストの何回目かを決める。`biboroku/biboroku-data.js` の PLAYLISTS を見て、既存シリーズの続きならその `id` と次の `ep`。原稿が新シリーズの第1回なら PLAYLISTS に追加する（id・title・category・description）。単発なら playlist を付けず category を付ける
- category は 受験数学・受験化学・受験生物・参考書の使い方・京大のリアル のどれか
- 題名は既存回にそろえる：検索される問いを前に置き「｜」のあとに切り口、最後に【分野】（例：「緩衝液のpHの求め方と近似が使える条件｜高校教科書と大学教科書の2通りで導く【電離平衡】」）
- slug は内容を表すローマ字。既存ファイルと重複しないか確かめる

## 2. 本文を書く

ひな形は同じ再生リストの直前の回（新シリーズなら `biboroku/kanshoueki-ph.html`）。head（KaTeX の読み込みを含む）・ヘッダー・フッター・`diag-cta` の構成をそろえる。

本文の流れは次の形を基本にする。

1. 導入：前の回があれば「第◯回では〜」とリンク付きで受ける
2. `## 結論`：`point-box` で式や結論を先に示す
3. なぜそうなるか：導出や論理。高校の方法と大学・論理的な方法を並べられるなら比較表にする
4. 例題・演習：入試の改題なら「〇〇年度 〇〇大学 第〇問（改題）」と出典を書く。オリジナルなら「演習（オリジナル）」
5. `## よくある間違い`：`point-box` と `point-label` で1つずつ
6. `## この考え方をもっと学ぶなら`：参考書を `<div class="book-link" data-book="書名" data-amz="https://www.amazon.co.jp/dp/<ASIN>?tag=jukenshindan-22">` で入れる。関連する記事があればリンクする

- 数式は KaTeX（インライン `\( \)`、別行 `\[ \]`）。化学式は `\mathrm{}` を使う
- 計算や数値は自分で検算してから載せる。原稿の数値が合わなければ直さずに報告に書く
- 各章の大事な1文は `<strong class="hl">` で囲む（備忘録は highlights.json の対象外なので手で付ける）
- `diag-cta` は科目に対応する診断ページへ誘導する

## 3. 登録する

- `biboroku/biboroku-data.js` の POSTS の先頭に1件追加する（slug・title・description・playlist と ep または category・date・order）
- 前の回の本文に次の回へのリンクを足す必要はない（再生リスト欄はビルドで更新される）

## 4. ビルドして確かめる

```
python3 scripts/build_site.py
```

- エラーが出たら直して再実行する
- `git status` と `git diff --stat` で変更が今回のページに関係するファイルだけか確かめる。無関係なファイルが変わっていたら push せず報告して止まる
- 再生リスト欄・パンくず・表紙が入っているか確かめる

## 5. コミットして push する

```
git add -A
git commit -m "備忘録: <再生リスト名> #<ep> <短い題名>を公開"
git pull --rebase origin main
git push origin main
```

単発の回は「備忘録: <短い題名>を公開」。push が失敗したら原因を報告して止まる（force push はしない）。

## 6. 報告する

- 公開URL（`https://jukenshindan.com/biboroku/<slug>`）
- 再生リストと回数（新シリーズを作った場合はその名前と説明）
- 題名を原稿から変えた場合は元の題名と新しい題名
- 検算で合わなかった数値や原稿から直した点
