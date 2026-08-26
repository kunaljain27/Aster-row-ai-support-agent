from __future__ import annotations
import json, re
from pathlib import Path
from datetime import datetime

SAFE_FIELDS = {'order_id','status','shipped_at','delivered_at','carrier','tracking_number','estimated_delivery','customer_safe_message','items'}

def load_orders(path='data/orders.json'):
    with open(path, encoding='utf-8') as f: return {o['order_id']:o for o in json.load(f)['orders']}

class OrderLookup:
    def __init__(self, path='data/orders.json'):
        self.orders=load_orders(path); self.calls=[]

    def lookup(self, order_id: str):
        normalized=(order_id or '').strip().upper()
        self.calls.append(normalized)
        if not re.fullmatch(r'ORD-[0-9]{4}', normalized): return {'found':False,'reason':'malformed','order_id':normalized}
        o=self.orders.get(normalized)
        if not o: return {'found':False,'reason':'not_found','order_id':normalized}
        result={k:o[k] for k in SAFE_FIELDS if k in o}
        result['items']=[{'sku':x['sku'],'name':x['name'],'quantity':x['quantity']} for x in o.get('items',[])]
        if o['status'] in {'cancelled','returned'}:
            result['carrier']=None; result['tracking_number']=None; result['estimated_delivery']=None
        return {'found':True,**result}
