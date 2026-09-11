#!/usr/bin/env python3
"""Serve a loopback-only synthetic Ads UI exercising the operating core. No external calls."""
import argparse,copy,json,tempfile
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
import operating_core as core
ROOT=Path(__file__).resolve().parents[1]
HTML='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ChatGPT Ads operating lab</title><style>body{font:17px system-ui;background:#f3f5f2;color:#163b33;max-width:900px;margin:60px auto;padding:24px}h1{font-size:40px}label{display:block;margin:24px 0 8px}select,button{font:inherit;padding:12px;border:1px solid #527267;border-radius:8px}button{background:#164c3d;color:white;cursor:pointer;margin:12px 8px 12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:24px;border-radius:12px}.badge{background:#dbe8d9;padding:8px 12px;border-radius:20px}#result{min-height:120px}</style><span class="badge">LOCAL SIMULATION · NO AD ACCOUNT</span><h1>ChatGPT Ads operating lab</h1><p>Exercise exact-action checks and uncertain-save recovery through the actual local Python operating core. Nothing here spends money or contacts an advertising service.</p><label for="scenario">Scenario</label><select id="scenario"><option value="success">Approved synthetic campaign</option><option value="wrong_account">Wrong account</option><option value="changed_ui">Changed UI</option><option value="changed_budget">Changed budget</option><option value="lost_session">Lost session</option><option value="uncertain">Save succeeded, acknowledgement lost</option><option value="expired">Expired approval</option></select><p><button id="run">Run scenario</button><button id="retry">Retry same operation</button></p><div role="status" aria-live="polite" id="summary">Choose a scenario.</div><pre id="result">No operation performed.</pre><script>async function run(retry){const res=await fetch('/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scenario:document.querySelector('#scenario').value,retry})});const x=await res.json();document.querySelector('#summary').textContent=x.error?'Error: '+x.error:'Outcome: '+x.receipt.outcome+' · Campaign count: '+x.campaign_count;document.querySelector('#result').textContent=JSON.stringify(x,null,2)}document.querySelector('#run').onclick=()=>run(false);document.querySelector('#retry').onclick=()=>run(true)</script></html>'''
class Lab:
 def __init__(self):self.tmp=None;self.ui=None
 def run(self,scenario,retry):
  if not retry:
   if self.tmp:self.tmp.cleanup()
   self.tmp=tempfile.TemporaryDirectory(prefix='chatgpt-ads-simulation-')
   self.action=json.loads((ROOT/'examples/operations/action-plan.json').read_text());self.plan=json.loads((ROOT/'examples/operations/campaign-plan.json').read_text());record=json.loads((ROOT/'examples/operations/simulated-ui-state.json').read_text())
   if scenario=='wrong_account':record['account_id']='different-account'
   if scenario=='changed_ui':record['ui_revision']='different-ui'
   if scenario=='changed_budget':
    key=next(k for k in record if 'budget' in k);record[key]*=10
   if scenario=='lost_session':record['session_active']=False
   if scenario=='uncertain':record['save_mode']='uncertain_after_create'
   if scenario=='expired':
    self.action['approval']=core.make_action_binding(self.action['action'],decision_id='expired-fixture',approved_by='Synthetic owner',approved_at='1999-01-01T00:00:00Z',expires_at='2000-01-01T00:00:00Z')
   self.ui=core.SimulatedAdsUI.from_record(record)
  if self.ui is None:raise ValueError('Run a scenario before retrying')
  receipt=core.execute_simulated(self.action,self.plan,self.ui,Path(self.tmp.name),'browser-lab')
  return {'receipt':receipt,'campaign_count':len(self.ui.campaigns),'simulated':True}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8765);a=p.parse_args();lab=Lab()
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_GET(self):
   if self.path!='/':self.send_error(404);return
   body=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def do_POST(self):
   if self.path!='/run':self.send_error(404);return
   try:
    n=int(self.headers.get('Content-Length','0'))
    if not 0<n<2048:raise ValueError('invalid request')
    x=json.loads(self.rfile.read(n));result=lab.run(x['scenario'],bool(x.get('retry',False)))
   except Exception as e:result={'error':str(e),'simulated':True}
   body=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 server=HTTPServer(('127.0.0.1',a.port),Handler);print('Synthetic lab at http://127.0.0.1:'+str(a.port),flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:
  server.server_close()
  if lab.tmp:lab.tmp.cleanup()
if __name__=='__main__':main()
