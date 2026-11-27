import os,pathlib,json,time
os.environ['PADDLE_PDX_CACHE_HOME']='/workspace/ocr_work/cache';os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK']='True';os.environ['XDG_CACHE_HOME']='/workspace/ocr_work/cache';os.environ['HF_HOME']='/workspace/ocr_work/cache/hf'
from paddleocr import LayoutDetection
m=LayoutDetection(model_name='PP-DocLayout-S',device='cpu',cpu_threads=1,enable_mkldnn=True)
P=pathlib.Path('/workspace/math2026p2_work')
for n in range(1,181):
 f=P/'layout'/f'{n:03}.json'
 if f.exists():continue
 image=P/'original'/f'{n:03}.png'
 while not image.exists():time.sleep(1)
 r=list(m.predict(str(image)))[0];d=r.json
 if isinstance(d,str):d=json.loads(d)
 f.write_text(json.dumps(d,ensure_ascii=False,indent=2));print(n,flush=True)
