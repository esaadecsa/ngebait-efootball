#!/usr/bin/env python3
"""
Ngebait sync engine.
- Reads optional PlayersDB JSON/JSONL/CSV exports if configured.
- Keeps the repository usable even when a source is unavailable.
- Collects official eFootball/KONAMI news headlines via RSS/HTML where possible.
- Writes data/*.json.
"""
import csv, io, json, os, re, sys, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data")
os.makedirs(DATA, exist_ok=True)

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def fetch(url, timeout=25):
    req=Request(url, headers={"User-Agent":"Ngebait-eFootball-Sync/1.0"})
    with urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("content-type","")

def write(name,obj):
    with open(os.path.join(DATA,name),"w",encoding="utf-8") as f:
        json.dump(obj,f,ensure_ascii=False,indent=2)

def tier(ovr):
    try: o=int(ovr)
    except: return "C"
    return "S" if o>=95 else "A" if o>=90 else "B" if o>=85 else "C"

def normalize_players(rows):
    out=[]
    for x in rows:
        name=x.get("name") or x.get("player") or x.get("player_name")
        if not name: continue
        try: ovr=int(x.get("ovr") or x.get("overall") or x.get("rating") or 0)
        except: ovr=0
        out.append({
            "id":str(x.get("id") or x.get("pes_id") or x.get("player_id") or ""),
            "name":name,
            "position":x.get("position") or x.get("pos") or "",
            "ovr":ovr,
            "tier":tier(ovr),
            "club":x.get("club") or x.get("team") or "",
            "nationality":x.get("nationality") or "",
            "source":x.get("source") or "PlayersDB"
        })
    return out

def load_external_players():
    url=os.environ.get("PLAYERSDB_EXPORT_URL","").strip()
    if not url: return None
    raw,ctype=fetch(url)
    text=raw.decode("utf-8-sig","replace")
    if url.lower().endswith(".jsonl"):
        rows=[json.loads(line) for line in text.splitlines() if line.strip()]
    elif url.lower().endswith(".csv"):
        rows=list(csv.DictReader(io.StringIO(text)))
    else:
        obj=json.loads(text)
        rows=obj.get("players",obj) if isinstance(obj,dict) else obj
    return normalize_players(rows)

class NewsParser(HTMLParser):
    def __init__(self,base):
        super().__init__(); self.base=base; self.items=[]; self.in_a=False; self.href=""; self.buf=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            d=dict(attrs); self.in_a=True; self.href=urljoin(self.base,d.get("href","")); self.buf=[]
    def handle_data(self,data):
        if self.in_a: self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.in_a:
            title=" ".join(" ".join(self.buf).split())
            if len(title)>=12 and self.href.startswith("http"):
                self.items.append({"title":title,"url":self.href})
            self.in_a=False

def official_news():
    url=os.environ.get("KONAMI_NEWS_URL","https://www.konami.com/efootball/en/topic/news")
    try:
        raw,_=fetch(url)
        p=NewsParser(url); p.feed(raw.decode("utf-8","replace"))
        seen=set(); out=[]
        for x in p.items:
            if x["url"] in seen: continue
            seen.add(x["url"])
            if any(k in x["title"].lower() for k in ["efootball","campaign","event","update","player","login"]):
                x["publishedAt"]=now(); out.append(x)
            if len(out)>=30: break
        return out
    except Exception as e:
        print("Official news sync warning:",e)
        return []

def main():
    updated=now()
    players=None
    try: players=load_external_players()
    except Exception as e: print("PlayersDB export unavailable:",e)
    if players:
        write("players.json",{"updatedAt":updated,"source":"PlayersDB export","players":players})
    else:
        # Preserve the checked-in starter snapshot when no export URL is configured.
        path=os.path.join(DATA,"players.json")
        if os.path.exists(path):
            obj=json.load(open(path,encoding="utf-8")); obj["lastSyncAttempt"]=updated; write("players.json",obj)
    news=official_news()
    old={}
    ep=os.path.join(DATA,"events.json")
    if os.path.exists(ep):
        try: old=json.load(open(ep,encoding="utf-8"))
        except: old={}
    write("events.json",{"updatedAt":updated,"source":"KONAMI official news","events":news or old.get("events",[])})
    write("meta.json",{"updatedAt":updated,"status":"ok","playersSource":"PlayersDB export" if players else "starter snapshot","newsSource":"KONAMI official eFootball news","workflow":"GitHub Actions"})
    print("Ngebait sync finished:",updated)

if __name__=="__main__": main()
