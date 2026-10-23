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
  { id:"kiseki-ryouiki", title:"論理で解く軌跡と領域", category:"受験数学", description:"軌跡と領域の問題を「存在する」「または」などの論理で処理する連載です。順像法・逆像法・通過領域を1本の考え方でつなぎます。" },
];

const POSTS = [
  { slug:"junzouhou-gyakuzouhou.html", title:"順像法と逆像法の違いとは？実は同じものだと論理で示す【軌跡・領域】", description:"2007年東大理系第3問（改題）を順像法と逆像法の両方で解き比べ、2つが軌跡の定義の言い換えにすぎないことを論理で示します。", playlist:"kiseki-ryouiki", ep:1, date:"2026-10-24", order:1 },
];
