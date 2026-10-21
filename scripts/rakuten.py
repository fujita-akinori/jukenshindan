"""
楽天ブックスAPIから表紙画像とアフィリエイトリンクを取得し、data/rakuten-cache.json に保存する。

- APIキーはリポジトリに置かず、環境変数で渡す:
    RAKUTEN_APP_ID / RAKUTEN_ACCESS_KEY / RAKUTEN_AFFILIATE_ID
  （作業環境では ~/.rakuten.env を読み込む）
- キーがない環境でもビルドは通る。その場合はキャッシュ済みの本だけ表紙が付く。
- キャッシュには画像URLとアフィリエイトリンクだけが入る（キーは入らない）。
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(ROOT, "data", "rakuten-cache.json")
API = "https://openapi.rakuten.co.jp/services/api"
REFERER = "https://jukenshindan.com/"


def _load_env():
    env = {k: os.environ.get(k) for k in ("RAKUTEN_APP_ID", "RAKUTEN_ACCESS_KEY", "RAKUTEN_AFFILIATE_ID")}
    cands = [os.path.expanduser("~/.rakuten.env"), os.path.join(os.path.dirname(ROOT), ".rakuten.env")]
    p = next((c for c in cands if os.path.exists(c)), "")
    if not all(env.values()) and p:
        for line in open(p, encoding="utf-8"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                env.setdefault(k, v)
                if not env.get(k):
                    env[k] = v
    return env


ENV = _load_env()
HAS_KEY = all(ENV.values())
AFFILIATE_ID = ENV.get("RAKUTEN_AFFILIATE_ID") or "58abd59b.2a7aebd9.58abd59c.6bc494c1"  # 公開されるIDなのでキャッシュがなくても使う

_cache = None
_last_call = 0.0


def cache():
    global _cache
    if _cache is None:
        _cache = json.load(open(CACHE_PATH, encoding="utf-8")) if os.path.exists(CACHE_PATH) else {}
    return _cache


def save_cache():
    if _cache is None:
        return
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(_cache, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def _call(path, **params):
    global _last_call
    wait = 1.1 - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    params.update(format="json", formatVersion=2, applicationId=ENV["RAKUTEN_APP_ID"],
                  accessKey=ENV["RAKUTEN_ACCESS_KEY"], affiliateId=ENV["RAKUTEN_AFFILIATE_ID"])
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Referer": REFERER, "Origin": REFERER.rstrip("/")})
    _last_call = time.time()
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def isbn10_to_13(a):
    if not re.fullmatch(r"\d{9}[\dX]", a):
        return None
    c = "978" + a[:9]
    t = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(c))
    return c + str((10 - t % 10) % 10)


def _norm(s):
    s = re.sub(r"[（(].*?[)）]", "", s)
    return re.sub(r"[\s・／/［\[\]］〔〕「」『』:：,，.。\-－]", "", s).lower()


def _plausible(name, title, author=""):
    """キーワード検索の結果が本当にその本かを判定する"""
    n, t = _norm(name), _norm(title)
    core = n[:6] if len(n) >= 6 else n
    if not core or not (core in t or t[:6] in n):
        return False
    if "中学" in title and "中学" not in name:
        return False
    m = re.search(r"[（(]([^）)]+)[)）]", name)  # 名前の括弧書きが人名なら、著者と一致するか確かめる
    if m and author and not re.search(r"版|出版|社|塾|系|編|学習|河合|駿台|東進", m.group(1)):
        if _norm(m.group(1))[:3] not in _norm(author):
            return False
    return True


def _pick(item):
    img = item.get("largeImageUrl") or item.get("mediumImageUrl") or ""
    if "noimage" in img:
        img = ""
    return {"title": item.get("title", ""), "image": img, "url": item.get("affiliateUrl") or item.get("itemUrl", "")}


EDITION = r"(新装|新課程|新訂|改訂第?\d*|[一二三四五六七八九十0-9]+訂|第?\d+版|\d+th Edition|[0-9]{4})版?"


def _keywords(name, query):
    """検索語の候補。版の表記や括弧書きを外したものも順に試す"""
    base = re.sub(r"[（(].*?[)）]", " ", name)
    cands = [query, name, re.sub(EDITION, " ", base), re.sub(EDITION, " ", re.sub(r"[［\[〔].*?[\]］〕]", " ", base))]
    out = []
    for c in cands:
        if c:
            c = re.sub(r"\s+", " ", c.replace("・", " ").replace("／", " ")).strip()
            if c and c not in out:
                out.append(c)
    return out


def search_link(keyword):
    target = "https://books.rakuten.co.jp/search?sitem=" + urllib.parse.quote(keyword)
    return f"https://hb.afl.rakuten.co.jp/hgc/{AFFILIATE_ID}/?pc={urllib.parse.quote(target, safe='')}"


def lookup(name, amazon_url):
    """記事の紹介枠の1行（本の名前とAmazonのURL）から、楽天の表紙とリンクを返す"""
    m = re.search(r"/dp/([0-9X]{10})", amazon_url)
    isbn = isbn10_to_13(m.group(1)) if m else None
    if isbn:
        key = "isbn:" + isbn
    else:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(amazon_url).query).get("k", [name])[0]
        key = "q:" + q
    c = cache()
    if key in c:
        return c[key]
    if not HAS_KEY:
        return {"title": "", "image": "", "url": search_link(name if isbn else key[2:])}
    res = {"title": "", "image": "", "url": ""}
    try:
        if "シリーズ" in name:
            pass  # シリーズ全体へのリンクは、特定の巻の表紙を出すと誤解を招くので画像なし
        else:
            if isbn:
                d = _call("BooksBook/Search/20170404", isbn=isbn)
                items = d.get("Items") or []
                if items:
                    res = _pick(items[0].get("Item", items[0]))
            if not res["url"] and not isbn:  # ISBNで見つからない本は、別の巻を拾わないよう名前では探さない
                for kw in _keywords(name, key[2:]):
                    d = _call("BooksTotal/Search/20170404", keyword=kw, booksGenreId="001", hits=5)
                    hit = next((it.get("Item", it) for it in d.get("Items") or [] if _plausible(name, it.get("Item", it).get("title", ""), it.get("Item", it).get("author", ""))), None)
                    if hit:
                        res = _pick(hit)
                        break
    except Exception as e:  # 通信エラーはキャッシュせず、次回もう一度試す
        print("  楽天API エラー:", name, e)
        return {"title": "", "image": "", "url": search_link(name)}
    if not res["url"]:
        res["url"] = search_link(name if isbn else key[2:])
    c[key] = res
    return res
