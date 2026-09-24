#!/usr/bin/env python3
from pathlib import Path
import json, html, re, os
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "site.json").read_text("utf-8"))
SITE_BASE = os.getenv("SITE_BASE", "https://campanhasupernow-rgb.github.io/sitescs").rstrip("/")

for d in ("news", "teams", "players", "tournaments", "matches"):
    (ROOT / d).mkdir(parents=True, exist_ok=True)

def slug(value):
    value = value.lower().strip()
    for a, b in {"á":"a","à":"a","ã":"a","â":"a","é":"e","ê":"e","í":"i","ó":"o","ô":"o","õ":"o","ú":"u","ç":"c"}.items():
        value = value.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")

def shell(title, body, lang="en-US", desc="Counter-Strike 2 portal", prefix=""):
    pt = lang.startswith("pt")
    k = "pt" if pt else "en"
    brand = "CS2 NOTÍCIAS" if pt else "CS2NEWS"
    home = f"{prefix}{'cs2noticias' if pt else 'cs2news'}/"
    switch = f"{prefix}{'cs2news' if pt else 'cs2noticias'}/"
    switch_label = "🇺🇸 EN" if pt else "🇧🇷 PT"
    nav_labels = ("Notícias","Partidas","Campeonatos","Ranking","Times","Jogadores") if pt else ("News","Matches","Tournaments","Rankings","Teams","Players")
    nav_targets = (
        f"{prefix}news-{k}.html",
        f"{home}#matches-sec",
        f"{prefix}tournaments-{k}.html",
        f"{prefix}rankings-{k}.html",
        f"{prefix}teams-{k}.html",
        f"{prefix}players-{k}.html",
    )
    navhtml = "".join(f'<a href="{u}">{n}</a>' for n, u in zip(nav_labels, nav_targets))
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="stylesheet" href="{prefix}assets/styles.css"></head><body><div class="topline"></div><header class="header"><div class="wrap headrow"><a class="brand" href="{home}"><span class="brandmark">2</span>{html.escape(brand)}</a><nav class="nav">{navhtml}</nav><div class="actions"><a class="pill" href="{switch}">{switch_label}</a></div></div></header><main class="wrap main">{body}</main><footer class="footer"><div class="wrap"><span class="source">Independent CS2 news & data portal.</span></div></footer></body></html>'''

teams = ["FURIA","Team Liquid","M80","NRG","Vitality","Spirit","MOUZ","Falcons","G2","Natus Vincere","Legacy","paiN","MIBR"]
players = ["FalleN","KSCERATO","yuurih","donk","m0NESY","ZywOo","s1mple","NiKo","ropz"]

for lang in ("pt-BR", "en-US"):
    k = "pt" if lang.startswith("pt") else "en"

    title = "Ranking CS2 da Valve" if k == "pt" else "Valve CS2 Rankings"
    rows = "".join(
        f'<tr><td class="rank">{r["rank"]}</td><td><b>{html.escape(r["team"])}</b></td><td>{r["points"]}</td><td>{html.escape(r.get("region","Global"))}</td></tr>'
        for r in DATA.get("rankings", [])
    )
    body = f'<h1>{title}</h1><div class="card tablecard"><table class="table"><thead><tr><th>#</th><th>{"Time" if k=="pt" else "Team"}</th><th>{"Pontos" if k=="pt" else "Points"}</th><th>{"Região" if k=="pt" else "Region"}</th></tr></thead><tbody>{rows}</tbody></table></div>'
    (ROOT / f"rankings-{k}.html").write_text(shell(title, body, lang), "utf-8")

    news_cards = []
    news_source = DATA.get("news_pt", []) if k == "pt" else DATA.get("news", [])
    for n in news_source:
        if k == "pt":
            category = n.get("category", "")
            title_value = n.get("title", "")
            summary_value = n.get("summary", "")
        else:
            category = (n.get("category") or {}).get("en", "")
            title_value = (n.get("title") or {}).get("en", "")
            summary_value = (n.get("summary") or {}).get("en", "")
        if not title_value:
            continue
        s = slug(title_value)
        href = f'news/{s}-{k}.html'
        news_cards.append(
            f'<a class="card news" href="{href}"><span class="tag">{html.escape(category)}</span><h3>{html.escape(title_value)}</h3><p>{html.escape(summary_value)}</p><div class="meta"><span>{html.escape(n.get("date",""))}</span><span>{html.escape(n.get("source",""))}</span></div></a>'
        )
        article = f'<article class="card" style="padding:28px;max-width:900px;margin:auto"><span class="tag">{html.escape(category)}</span><h1>{html.escape(title_value)}</h1><div class="meta"><span>{html.escape(n.get("date",""))}</span><span>{html.escape(n.get("source",""))}</span></div><p>{html.escape(summary_value)}</p></article>'
        (ROOT / "news" / f"{s}-{k}.html").write_text(
            shell(title_value, article, lang, summary_value, prefix="../"),
            "utf-8",
        )
    title = "Últimas notícias de CS2" if k == "pt" else "Latest CS2 News"
    (ROOT / f"news-{k}.html").write_text(
        shell(title, f'<h1>{title}</h1><div class="newsgrid">{"".join(news_cards)}</div>', lang),
        "utf-8",
    )

    event_blocks = "".join(
        f'<div class="card" style="padding:22px"><span class="badge {"live" if e["status"]=="live" else "up"}">{("AO VIVO" if k=="pt" else "LIVE") if e["status"]=="live" else ("EM BREVE" if k=="pt" else "UPCOMING")}</span><h2>{html.escape(e["name"])}</h2><p>{html.escape(e["dates"][k])} · {html.escape(e.get("location","Online"))}</p></div>'
        for e in DATA.get("events", [])
    )
    title = "Campeonatos de CS2" if k == "pt" else "CS2 Tournaments"
    (ROOT / f"tournaments-{k}.html").write_text(
        shell(title, f'<h1>{title}</h1><div class="rosters">{event_blocks}</div>', lang),
        "utf-8",
    )

    team_cards = "".join(
        f'<a class="card stat" href="teams/{slug(t)}-{k}.html"><b>{html.escape(t)}</b></a>'
        for t in teams
    )
    title = "Times de CS2" if k == "pt" else "CS2 Teams"
    (ROOT / f"teams-{k}.html").write_text(
        shell(title, f'<h1>{title}</h1><div class="statsgrid">{team_cards}</div>', lang),
        "utf-8",
    )
    for t in teams:
        body = f'<article class="card" style="padding:28px"><span class="tag">TEAM</span><h1>{html.escape(t)}</h1><p>{"Página preparada para roster, partidas, resultados, VRS e notícias." if k=="pt" else "Prepared for roster, matches, results, VRS and related news."}</p></article>'
        (ROOT / "teams" / f"{slug(t)}-{k}.html").write_text(shell(t, body, lang, prefix="../"), "utf-8")

    player_cards = "".join(
        f'<a class="card stat" href="players/{slug(p)}-{k}.html"><b>{html.escape(p)}</b></a>'
        for p in players
    )
    title = "Jogadores de CS2" if k == "pt" else "CS2 Players"
    (ROOT / f"players-{k}.html").write_text(
        shell(title, f'<h1>{title}</h1><div class="statsgrid">{player_cards}</div>', lang),
        "utf-8",
    )
    for p in players:
        body = f'<article class="card" style="padding:28px"><span class="tag">PLAYER</span><h1>{html.escape(p)}</h1><p>{"Página preparada para estatísticas, histórico e highlights." if k=="pt" else "Prepared for stats, history and highlights."}</p></article>'
        (ROOT / "players" / f"{slug(p)}-{k}.html").write_text(shell(p, body, lang, prefix="../"), "utf-8")

redirects = {
    "news/index.html": "../news-en.html",
    "teams/index.html": "../teams-en.html",
    "players/index.html": "../players-en.html",
    "tournaments/index.html": "../tournaments-en.html",
    "matches/index.html": "../cs2news/#matches-sec",
}
for path, target in redirects.items():
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f'<!doctype html><meta http-equiv="refresh" content="0;url={target}">', "utf-8")

urls = [
    "/cs2noticias/","/cs2news/",
    "/rankings-pt.html","/rankings-en.html",
    "/news-pt.html","/news-en.html",
    "/teams-pt.html","/teams-en.html",
    "/players-pt.html","/players-en.html",
    "/tournaments-pt.html","/tournaments-en.html",
]
for d in ("news", "teams", "players"):
    urls += [f"/{d}/{p.name}" for p in (ROOT / d).glob("*.html") if p.name != "index.html"]

now = datetime.now(timezone.utc).date().isoformat()
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    + "".join(f"<url><loc>{SITE_BASE}{u}</loc><lastmod>{now}</lastmod></url>" for u in urls)
    + "</urlset>",
    "utf-8",
)
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE}/sitemap.xml\n", "utf-8")
print("Built", len(urls), "routes")
