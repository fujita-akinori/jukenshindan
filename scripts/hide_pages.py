"""AdSense審査中だけ中身の薄いページを非公開にする／元に戻す

  python3 scripts/hide_pages.py hide     data/hidden.json のページを _hidden/ に移して非公開にする
  python3 scripts/hide_pages.py restore  _hidden/ のページをすべて元の場所に戻す

_ から始まるフォルダは GitHub Pages（Jekyll）で公開されないので、移したページは見えなくなる。
ほかのページからのリンクは消さずに目印付きのコメントにしておき、restore で元に戻す。
どちらも実行後に python3 scripts/build_site.py を実行してからコミットする。
"""
import glob
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HID = os.path.join(ROOT, "_hidden")
os.chdir(ROOT)


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    open(p, "w", encoding="utf-8").write(s)


def pages():
    return sorted(set(glob.glob("*.html") + glob.glob("articles/*.html") + glob.glob("biboroku/*.html")))


def href_re(rel):
    name = os.path.basename(rel)
    pre = r'(?:\.\./|/)?(?:articles/)?' if rel.startswith("articles/") else r'(?:\.\./|/)?'
    return pre + re.escape(name) + r'(?:#[^"]*)?'


def hide():
    cfg = json.load(open("data/hidden.json", encoding="utf-8"))
    targets = [f"articles/{s}" for s in cfg["articles"]] + cfg["pages"]
    targets = [t for t in targets if os.path.exists(t)]
    # 記事データの行を退避
    data = read("articles/articles-data.js")
    kept = []
    for slug in cfg["articles"]:
        m = re.search(r'\n[ \t]*\{ slug:"' + re.escape(slug) + r'".*?\},?(?=\n)', data)
        if m:
            kept.append(m.group(0).strip())
            data = data[:m.start()] + data[m.end():]
    write("articles/articles-data.js", data)
    old = json.load(open(f"{HID}/articles-data.json", encoding="utf-8")) if os.path.exists(f"{HID}/articles-data.json") else []
    os.makedirs(f"{HID}/articles", exist_ok=True)
    json.dump(old + kept, open(f"{HID}/articles-data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 移動
    for t in targets:
        shutil.move(t, os.path.join(HID, t))
    # 残るページからのリンクを目印付きコメントにする
    for p in pages():
        s = s0 = read(p)
        for t in targets:
            h = href_re(t)
            s = re.sub(r'<li\b[^>]*>\s*<a [^>]*href="' + h + r'"[^>]*>.*?</li>', lambda m: f"<!--HIDDEN{m.group(0)}HIDDEN-->", s, flags=re.S)
            def anchor(m):
                inner = m.group(0)
                if re.search(r"<(div|h\d|p|span)\b", inner):
                    return f"<!--HIDDEN{inner}HIDDEN-->"
                txt = re.sub(r"^<a [^>]*>|</a>$", "", inner, flags=re.S)
                return f'<span data-hidden-link="{re.sub(chr(34), "&quot;", inner)}">{txt}</span><!--/HL-->'
            # すでにコメントにした部分の中は触らない
            parts = re.split(r"(<!--HIDDEN.*?HIDDEN-->)", s, flags=re.S)
            s = "".join(x if x.startswith("<!--HIDDEN") else re.sub(r'<a [^>]*href="' + h + r'"[^>]*>.*?</a>', anchor, x, flags=re.S) for x in parts)
        if s != s0:
            write(p, s)
    # 診断の「解説記事を読む」の対応表から非公開の記事を外す
    for p in glob.glob("*-shindan.html"):
        d = d0 = read(p)
        for slug in cfg["articles"]:
            d = d.replace(':"' + slug[:-5] + '"', ':"" /*HIDDEN:' + slug[:-5] + '*/')
        if d != d0:
            write(p, d)
    nav = read("nav.js")
    for t in targets:
        nav = re.sub(r'^([ \t]*)(\[\s*"' + re.escape(os.path.basename(t)) + r'".*?\],?)$', r'\1/*HIDDEN\2HIDDEN*/', nav, flags=re.M)
    write("nav.js", nav)
    print(f"非公開にしました: {len(targets)} ページ")


def restore():
    moved = [os.path.relpath(p, HID) for p in glob.glob(f"{HID}/**/*.html", recursive=True)]
    for t in moved:
        os.makedirs(os.path.dirname(t) or ".", exist_ok=True)
        shutil.move(os.path.join(HID, t), t)
    if os.path.exists(f"{HID}/articles-data.json"):
        kept = json.load(open(f"{HID}/articles-data.json", encoding="utf-8"))
        data = read("articles/articles-data.js")
        i = data.index("\n];", data.index("const ARTICLES")) + 1
        head = data[:i].rstrip()
        if not head.endswith(","):
            head += ","
        data = head + "\n" + "\n".join("  " + k.rstrip(",") + "," for k in kept) + "\n" + data[i:]
        write("articles/articles-data.js", data)
        os.remove(f"{HID}/articles-data.json")
    for p in pages():
        s = s0 = read(p)
        s = re.sub(r"<!--HIDDEN(.*?)HIDDEN-->", r"\1", s, flags=re.S)
        s = re.sub(r'<span data-hidden-link="([^"]*)">.*?</span><!--/HL-->', lambda m: m.group(1).replace("&quot;", '"'), s, flags=re.S)
        if s != s0:
            write(p, s)
    for p in glob.glob("*-shindan.html"):
        d = read(p)
        d2 = re.sub(r':"" /\*HIDDEN:([a-z0-9-]+)\*/', r':"\1"', d)
        if d2 != d:
            write(p, d2)
    write("nav.js", re.sub(r"/\*HIDDEN(.*?)HIDDEN\*/", r"\1", read("nav.js")))
    print(f"元に戻しました: {len(moved)} ページ")


if __name__ == "__main__":
    {"hide": hide, "restore": restore}[sys.argv[1]]()
