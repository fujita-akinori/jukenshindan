// ===========================================================
// 受験診断ドットコム - 京大生の備忘録（共有データ）
// scripts/build_site.py がこのファイルを読み、備忘録トップ（biboroku/index.html）の
// 再生リスト・投稿一覧と、各記事のパンくず・再生リスト欄・SEO用タグを書き出します。
//
// 新しい記事を追加する場合は POSTS に1つオブジェクトを追加し、
// リポジトリのルートで `python3 scripts/build_site.py` を実行してください。
//
// PLAYLISTS（再生リスト）
//   id: 再生リストの識別子 / title: 名前 / category: 下の CATEGORIES のどれか / description: 説明
// POSTS（投稿）
//   slug: biboroku/フォルダ内のファイル名
//   playlist: 属する再生リストの id（単発の記事は省略）/ ep: 再生リスト内の回（第何回か）
//   category: 再生リストに属さない記事のカテゴリ（再生リストに属する記事は再生リストのカテゴリを使う）
//   date: "YYYY-MM-DD"（投稿順に使用）/ order: 同じ日付の並び順（大きいほど新しい）
// CATEGORIES: 受験数学・受験化学・受験生物・参考書の使い方・京大のリアル
// ===========================================================
const PLAYLISTS = [
  { id:"denri-heikou", title:"近似で解く電離平衡", category:"受験化学", description:"電離平衡の計算を物質収支と電荷収支の4本の式から近似で解く連載です。弱酸・緩衝液・塩の加水分解・多段階電離を同じ考え方で扱います。" },
  { id:"kiseki-ryouiki", title:"論理で解く軌跡と領域", category:"受験数学", description:"軌跡と領域の問題を「存在する」「または」などの論理で処理する連載です。順像法・逆像法・通過領域を1本の考え方でつなぎます。" },
];

const POSTS = [
  { slug:"kanshoueki-ph.html", title:"緩衝液のpHの求め方と近似が使える条件｜高校教科書と大学教科書の2通りで導く【電離平衡】", description:"緩衝液のpHの式を共通イオン効果による方法と物質収支・電荷収支による方法の2通りで導き、薄めたときに近似が破れる条件とpHが変わりにくい理由を解説します。", playlist:"denri-heikou", ep:2, date:"2026-10-28", order:1 },
  { slug:"jakusan-ph-kinjishiki.html", title:"弱酸のpHの近似式の求め方｜高校教科書と大学教科書の2通りで導く【京大頻出・電離平衡】", description:"弱酸のpHの近似式を電離度による方法と物質収支・電荷収支による方法の2通りで導き、京大化学2002年度第2問（改題）で使い方を確かめます。", playlist:"denri-heikou", ep:1, date:"2026-10-26", order:1 },
  { slug:"junzouhou-gyakuzouhou.html", title:"順像法と逆像法の違いとは？実は同じものだと論理で示す【軌跡・領域】", description:"2007年東大理系第3問（改題）を順像法と逆像法の両方で解き比べ、2つが軌跡の定義の言い換えにすぎないことを論理で示します。", playlist:"kiseki-ryouiki", ep:1, date:"2026-10-24", order:1 },
];
