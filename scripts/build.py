#!/usr/bin/env python3
from pathlib import Path
import html, json, os, re
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/"data/site.json").read_text("utf-8"))
SITE_BASE=os.getenv("SITE_BASE","https://campanhasupernow-rgb.github.io/sitescs").rstrip("/")
CONTACT="campanhasupernow@gmail.com"
for d in ("news","teams","players","tournaments","matches","about","privacy","editorial","advertise","contact","search","rosters"):
    (ROOT/d).mkdir(parents=True,exist_ok=True)

def esc(x): return html.escape(str(x or ""))
def slug(s):
    s=str(s).lower().strip()
    table=str.maketrans("áàãâäéêíóôõöúüçñ","aaaaaeeioooouucn")
    return re.sub(r"[^a-z0-9]+","-",s.translate(table)).strip("-")

def movement(r,pt=False):
    d=r.get("rank_delta") or 0
    if not r.get("previous_rank"): return "NEW" if not pt else "NOVO"
    if d>0:return f"▲ {d}"
    if d<0:return f"▼ {abs(d)}"
    return "—"

def shell(title,body,lang="en-US",desc="Counter-Strike 2 news and data portal",prefix="",canonical="",alternate=""):
    pt=lang.startswith("pt"); k="pt" if pt else "en"
    home=f"{prefix}{'cs2noticias' if pt else 'cs2news'}/"
    labels=("Notícias","Partidas","Campeonatos","Ranking","Times","Jogadores","Rosters") if pt else ("News","Matches","Tournaments","Rankings","Teams","Players","Rosters")
    hrefs=(f"{prefix}news-{k}.html",f"{prefix}matches/{k}.html",f"{prefix}tournaments-{k}.html",f"{prefix}rankings-{k}.html",f"{prefix}teams-{k}.html",f"{prefix}players-{k}.html",f"{prefix}rosters/{k}.html")
    nav="".join(f'<a href="{u}">{n}</a>' for n,u in zip(labels,hrefs))
    switch=f"{prefix}{'cs2news' if pt else 'cs2noticias'}/"
    canon=canonical or SITE_BASE+"/"; alt=alternate or canon
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="theme-color" content="#0b0d12"><link rel="canonical" href="{esc(canon)}"><link rel="alternate" hreflang="{'en-US' if pt else 'pt-BR'}" href="{esc(alt)}"><link rel="manifest" href="{prefix}site.webmanifest"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{esc(canon)}"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="{prefix}assets/styles.css"></head><body data-root="{prefix or '.'}"><div class="topline"></div><header class="header"><div class="wrap headrow"><a class="brand" href="{home}"><span class="brandmark">2</span><span>CS2</span><em>{' NOTÍCIAS' if pt else 'NEWS'}</em></a><nav class="nav">{nav}</nav><div class="actions"><a class="iconbtn" href="{prefix}search/{k}.html" aria-label="Search">⌕</a><a class="pill" href="{switch}">{'🇺🇸 EN' if pt else '🇧🇷 PT'}</a></div></div></header><main class="wrap main">{body}</main><footer class="footer"><div class="wrap footergrid"><div><a class="brand" href="{home}"><span class="brandmark">2</span><span>CS2</span><em>{' NOTÍCIAS' if pt else 'NEWS'}</em></a><p>{'Portal independente de Counter-Strike 2.' if pt else 'Independent Counter-Strike 2 news and data portal.'}</p></div><div class="footlinks"><a href="{prefix}about/{k}.html">{'Sobre' if pt else 'About'}</a><a href="{prefix}editorial/{k}.html">{'Política editorial' if pt else 'Editorial policy'}</a><a href="{prefix}privacy/{k}.html">{'Privacidade' if pt else 'Privacy'}</a><a href="{prefix}advertise/{k}.html">{'Anuncie' if pt else 'Advertise'}</a><a href="{prefix}contact/{k}.html">{'Contato' if pt else 'Contact'}</a></div></div></footer><script src="{prefix}assets/app.js"></script></body></html>'''

def news_items(k): return DATA.get("news_pt",[]) if k=="pt" else DATA.get("news",[])

def make_home(lang):
    pt=lang.startswith("pt"); k="pt" if pt else "en"; news=news_items(k); lead=news[0] if news else {}
    rankings=DATA.get("rankings",[])[:10]; events=DATA.get("events",[])
    rows="".join(f'<tr><td class="rank">{r["rank"]}</td><td><a href="../teams/{slug(r["team"])}-{k}.html"><b>{esc(r["team"])}</b></a></td><td>{r["points"]}</td><td>{movement(r,pt)}</td></tr>' for r in rankings)
    cards="".join(f'<a class="card newscard" href="../news/{slug(n.get("title",""))}-{k}.html"><span class="tag">{esc(n.get("category"))}</span><h3>{esc(n.get("title"))}</h3><p>{esc(n.get("summary"))}</p><div class="meta"><span>{esc(n.get("date"))}</span><span>{esc(n.get("source"))}</span></div></a>' for n in news[:5])
    ev="".join(f'<div class="event"><div><span class="badge {e.get("status")}">{("AO VIVO" if pt else "LIVE") if e.get("status")=="live" else ("EM BREVE" if pt else "UPCOMING")}</span><h4>{esc(e.get("name"))}</h4><p>{esc((e.get("dates") or {}).get(k))} · {esc(e.get("location"))}</p></div><b>${e.get("prize",0):,}</b></div>' for e in events)
    changes=DATA.get("roster_changes",[])[:4]
    rc="".join(f'<div class="rosterline"><div><b>{esc(c["team"])}</b><small>#{c.get("rank")}</small></div><span class="in">+ {esc(", ".join(c.get("joined",[])) or "—")}</span><span class="out">− {esc(", ".join(c.get("left",[])) or "—")}</span></div>' for c in changes) or f'<div class="empty">{"Nenhuma mudança detectada." if pt else "No roster changes detected."}</div>'
    hero_title=lead.get("title") or ("Tudo do CS2 em um só lugar." if pt else "Counter-Strike 2. All day. Every day.")
    hero_summary=lead.get("summary") or ("Dados, notícias e rankings." if pt else "Data, news and rankings.")
    status=("Feed de partidas conectado" if DATA.get("pandascore_status")=="connected" else "Rankings + notícias oficiais ativos") if pt else ("Match feed connected" if DATA.get("pandascore_status")=="connected" else "Official rankings + news active")
    players_count=len({p for r in DATA.get("rankings",[]) for p in r.get("roster",[])})
    body=f'''<div class="tickerbar"><span class="livebadge">CS2 DATA</span><div class="tickeritems" id="tickeritems"></div></div><section class="hero2"><div class="heroCopy"><span class="eyebrow">{esc(lead.get("category","CS2"))}</span><h1>{esc(hero_title)}</h1><p>{esc(hero_summary)}</p><div class="heroActions"><a class="primary" href="../news-{k}.html">{"Últimas notícias" if pt else "Latest news"}</a><a class="secondary" href="../rankings-{k}.html">{"Ranking Valve" if pt else "Valve rankings"}</a></div></div><aside class="dataPulse"><div class="pulseDot"></div><b>{status}</b><span>{"Atualização automatizada com fontes." if pt else "Automated updates with attribution."}</span><strong>{esc(DATA.get("ranking_date",""))}</strong></aside></section><section class="section"><div class="sectiontitle"><h2>{"Em destaque" if pt else "Top stories"}</h2><a href="../news-{k}.html">{"Ver tudo" if pt else "View all"}</a></div><div class="newsgrid5">{cards}</div></section><section class="section dashboard"><div class="card tablecard"><div class="sectiontitle"><h2>Valve Global Top 10</h2><a href="../rankings-{k}.html">{"Ranking completo" if pt else "Full rankings"}</a></div><table class="table"><thead><tr><th>#</th><th>{"Time" if pt else "Team"}</th><th>{"Pontos" if pt else "Points"}</th><th>Δ</th></tr></thead><tbody>{rows}</tbody></table></div><div class="stack"><div class="card panel"><div class="sectiontitle"><h2>{"Campeonatos" if pt else "Tournaments"}</h2><a href="../tournaments-{k}.html">{"Calendário" if pt else "Calendar"}</a></div>{ev}</div><div class="card panel"><div class="sectiontitle"><h2>VRS Roster Watch</h2><a href="../rosters/{k}.html">{"Abrir" if pt else "Open"}</a></div>{rc}</div></div></section><section class="section featuregrid"><a class="feature card" href="../teams-{k}.html"><b>{len(DATA.get("rankings",[]))}+</b><span>{"times indexados" if pt else "indexed teams"}</span></a><a class="feature card" href="../players-{k}.html"><b>{players_count}+</b><span>{"jogadores em rosters VRS" if pt else "players in VRS rosters"}</span></a><a class="feature card" href="../rankings-{k}.html"><b>4</b><span>{"rankings regionais" if pt else "ranking regions"}</span></a><a class="feature card" href="../advertise/{k}.html"><b>360°</b><span>{"inventário portal + social" if pt else "portal + social inventory"}</span></a></section>'''
    desc="Portal brasileiro de Counter-Strike 2 com notícias, rankings oficiais da Valve, times, jogadores, rosters e campeonatos." if pt else "Counter-Strike 2 news and data portal with official Valve rankings, teams, players, roster tracking and tournaments."
    return shell("CS2 NOTÍCIAS — Counter-Strike 2" if pt else "CS2NEWS — Counter-Strike 2 News & Data",body,lang,desc,prefix="../",canonical=f"{SITE_BASE}/{'cs2noticias' if pt else 'cs2news'}/",alternate=f"{SITE_BASE}/{'cs2news' if pt else 'cs2noticias'}/")

for lang in ("pt-BR","en-US"):
    pt=lang.startswith("pt"); k="pt" if pt else "en"
    (ROOT/("cs2noticias" if pt else "cs2news")/"index.html").write_text(make_home(lang),"utf-8")
    news=news_items(k)
    cards=[]
    for n in news:
        title=n.get("title","");summary=n.get("summary","");cat=n.get("category","");s=slug(title);u=f"news/{s}-{k}.html"
        cards.append(f'<a class="card articlecard" href="{u}"><span class="tag">{esc(cat)}</span><h2>{esc(title)}</h2><p>{esc(summary)}</p><div class="meta"><span>{esc(n.get("date"))}</span><span>{esc(n.get("source"))}</span></div></a>')
        source=f'<a class="sourcebtn" rel="noopener" target="_blank" href="{esc(n.get("source_url"))}">{"Abrir fonte" if pt else "Open source"} ↗</a>' if n.get("source_url") else ""
        article=f'<article class="article"><span class="tag">{esc(cat)}</span><h1>{esc(title)}</h1><div class="meta"><span>{esc(n.get("date"))}</span><span>{esc(n.get("source"))}</span></div><p class="lead">{esc(summary)}</p>{source}<div class="disclosure">{"Conteúdo produzido a partir dos dados e da fonte identificada acima." if pt else "This page is produced from the data and attributed source shown above."}</div></article>'
        (ROOT/"news"/f"{s}-{k}.html").write_text(shell(title,article,lang,summary,prefix="../",canonical=f"{SITE_BASE}/news/{s}-{k}.html"),"utf-8")
    (ROOT/f"news-{k}.html").write_text(shell("Últimas notícias de CS2" if pt else "Latest CS2 News",f'<div class="pagehead"><span class="eyebrow">{"COBERTURA" if pt else "COVERAGE"}</span><h1>{"Últimas notícias de CS2" if pt else "Latest CS2 News"}</h1></div><div class="articlegrid">{"".join(cards)}</div>',lang,prefix="",canonical=f"{SITE_BASE}/news-{k}.html"),"utf-8")

    top_team_names={r["team"] for r in DATA.get("rankings",[])[:120]}
    rankbody=""
    for region,label in [("global","Global"),("americas","Américas" if pt else "Americas"),("europe","Europa" if pt else "Europe"),("asia","Ásia" if pt else "Asia")]:
        rr=DATA.get("regional_rankings",{}).get(region,DATA.get("rankings",[]) if region=="global" else [])
        rows=[]
        for r in rr:
            team_html=f'<a href="teams/{slug(r["team"])}-{k}.html"><b>{esc(r["team"])}</b></a>' if r["team"] in top_team_names else f'<b>{esc(r["team"])}</b>'
            rows.append(f'<tr><td class="rank">{r["rank"]}</td><td>{team_html}</td><td>{r["points"]}</td><td>{movement(r,pt) if region=="global" else "—"}</td></tr>')
        rows="".join(rows)
        rankbody+=f'<section class="rankingsection" id="{region}"><div class="sectiontitle"><h2>{label}</h2><span class="source">{esc(DATA.get("ranking_"+region+"_date",""))}</span></div><div class="card tablecard"><table class="table"><thead><tr><th>#</th><th>{"Time" if pt else "Team"}</th><th>{"Pontos" if pt else "Points"}</th><th>Δ</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    ranknav='<div class="subnav"><a href="#global">Global</a><a href="#americas">Americas</a><a href="#europe">Europe</a><a href="#asia">Asia</a></div>'
    (ROOT/f"rankings-{k}.html").write_text(shell("Ranking CS2 da Valve" if pt else "Valve CS2 Rankings",f'<div class="pagehead"><span class="eyebrow">VRS</span><h1>{"Ranking oficial da Valve" if pt else "Official Valve Rankings"}</h1><p>{"Snapshots oficiais com comparação de posição e rosters registrados." if pt else "Official snapshots with rank movement and registered rosters."}</p></div>{ranknav}{rankbody}',lang,prefix="",canonical=f"{SITE_BASE}/rankings-{k}.html"),"utf-8")

    rankings=DATA.get("rankings",[])
    teamcards="".join(f'<a class="card entitycard" href="teams/{slug(r["team"])}-{k}.html"><span class="rank">#{r["rank"]}</span><h3>{esc(r["team"])}</h3><p>{esc(r.get("region"))} · {r["points"]} pts</p><small>{esc(", ".join(r.get("roster",[])))}</small></a>' for r in rankings[:120])
    (ROOT/f"teams-{k}.html").write_text(shell("Times de CS2" if pt else "CS2 Teams",f'<div class="pagehead"><h1>{"Times de CS2" if pt else "CS2 Teams"}</h1><p>{"Top 120 do VRS global atual." if pt else "Current global VRS top 120."}</p></div><div class="entitygrid">{teamcards}</div>',lang,prefix="",canonical=f"{SITE_BASE}/teams-{k}.html"),"utf-8")
    player_map={}
    for r in rankings[:120]:
        for p in r.get("roster",[]): player_map.setdefault(p,[]).append(r)
        rosterlinks="".join(f'<a class="playerchip" href="../players/{slug(p)}-{k}.html">{esc(p)}</a>' for p in r.get("roster",[]))
        body=f'<div class="entityhero"><span class="rank">#{r["rank"]}</span><h1>{esc(r["team"])}</h1><p>{esc(r.get("region"))} · {r["points"]} pts · Δ {movement(r,pt)}</p></div><section class="card panel"><div class="sectiontitle"><h2>Roster VRS</h2><span class="source">{esc(DATA.get("ranking_date"))}</span></div><div class="chips">{rosterlinks}</div></section><div class="disclosure">{"Roster conforme snapshot oficial do VRS; não representa anúncio de transferência." if pt else "Roster shown from the official VRS snapshot; this is not a transfer announcement."}</div>'
        (ROOT/"teams"/f'{slug(r["team"])}-{k}.html').write_text(shell(r["team"],body,lang,prefix="../",canonical=f'{SITE_BASE}/teams/{slug(r["team"])}-{k}.html'),"utf-8")
    players=sorted(player_map.items(),key=lambda x:(x[1][0]["rank"],x[0].lower()))
    pcards="".join(f'<a class="card entitycard" href="players/{slug(p)}-{k}.html"><h3>{esc(p)}</h3><p>{esc(rs[0]["team"])} · #{rs[0]["rank"]}</p></a>' for p,rs in players)
    (ROOT/f"players-{k}.html").write_text(shell("Jogadores de CS2" if pt else "CS2 Players",f'<div class="pagehead"><h1>{"Jogadores em rosters VRS" if pt else "Players in VRS rosters"}</h1></div><div class="entitygrid">{pcards}</div>',lang,prefix="",canonical=f"{SITE_BASE}/players-{k}.html"),"utf-8")
    for p,rs in players:
        r=rs[0];body=f'<div class="entityhero"><span class="eyebrow">PLAYER</span><h1>{esc(p)}</h1><p>{"Roster registrado:" if pt else "Registered roster:"} <a href="../teams/{slug(r["team"])}-{k}.html"><b>{esc(r["team"])}</b></a> · VRS #{r["rank"]}</p></div><div class="disclosure">{"Página baseada no roster oficial registrado no snapshot da Valve." if pt else "Page based on the roster registered in the official Valve snapshot."}</div>'
        (ROOT/"players"/f"{slug(p)}-{k}.html").write_text(shell(p,body,lang,prefix="../",canonical=f"{SITE_BASE}/players/{slug(p)}-{k}.html"),"utf-8")

    events=DATA.get("events",[])
    evcards="".join(f'<div class="card eventbig"><span class="badge {e.get("status")}">{("AO VIVO" if pt else "LIVE") if e.get("status")=="live" else ("EM BREVE" if pt else "UPCOMING")}</span><h2>{esc(e.get("name"))}</h2><p>{esc((e.get("dates") or {}).get(k))} · {esc(e.get("location"))}</p><b>${e.get("prize",0):,}</b><a target="_blank" rel="noopener" href="{esc(e.get("source_url"))}">{"Fonte" if pt else "Source"} ↗</a></div>' for e in events)
    (ROOT/f"tournaments-{k}.html").write_text(shell("Campeonatos de CS2" if pt else "CS2 Tournaments",f'<div class="pagehead"><h1>{"Campeonatos de CS2" if pt else "CS2 Tournaments"}</h1><p>{"Calendário verificado com fontes identificadas." if pt else "Verified calendar with identified sources."}</p></div><div class="eventgrid">{evcards}</div>',lang,prefix="",canonical=f"{SITE_BASE}/tournaments-{k}.html"),"utf-8")

    matches=DATA.get("matches",[])
    if matches:
        mhtml="".join(f'<div class="card matchbig"><span class="badge {m.get("status")}">{esc(m.get("status"))}</span><small>{esc(m.get("league"))}</small><h3>{esc(m.get("team1"))} <span>vs</span> {esc(m.get("team2"))}</h3><p>BO{m.get("bo")} · {esc(m.get("when"))}</p></div>' for m in matches)
    else:
        mhtml=f'<div class="card statuscard"><b>{"Feed de placares preparado" if pt else "Live-score feed ready"}</b><p>{"A infraestrutura está validada; a fonte de partidas em tempo real exige uma chave de provedor externo. Rankings, rosters e notícias oficiais seguem automatizados." if pt else "Infrastructure is validated; real-time match data requires an external provider key. Rankings, rosters and official news remain automated."}</p></div>'
    (ROOT/"matches"/f"{k}.html").write_text(shell("Partidas de CS2" if pt else "CS2 Matches",f'<div class="pagehead"><h1>{"Partidas" if pt else "Matches"}</h1></div><div class="matchlist">{mhtml}</div>',lang,prefix="../",canonical=f"{SITE_BASE}/matches/{k}.html"),"utf-8")

    changes=DATA.get("roster_changes",[])
    changehtml="".join(f'<div class="card rosterchange"><span class="rank">#{c.get("rank")}</span><h3>{esc(c.get("team"))}</h3><p class="in">+ {esc(", ".join(c.get("joined",[])) or "—")}</p><p class="out">− {esc(", ".join(c.get("left",[])) or "—")}</p></div>' for c in changes) or '<div class="empty">No detected changes.</div>'
    (ROOT/"rosters"/f"{k}.html").write_text(shell("VRS Roster Tracker",f'<div class="pagehead"><h1>VRS Roster Tracker</h1><p>{"Compara os dois snapshots globais mais recentes da Valve. Não é um feed de rumores." if pt else "Compares the two latest Valve global snapshots. This is not a rumor feed."}</p></div><div class="entitygrid">{changehtml}</div>',lang,prefix="../",canonical=f"{SITE_BASE}/rosters/{k}.html"),"utf-8")

    static_pages={
      "about":("Sobre o projeto" if pt else "About", "CS2 NOTÍCIAS e CS2NEWS formam um portal independente de dados e notícias de Counter-Strike 2, com duas linhas editoriais e uma base compartilhada." if pt else "CS2 NOTÍCIAS and CS2NEWS are an independent Counter-Strike 2 news and data project with two editorial editions and one shared data layer."),
      "editorial":("Política editorial" if pt else "Editorial policy", "Dados estruturados são atribuídos à fonte. Mudanças de roster do VRS são tratadas como mudanças de registro, não como confirmação de transferência. Notícias oficiais apontam para a publicação original." if pt else "Structured data is attributed to its source. VRS roster changes are described as registration changes, not confirmed transfers. Official news links back to the original publication."),
      "privacy":("Privacidade" if pt else "Privacy", "O portal atualmente não utiliza login próprio nem vende dados pessoais. Analytics e publicidade só serão ativados após configuração de consentimento e política compatível com a região do visitante." if pt else "The portal currently has no first-party login and does not sell personal data. Analytics and advertising will only be enabled after region-appropriate consent and privacy configuration."),
      "advertise":("Anuncie no CS2 NOTÍCIAS" if pt else "Advertise on CS2NEWS", "Inventário comercial para marcas de hardware, periféricos, tecnologia, esports e serviços para gamers: patrocínio de editoria, cards nativos, takeover de campeonato e pacotes portal + social. Não publicamos métricas que ainda não existam." if pt else "Commercial inventory for hardware, peripherals, technology, esports and gamer services: section sponsorships, native cards, tournament takeovers and portal + social packages. We do not publish audience metrics that do not yet exist."),
      "contact":("Contato comercial" if pt else "Commercial contact", f'{"Parcerias, mídia e publicidade:" if pt else "Partnerships, media and advertising:"} <a href="mailto:{CONTACT}">{CONTACT}</a>')
    }
    for folder,(t,txt) in static_pages.items():
        body=f'<article class="article"><span class="eyebrow">CS2 MEDIA</span><h1>{esc(t)}</h1><p class="lead">{txt if "<a " in txt else esc(txt)}</p></article>'
        (ROOT/folder/f"{k}.html").write_text(shell(t,body,lang,prefix="../",canonical=f"{SITE_BASE}/{folder}/{k}.html"),"utf-8")

    search_items=[]
    for n in news:search_items.append({"title":n.get("title"),"type":"news","url":f"../news/{slug(n.get('title'))}-{k}.html"})
    for r in rankings[:120]:search_items.append({"title":r["team"],"type":"team","url":f"../teams/{slug(r['team'])}-{k}.html"})
    for p,_ in players:search_items.append({"title":p,"type":"player","url":f"../players/{slug(p)}-{k}.html"})
    (ROOT/"data"/f"search-{k}.json").write_text(json.dumps(search_items,ensure_ascii=False),"utf-8")
    sb=f'<div class="pagehead"><h1>{"Buscar" if pt else "Search"}</h1></div><input id="site-search" class="searchbox" autocomplete="off" placeholder="{"Time, jogador ou notícia..." if pt else "Team, player or story..."}"><div id="search-results" class="searchresults"></div>'
    (ROOT/"search"/f"{k}.html").write_text(shell("Busca" if pt else "Search",sb,lang,prefix="../",canonical=f"{SITE_BASE}/search/{k}.html"),"utf-8")

redirects={
    "news/index.html":"../news-en.html",
    "teams/index.html":"../teams-en.html",
    "players/index.html":"../players-en.html",
    "tournaments/index.html":"../tournaments-en.html",
    "matches/index.html":"en.html",
}
for path,target in redirects.items():
    (ROOT/path).write_text(f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CS2NEWS Redirect</title><meta http-equiv="refresh" content="0;url={target}"></head><body><a href="{target}">Continue</a></body></html>',"utf-8")

root='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CS2 NEWS</title><script>const p=(navigator.language||"").toLowerCase().startsWith("pt")?"cs2noticias/":"cs2news/";location.replace(p)</script><noscript><meta http-equiv="refresh" content="0;url=cs2news/"></noscript></head><body></body></html>'''
(ROOT/"index.html").write_text(root,"utf-8")
(ROOT/"404.html").write_text(shell("404",'<article class="article"><h1>404</h1><p>Page not found / Página não encontrada.</p></article>',"en-US",prefix=""),"utf-8")
manifest={"name":"CS2NEWS / CS2 NOTÍCIAS","short_name":"CS2NEWS","start_url":"./","display":"standalone","background_color":"#090b10","theme_color":"#ff5a1f","icons":[]}
(ROOT/"site.webmanifest").write_text(json.dumps(manifest,ensure_ascii=False),"utf-8")
urls=[]
for p in ROOT.rglob("*.html"):
    if ".github" not in p.parts:
        urls.append("/"+p.relative_to(ROOT).as_posix())
now=datetime.now(timezone.utc).date().isoformat()
(ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE_BASE}{u}</loc><lastmod>{now}</lastmod></url>' for u in sorted(urls))+"</urlset>","utf-8")
(ROOT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE}/sitemap.xml\n","utf-8")
print("Built",len(urls),"HTML routes")
