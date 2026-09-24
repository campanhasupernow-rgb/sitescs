#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]
checked=0

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a" and a.get("href"): self.links.append(("href",a["href"]))
        if tag=="script" and a.get("src"): self.links.append(("asset",a["src"]))
        if tag=="link" and a.get("rel")=="stylesheet" and a.get("href"): self.links.append(("asset",a["href"]))

required=["index.html","cs2noticias/index.html","cs2news/index.html","news-pt.html","news-en.html","rankings-pt.html","rankings-en.html","teams-pt.html","teams-en.html","players-pt.html","players-en.html","tournaments-pt.html","tournaments-en.html","matches/pt.html","matches/en.html","rosters/pt.html","rosters/en.html","privacy/pt.html","privacy/en.html","advertise/pt.html","advertise/en.html","search/pt.html","search/en.html","sitemap.xml","robots.txt","data/search-pt.json","data/search-en.json"]
for r in required:
    if not (ROOT/r).exists(): errors.append("missing required: "+r)

data=json.loads((ROOT/"data/site.json").read_text("utf-8"))
if len(data.get("rankings",[]))<50: errors.append("ranking dataset too small")
if not data.get("ranking_date"): errors.append("missing ranking_date")
if not data.get("news") or not data.get("news_pt"): errors.append("missing bilingual news feeds")

for path in ROOT.rglob("*.html"):
    if ".git" in path.parts: continue
    checked+=1
    text=path.read_text("utf-8",errors="replace")
    if "<title>" not in text: errors.append(f"{path.relative_to(ROOT)} missing title")
    if path.name!="index.html" and 'name="viewport"' not in text: errors.append(f"{path.relative_to(ROOT)} missing viewport")
    if "${" in text or "{{" in text: errors.append(f"{path.relative_to(ROOT)} contains unresolved template")
    parser=P()
    try: parser.feed(text)
    except Exception as e: errors.append(f"{path.relative_to(ROOT)} parse error: {e}"); continue
    for kind,link in parser.links:
        if not link or link.startswith(("#","mailto:","javascript:","data:")): continue
        u=urlparse(link)
        if u.scheme in ("http","https"): continue
        clean=link.split("#",1)[0].split("?",1)[0]
        if not clean: continue
        target=(path.parent/clean).resolve()
        try: target.relative_to(ROOT.resolve())
        except ValueError: continue
        if clean.endswith("/"): target=target/"index.html"
        if not target.exists(): errors.append(f"{path.relative_to(ROOT)} broken {kind}: {link}")

for p in ("data/search-pt.json","data/search-en.json"):
    try:
        arr=json.loads((ROOT/p).read_text("utf-8"))
        if len(arr)<100: errors.append(f"{p} search index too small")
    except Exception as e: errors.append(f"{p} invalid json: {e}")

if errors:
    print("VALIDATION FAILED")
    for e in errors[:100]: print("-",e)
    print("Total errors:",len(errors))
    sys.exit(1)
print(f"VALIDATION OK: {checked} HTML files; {len(data.get('rankings',[]))} ranked teams")
