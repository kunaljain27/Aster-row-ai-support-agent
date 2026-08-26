import argparse, logging
from app import Agent, Session

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--debug',action='store_true'); args=ap.parse_args()
    logging.basicConfig(level=logging.INFO if args.debug else logging.WARNING)
    agent=Agent(); session=Session()
    print('Aster & Row Support Agent. Type "exit" to quit.')
    while True:
        try: q=input('\nYou: ').strip()
        except (EOFError,KeyboardInterrupt): break
        if q.lower() in {'exit','quit'}: break
        r=agent.ask(q,session); print('\nAgent:',r['answer'])
        if r['sources']: print('Sources:'); [print(' -',s) for s in r['sources']]
        if r['handoff']: print('Handoff: recommended')

if __name__=='__main__': main()
