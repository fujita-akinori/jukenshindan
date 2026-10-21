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
