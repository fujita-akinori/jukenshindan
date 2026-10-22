// ===========================================================
// 受験診断ドットコム - 記事メタデータ（共有データ）
// scripts/build_site.py がこのファイルを読み、ホーム・記事一覧・
// タグ別一覧の記事カードを静的HTMLとして書き出します。
//
// 新しい記事を追加する場合は、この配列に1つオブジェクトを追加し、
// リポジトリのルートで `python3 scripts/build_site.py` を実行してください。
// 記事一覧・タグ別一覧・ホームの新着・sitemap.xml・SEO用タグが更新されます。
//
// slug: articles/フォルダ内のファイル名
// date: "YYYY-MM-DD" 形式（新着順ソートに使用）
// order: 同じ日付の記事が複数ある場合の並び順（大きいほど新しい）
// subject: 記事の科目（数学・英語・国語・化学・生物・物理・社会）。記事一覧の「科目別」で絞り込むのに使う。科目に関係ない記事は省略
// ===========================================================
const ARTICLES = [
  { slug:"aoi-chart-vs-focus-gold.html", title:"青チャートとFocus Gold、結局どっちを選ぶべきか", description:"数学の網羅系参考書の2大巨頭を、収録問題数・解説の丁寧さ・レイアウトの3つの観点で比較します。", tag:"参考書比較", subject:"数学", date:"2026-07-07", order:1 },
  { slug:"kaihou-anki-vs-rikai.html", title:"解法暗記か理解か、受験数学の正解は「暗記→理解→暗記」｜3段階の勉強法と参考書", description:"解法暗記か理解かの答えは「暗記→理解→暗記」の3段階。段階ごとに使う参考書と、段階を飛ばすと数学ができないまま本番を迎える理由を筆者の経験から解説します。", tag:"勉強法", subject:"数学", date:"2026-07-08", order:2 },
  { slug:"suujaku-suukyou-ronri.html", title:"数学が伸びない原因は「論理」だった｜偏差値60から京大本番で合格者平均を超えた勉強法", description:"河合で偏差値60前後だった筆者が京大本番で合格者平均を大きく超えた理由は論理。数強と数弱の違い、入試で落とす4つの典型、論理の学び方と毎日の習慣を解説します。", tag:"勉強法", subject:"数学", date:"2026-07-08", order:3 },
  { slug:"keisanryoku-9wari.html", title:"受験数学は計算力で決まる？計算ミスで15点差不合格だった京大生が教える計算力の鍛え方", description:"京大入試で積分計算の小問を落とし15点差で不合格だった筆者が、論理が合っていても計算で点を失う理由と、計算ミスの原因別対策・省略力の具体例・検算・参考書を解説します。", tag:"勉強法", subject:"数学", date:"2026-07-08", order:4 },
  { slug:"pomodoro-syuuchuuryoku.html", title:"集中力を持続させる方法：ポモドーロ・テクニック", description:"受験勉強の集中力が続かない人向けに、時間管理法「ポモドーロ・テクニック」の仕組みと取り入れ方を解説します。", tag:"受験戦略", date:"2026-07-08", order:5 },
  { slug:"sawaruna-sankousho-3sen.html", title:"触れるな注意 難しすぎる受験参考書3選", description:"内容は良書でも、対象読者を間違えると挫折を招く難関参考書3冊を紹介。自分に合うレベルの見極め方を解説します。", tag:"参考書比較", subject:"数学", date:"2026-07-08", order:6 },
  { slug:"sankousho-root-no-yami.html", title:"参考書ルートの闇：参考書診断がなぜ必要なのか", description:"ネット上に溢れる「参考書ルート」コンテンツに共通する3つの問題点と、個別診断という形が必要な理由を解説します。", tag:"受験戦略", date:"2026-07-08", order:7 },
  { slug:"shin-kaihou-eno-michi.html", title:"これさえやれば大丈夫？難関大受験の新定番「真・解法への道」を紹介", description:"網羅系参考書を終えたのに難関大の過去問で手が止まる受験生に向けて、特徴と使い方を解説します。", tag:"参考書比較", subject:"数学", date:"2026-07-08", order:8 },
  { slug:"yobiko-no-jugyou-3sen.html", title:"まるで予備校の授業な数学の参考書3選", description:"ハイレベル完全攻略・世界一わかりやすい京大の理系数学/文系数学・真解法への道の3冊を、著者の講師経歴と合わせて紹介します。", tag:"参考書比較", subject:"数学", date:"2026-07-08", order:9 },
  { slug:"zeppan-kami-sankousho-3sen.html", title:"絶版になってしまった神参考書3選", description:"長岡亮介『総合的研究』、松田聡平『最高の演習』、秋山仁『発見的教授法による数学シリーズ』。今は入手困難な伝説の参考書と著者の経歴を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-07-08", order:10 },
  { slug:"sankousho-syuukaisuu.html", title:"参考書は何周すべき？「1冊を完璧に」が正しいのは1冊目だけ｜京大生の周回数と一期一会の勉強法", description:"「1冊を完璧に」は1冊目の基本書だけ正しい。土台の1冊は覚えるまで繰り返し、上達後は一期一会で問題に向き合う勉強法と、段階別の周回数の目安を京大生が解説します。", tag:"勉強法", date:"2026-07-08", order:11 },
  { slug:"moshi-tokinaoshi-note.html", title:"模試の解き直しノート、意味があるのか問題", description:"模試の解き直しノートが機能しない理由と、本当に実力につながる解き直しの条件を解説します。", tag:"受験戦略", date:"2026-07-08", order:12 },
  { slug:"natsuyasumi-suugaku-jikan.html", title:"夏休みの数学、何時間やればいいのか問題", description:"夏休みに数学へ割く時間について、「時間数」ではなく「到達点」から逆算する考え方を解説します。", tag:"受験戦略", subject:"数学", date:"2026-07-08", order:13 },
  { slug:"kyoutsuu-test-kaitou-junjo.html", title:"共通テスト数学、時間が足りない人のための解答順序戦略", description:"共通テスト数学で時間が足りない受験生に向けて、解答順序の工夫とマークミスを防ぐ習慣を解説します。", tag:"勉強法", subject:"数学", date:"2026-07-08", order:14 },
  { slug:"seisuu-mondai-pattern.html", title:"整数問題の解き方は「必要条件で絞る」だけ｜積の形・余り・範囲の3パターンを例題で解説", description:"整数問題の解き方は本質的に「必要条件で絞る」1つ。積の形・余り（mod）・範囲を絞る3つのパターンと十分性の確認を、例題つきで京大生が解説します。", tag:"勉強法", subject:"数学", date:"2026-07-08", order:15 },
  { slug:"vector-zu-de-kangaero.html", title:"ベクトルは図で考えろ：計算に逃げると伸びない理由", description:"ベクトル分野で計算だけに頼ると応用問題で詰まる理由と、図を描く習慣の重要性を解説します。", tag:"勉強法", subject:"数学", date:"2026-07-08", order:16 },
  { slug:"bisekibun-imi-de-rikai.html", title:"微積分は「公式より意味」で理解しろ", description:"微分・積分の公式暗記だけでは対応できない理由と、意味から理解する重要性を解説します。", tag:"勉強法", subject:"数学", date:"2026-07-08", order:17 },
  { slug:"ichitaichi-vs-shinsuta.html", title:"1対1対応の演習と新数学スタンダード演習はどっちをやるべき？レベル・解説・レイアウトを京大生が比較", description:"同じ東京出版の1対1対応の演習と新数学スタンダード演習を、レベル・問題数・解説・レイアウトで比較。多くの人に勧められるのはどちらか、1対1の次に進む本まで京大生が解説します。", tag:"参考書比較", subject:"数学", date:"2026-07-08", order:18 },
  { slug:"bunkei-purachika.html", title:"文系プラチカは理系プラチカより難しい？レベル・対象・理系が使う意味を京大生が解説", description:"文系プラチカは名前に反して理系プラチカより難しい。理由とレベル、向いている人、理系が数IIの微積分対策に使う意味までを京大生が解説します。", tag:"参考書比較", subject:"数学", date:"2026-07-08", order:19 },
  { slug:"tokui-nobasu-ka-nigate-umeru-ka.html", title:"「得意科目を伸ばす」か「苦手科目を埋める」か", description:"限られた勉強時間の配分について、得意を伸ばす戦略と苦手を埋める戦略のどちらが向いているかを解説します。", tag:"受験戦略", date:"2026-07-08", order:20 },
  { slug:"yobiko-type-betsu-matome.html", title:"結局どこが良いの？東進・河合塾・駿台・武田塾をタイプ別に整理", description:"東進・河合塾・駿台・武田塾の4校を授業形式と管理のされ方で整理し、向いている人と注意点を比較します。", tag:"予備校", date:"2026-10-17", order:21 },
  { slug:"toshin-suugaku-kouza.html", title:"東進で数学を取るなら？おすすめ3講座と講師の特徴", description:"東進の数学講座「数学の真髄」「入試数学の戦術」「数学ぐんぐん」を、担当講師の教え方の違いから比較します。", tag:"予備校", subject:"数学", date:"2026-10-17", order:22 },
  { slug:"suugaku-no-shinzui.html", title:"青木純二「数学の真髄」シリーズ 徹底解説", description:"東進ブックス『数学の真髄』の論理・写像編とベクトル編を、講座版との違いや使う時期とあわせて解説します。", tag:"参考書比較", subject:"数学", date:"2026-10-17", order:23 },
  { slug:"seibutsu-benkyouhou.html", title:"生物の勉強法：初学から難関大までの参考書ルート", description:"生物は教科書が軸。田部の合格77講とセミナーで東大レベルまで届くシンプルなルートと、思考問題対策の標準問題精講を紹介します。", tag:"勉強法", subject:"生物", date:"2026-10-17", order:24 },
  { slug:"kagaku-benkyouhou.html", title:"化学の勉強法：初学から難関大までの参考書ルート", description:"Doシリーズと入門・基礎・標準・上級問題精講で完結する化学の参考書ルートを、著者紹介と志望校別の止めどころとあわせて解説します。", tag:"勉強法", subject:"化学", date:"2026-10-17", order:25 },
  { slug:"kyoutsuu-seikei-shougatsu.html", title:"正月から始めて9割：共通テスト政経の最短勉強法", description:"正月から始めて現役97点。miniいけ先生の動画と過去問・予想問題だけで、共通テスト公共、政治・経済で9割を狙う勉強法を紹介します。", tag:"勉強法", subject:"社会", date:"2026-10-18", order:26 },
  { slug:"kyoutsuu-mochimono.html", title:"共通テスト当日に忘れたら困る持ち物チェックリスト", description:"共通テスト当日に必要な持ち物、あると助かるもの、持ち込むと不正行為になるものをチェックリストにまとめました。", tag:"受験戦略", date:"2026-10-18", order:27 },
  { slug:"kakureta-ryousho-3sen.html", title:"隠れた良書：もっと使われていい数学参考書3選", description:"最重要問題100・入試のツボを押さえる重点学習・実戦 数学重要問題集。知名度は低いが実力は定番に劣らない3冊をレベル別に紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-18", order:28 },
  { slug:"sougouteki-kenkyuu-series.html", title:"本格派数学参考書レーベル「総合的研究」シリーズ全解説", description:"旺文社「総合的研究」の数学の本を全冊解説。各冊の特徴と、どの順番で読むかを紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-18", order:29 },
  { slug:"leap-saikyou.html", title:"ターゲットでもシス単でもなく、結局LEAPが最強な理由", description:"ターゲット1900・システム英単語と比べて、LEAPが最強の英単語帳である理由を解説します。第一義だけ隠せる構成と質の高い例文が強みです。", tag:"参考書比較", subject:"英語", date:"2026-10-18", order:30 },
  { slug:"ichitaichi-tsukaikata.html", title:"1対1対応の演習の使い方とレベル｜いつから何周やるか・次にやる問題集まで解説", description:"1対1対応の演習（東京出版）のレベル・使い方・何周やるべきか・いつから始めるかを解説。網羅系参考書の次に使う定番問題集の進め方を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-19", order:31 },
  { slug:"focus-gold-tsukaikata.html", title:"Focus Goldの使い方とレベル｜青チャートとの違いと何周やるべきかを解説", description:"Focus Gold 6th Editionのレベル・使い方・何周やるべきかを解説。分厚い網羅系を挫折せずにやり切る例題中心の進め方を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-19", order:32 },
  { slug:"yasashii-rikei-sugaku.html", title:"やさしい理系数学のレベルと使い方｜本当にやさしい？いつから始めるかを解説", description:"やさしい理系数学（河合出版）のレベル・使い方・何周やるべきかを解説。本当にやさしいのか、別解を活かした使い方を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-19", order:33 },
  { slug:"hyoujun-mondai-seikou-sugaku.html", title:"標準問題精講（数学）のレベルと使い方｜1対1対応の演習との違いも解説", description:"標準問題精講（旺文社）のレベル・使い方・何周やるべきかを解説。1対1対応の演習との違いと、精講を活かした進め方を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-19", order:34 },
  { slug:"ukaru-keisan-tsukaikata.html", title:"合格る計算の使い方とレベル｜計算ミスが減る勉強法と何周やるべきか", description:"合格る計算（文英堂・広瀬和之）のレベル・使い方・何周やるべきかを解説。計算ミスや時間切れで点を落とす人のための進め方を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-19", order:35 },
  { slug:"high-level-rikei-sugaku.html", title:"ハイレベル理系数学のレベルと使い方｜やさしい理系数学との違い・いつから始めるか", description:"ハイレベル理系数学（河合出版）のレベル・使い方・何周やるべきかを解説。やさしい理系数学との違いと、最難関大志望が取り組む時期を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-20", order:36 },
  { slug:"sekaiichi-kyodai-rikei.html", title:"世界一わかりやすい京大の理系数学の使い方とレベル｜京大志望はいつから始めるべきか", description:"世界一わかりやすい京大の理系数学 合格講座（池谷哲）のレベル・使い方・始める時期を解説。4つの思考過程を活かした進め方を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-20", order:37 },
  { slug:"bisekibun-kiso-no-gokui.html", title:"微積分 基礎の極意の使い方とレベル｜数Ⅲの微積分を得点源にする進め方", description:"微積分 基礎の極意（東京出版）のレベル・使い方・何周やるべきかを解説。約200の手筋をまとめた第2部を中心にした進め方を紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-20", order:38 },
  { slug:"nyuushi-sugaku-no-shouaku.html", title:"入試数学の掌握のレベルと使い方｜3部作の順番と挫折しない進め方", description:"入試数学の掌握（近藤至徳）のレベル・使い方を解説。赤（論理）・青（通過領域）・緑（図形）の違いと、志望校別にどれをやるべきかを紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-20", order:39 },
  { slug:"master-of-seisuu.html", title:"マスター・オブ・整数のレベルと使い方｜整数問題を得点源にする進め方", description:"マスター・オブ・整数（東京出版）のレベル・使い方を解説。新課程で整数の出題が絞られるなか、この本に時間をかけるべきかの判断基準も紹介します。", tag:"参考書比較", subject:"数学", date:"2026-10-20", order:40 },
  { slug:"idiomatic-300.html", title:"IDIOMATIC 300は熟語帳ではない｜レベル・使い方と完成までの期間を解説", description:"大学入試 飛躍のフレーズ IDIOMATIC 300（山崎竜成）のレベル・使い方を解説。熟語帳との違い、完成までにかかる期間、東大・早慶での効き方を体験とあわせて紹介します。", tag:"参考書比較", subject:"英語", date:"2026-10-21", order:41 },
];

// 新着順（日付→order）にソートして返す
function getSortedArticles(){
  return [...ARTICLES].sort((a,b)=>{
    if(a.date !== b.date) return a.date < b.date ? 1 : -1;
    return b.order - a.order;
  });
}
