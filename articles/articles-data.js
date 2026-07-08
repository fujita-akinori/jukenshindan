// ===========================================================
// 受験診断ドットコム - 記事メタデータ（共有データ）
// ホーム(index.html)と記事一覧(articles/index.html)の両方が
// このファイルを参照して記事カードを自動生成します。
//
// 新しい記事を追加する場合は、この配列に1つオブジェクトを
// 追加するだけでOK。ホーム・記事一覧どちらにも自動反映されます。
//
// slug: articles/フォルダ内のファイル名
// date: "YYYY-MM-DD" 形式（新着順ソートに使用）
// order: 同じ日付の記事が複数ある場合の並び順（大きいほど新しい）
// ===========================================================
const ARTICLES = [
  { slug:"aoi-chart-vs-focus-gold.html", title:"青チャートとFocus Gold、結局どっちを選ぶべきか", description:"数学の網羅系参考書の2大巨頭を、収録問題数・解説の丁寧さ・レイアウトの3つの観点で比較します。", tag:"参考書比較", date:"2026-07-07", order:1 },
  { slug:"kaihou-anki-vs-rikai.html", title:"解法暗記VS理解、受験数学はどっちが正解か", description:"「解法は暗記すべきか理解すべきか」という永遠の論争を、学習段階という観点から整理します。", tag:"受験戦略", date:"2026-07-08", order:2 },
  { slug:"suujaku-suukyou-ronri.html", title:"数弱が数強になるための武器：論理", description:"数学が苦手な受験生の多くがつまずいているのは計算力ではなく論理力。伸び悩みを打開する視点を整理します。", tag:"受験戦略", date:"2026-07-08", order:3 },
  { slug:"keisanryoku-9wari.html", title:"受験数学は計算力が9割", description:"発想力よりも計算力。受験数学の得点を左右する地味だが決定的な要素と、その鍛え方を解説します。", tag:"受験戦略", date:"2026-07-08", order:4 },
  { slug:"pomodoro-syuuchuuryoku.html", title:"集中力を持続させる方法：ポモドーロ・テクニック", description:"受験勉強の集中力が続かない人向けに、時間管理法「ポモドーロ・テクニック」の仕組みと取り入れ方を解説します。", tag:"受験戦略", date:"2026-07-08", order:5 },
  { slug:"sawaruna-sankousho-3sen.html", title:"触れるな注意 難しすぎる受験参考書3選", description:"内容は良書でも、対象読者を間違えると挫折を招く難関参考書3冊を紹介。自分に合うレベルの見極め方を解説します。", tag:"参考書比較", date:"2026-07-08", order:6 },
  { slug:"sankousho-root-no-yami.html", title:"参考書ルートの闇：参考書診断がなぜ必要なのか", description:"ネット上に溢れる「参考書ルート」コンテンツに共通する3つの問題点と、個別診断という形が必要な理由を解説します。", tag:"受験戦略", date:"2026-07-08", order:7 },
  { slug:"shin-kaihou-eno-michi.html", title:"これさえやれば大丈夫？難関大受験の新定番「真・解法への道」を紹介", description:"網羅系参考書を終えたのに難関大の過去問で手が止まる受験生に向けて、特徴と使い方を解説します。", tag:"参考書比較", date:"2026-07-08", order:8 },
  { slug:"yobiko-no-jugyou-3sen.html", title:"まるで予備校の授業な数学の参考書3選", description:"ハイレベル完全攻略・世界一わかりやすい京大の理系数学/文系数学・真解法への道の3冊を、著者の講師経歴と合わせて紹介します。", tag:"参考書比較", date:"2026-07-08", order:9 },
  { slug:"zeppan-kami-sankousho-3sen.html", title:"絶版になってしまった神参考書3選", description:"長岡亮介『総合的研究』、松田聡平『最高の演習』、秋山仁『発見的教授法による数学シリーズ』。今は入手困難な伝説の参考書と著者の経歴を紹介します。", tag:"参考書比較", date:"2026-07-08", order:10 },
  { slug:"sankousho-syuukaisuu.html", title:"「1冊を完璧に」は本当か？参考書の周回数について", description:"「1冊を完璧にすべき」という定番アドバイスを、周回数の目安と「完璧」の正しい定義から解説します。", tag:"受験戦略", date:"2026-07-08", order:11 },
  { slug:"moshi-tokinaoshi-note.html", title:"模試の解き直しノート、意味があるのか問題", description:"模試の解き直しノートが機能しない理由と、本当に実力につながる解き直しの条件を解説します。", tag:"受験戦略", date:"2026-07-08", order:12 },
  { slug:"natsuyasumi-suugaku-jikan.html", title:"夏休みの数学、何時間やればいいのか問題", description:"夏休みに数学へ割く時間について、「時間数」ではなく「到達点」から逆算する考え方を解説します。", tag:"受験戦略", date:"2026-07-08", order:13 },
  { slug:"kyoutsuu-test-kaitou-junjo.html", title:"共通テスト数学、時間が足りない人のための解答順序戦略", description:"共通テスト数学で時間が足りない受験生に向けて、解答順序の工夫とマークミスを防ぐ習慣を解説します。", tag:"科目別対策", date:"2026-07-08", order:14 },
  { slug:"seisuu-mondai-pattern.html", title:"整数問題が苦手な人へ：頻出解法パターンの整理", description:"因数分解・余りによる分類・不等式による絞り込みなど、整数問題の頻出解法パターンを整理します。", tag:"科目別対策", date:"2026-07-08", order:15 },
  { slug:"vector-zu-de-kangaero.html", title:"ベクトルは図で考えろ：計算に逃げると伸びない理由", description:"ベクトル分野で計算だけに頼ると応用問題で詰まる理由と、図を描く習慣の重要性を解説します。", tag:"科目別対策", date:"2026-07-08", order:16 },
  { slug:"bisekibun-imi-de-rikai.html", title:"微積分は「公式より意味」で理解しろ", description:"微分・積分の公式暗記だけでは対応できない理由と、意味から理解する重要性を解説します。", tag:"科目別対策", date:"2026-07-08", order:17 },
  { slug:"ichitaichi-vs-shinsuta.html", title:"1対1対応の演習 vs 新数学スタンダード演習、どっちをやるべきか", description:"網羅系参考書の後に取り組む定番演習書2冊を、使う順番・向いているタイプの観点から比較します。", tag:"参考書比較", date:"2026-07-08", order:18 },
  { slug:"bunkei-purachika.html", title:"文系の数学 良問プラチカ、実際のレベル感と使い方", description:"文系数学の定番演習書「良問プラチカ」のレベル感、着手のタイミング、効果的な使い方を解説します。", tag:"参考書比較", date:"2026-07-08", order:19 },
  { slug:"tokui-nobasu-ka-nigate-umeru-ka.html", title:"「得意科目を伸ばす」か「苦手科目を埋める」か", description:"限られた勉強時間の配分について、得意を伸ばす戦略と苦手を埋める戦略のどちらが向いているかを解説します。", tag:"受験戦略", date:"2026-07-08", order:20 },
];

// 新着順（日付→order）にソートして返す
function getSortedArticles(){
  return [...ARTICLES].sort((a,b)=>{
    if(a.date !== b.date) return a.date < b.date ? 1 : -1;
    return b.order - a.order;
  });
}
