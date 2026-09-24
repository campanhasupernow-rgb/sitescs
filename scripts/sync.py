#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sys,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data'/'site.json';UA={'User-Agent':'CS2NEWS/0.2'}
def get_json(url,headers=None):
 h=dict(UA);h.update(headers or {});req=urllib.request.Request(url,headers=h)
 with urllib.request.urlopen(req,timeout=20) as r:return json.loads(r.read().decode())
def get_text(url):
 req=urllib.request.Request(url,headers=UA)
 with urllib.request.urlopen(req,timeout=20) as r:return r.read().decode('utf-8','replace')
def load():return json.loads(OUT.read_text('utf-8')) if OUT.exists() else {'rankings':[],'events':[],'news':[],'ticker':[],'matches':[]}
def sync_valve(d):
 year=datetime.now().year;listing=get_json(f'https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/{year}')
 files=[x for x in listing if re.match(r'standings_global_\d{4}_\d{2}_\d{2}\.md$',x.get('name',''))]
 if not files:return
 latest=sorted(files,key=lambda x:x['name'])[-1];rows=[]
 for line in get_text(latest['download_url']).splitlines():
  m=re.match(r'\|?\s*(\d+)\s*\|\s*([0-9.]+)\s*\|\s*([^|]+?)\s*\|',line)
  if m:rows.append({'rank':int(m.group(1)),'points':round(float(m.group(2))),'team':m.group(3).strip(),'region':'Global'})
 if rows:d['rankings']=rows
def sync_steam(d):
 js=get_json('https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid=730&count=6&maxlength=500&format=json');items=js.get('appnews',{}).get('newsitems',[])
 if not items:return
 out=[]
 for n in items:
  title=n.get('title','Counter-Strike 2 Update').strip();desc=re.sub(r'<[^>]+>',' ',n.get('contents',''));desc=re.sub(r'\s+',' ',desc).strip()[:280];dt=datetime.fromtimestamp(n.get('date',0),tz=timezone.utc).strftime('%m/%d/%Y')
  out.append({'category':{'pt':'VALVE / STEAM','en':'VALVE / STEAM'},'title':{'pt':title,'en':title},'summary':{'pt':desc,'en':desc},'date':dt,'source':'Valve / Steam'})
 d['news']=out
def sync_pandascore(d):
 token=os.getenv('PANDASCORE_TOKEN','').strip()
 if not token:d['matches']=[];return
 headers={'Authorization':f'Bearer {token}'};base='https://api.pandascore.co/csgo/matches';out=[]
 for kind in ('running','upcoming'):
  for m in get_json(f'{base}/{kind}?per_page=12&sort=begin_at',headers):
   opp=m.get('opponents') or []
   if len(opp)<2:continue
   getn=lambda x:(x.get('opponent') or {}).get('name','TBD');score={r.get('team_id'):r.get('score') for r in (m.get('results') or [])};t1=opp[0].get('opponent') or {};t2=opp[1].get('opponent') or {};league=(m.get('league') or {}).get('name') or 'CS2'
   out.append({'league':league,'status':'running' if kind=='running' else 'upcoming','team1':getn(opp[0]),'team2':getn(opp[1]),'score1':score.get(t1.get('id')),'score2':score.get(t2.get('id')),'bo':m.get('number_of_games') or 3,'when':m.get('begin_at','')})
 d['matches']=out[:12]
def main():
 d=load()
 for name,fn in [('Valve',sync_valve),('Steam',sync_steam),('PandaScore',sync_pandascore)]:
  try:fn(d);print('OK',name)
  except Exception as e:print('WARN',name,e,file=sys.stderr)
 d['generated_at']=datetime.now(timezone.utc).isoformat();OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')
if __name__=='__main__':main()
