"""Host regression tests for the actual S3 GPIO and UI policy, no hardware access."""
from pathlib import Path
import json
import re
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
def read(p): return (ROOT / p).read_text()
def function(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return text[start:end]

class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.tags=[]; self.feed(html)
    def handle_starttag(self, tag, attrs): self.tags.append((tag,dict(attrs)))

class S3Contract(unittest.TestCase):
    def test_gpio_interlocks_execute_actual_setRelay(self):
        # Compile the firmware implementation with mocked GPIO/FreeRTOS only.
        code = '''#include <cassert>
#include "board_profile.h"
constexpr int NUM_RELAYS=8, HIGH=1, LOW=0, pdTRUE=1;
int activeRelayCount=6; int relayPins[]={1,2,41,42,45,46,-1,-1};
bool relayStates[8]={}, relayActive[8]={};
bool irrigationStopRequested=false;
struct {bool pumpEnabled[3]={true,true,true};} irrigation;
int relayMutex=1; bool mutexAvailable=true; int writes=0;
int xSemaphoreTake(int,int){return mutexAvailable;} void xSemaphoreGive(int){}
int pdMS_TO_TICKS(int n){return n;} void logPrint(const char*){}
void digitalWrite(int pin,int state){assert(pin>=0); (void)state; ++writes;}
'''+function(read('src/function.h'),'void setRelay(int idx, bool on)')+'''
void reset(){for(int i=0;i<8;i++){relayStates[i]=false;relayActive[i]=false;} for(int i=0;i<3;i++)irrigation.pumpEnabled[i]=true; irrigationStopRequested=false; writes=0;mutexAvailable=true;}
int main(){
 for(int i=-2;i<=9;i++){
   assert(isControlRelayIndex(i)==(i>=3&&i<=5));
   assert(isPumpRelayIndex(i)==(i>=0&&i<=2));
   assert(isValidBoardHeatingRelay(i)==(i>=4&&i<=6));
   assert(isValidBoardRelayCount(i)==(i==6));
 }
 for(int pump=0;pump<3;pump++){
   reset(); irrigation.pumpEnabled[pump]=false; setRelay(pump,true);assert(writes==0);
   setRelay(pump,false);assert(writes==1); // disabled pumps must still stop
   reset(); irrigationStopRequested=true;setRelay(pump,true);assert(writes==0);
   for(int other=0;other<3;other++)if(other!=pump){
     reset();relayStates[other]=true;setRelay(pump,true);assert(writes==0);
     reset();relayActive[other]=true;setRelay(pump,true);assert(writes==0);
   }
   reset();setRelay(pump,true);assert(relayStates[pump]&&writes==1);
   setRelay(pump,false);assert(!relayStates[pump]&&writes==2);
 }
 for(int i=3;i<6;i++){reset();setRelay(i,true);assert(relayStates[i]&&writes==1);}
 for(int i: {-1,6,7,8}){reset();setRelay(i,true);assert(writes==0);}
 reset();mutexAvailable=false;setRelay(0,true);assert(writes==0);
 reset();relayMutex=0;setRelay(0,true);assert(writes==0);setRelay(0,false);assert(writes==1);
}
'''
        code=code.replace('#include <cassert>','#include <cassert>\n#include <initializer_list>')
        with tempfile.TemporaryDirectory() as d:
            cpp=Path(d)/'test.cpp'; binary=Path(d)/'test';cpp.write_text(code)
            subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-I',str(ROOT/'src'),str(cpp),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)

    def test_dom_has_one_control_per_physical_output(self):
        tags=Tags(read('src/index_html.h')).tags
        ids=[a['id'] for _,a in tags if 'id' in a]
        self.assertEqual(len(ids),len(set(ids)), 'Duplicate HTML IDs')
        for n in range(1,7): self.assertIn(f'relay-Status{n}',ids)
        for n in range(1,4):
            self.assertIn(f'pumpButton{n}',ids)
            self.assertNotIn(f'espRelay{n}Row',ids)
            self.assertNotIn(f'webRelayName{n}',ids)
        for n in range(4,7):
            self.assertIn(f'espRelay{n}Row',ids)
            self.assertIn(f'webRelayName{n}',ids)
        for _,a in tags:
            if re.match(r'espRelay[456](On|Off)Min',a.get('id','')): self.assertEqual(a['max'],'59')
        self.assertNotIn('"relays[6]',read('src/vars_registry.cpp'))
        self.assertNotIn('"relays[7]',read('src/vars_registry.cpp'))

    def test_actual_browser_functions_use_s3_mapping(self):
        js=read('src/java_script.h')
        snippets=[]
        for signature in ['function applyRelayVisibility(relayCount)', 'window.refreshRelayStatesDirect = async function', 'window.toggleRelay = async function']:
            snippets.append(function(js,signature)+';')
        # Default function arg refers to RELAY_COUNT; provide the actual S3 count.
        script='''const assert=require('node:assert/strict');
const nodes=new Map(); const fetches=[];
const document={getElementById(id){if(!nodes.has(id))nodes.set(id,{style:{},dataset:{}});return nodes.get(id)},querySelector(){return null}};
const window={_relayPendingCount:0,_relayDirectRefreshSeq:0,updateRelayButtons(){}};let RELAY_COUNT=6;let relayStates=Array(8).fill(false);
async function fetch(url){fetches.push(url);return{ok:true,json:async()=>({stateReadable:true,state:true})}}
'''+ '\n'.join(snippets)+'''
(async()=>{
 applyRelayVisibility(6);assert.equal(nodes.get('irrigationSection').style.display,'');
 assert.equal(nodes.get('espRelay6Row').style.display,'');
 assert.equal(nodes.get('settingsRelay6Row').style.display,'');
 await window.refreshRelayStatesDirect(6);
 assert.deepEqual(fetches.map(s=>s.match(/relay\\/(\\d)/)[1]),['4','5','6']);
 fetches.length=0;for(const n of [0,1,2,3,7,8])await window.toggleRelay(n);
 assert.equal(fetches.length,0,'Generic pump toggle must never send requests');
})().catch(e=>{console.error(e);process.exitCode=1});
'''
        subprocess.run(['node','-e',script],check=True)

    def test_payload_and_script_syntax(self):
        js=read('src/java_script.h').split('R"rawliteral(',1)[1].rsplit(')rawliteral";',1)[0]
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'payload.js';file.write_text(js)
            subprocess.run(['node','--check',str(file)],check=True)
        for file in ['tests/test_async_transport_stress.sh','tests/test_ota_transport.sh']:
            subprocess.run(['bash','-n',str(ROOT/file)],check=True)

    def test_api_and_persistence_guards(self):
        main=read('src/main.cpp');runtime=read('src/runtime.h')
        for name in ['handleAsyncRelayNamePost','handleAsyncRelaySchedulePost','handleAsyncRelaySetPost','queueAsyncRelayAction']:
            self.assertIn('isControlRelayIndex(idx)',function(main,'static void '+name+'('))
        self.assertIn('!isControlRelayIndex(pending.relayIndex)',function(main,'static void processAsyncRelayScheduleApply('))
        self.assertIn('!irrigation.pumpEnabled[pending.pumpSlot]',function(main,'static void processAsyncWateringActionApply('))
        self.assertNotRegex(main,r'/pump/[678]/triggerPump10s')
        self.assertIn('!isValidBoardHeatingRelay(settings.heating.Relay)',runtime)
        self.assertIn('KEY_RELAY_START_6',runtime)
        self.assertIn('GITHUB_REPO = "GrowTent-S3"',read('src/ota.cpp'))
        self.assertNotIn('nodemcu-32s',read('.github/workflows/release-firmware.yml'))

if __name__=='__main__': unittest.main()
