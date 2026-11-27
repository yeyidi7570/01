import os,json,time,pathlib,sys
os.environ['PADDLE_PDX_CACHE_HOME']='/workspace/ocr_work/cache';os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK']='True';os.environ['XDG_CACHE_HOME']='/workspace/ocr_work/cache';os.environ['HF_HOME']='/workspace/ocr_work/cache/hf';os.environ['OMP_NUM_THREADS']='2'
from paddleocr import PaddleOCR
ocr=PaddleOCR(text_detection_model_name='PP-OCRv5_mobile_det',text_recognition_model_name='cyrillic_PP-OCRv5_mobile_rec',use_doc_orientation_classify=False,use_doc_unwarping=False,use_textline_orientation=False,device='cpu',cpu_threads=2,enable_mkldnn=True,text_det_limit_side_len=1800,text_det_limit_type='max',text_recognition_batch_size=16,text_rec_score_thresh=0.0)
P=pathlib.Path('/workspace/math2026p2_work');worker=int(sys.argv[1]) if len(sys.argv)>1 else 0;workers=int(sys.argv[2]) if len(sys.argv)>2 else 1
order=[start+k for k in range(30) for start in [1,31,61,91,121,151]];order=order[worker::workers]
for n in order:
 f=P/'raw'/f'{n:03}.json'
 if f.exists():continue
 im=P/'original'/f'{n:03}.png'
 while not im.exists():time.sleep(1)
 t=time.time();r=ocr.predict(str(im))[0];d=r.json
 if isinstance(d,str):d=json.loads(d)
 d=d.get('res',d);lines=[]
 for i,(s,b,sc) in enumerate(zip(d['rec_texts'],d['rec_polys'],d['rec_scores'])):
  xx=[p[0] for p in b];yy=[p[1] for p in b];lines.append({'id':str(i),'text':s,'bbox':[min(xx),min(yy),max(xx),max(yy)],'poly':b,'score':sc})
 lines.sort(key=lambda z:(round(z['bbox'][1]/7),z['bbox'][0]))
 data={'page':n,'pdf_page_number':n,'width':1190,'height':1684,'lines':lines,'provenance':{'engine':'PP-OCRv5','detection':'PP-OCRv5_mobile_det','recognition':'cyrillic_PP-OCRv5_mobile_rec','language':'kk-Cyrl'}}
 tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));tmp.replace(f)
 (P/'raw'/f'{n:03}.txt').write_text('\n'.join(f"{a['id']} | {a['text']}" for a in lines));print(n,len(lines),round(time.time()-t,2),flush=True)
