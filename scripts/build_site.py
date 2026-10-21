#!/usr/bin/env python3
"""
受験診断ドットコム サイト生成スクリプト

articles/articles-data.js の記事データをもとに、次のものを生成・更新します。
  - 記事一覧（articles/index.html）とタグ別一覧（articles/tag-*.html）の記事カード
  - ホームの新着記事3件
  - 全ページの canonical / OGP / 構造化データ（JSON-LD）
  - 記事ページのパンくずと執筆者表示
  - sitemap.xml

記事を追加・修正したら、リポジトリのルートで次を実行してからコミットしてください。
    python3 scripts/build_site.py
何度実行しても同じ結果になります（マーカーで囲んだ部分だけを書き換えます）。
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = "https://jukenshindan.com"
SITE = "受験診断ドットコム"
OG_IMAGE = f"{BASE}/og-image.png"
LOGO = f"{BASE}/logo-mark.png"
AUTHOR_NAME = "受験診断ドットコム運営メンバー（現役京大生）"

TAGS = [  # (タグ名, ファイル名, 説明)
    ("参考書比較", "tag-sankousho-hikaku.html", "数学・英語などの参考書を比較し、レベル感や使い方を解説した記事の一覧です。"),
    ("勉強法", "tag-benkyouhou.html", "数学・理科・社会など、科目ごとの勉強法と対策をまとめた記事の一覧です。"),
    ("受験戦略", "tag-juken-senryaku.html", "勉強計画の立て方や試験当日の準備など、受験全体の戦略に関する記事の一覧です。"),
    ("予備校", "tag-yobiko.html", "東進・河合塾・駿台・武田塾など、予備校選びと講座選びに関する記事の一覧です。"),
]
TAG_FILE = {t: f for t, f, _ in TAGS}
SUBJECTS = ["数学", "英語", "国語", "化学", "生物", "物理", "社会"]  # 記事一覧の「科目別」に出す順（記事がある科目だけ出す）
TAG_COLOR = {"参考書比較": "var(--tag-sankousho)", "受験戦略": "var(--tag-senryaku)", "勉強法": "var(--tag-kamoku)", "予備校": "var(--tag-yobiko)"}

STATIC_PAGES = [  # (ファイル, パンくず名, sitemap に載せるか)
    ("index.html", None, True),
    ("sugaku-shindan.html", "数学の参考書診断", True),
    ("seibutsu-shindan.html", "生物の参考書診断", True),
    ("kagaku-shindan.html", "化学の参考書診断", True),
    ("shindan-ichiran.html", "診断一覧", True),
    ("about.html", "運営者情報", True),
    ("contact.html", "お問い合わせ", True),
    ("privacy-policy.html", "プライバシーポリシー", True),
]


def path(*p):
    return os.path.join(ROOT, *p)


def read(p):
    with open(path(p), encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(path(p), "w", encoding="utf-8") as f:
        f.write(s)


def url_of(rel):
    if rel == "index.html":
        return BASE + "/"
    if rel == "articles/index.html":
        return BASE + "/articles/"
    return f"{BASE}/{rel}"


def git_date(rel):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
        if out and not dirty:
            return out
    except Exception:
        pass
    return date.today().isoformat()


def load_articles():
    src = read("articles/articles-data.js")
    arts = []
    for m in re.finditer(r"\{\s*slug:\"([^\"]+)\".*?\}", src):
        obj = m.group(0)
        g = lambda k: re.search(k + r':"((?:[^"\\]|\\.)*)"', obj).group(1)
        arts.append({"slug": g("slug"), "title": g("title"), "description": g("description"), "tag": g("tag"),
                     "date": g("date"), "order": int(re.search(r"order:(\d+)", obj).group(1)),
                     "subject": (re.search(r'subject:"([^"]*)"', obj) or [None, ""])[1]})
    arts.sort(key=lambda a: (a["date"], a["order"]), reverse=True)
    return arts


def replace_block(s, name, content, anchor_before=None, anchor_after=None):
    """<!-- name:BEGIN -->...<!-- name:END --> を置き換える。なければアンカーの前/後に挿入する。"""
    begin, end = f"<!-- {name}:BEGIN -->", f"<!-- {name}:END -->"
    block = f"{begin}\n{content}\n{end}"
    if begin in s:
        return re.sub(re.escape(begin) + r".*?" + re.escape(end), lambda _: block, s, count=1, flags=re.S)
    if anchor_before:
        assert anchor_before in s, (name, anchor_before)
        return s.replace(anchor_before, block + "\n" + anchor_before, 1)
    assert anchor_after in s, (name, anchor_after)
    return s.replace(anchor_after, anchor_after + "\n" + block, 1)


def meta_of(s):
    title = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip())
    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    return title, html.unescape(m.group(1)) if m else ""


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def crumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}


ORG = {"@type": "Organization", "name": SITE, "url": BASE + "/", "logo": {"@type": "ImageObject", "url": LOGO}}


def seo_head(rel, s, og_type="website", extra_ld=()):
    title, desc = meta_of(s)
    u = url_of(rel)
    e = lambda x: html.escape(x, quote=True)
    lines = [
        f'<link rel="canonical" href="{u}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{SITE}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{u}">',
        f'<meta property="og:image" content="{OG_IMAGE}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:locale" content="ja_JP">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(title)}">',
        f'<meta name="twitter:description" content="{e(desc)}">',
        f'<meta name="twitter:image" content="{OG_IMAGE}">',
    ] + [jsonld(x) for x in extra_ld]
    return replace_block(s, "SEO", "\n".join(lines), anchor_before="</head>")


def card_list_html(arts):
    out = []
    for a in arts:
        out.append(f'''    <a href="{a["slug"]}" class="article-card" data-tag="{a["tag"]}" data-subj="{a.get("subject", "")}" data-slug="{a["slug"]}">
      <span class="tag">{a["tag"]}</span>
      <h2>{a["title"]}</h2>
      <p>{a["description"]}</p>
      <span class="meta">{a["date"].replace("-", ".")}</span>
    </a>''')
    return "\n".join(out)


SEARCH_BOX = """  <div class="search-box" id="search">
    <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg>
    <input type="search" id="article-search" placeholder="記事をキーワードで検索（例：青チャート 使い方）" aria-label="記事をキーワードで検索" autocomplete="off">
  </div>
  <p class="search-empty" id="search-empty" hidden>該当する記事はありません。別のキーワードで試してみてください。</p>"""

SEARCH_SCRIPT = """<script>
(function(){
  var input = document.getElementById('article-search');
  if(!input) return;
  var empty = document.getElementById('search-empty');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.article-card'));
  var index = null, loading = null;
  function norm(t){
    t = (t || '').normalize('NFKC').toLowerCase();
    return t.replace(/[\\u30a1-\\u30f6]/g, function(c){ return String.fromCharCode(c.charCodeAt(0) - 0x60); });
  }
  function load(){
    if(index) return Promise.resolve(index);
    if(!loading){
      loading = fetch('search-index.json').then(function(r){ return r.json(); }).then(function(d){
        index = {};
        d.forEach(function(a){ index[a.slug] = norm([a.title, a.description, a.tag, a.text].join(' ')); });
        return index;
      }).catch(function(){
        index = {};
        cards.forEach(function(c){ index[c.dataset.slug] = norm(c.textContent); });
        return index;
      });
    }
    return loading;
  }
  function run(){
    var words = norm(input.value).split(/\\s+/).filter(Boolean);
    if(!words.length){ cards.forEach(function(c){ c.hidden = false; }); empty.hidden = true; return; }
    load().then(function(idx){
      var shown = 0;
      cards.forEach(function(c){
        var hay = idx[c.dataset.slug] || norm(c.textContent);
        var ok = words.every(function(w){ return hay.indexOf(w) !== -1; });
        c.hidden = !ok; if(ok) shown++;
      });
      empty.hidden = shown !== 0;
    });
  }
  input.addEventListener('input', run);
  var q = new URLSearchParams(location.search).get('q');
  if(q){ input.value = q; run(); }
  if(location.hash === '#search' || q){ input.focus(); }
})();
</script>"""


def chips_html(active, arts=None):
    items = [("すべて", "index.html", active is None)] + [(t, f, active == t) for t, f, _ in TAGS]
    out = [f'    <a class="filter-chip{" active" if on else ""}" href="{h}">{n}</a>' for n, h, on in items]
    if arts is None:  # タグ別一覧からは記事一覧の「科目別」に飛ぶ
        out.append('    <a class="filter-chip kamoku-chip" href="index.html#kamoku">科目別</a>')
    else:  # 記事一覧では押すと科目のチップが横にスライドして出てくる
        subs = [x for x in SUBJECTS if any(a.get("subject") == x for a in arts)]
        out.append('    <button type="button" class="filter-chip kamoku-chip" id="kamoku-chip" aria-expanded="false">科目別</button>')
        out.append('    <span class="subj-row" id="subj-row">' + "".join(
            f'<button type="button" class="filter-chip subj-chip" data-subj="{x}" style="--i:{i}">{x}</button>' for i, x in enumerate(subs)) + '</span>')
    return "\n".join(out)


KAMOKU_STYLE = """<style>
  .filter-row{ align-items:center; }
  .subj-row{ display:inline-flex; gap:10px; flex-wrap:nowrap; max-width:0; max-height:0; overflow:hidden; opacity:0; transition:max-width .45s ease, opacity .3s ease; }
  .subj-row.open{ max-width:760px; max-height:240px; opacity:1; flex-wrap:wrap; }
  .subj-chip{ transform:translateX(-14px); opacity:0; transition:transform .35s ease, opacity .35s ease; transition-delay:calc(var(--i) * 45ms); }
  .subj-row.open .subj-chip{ transform:none; opacity:1; }
  button.filter-chip{ line-height:inherit; }
  .article-card.subj-off{ display:none; }
  @media (prefers-reduced-motion: reduce){ .subj-row, .subj-chip{ transition:none; } }
</style>"""

KAMOKU_SCRIPT = """<script>
(function(){
  var chip = document.getElementById('kamoku-chip'), row = document.getElementById('subj-row');
  if(!chip || !row) return;
  var all = document.querySelector('.filter-row a.filter-chip.active');
  var subs = Array.prototype.slice.call(row.querySelectorAll('.subj-chip'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('.article-card'));
  function filter(sub){
    subs.forEach(function(b){ b.classList.toggle('active', b.dataset.subj === sub); });
    cards.forEach(function(c){ c.classList.toggle('subj-off', !!sub && c.dataset.subj !== sub); });
    history.replaceState(null, '', sub ? '#kamoku-' + encodeURIComponent(sub) : (row.classList.contains('open') ? '#kamoku' : location.pathname));
  }
  function open(on){
    row.classList.toggle('open', on); chip.classList.toggle('active', on); chip.setAttribute('aria-expanded', on);
    if(all) all.classList.toggle('active', !on);
    if(!on) filter(null); else history.replaceState(null, '', '#kamoku');
  }
  chip.addEventListener('click', function(){ open(!row.classList.contains('open')); });
  subs.forEach(function(b){ b.addEventListener('click', function(){ filter(b.classList.contains('active') ? null : b.dataset.subj); }); });
  var h = decodeURIComponent(location.hash);
  if(h.indexOf('#kamoku') === 0){ open(true); if(h.indexOf('#kamoku-') === 0) filter(h.slice(8)); }
})();
</script>"""


def add_search(s):
    s = replace_block(s, "SEARCH", SEARCH_BOX, anchor_before='  <div class="filter-row" id="filter-row">')
    s = replace_block(s, "SEARCH-SCRIPT", SEARCH_SCRIPT, anchor_before="</body>")
    return s


def build_search_index(arts):
    out = []
    for a in arts:
        s = read(f"articles/{a['slug']}")
        body = s[s.index('<div class="article-body">'):s.index('<div class="diag-cta">')]
        body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
        body = re.sub(r'<div class="aff-box">.*?</div>\s*$', " ", body, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", body))
        text = re.sub(r"\s+", " ", text).strip()
        out.append({"slug": a["slug"], "title": a["title"], "description": a["description"],
                    "tag": a["tag"], "text": text})
    write("articles/search-index.json", json.dumps(out, ensure_ascii=False, separators=(",", ":")))


SEARCH_ICON = ('<a class="nav-search" href="{href}" aria-label="記事を検索" title="記事を検索">'
               '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle>'
               '<line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg></a>')


GA4_ID = "G-2WNQN0ZF8D"
GA4_TAG = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA4_ID}');
</script>"""


def add_ga4():
    """全ページの <head> の直後に Google アナリティクス（GA4）のタグを入れる"""
    pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html")) + ["articles/" + f for f in sorted(os.listdir(path("articles"))) if f.endswith(".html")]
    for rel in pages:
        s = read(rel)
        if "<head>" not in s:
            continue
        s2 = replace_block(s, "GA4", GA4_TAG, anchor_after="<head>")
        if s2 != s:
            write(rel, s2)


def add_nav_search():
    pages = [p for p, _, _ in STATIC_PAGES] + ["articles/" + f for f in sorted(os.listdir(path("articles"))) if f.endswith(".html")]
    for rel in pages:
        s = read(rel)
        if '<nav class="nav-links">' not in s:
            continue
        href = "index.html#search" if rel.startswith("articles/") else "articles/index.html#search"
        nav = s[s.index('<nav class="nav-links">'):]
        nav_end = s.index('<nav class="nav-links">') + nav.index("</nav>")
        head, tail = s[:nav_end], s[nav_end:]
        begin, end = "<!-- NAVSEARCH:BEGIN -->", "<!-- NAVSEARCH:END -->"
        block = f"{begin}{SEARCH_ICON.format(href=href)}{end}"
        if begin in head:
            head = re.sub(re.escape(begin) + ".*?" + re.escape(end), lambda _: block, head, count=1, flags=re.S)
        else:
            head = head.rstrip() + "\n      " + block + "\n    "
        write(rel, head + tail)


def build_list_pages(arts):
    base = read("articles/index.html")
    # 旧仕様（JSで描画）の残りを掃除
    base = re.sub(r'\s*<p class="empty-note" id="empty-note"[^>]*>.*?</p>', "", base, flags=re.S)
    base = re.sub(r'\s*<!--\s*記事を追加する場合は.*?-->', "", base, flags=re.S)
    base = re.sub(r'<script src="articles-data\.js[^"]*"></script>\s*<script>.*?</script>\s*', "", base, flags=re.S)
    base = re.sub(r'<div class="filter-row" id="filter-row">.*?</div>',
                  '<div class="filter-row" id="filter-row">\n<!-- CHIPS:BEGIN -->\n<!-- CHIPS:END -->\n  </div>',
                  base, count=1, flags=re.S) if "CHIPS:BEGIN" not in base else base
    base = re.sub(r'<div class="article-grid" id="article-grid">\s*</div>',
                  '<div class="article-grid" id="article-grid">\n<!-- CARDS:BEGIN -->\n<!-- CARDS:END -->\n  </div>',
                  base, count=1) if "CARDS:BEGIN" not in base else base
    if "a.filter-chip" not in base:
        base = base.replace(".filter-chip.active{", "a.filter-chip{ text-decoration:none; display:inline-block; }\n  .filter-chip.active{", 1)

    def page(active, arts_, title, h1, lead, rel):
        s = re.sub(r"<!-- KAMOKU-(STYLE|SCRIPT):BEGIN -->.*?<!-- KAMOKU-\1:END -->\n?", "", base, flags=re.S)  # 科目別の絞り込みは記事一覧だけ
        s = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", s, count=1)
        s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{lead}">', s, count=1)
        s = re.sub(r'<h1 class="page-title">.*?</h1>', f'<h1 class="page-title">{h1}</h1>', s, count=1)
        s = re.sub(r'<p class="page-lead">.*?</p>', f'<p class="page-lead">{lead}</p>', s, count=1)
        s = replace_block(s, "CHIPS", chips_html(active))
        s = replace_block(s, "CARDS", card_list_html(arts_))
        s = add_search(s)
        crumbs = [("ホーム", BASE + "/"), ("記事一覧", BASE + "/articles/")]
        if active:
            crumbs.append((f"{active}の記事", url_of(rel)))
        item_list = {"@context": "https://schema.org", "@type": "ItemList",
                     "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{BASE}/articles/{a['slug']}"}
                                         for i, a in enumerate(arts_)]}
        s = seo_head(rel, s, "website", [crumb_ld(crumbs), item_list])
        write(rel, s)

    index_lead = re.search(r'<p class="page-lead">(.*?)</p>', base, re.S).group(1)
    index_desc = re.search(r'<meta name="description" content="([^"]*)"', base).group(1)
    s_title = "記事一覧 | " + SITE
    # 記事一覧（説明文は既存のものを維持）
    s = base
    s = replace_block(s, "CHIPS", chips_html(None, arts))
    s = replace_block(s, "KAMOKU-STYLE", KAMOKU_STYLE, anchor_before="</head>")
    s = replace_block(s, "KAMOKU-SCRIPT", KAMOKU_SCRIPT, anchor_before="</body>")
    s = replace_block(s, "CARDS", card_list_html(arts))
    s = add_search(s)
    item_list = {"@context": "https://schema.org", "@type": "ItemList",
                 "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{BASE}/articles/{a['slug']}"}
                                     for i, a in enumerate(arts)]}
    s = seo_head("articles/index.html", s, "website",
                 [crumb_ld([("ホーム", BASE + "/"), ("記事一覧", BASE + "/articles/")]), item_list])
    write("articles/index.html", s)
    for tag, fname, lead in TAGS:
        page(tag, [a for a in arts if a["tag"] == tag], f"{tag}の記事一覧 | {SITE}", f"{tag}の記事", lead, f"articles/{fname}")


def build_home(arts):
    s = read("index.html")
    cards = []
    for a in arts[:3]:
        c = TAG_COLOR.get(a["tag"], "var(--lv2)")
        cards.append(f'''      <a href="articles/{a["slug"]}" class="diag-card available" style="--tag-color:{c};">
        <div class="subject-tag" style="color:{c};">{a["tag"]}</div>
        <h3>{a["title"]}</h3>
        <p>{a["description"]}</p>
        <span class="status" style="color:{c};"><span class="status-dot" style="background:{c};"></span>{a["date"].replace("-", ".")}</span>
      </a>''')
    if "HOME-ARTICLES:BEGIN" not in s:
        s = s.replace('<div class="diag-grid" id="home-article-grid"></div>',
                      '<div class="diag-grid" id="home-article-grid">\n<!-- HOME-ARTICLES:BEGIN -->\n<!-- HOME-ARTICLES:END -->\n    </div>', 1)
        s = re.sub(r'<script src="articles/articles-data\.js[^"]*"></script>\s*<script>.*?</script>\s*', "", s, count=1, flags=re.S)
    s = replace_block(s, "HOME-ARTICLES", "\n".join(cards))
    website = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE + "/",
               "publisher": ORG}
    s = seo_head("index.html", s, "website", [website, dict({"@context": "https://schema.org"}, **ORG)])
    write("index.html", s)


def build_static_pages():
    for rel, crumb, _ in STATIC_PAGES:
        if rel == "index.html":
            continue
        s = read(rel)
        lds = [crumb_ld([("ホーム", BASE + "/"), (crumb, url_of(rel))])]
        if rel.endswith("-shindan.html"):
            title, desc = meta_of(s)
            lds.append({"@context": "https://schema.org", "@type": "WebApplication", "name": crumb,
                        "url": url_of(rel), "description": desc, "applicationCategory": "EducationalApplication",
                        "operatingSystem": "All", "inLanguage": "ja",
                        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "publisher": ORG})
        write(rel, seo_head(rel, s, "website", lds))


def build_articles(arts):
    for a in arts:
        rel = f"articles/{a['slug']}"
        s = read(rel)
        tag_file = TAG_FILE.get(a["tag"], "index.html")
        crumbs_html = (f'    <nav class="crumbs" aria-label="パンくずリスト"><a href="../index.html">ホーム</a>'
                       f'<span>›</span><a href="index.html">記事一覧</a>'
                       f'<span>›</span><a href="{tag_file}">{a["tag"]}</a></nav>')
        byline = (f'    <span class="byline">執筆：<a href="../about.html">{AUTHOR_NAME}</a></span>')
        s = replace_block(s, "CRUMBS", crumbs_html, anchor_after='<div class="article-header">')
        s = replace_block(s, "BYLINE", byline, anchor_before="  </div>\n\n  <div class=\"article-body\">")
        modified = max(a["date"], git_date(rel))
        title, desc = meta_of(s)
        article = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
                   "description": desc, "datePublished": a["date"], "dateModified": modified,
                   "image": [OG_IMAGE], "inLanguage": "ja", "articleSection": a["tag"],
                   "mainEntityOfPage": {"@type": "WebPage", "@id": url_of(rel)},
                   "author": {"@type": "Organization", "name": AUTHOR_NAME, "url": BASE + "/about.html"},
                   "publisher": ORG}
        crumbs = crumb_ld([("ホーム", BASE + "/"), ("記事一覧", BASE + "/articles/"),
                           (a["tag"], f"{BASE}/articles/{tag_file}"), (a["title"], url_of(rel))])
        write(rel, seo_head(rel, s, "article", [article, crumbs]))


def bust_css_cache():
    """style.css の内容から版番号を作り、全ページの読み込みURLに付ける（ブラウザに古いデザインを使わせない）"""
    import hashlib
    ver = hashlib.md5(read("style.css").encode("utf-8")).hexdigest()[:8]
    pages = [p for p, _, _ in STATIC_PAGES] + ["articles/" + f for f in sorted(os.listdir(path("articles"))) if f.endswith(".html")]
    for rel in pages:
        s = read(rel)
        s2 = re.sub(r'href="((?:\.\./)?style\.css)(?:\?v=[0-9a-f]+)?"', lambda m: f'href="{m.group(1)}?v={ver}"', s)
        if s2 != s:
            write(rel, s2)


def build_sitemap(arts):
    rows = []
    for rel, _, on in STATIC_PAGES:
        if on:
            rows.append((url_of(rel), git_date(rel)))
    rows.append((url_of("articles/index.html"), date.today().isoformat()))
    for _, f, _ in TAGS:
        rows.append((url_of(f"articles/{f}"), date.today().isoformat()))
    for a in arts:
        rel = f"articles/{a['slug']}"
        rows.append((url_of(rel), max(a["date"], git_date(rel))))
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in rows)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')


def main():
    arts = load_articles()
    for a in arts:
        assert os.path.exists(path("articles", a["slug"])), a["slug"]
        assert a["tag"] in TAG_FILE, (a["slug"], a["tag"])
    import affbox
    affbox.build(ROOT, read, write)
    affbox.build_inline(ROOT, read, write)
    import highlight
    hl_done, hl_missing = highlight.build(ROOT, read, write)
    for slug, sent in hl_missing:
        print("  強調する文が見つからない:", slug, sent[:30])
    got, total = affbox.build_diag(ROOT, read, write)
    print(f"数学診断の表紙: {got}/{total} 冊")
    got, total = affbox.build_diag(ROOT, read, write, "seibutsu-shindan.html")
    print(f"生物診断の表紙: {got}/{total} 冊")
    got, total = affbox.build_diag(ROOT, read, write, "kagaku-shindan.html")
    print(f"化学診断の表紙: {got}/{total} 冊")
    build_articles(arts)
    build_list_pages(arts)
    build_home(arts)
    build_static_pages()
    build_search_index(arts)
    add_nav_search()
    add_ga4()
    bust_css_cache()
    build_sitemap(arts)
    print(f"OK: 記事 {len(arts)} 本 / タグページ {len(TAGS)} 枚を生成しました")


if __name__ == "__main__":
    main()
