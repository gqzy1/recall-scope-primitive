"""Real pinned SDK direct-mode checks, mocked external facts. Not network consensus."""
from pathlib import Path
import json
import sys
import subprocess
from gltest.direct import sdk_loader

# Use the linter asset resolver; gltest 0.29.2 assumes an obsolete release asset URL.
subprocess.run([str(Path(sys.executable).with_name("genvm-lint")), "download", "--version", "v0.3.0-rc7"], check=True)
sdk_loader.CACHE_DIR = Path.home() / ".cache" / "genvm-linter"
from gltest.direct import VMContext,deploy_contract
p=Path(__file__).resolve().parents[1]/'contracts/recall_scope.py'
vm=VMContext()
notice='Recall Date: June 12, 2025. Description: Anker PowerCore 10000 model A1263. Sold in United States. Check serial number with manufacturer. Remedy: Contact manufacturer. '+('Official details. '*30)
result={k:{'label':'UNKNOWN','quote':'','reason':'The required evidence is not provided.'} for k in ['identity','variant','period','region']}
result['identity']={'label':'MATCH','quote':'Anker PowerCore 10000','reason':'The named brand and product family match.'}
vm.mock_web('cpsc',{'status':200,'body':notice})
vm.mock_llm('(?s)^Evaluate ONE(?!.*FINAL TASK: Audit)',json.dumps(result))
vm.mock_llm('FINAL TASK: Audit',json.dumps({'supported':True}))
d={'notice_url':'https://www.cpsc.gov/Recalls/2025/Example-Notice','product':{'brand':'Anker','model':'A1263','batch':'','original_sale':'','region':'United States','details':''}}
with vm.activate():
 c=deploy_contract(p,vm,sdk_version='v0.3.0-rc7')
 print('DEPLOYED_REAL_SDK',type(c).__name__)
 r=json.loads(c.assess('sdk-one',json.dumps(d)))
 assert r['state']=='NEEDS_DETAILS'
 assert c.get_count(r['owner'])==1
 assert json.loads(c.get_record(r['owner'],'sdk-one'))==r
 assert json.loads(c.assess('sdk-one',json.dumps(d)))==r
 print('REAL_SDK_STORAGE_READBACK_AND_IDEMPOTENCE_PASS',r['notice_sha256'])
 assert vm.run_validator() is True
 print('REAL_SDK_VALIDATOR_ACCEPT_PASS')
 vm.clear_mocks()
 vm.mock_llm('(?s)^Evaluate ONE(?!.*FINAL TASK: Audit)',json.dumps(result))
 vm.mock_llm('FINAL TASK: Audit',json.dumps({'supported':False}))
 assert vm.run_validator() is False
 print('REAL_SDK_UNSUPPORTED_EVIDENCE_REJECTION_PASS')
 import cloudpickle
 for i,(_,leader,validator) in enumerate(vm._captured_validators):
  for name,fn in [('leader',leader),('validator',validator)]:
   encoded=cloudpickle.dumps(fn)
   print('CALLBACK_SERIALIZATION_PASS',i,name,len(encoded))
