import re

PRIVATE_PATTERNS=[r'email',r'address',r'internal note',r'risk score',r'fraud review',r'hidden prompt',r'system prompt',r'credentials?',r'api key',r'secret']
ACTION_PATTERNS=[r'approve',r'issue a refund',r'cancel\b',r'replace',r'price adjustment',r'change (my )?address']

def asks_private(q): return any(re.search(p,q,re.I) for p in PRIVATE_PATTERNS)
def asks_action(q): return any(re.search(p,q,re.I) for p in ACTION_PATTERNS)

def is_order_query(q): return bool(re.search(r'\bORD[- ]?\d{4}\b|\bmy order\b|\bwhere is my order\b|\bwhen will.*order',q,re.I))
def extract_order_id(text):
    m=re.search(r'\bORD[- ]?(\d{4})\b', text, re.I)
    return f'ORD-{m.group(1)}' if m else None
