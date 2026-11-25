#!/usr/bin/env python3
"""从 index.html 的 EVENTS + data/*.json 生成静态详情页。"""
import re, json, pathlib, html, datetime

ROOT = pathlib.Path(__file__).resolve().parent
src = (ROOT / "index.html").read_text(encoding="utf-8")
body = re.search(r"const EVENTS=\[(.*?)\n\];", src, re.S).group(1)
EV = {}
for blk in re.split(r"\n \{id:", body):
    blk = blk.strip()
    if not blk[:1].isdigit():
        continue
    i = int(blk.split(",", 1)[0])
    def g(k, _b=blk):
        return re.search(k + r':"((?:[^"\\]|\\.)*)"', _b).group(1)
    EV[i] = dict(id=i, s=g("s"), img=g("img"), t=g("t"), m=g("m"), tag=g("tag"))

BODIES = json.loads((ROOT / "data/bodies.json").read_text(encoding="utf-8"))
SRC = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
ORDER = sorted(int(k) for k in BODIES)

CSS = """
:root{--pape:#F7F4EE;--ink:#141414;--mid:#6B6B6B;--line:#DED8CB;--accent:#D8F33A}
*{box-sizing:border-box}
body{margin:0;background:var(--pape);color:var(--ink);
 font:16px/1.85 -apple-system,"PingFang SC","Hiragino Sans GB",system-ui,sans-serif}
a{color:inherit}
.top{display:flex;justify-content:space-between;align-items:center;padding:18px 26px;
 border-bottom:1px solid var(--line);font-size:13px}
.top .b{letter-spacing:.22em;font-weight:700;font-size:12px}
.top a{text-decoration:none;color:var(--mid)}
.top a:hover{color:var(--ink)}
.wrap{max-width:700px;margin:0 auto;padding:54px 26px 90px}
.no{font:12px/1 ui-monospace,Menlo,monospace;letter-spacing:.18em;color:var(--mid)}
h1{font-size:34px;line-height:1.35;margin:14px 0 10px;font-weight:700;letter-spacing:-.01em}
.meta{font:12.5px/1.7 ui-monospace,Menlo,monospace;color:var(--mid);
 padding-bottom:22px;border-bottom:1px solid var(--line)}
.lead{margin:26px 0 0;font-size:19px;line-height:1.75;color:#2a2a2a}
.hero{width:180px;float:right;margin:6px 0 18px 26px}
.hero img{width:100%;height:auto;display:block}
p{margin:18px 0;text-align:justify}
h2{font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--mid);
 margin:48px 0 14px;font-weight:600}
ol.src{padding-left:20px;margin:0}
ol.src li{margin:10px 0;font-size:14.5px;line-height:1.7}
ol.src a{text-decoration:none;border-bottom:1px solid var(--line)}
ol.src a:hover{border-color:var(--ink)}
.tag{display:inline-block;margin-top:26px;padding:4px 12px;border-radius:999px;
 background:var(--accent);font-size:12.5px;font-weight:600}
.nav{display:flex;justify-content:space-between;gap:16px;margin-top:56px;
 padding-top:26px;border-top:1px solid var(--line);font-size:14px}
.nav a{text-decoration:none;max-width:46%}
.nav a:hover{text-decoration:underline}
.nav .r{text-align:right;margin-left:auto}
.foot{margin-top:60px;font-size:12px;color:var(--mid);line-height:1.9}
@media(max-width:640px){.hero{float:none;width:140px;margin:0 0 16px}h1{font-size:26px}}
"""

def page(i):
    e = EV[i]
    ps = BODIES[str(i)]
    n = ORDER.index(i)
    prev_id = ORDER[n - 1] if n > 0 else None
    next_id = ORDER[n + 1] if n < len(ORDER) - 1 else None
    srcs = "".join(
        f'<li><a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(t)}</a></li>'
        for t, u in SRC[str(i)])
    paras = "".join(f"<p>{html.escape(x)}</p>" for x in ps[1:])
    lead = html.escape(ps[0])
    nav = ""
    if prev_id:
        nav += f'<a href="{prev_id}.html">← {html.escape(EV[prev_id]["t"])}</a>'
    if next_id:
        nav += f'<a class="r" href="{next_id}.html">{html.escape(EV[next_id]["t"])} →</a>'
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(e['t'])} · Drama Court</title>
<meta name="description" content="{html.escape(ps[0][:90])}">
<style>{CSS}</style></head><body>
<div class="top"><span class="b">DRAMA COURT</span><a href="../index.html">← 回到球场</a></div>
<div class="wrap">
  <div class="no">CASE #{i:03d}</div>
  <h1>{html.escape(e['t'])}</h1>
  <div class="meta">{html.escape(e['m'])}</div>
  <div class="hero"><img src="../assets/{e['img']}.webp" alt=""></div>
  <p class="lead">{lead}</p>
  {paras}
  <span class="tag">{html.escape(e['tag'])}</span>
  <h2>出处</h2><ol class="src">{srcs}</ol>
  <div class="nav">{nav}</div>
  <div class="foot">本页为个人整理的非官方档案。事件描述基于上方公开报道，图片为二次创作插画，
  不对应任何官方影像。若发现事实错误，欢迎指出。</div>
</div></body></html>"""

def index_page():
    items = "".join(
        f'<li><a href="{i}.html"><span class="n">{i:03d}</span>'
        f'<span class="t">{html.escape(EV[i]["t"])}</span>'
        f'<span class="m">{html.escape(EV[i]["m"])}</span></a></li>' for i in ORDER)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>红土册 · Drama Court</title><style>{CSS}
ul.list{{list-style:none;padding:0;margin:28px 0}}
ul.list li{{border-bottom:1px solid var(--line)}}
ul.list a{{display:grid;grid-template-columns:52px 1fr;gap:6px 14px;padding:16px 0;text-decoration:none}}
ul.list .n{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--mid)}}
ul.list .t{{font-size:16.5px;line-height:1.5}}
ul.list .m{{grid-column:2;font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--mid)}}
ul.list a:hover .t{{text-decoration:underline}}
</style></head><body>
<div class="top"><span class="b">DRAMA COURT</span><a href="../index.html">← 回到球场</a></div>
<div class="wrap"><div class="no">红土册 · {len(ORDER)} 条</div>
<h1>红土场上发生过的事</h1>
<div class="meta">每条都附至少两个可点击出处</div>
<ul class="list">{items}</ul></div></body></html>"""

out = ROOT / "cases"; out.mkdir(exist_ok=True)
for i in ORDER:
    (out / f"{i}.html").write_text(page(i), encoding="utf-8")
(out / "index.html").write_text(index_page(), encoding="utf-8")
print(f"生成 {len(ORDER)} 个详情页 + 1 个索引页 → cases/")
