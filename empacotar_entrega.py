from pathlib import Path
import json,hashlib,zipfile
BASE=Path(__file__).resolve().parent
selecionados=[]
for p in BASE.rglob("*"):
 if not p.is_file():continue
 rel=p.relative_to(BASE)
 if any(x in ("__pycache__","matplotlib_cache") or x.startswith("tmp") for x in rel.parts):continue
 if p.suffix in (".log",".pyc"):continue
 if rel.as_posix()=="manifesto_sha256.json":continue
 selecionados.append(p)
manifesto={str(p.relative_to(BASE)).replace("\\","/"):hashlib.sha256(p.read_bytes()).hexdigest() for p in selecionados}
(BASE/"manifesto_sha256.json").write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding="utf-8")
selecionados.append(BASE/"manifesto_sha256.json")
zip_path=BASE.parent/"Supply_Chain_Entrega_Final.zip"
with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in selecionados:z.write(p,p.relative_to(BASE).as_posix())
with zipfile.ZipFile(zip_path) as z:
 if z.testzip() is not None:raise ValueError("ZIP corrompido")
print(json.dumps(dict(arquivos=len(selecionados),bytes=zip_path.stat().st_size)))
