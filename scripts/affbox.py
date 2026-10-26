"""記事末尾の「紹介した参考書」枠に、楽天の表紙画像と「楽天で見る」ボタンを付ける"""
import html
import os
import re

import rakuten

AFF_DISCLOSURE = "Amazonのアソシエイトとして、当メンバーは適格販売により収入を得ています。当サイトは楽天アフィリエイトに参加しています。"


def _row_html(name, amz, r):
    e = lambda x: html.escape(x, quote=True)
    if r["image"]:
        img = (f'<img class="aff-cover" src="{e(r["image"])}" alt="{e(name)}の表紙" '
               f'width="64" height="90" loading="lazy" decoding="async">')
    else:
        img = ''
    return ("        <li class=\"aff-item\">" + img
            + "<div class=\"aff-main\"><span class=\"aff-name\">" + e(name) + "</span>"
            + "<div class=\"aff-btns\">"
            + f'<a class="aff-btn" href="{e(amz)}" target="_blank" rel="sponsored noopener">Amazonで見る</a>'
            + f'<a class="aff-btn aff-btn-rakuten" href="{e(r["url"])}" target="_blank" rel="sponsored noopener">楽天で見る</a>'
            + "</div></div></li>")


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
            am = re.search(r'href="(https://www\.amazon\.co\.jp/[^"]+)"', li)
            if not (nm and am):
                continue
            name = html.unescape(re.sub(r"<[^>]+>", "", nm.group(1))).strip()
            rows.append((name, html.unescape(am.group(1))))
        out = [_row_html(name, amz, rakuten.lookup(name, amz)) for name, amz in rows]
        tail = re.sub(r'<p class="aff-disclosure">.*?</p>', f'<p class="aff-disclosure">{AFF_DISCLOSURE}</p>', m.group(4), flags=re.S)
        new = m.group(1) + "\n" + "\n".join(out) + "\n      " + m.group(3) + tail + m.group(5)
        s2 = s[:m.start()] + new + s[m.end():]
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


# AdSense審査中は本文中の表紙をリンクにしない（記事末の「紹介した参考書」だけにリンクを置く）。
# 承認後に True に戻せば本文中の表紙も楽天へのリンクに戻る。
INLINE_AFF_LINKS = False


def _cover_html(name, r):
    e = lambda x: html.escape(x, quote=True)
    if not INLINE_AFF_LINKS:
        return (f'<span class="inline-cover"><img src="{e(r["image"].replace("_ex=200x200", "_ex=400x400"))}" alt="{e(name)}の表紙" '
                f'width="200" height="284" loading="lazy" decoding="async"></span>')
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
            am = re.search(r'href="(https://www\.amazon\.co\.jp/[^"]+)"', li)
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


# ---------------------------------------------------------------- 数学診断の結果カード
def build_diag(root, read, write, rel="sugaku-shindan.html"):
    import json as _json
    s = read(rel)
    covers = {}
    for name, asin in re.findall(r'\{name:"([^"]+)",note:"[^"]*",(?:asin:"([^"]*)")?', s):
        if name.startswith("志望大学の過去問"):
            continue  # 特定の本ではないので表紙も楽天リンクも付けない
        amz = (f"https://www.amazon.co.jp/dp/{asin}" if asin
               else "https://www.amazon.co.jp/s?k=" + rakuten.urllib.parse.quote(name))
        if "予想問題集" in name:  # 予備校ごとに何冊も出ている本なので、1冊の表紙は出さず楽天の検索結果へ
            covers[name] = {"i": "", "u": rakuten.search_link(re.sub(r"[（）]", " ", name).replace("・", " "))}
            continue
        r = rakuten.lookup(name, amz)
        covers[name] = {"i": r["image"], "u": r["url"]}
    blob = "const COVERS = " + _json.dumps(covers, ensure_ascii=False, separators=(",", ":")) + ";"
    s2 = re.sub(r"/\* COVERS:BEGIN \*/.*?/\* COVERS:END \*/", lambda _: "/* COVERS:BEGIN */" + blob + "/* COVERS:END */", s, flags=re.S)
    if s2 != s:
        write(rel, s2)
    rakuten.save_cache()
    return sum(1 for v in covers.values() if v["i"]), len(covers)
