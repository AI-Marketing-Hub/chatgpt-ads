"""Source-checkout convenience dispatcher; the portable ZIP is the supported distribution."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main(argv=None):
 p=argparse.ArgumentParser(description='ChatGPT Ads local tools')
 p.add_argument('command',choices=['query','knowledge','operate','validate']);p.add_argument('arguments',nargs=argparse.REMAINDER);a=p.parse_args(argv)
 scripts={'query':'query_brain.py','knowledge':'knowledge_core.py','operate':'operating_core.py','validate':'validate_pack.py'}
 return subprocess.call([sys.executable,str(ROOT/'scripts'/scripts[a.command]),*a.arguments])
if __name__=='__main__':raise SystemExit(main())
