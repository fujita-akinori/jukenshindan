"""記事末尾の「紹介した参考書」枠に、楽天の表紙画像と「楽天で見る」ボタンを付ける"""
import html
import os
import re
import urllib.parse

import rakuten

AFF_DISCLOSURE = "Amazonのアソシエイトとして、当メンバーは適格販売により収入を得ています。当サイトは楽天アフィリエイトに参加しています。"

# アフィリエイトの全体スイッチ。AdSense審査が通るまで False にしてある。
# False のあいだは購入ボタン・PR表記・開示文を出さず、表紙は楽天の商品ページへの通常リンク（紹介料なし）にする。
# 承認後に True に戻して python3 scripts/build_site.py を実行すれば、記事・備忘録・診断のリンクがすべて元に戻る。
AFF_ENABLED = False
PR_NOTE = '<span class="pr-note"><span class="pr-tag">PR</span>この記事にはアフィリエイト広告が含まれています</span>'


AMAZON_TAG = "jukenshindan-22"


def _strip_tag(u):
    return re.sub(r"([?&])tag=[^&]*&?", r"\1", u).rstrip("?&")


def _with_tag(u):
    if "tag=" in u:
        return u
    return u + ("&" if "?" in u else "?") + "tag=" + AMAZON_TAG


def plain_url(url):
    """楽天のアフィリエイトURLから、紹介料の発生しない通常の商品ページURLを取り出す"""
    m = re.search(r"[?&]pc=([^&]+)", url or "")
    return urllib.parse.unquote(m.group(1)) if m else (url or "")


def cover_url(r):
    return r["url"] if AFF_ENABLED else plain_url(r["url"])


def _row_html(name, amz, r):
    e = lambda x: html.escape(x, quote=True)
    img = ''
    if r["image"]:
        img = (f'<img class="aff-cover" src="{e(r["image"])}" alt="{e(name)}の表紙" '
               f'width="64" height="90" loading="lazy" decoding="async">')
    if not AFF_ENABLED:
        if img:
            img = f'<a class="aff-cover-link" href="{e(plain_url(r["url"]))}" target="_blank" rel="noopener">{img}</a>'
        return (f"        <li class=\"aff-item\" data-amz=\"{e(_strip_tag(amz))}\">" + img
                + "<div class=\"aff-main\"><span class=\"aff-name\">" + e(name) + "</span></div></li>")
    return ("        <li class=\"aff-item\">" + img
            + "<div class=\"aff-main\"><span class=\"aff-name\">" + e(name) + "</span>"
            + "<div class=\"aff-btns\">"
            + f'<a class="aff-btn" href="{e(_with_tag(amz))}" target="_blank" rel="sponsored noopener">Amazonで見る</a>'
            + f'<a class="aff-btn aff-btn-rakuten" href="{e(r["url"])}" target="_blank" rel="sponsored noopener">楽天で見る</a>'
            + "</div></div></li>")


def _amz_of(li):
    m = re.search(r'href="(https://www\.amazon\.co\.jp/[^"]+)"', li) or re.search(r'data-amz="([^"]+)"', li)
    return m


def _pr_note(s):
    if AFF_ENABLED:
        return s.replace("<!-- PRNOTE -->", PR_NOTE)
    return s.replace(PR_NOTE, "<!-- PRNOTE -->")


def build(root, read, write):
    files = ["articles/" + f for f in sorted(os.listdir(os.path.join(root, "articles"))) if f.endswith(".html")]
    for rel in files:
        s = read(rel)
        m = re.search(r'(<div class="aff-box">.*?<ul>)(.*?)(</ul>)(.*?)(</div>)', s, re.S)
        if not m:
            continue
        rows = []
        for li in re.findall(r"<li\b.*?</li>", m.group(2), re.S):
            nm = re.search(r'<span class="aff-name">(.*?)</span>', li, re.S)
            am = _amz_of(li)
            if not (nm and am):
                continue
            name = html.unescape(re.sub(r"<[^>]+>", "", nm.group(1))).strip()
            rows.append((name, html.unescape(am.group(1))))
        out = [_row_html(name, amz, rakuten.lookup(name, amz)) for name, amz in rows]
        tail = re.sub(r'\s*<p class="aff-disclosure">.*?</p>', '', m.group(4), flags=re.S)
        if AFF_ENABLED:
            tail = f'\n      <p class="aff-disclosure">{AFF_DISCLOSURE}</p>' + tail
        new = m.group(1) + "\n" + "\n".join(out) + "\n      " + m.group(3) + tail + m.group(5)
        s2 = _pr_note(s[:m.start()] + new + s[m.end():])
        if s2 != s:
            write(rel, s2)
    rakuten.save_cache()


# ---------------------------------------------------------------- 本文中の表紙
COVER_RE = re.compile(r'<!-- COVER:(.*?) -->(.*?)<!-- /COVER -->', re.S)


def _core(text):
    t = re.sub(r"[（(].*?[)）]", "", text)
    t = re.sub(rakuten.EDITION, "", t)
    t = re.sub(r"[\s・／/［\[\]］〔〕「」『』:：,，.。\-－｜|]", "", t).lower()
    return t


# 本文中の表紙のリンク。AFF_ENABLED が False のあいだは楽天の通常の商品ページへのリンクにする。
INLINE_AFF_LINKS = True


def _cover_html(name, r):
    e = lambda x: html.escape(x, quote=True)
    if not (AFF_ENABLED and INLINE_AFF_LINKS):
        return (f'<a class="inline-cover" href="{e(plain_url(r["url"]))}" target="_blank" rel="noopener">'
                f'<img src="{e(r["image"].replace("_ex=200x200", "_ex=400x400"))}" alt="{e(name)}の表紙" '
                f'width="200" height="284" loading="lazy" decoding="async"></a>')
    return (f'<a class="inline-cover" href="{e(r["url"])}" target="_blank" rel="sponsored noopener" '
            f'aria-label="{e(name)}を楽天で見る"><img src="{e(r["image"].replace("_ex=200x200", "_ex=400x400"))}" alt="{e(name)}の表紙" '
            f'width="200" height="284" loading="lazy" decoding="async"><span>楽天で見る</span></a>')


def _place_markers(s, entries):
    """初回だけ、各本を紹介している見出しの直後に表紙の目印を置く"""
    body_start = s.index('<div class="article-body">')
    body_end = s.index('<div class="aff-box">') if '<div class="aff-box">' in s else s.index('<div class="diag-cta">')
    body = s[body_start:body_end]
    heads = [(m.start(), m.end(), _core(re.sub(r"<[^>]+>", "", m.group(2)))) for m in re.finditer(r"<(h2|h3)>(.*?)</\1>", body, re.S)]
    inserts, used = [], set()
    for name, key in entries:
        c = _core(name)
        if len(c) < 3:
            continue
        probe = c[:6]
        for hs, he, ht in heads:
            if he in used:
                continue
            if probe in ht or (len(ht) >= 6 and ht[:6] in c):
                inserts.append((he, key)); used.add(he)
                break
    if not inserts and entries:  # 1冊の解説記事：基本情報の表（なければ最初の段落）の直後に置く
        m = re.search(r'</table>\s*</div>', body) or re.search(r"</p>", body)
        if m:
            inserts.append((m.end(), entries[0][1]))
    for pos, key in sorted(inserts, reverse=True):
        body = body[:pos] + f"\n    <!-- COVER:{key} --><!-- /COVER -->" + body[pos:]
    return s[:body_start] + body + s[body_end:]


def build_inline(root, read, write):
    files = ["articles/" + f for f in sorted(os.listdir(os.path.join(root, "articles"))) if f.endswith(".html")]
    for rel in files:
        s = read(rel)
        m = re.search(r'<div class="aff-box">.*?<ul>(.*?)</ul>', s, re.S)
        if not m:
            continue
        entries, info = [], {}
        for li in re.findall(r"<li\b.*?</li>", m.group(1), re.S):
            nm = re.search(r'<span class="aff-name">(.*?)</span>', li, re.S)
            am = _amz_of(li)
            if not (nm and am):
                continue
            name = html.unescape(re.sub(r"<[^>]+>", "", nm.group(1))).strip()
            r = rakuten.lookup(name, html.unescape(am.group(1)))
            if r["image"]:
                key = _core(name)[:24]
                entries.append((name, key)); info[key] = (name, r)
        if not entries:
            continue
        if "<!-- COVER:" not in s and "<!-- NOCOVER -->" not in s:
            s = _place_markers(s, entries)
        s2 = COVER_RE.sub(lambda mm: f"<!-- COVER:{mm.group(1)} -->" + (_cover_html(*info[mm.group(1)]) if mm.group(1) in info else "") + "<!-- /COVER -->", s)
        if s2 != read(rel):
            write(rel, s2)


AFF_NOTE = "※Amazonのアソシエイトとして、当メンバーは適格販売により収入を得ています。当サイトは楽天アフィリエイトに参加しています。"


def _diag_note(s):
    if AFF_ENABLED:
        return re.sub(r"<!-- AFFNOTE:(.*?) -->", lambda m: "<br>\n      " + m.group(1), s)
    return re.sub(r"<br>\s*(※Amazonのアソシエイトとして、当メンバーは適格販売により収入を得ています。(?:当サイトは楽天アフィリエイトに参加しています。)?)",
                  lambda m: f"<!-- AFFNOTE:{m.group(1)} -->", s)


BL_DISC_RE = re.compile(r'<p class="aff-disclosure bl-disclosure">(.*?)</p>', re.S)


def bibo_toggle(s):
    """備忘録の本文中に手書きされたAmazonリンクと開示文の出し入れ"""
    if AFF_ENABLED:
        s = re.sub(r"<!-- BLDISC:(.*?) -->", r'<p class="aff-disclosure bl-disclosure">\1</p>', s, flags=re.S)
        s = re.sub(r"<!-- BLGO:(.*?) -->", r'<a class="bl-go" href="\1" target="_blank" rel="sponsored noopener">Amazonで見る →</a>', s)
        s = re.sub(r'<span class="bl-name" data-amz="([^"]+)">(.*?)</span>',
                   r'<a class="bl-name" href="\1" target="_blank" rel="sponsored noopener">\2</a>', s, flags=re.S)
        return s
    s = BL_DISC_RE.sub(lambda m: f"<!-- BLDISC:{m.group(1)} -->", s)
    s = re.sub(r'<a class="bl-go" href="(https://www\.amazon\.co\.jp/[^"]+)"[^>]*>Amazonで見る →</a>', r"<!-- BLGO:\1 -->", s)
    s = re.sub(r'<a class="bl-name" href="(https://www\.amazon\.co\.jp/[^"]+)"[^>]*>(.*?)</a>',
               r'<span class="bl-name" data-amz="\1">\2</span>', s, flags=re.S)
    return s


# ---------------------------------------------------------------- 数学診断の結果カード
def build_diag(root, read, write, rel="sugaku-shindan.html"):
    import json as _json
    s = orig = read(rel)
    covers = {}
    for name, asin in re.findall(r'\{name:"([^"]+)",note:"[^"]*",(?:asin:"([^"]*)")?', s):
        if name.startswith("志望大学の過去問"):
            continue  # 特定の本ではないので表紙も楽天リンクも付けない
        amz = (f"https://www.amazon.co.jp/dp/{asin}" if asin
               else "https://www.amazon.co.jp/s?k=" + rakuten.urllib.parse.quote(name))
        if "予想問題集" in name:  # 予備校ごとに何冊も出ている本なので、1冊の表紙は出さず楽天の検索結果へ
            covers[name] = {"i": "", "u": cover_url({"url": rakuten.search_link(re.sub(r"[（）]", " ", name).replace("・", " "))})}
            continue
        r = rakuten.lookup(name, amz)
        covers[name] = {"i": r["image"], "u": cover_url(r)}
    s = _diag_note(s)
    blob = "const AFF_ON = " + ("true" if AFF_ENABLED else "false") + "; const COVERS = " + _json.dumps(covers, ensure_ascii=False, separators=(",", ":")) + ";"
    s2 = re.sub(r"/\* COVERS:BEGIN \*/.*?/\* COVERS:END \*/", lambda _: "/* COVERS:BEGIN */" + blob + "/* COVERS:END */", s, flags=re.S)
    if s2 != orig:
        write(rel, s2)
    rakuten.save_cache()
    return sum(1 for v in covers.values() if v["i"]), len(covers)
