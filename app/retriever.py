from __future__ import annotations
import math, re
from dataclasses import dataclass
from pathlib import Path
from collections import Counter

STOP = set('the a an and or of to in for on is are was were it this that with from by as at be have has had do does did i you your my we they their our can what how when where why which about into within after before only not no'.split())

@dataclass(frozen=True)
class Passage:
    filename: str
    heading: str
    text: str
    metadata: dict

    @property
    def authority(self) -> int:
        if self.metadata.get('policy_authority') == 'official' and self.metadata.get('status') == 'active': return 4
        if self.metadata.get('policy_authority') == 'official': return 3
        if self.metadata.get('status') == 'active': return 2
        return 0

def tokens(s: str):
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP]

def parse_frontmatter(raw: str):
    meta={}
    if raw.startswith('---'):
        end=raw.find('\n---', 3)
        if end >= 0:
            for line in raw[4:end].splitlines():
                if ':' in line:
                    k,v=line.split(':',1); meta[k.strip()] = v.strip()
    return meta

def chunk_markdown(path: Path):
    raw=path.read_text(encoding='utf-8')
    meta=parse_frontmatter(raw)
    body=raw
    if raw.startswith('---'):
        end=raw.find('\n---',3); body=raw[end+4:] if end>=0 else raw
    heading='Document'
    chunks=[]
    current=[]
    for line in body.splitlines():
        if line.startswith('#'):
            if current:
                chunks.append((heading,'\n'.join(current).strip())); current=[]
            heading=line.lstrip('#').strip()
        elif line.strip(): current.append(line.strip())
    if current: chunks.append((heading,'\n'.join(current).strip()))
    return [Passage(path.name,h,t,meta) for h,t in chunks if t]

class Retriever:
    def __init__(self, kb_dir='knowledge-base'):
        self.passages=[]
        for p in sorted(Path(kb_dir).glob('*.md')): self.passages.extend(chunk_markdown(p))
        self.df=Counter()
        self.docs=[]
        for p in self.passages:
            tf=Counter(tokens(p.text+' '+p.heading+' '+p.filename)); self.docs.append(tf)
            for term in tf: self.df[term]+=1

    def search(self, query, k=6):
        q=set(tokens(query)); scored=[]
        N=len(self.docs)
        for p,tf in zip(self.passages,self.docs):
            overlap=sum(tf[t] for t in q if t in tf)
            if not overlap: continue
            semantic=sum((1+math.log(tf[t]))*math.log((N+1)/(self.df[t]+1)) for t in q if t in tf)
            boost=0.0
            if p.authority==4: boost += 1.8
            if p.metadata.get('status')=='superseded': boost -= 1.5
            if p.metadata.get('audience')=='internal': boost -= 1.0
            if p.metadata.get('customer_answering')=='false': boost -= 1.5
            scored.append((semantic+boost,p))
        scored.sort(key=lambda x:x[0], reverse=True)
        return scored[:k]
