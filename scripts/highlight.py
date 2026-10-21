"""各章の大事な1文を太字＋マーカーにする（流し読みする人向け）。対象の文は data/highlights.json で管理する。"""
import html
import json
import os
import re

TAG = re.compile(r"<[^>]+>")


def _plain(x):
    return html.unescape(TAG.sub("", x)).strip()


def _wrap_in_p(inner, sentence):
    """<p>の中身を「。」で区切り、目的の1文だけを <strong class="hl"> で囲む"""
    pieces = re.split(r"(?<=。)", inner)
    for i, pc in enumerate(pieces):
        if _plain(pc) == sentence.strip() and pc.count("<") % 2 == 0:
            lead = re.match(r"\s*", pc).group(0)
            body = pc[len(lead):]
            if body.count("<a") != body.count("</a>") or body.count("<strong") != body.count("</strong>"):
                return None
            pieces[i] = f'{lead}<strong class="hl">{body}</strong>'
            return "".join(pieces)
    return None


def build(root, read, write):
    path = os.path.join(root, "data", "highlights.json")
    if not os.path.exists(path):
        return 0, []
    data = json.load(open(path, encoding="utf-8"))
    done, missing = 0, []
    for slug, sentences in data.items():
        rel = "articles/" + slug
        if not os.path.exists(os.path.join(root, rel)):
            continue
        s = read(rel)
        start = s.index('<div class="article-body">')
        for sent in sentences:
            ok = False
            for m in re.finditer(r"<p>(.*?)</p>", s[start:], re.S):
                if sent.strip() not in _plain(m.group(1)):
                    continue
                inner = m.group(1)
                if any(_plain(inner[k.end():]).startswith(sent.strip()) for k in re.finditer(r'<strong class="hl">', inner)):
                    ok = True
                    break
                new = _wrap_in_p(m.group(1), sent)
                if new is not None:
                    a, b = start + m.start(1), start + m.end(1)
                    s = s[:a] + new + s[b:]
                    ok = True
                    break
            if ok:
                done += 1
            else:
                missing.append((slug, sent))
        if s != read(rel):
            write(rel, s)
    return done, missing
