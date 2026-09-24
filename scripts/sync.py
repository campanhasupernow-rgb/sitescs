#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "site.json"
UA = {"User-Agent": "CS2NEWS/1.0 (+https://github.com/campanhasupernow-rgb/sitescs)"}

VERIFIED_EVENTS = [
    {
        "name": "Stake Pulse Beat II",
        "start_date": "2026-09-21",
        "end_date": "2026-09-26",
        "dates": {"pt": "21 a 26 de setembro", "en": "Sep 21–26"},
        "location": "Nordics / BME Studio",
        "prize": 60000,
        "source": "Stake",
        "source_url": "https://stake.com/sponsorships/stake-pulse",
    },
    {
        "name": "1win Private Club Season 1",
        "start_date": "2026-09-25",
        "end_date": "2026-09-28",
        "dates": {"pt": "25 a 28 de setembro", "en": "Sep 25–28"},
        "location": "Belgrade, Serbia",
        "prize": 100000,
        "source": "HLTV event listings",
        "source_url": "https://www.hltv.org/events",
    },
    {
        "name": "ESL Pro League Season 24",
        "start_date": "2026-10-03",
        "end_date": "2026-10-11",
        "dates": {"pt": "3 a 11 de outubro", "en": "Oct 3–11"},
        "location": "Katowice, Poland",
        "prize": 1000000,
        "source": "ESL / event listings",
        "source_url": "https://www.hltv.org/events/8244/esl-pro-league-season-24",
    },
]

def get_json(url, headers=None):
    h = dict(UA)
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())

def get_text(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")

def load():
    if OUT.exists():
        return json.loads(OUT.read_text("utf-8"))
    return {}

def parse_standings(text, region):
    rows = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 4 or not parts[0].isdigit():
            continue
        try:
            rank = int(parts[0])
            points = round(float(parts[1]))
        except ValueError:
            continue
        roster = [p.strip() for p in parts[3].split(",") if p.strip()]
        rows.append({
            "rank": rank,
            "points": points,
            "team": parts[2],
            "roster": roster,
            "region": region,
        })
    return rows

def ranking_files(year):
    listing = get_json(
        f"https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/{year}"
    )
    out = {"global": [], "americas": [], "europe": [], "asia": []}
    for item in listing:
        name = item.get("name", "")
        for region in out:
            if re.match(rf"standings_{region}_\d{{4}}_\d{{2}}_\d{{2}}\.md$", name):
                out[region].append(item)
    for region in out:
        out[region].sort(key=lambda x: x["name"])
    return out

def sync_valve(d):
    year = datetime.now(timezone.utc).year
    files = ranking_files(year)
    regional = {}
    for region in ("global", "americas", "europe", "asia"):
        if not files[region]:
            continue
        latest = files[region][-1]
        regional[region] = parse_standings(get_text(latest["download_url"]), region.title())
        d[f"ranking_{region}_source"] = latest.get("html_url")
        d[f"ranking_{region}_date"] = (
            latest["name"].replace(f"standings_{region}_", "").replace(".md", "").replace("_", "-")
        )

    global_rows = regional.get("global", [])
    previous_rows = []
    if len(files["global"]) > 1:
        previous_rows = parse_standings(get_text(files["global"][-2]["download_url"]), "Global")

    prev = {r["team"]: r for r in previous_rows}
    membership = {}
    for region in ("americas", "europe", "asia"):
        for row in regional.get(region, []):
            membership[row["team"]] = region.title()

    for row in global_rows:
        old = prev.get(row["team"])
        row["previous_rank"] = old["rank"] if old else None
        row["rank_delta"] = (old["rank"] - row["rank"]) if old else 0
        row["region"] = membership.get(row["team"], "Global")

    changes = []
    for row in global_rows:
        old = prev.get(row["team"])
        if not old:
            continue
        current = set(row.get("roster", []))
        prior = set(old.get("roster", []))
        joined = sorted(current - prior, key=str.lower)
        left = sorted(prior - current, key=str.lower)
        if joined or left:
            changes.append({
                "team": row["team"],
                "rank": row["rank"],
                "joined": joined,
                "left": left,
            })

    d["rankings"] = global_rows
    d["regional_rankings"] = regional
    d["roster_changes"] = changes
    d["ranking_date"] = d.get("ranking_global_date")
    d["ranking_source"] = d.get("ranking_global_source")

def clean_bbcode(value):
    value = re.sub(r"\[[^\]]+\]", " ", value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def sync_steam(d):
    url = (
        "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
        "?appid=730&count=20&maxlength=900&format=json&feeds=steam_community_announcements"
    )
    js = get_json(url)
    items = js.get("appnews", {}).get("newsitems", [])
    official = [n for n in items if n.get("feedname") == "steam_community_announcements"][:8]
    out = []
    for n in official:
        title = (n.get("title") or "Counter-Strike 2 Update").strip()
        desc = clean_bbcode(n.get("contents", ""))[:420]
        dt = datetime.fromtimestamp(n.get("date", 0), tz=timezone.utc).strftime("%Y-%m-%d")
        out.append({
            "category": "OFFICIAL UPDATE",
            "title": title,
            "summary": desc,
            "date": dt,
            "source": "Counter-Strike / Steam",
            "source_url": n.get("url", ""),
        })
    d["official_news"] = out

def build_editorial(d):
    rankings = d.get("rankings", [])
    official = d.get("official_news", [])
    date = d.get("ranking_date") or datetime.now(timezone.utc).date().isoformat()
    en = []
    pt = []

    if rankings:
        leader = rankings[0]
        furia = next((x for x in rankings if x["team"].lower() == "furia"), None)
        en_title = f'{leader["team"]} leads Valve global standings'
        pt_title = f'{leader["team"]} lidera o ranking global da Valve'
        if furia:
            en_title += f'; FURIA sits at #{furia["rank"]}'
            pt_title += f'; FURIA aparece em #{furia["rank"]}'
        en.append({
            "category": "RANKINGS",
            "title": en_title,
            "summary": f'Valve\'s latest global standings place {leader["team"]} at No. 1 with {leader["points"]} points. CS2NEWS tracks ranking movement and registered rosters directly from Valve data.',
            "date": date,
            "source": "Valve Regional Standings",
            "source_url": d.get("ranking_source", ""),
        })
        pt.append({
            "category": "RANKING",
            "title": pt_title,
            "summary": f'O ranking global mais recente da Valve coloca {leader["team"]} na liderança com {leader["points"]} pontos. O CS2 NOTÍCIAS acompanha movimentações e rosters registrados diretamente nos dados da Valve.',
            "date": date,
            "source": "Valve Regional Standings",
            "source_url": d.get("ranking_source", ""),
        })

        movers = [x for x in rankings[:60] if x.get("previous_rank") and x.get("rank_delta")]
        if movers:
            biggest = max(movers, key=lambda x: abs(x["rank_delta"]))
            direction_en = "climbs" if biggest["rank_delta"] > 0 else "drops"
            direction_pt = "sobe" if biggest["rank_delta"] > 0 else "cai"
            amount = abs(biggest["rank_delta"])
            en.append({
                "category": "DATA DESK",
                "title": f'{biggest["team"]} {direction_en} {amount} spots in Valve standings',
                "summary": f'{biggest["team"]} moved from #{biggest["previous_rank"]} to #{biggest["rank"]}. The comparison uses consecutive official Valve ranking snapshots.',
                "date": date,
                "source": "Valve Regional Standings",
                "source_url": d.get("ranking_source", ""),
            })
            pt.append({
                "category": "DADOS",
                "title": f'{biggest["team"]} {direction_pt} {amount} posições no ranking da Valve',
                "summary": f'{biggest["team"]} passou de #{biggest["previous_rank"]} para #{biggest["rank"]}. A comparação utiliza dois snapshots consecutivos do ranking oficial da Valve.',
                "date": date,
                "source": "Valve Regional Standings",
                "source_url": d.get("ranking_source", ""),
            })

    changes = d.get("roster_changes", [])
    if changes:
        c = sorted(changes, key=lambda x: x.get("rank", 9999))[0]
        joined = ", ".join(c.get("joined", [])) or "—"
        left = ", ".join(c.get("left", [])) or "—"
        en.append({
            "category": "VRS ROSTER WATCH",
            "title": f'Valve roster snapshot changes for {c["team"]}',
            "summary": f'Compared with the previous VRS snapshot, registered additions are {joined}; registered departures are {left}. This tracks VRS registration changes, not transfer rumors.',
            "date": date,
            "source": "Valve Regional Standings",
            "source_url": d.get("ranking_source", ""),
        })
        pt.append({
            "category": "ROSTER VRS",
            "title": f'Mudança no roster registrado da {c["team"]} no VRS',
            "summary": f'Na comparação com o snapshot anterior, as entradas registradas são {joined}; as saídas registradas são {left}. O dado acompanha alterações de registro no VRS, não rumores de transferência.',
            "date": date,
            "source": "Valve Regional Standings",
            "source_url": d.get("ranking_source", ""),
        })

    if official:
        latest = official[0]
        en.insert(0, latest)
        pt.insert(0, {
            "category": "ATUALIZAÇÃO OFICIAL",
            "title": f'Valve publica atualização de CS2: {latest["title"]}',
            "summary": "A Valve publicou uma nova comunicação oficial de Counter-Strike 2. O CS2 NOTÍCIAS aponta para a fonte original e mantém a cobertura de atualizações separada dos conteúdos de análise e dados.",
            "date": latest["date"],
            "source": latest["source"],
            "source_url": latest.get("source_url", ""),
        })

    d["news"] = en[:12]
    d["news_pt"] = pt[:12]

def sync_pandascore(d):
    token = os.getenv("PANDASCORE_TOKEN", "").strip()
    if not token:
        d["matches"] = []
        d["pandascore_status"] = "not_connected"
        return
    headers = {"Authorization": f"Bearer {token}"}
    base = "https://api.pandascore.co/csgo/matches"
    out = []
    for kind in ("running", "upcoming"):
        for m in get_json(f"{base}/{kind}?per_page=20&sort=begin_at", headers):
            opp = m.get("opponents") or []
            if len(opp) < 2:
                continue
            t1 = opp[0].get("opponent") or {}
            t2 = opp[1].get("opponent") or {}
            scores = {r.get("team_id"): r.get("score") for r in (m.get("results") or [])}
            out.append({
                "id": m.get("id"),
                "league": (m.get("league") or {}).get("name") or "CS2",
                "tournament": (m.get("tournament") or {}).get("name") or "",
                "status": "running" if kind == "running" else "upcoming",
                "team1": t1.get("name", "TBD"),
                "team2": t2.get("name", "TBD"),
                "score1": scores.get(t1.get("id")),
                "score2": scores.get(t2.get("id")),
                "bo": m.get("number_of_games") or 3,
                "when": m.get("begin_at", ""),
            })
    d["matches"] = out[:30]
    d["pandascore_status"] = "connected"

def sync_events(d):
    today = datetime.now(timezone.utc).date()
    events = []
    for event in VERIFIED_EVENTS:
        e = dict(event)
        start = datetime.fromisoformat(e["start_date"]).date()
        end = datetime.fromisoformat(e["end_date"]).date()
        e["status"] = "live" if start <= today <= end else ("upcoming" if today < start else "completed")
        events.append(e)
    d["events"] = [e for e in events if e["status"] != "completed"][:8]

def build_ticker(d):
    rankings = d.get("rankings", [])
    furia = next((x for x in rankings if x["team"].lower() == "furia"), None)
    leader = rankings[0] if rankings else None
    americas = (d.get("regional_rankings") or {}).get("americas", [])
    items = []
    if leader:
        value = f'{leader["team"]} #1'
        if furia:
            value += f' · FURIA #{furia["rank"]}'
        items.append({"label": {"pt": "VRS GLOBAL", "en": "GLOBAL VRS"}, "value": {"pt": value, "en": value}})
    if americas:
        items.append({"label": {"pt": "AMÉRICAS", "en": "AMERICAS"}, "value": {"pt": f'{americas[0]["team"]} #1 regional', "en": f'{americas[0]["team"]} #1 regional'}})
    items.append({"label": {"pt": "DADOS", "en": "DATA"}, "value": {"pt": "Valve + Steam sincronizados", "en": "Valve + Steam synced"}})
    d["ticker"] = items

def stable_payload(d):
    clone = dict(d)
    clone.pop("generated_at", None)
    clone.pop("content_hash", None)
    return json.dumps(clone, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def main():
    old = load()
    d = dict(old)
    for name, fn in [
        ("Valve", sync_valve),
        ("Steam", sync_steam),
        ("PandaScore", sync_pandascore),
        ("Events", sync_events),
    ]:
        try:
            fn(d)
            print("OK", name)
        except Exception as exc:
            print("WARN", name, exc, file=sys.stderr)

    build_editorial(d)
    build_ticker(d)
    payload = stable_payload(d)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    changed = digest != old.get("content_hash")
    d["content_hash"] = digest
    if changed or not OUT.exists():
        d["generated_at"] = datetime.now(timezone.utc).isoformat()
        OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), "utf-8")
        print("UPDATED", digest[:12])
    else:
        print("NO_CHANGES", digest[:12])

if __name__ == "__main__":
    main()
