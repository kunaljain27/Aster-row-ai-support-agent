import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import Agent, Session
ROOT=Path(__file__).resolve().parents[1]

def norm(s): return s.lower().replace('–','-').replace('—','-')
def run_case(agent, case):
    session=Session(); outputs=[]; before=len(agent.orders.calls)
    for m in case['messages']: outputs.append(agent.ask(m['content'],session))
    text=norm('\n'.join(x['answer'] for x in outputs)); sources=' '.join(s for x in outputs for s in x['sources']); calls=agent.orders.calls[before:]
    exp=case.get('expect',case); checks=[]
    for x in exp.get('must_include',[]): checks.append((f'include:{x}',norm(x) in text))
    aliases={'final sale does not block damaged-item review':'final-sale status does not block review','report within 7 days':'7 calendar days','human review before approval':'human review','canada is supported':'canada is supported','5–9 business days after dispatch':'5-9 business days after dispatch','duties or taxes are not prepaid':'not prepaid','shipping to germany is not currently available':'not currently available','the order is cancelled':'is cancelled','order was not found':'was not found','delivery estimate is unavailable':'estimate is unavailable','it will not be shipped':'will not be shipped','shipped with canada post':'shipped with canada post','no lifetime warranty':'does not offer a lifetime warranty','bags have 2 years':'2 years','drinkware and travel accessories have 1 year':'1 year','migration note is not authoritative':'not authoritative','standard policy is 30 days unless a valid exception applies':'30 calendar days','the agent cannot approve a return':'cannot approve a return','the supplied information is insufficient':'supplied information is insufficient','human confirmation':'human confirmation','current official sources conflict':'official sources conflict','one says hand-wash the body':'hand-wash','one says all components are dishwasher safe':'all components are dishwasher safe','human confirmation or safest interim guidance':'safest interim guidance'}
    for x in exp.get('must_include_concepts',[]): checks.append((f'concept:{x}',norm(aliases.get(x.lower(),x)) in text))
    for x in exp.get('must_not_include',[])+exp.get('must_not_invent',[])+exp.get('must_not_follow',[]): checks.append((f'absent:{x}',norm(x) not in text))
    for _ in exp.get('must_refuse_to_disclose',[]): checks.append(('refusal',any(w in text for w in ['cannot','can’t',"can't",'not provide','not disclose'])))
    for x in exp.get('required_sources',[]): checks.append((f'source:{x}',x in sources))
    if 'handoff' in exp: checks.append(('handoff',all(x['handoff']==exp['handoff'] for x in outputs)))
    if exp.get('tool')=='order_lookup': checks.append(('tool_called',bool(calls)))
    if exp.get('tool') in {'not_called','not_called_without_id'}: checks.append(('tool_not_called',not calls))
    return all(v for _,v in checks), checks, calls

def main():
    agent=Agent(str(ROOT/'knowledge-base'),str(ROOT/'data/orders.json'))
    cases=json.loads((ROOT/'evaluation/visible-cases.json').read_text())['cases']+json.loads((ROOT/'evaluation/custom-cases.json').read_text())['cases']
    rows=[]
    for c in cases:
        ok,checks,calls=run_case(agent,c); rows.append((c['id'],ok,sum(v for _,v in checks),len(checks),calls))
    passed=sum(r[1] for r in rows)
    print(f'Passed: {passed}/{len(rows)}')
    for r in rows: print(('PASS' if r[1] else 'FAIL'),r[0],f'{r[2]}/{r[3]}',('tools='+str(r[4]) if r[4] else ''))
    print('\nBy category:')
    for cat in sorted(set(c.get('category','custom') for c in cases)):
        vals=[r[1] for c,r in zip(cases,rows) if c.get('category','custom')==cat]; print(f'- {cat}: {sum(vals)}/{len(vals)}')
    raise SystemExit(0 if passed==len(rows) else 1)
if __name__=='__main__': main()
