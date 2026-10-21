import json
from pathlib import Path
from jsonschema import Draft7Validator
from referencing import Registry, Resource
BASE=Path(__file__).resolve().parent
schemas=json.loads((BASE/"powerbi/schemas/registry.json").read_text(encoding="utf-8"))
registry=Registry()
for url,sch in schemas.items():
 registry=registry.with_resource(url,Resource.from_contents(sch))
erros=[];n=0
for p in (BASE/"powerbi").rglob("*"):
 if p.suffix not in (".json",".pbip",".pbir",".pbism"):continue
 obj=json.loads(p.read_text(encoding="utf-8"))
 if "$schema" not in obj:continue
 n+=1
 for e in Draft7Validator(schemas[obj["$schema"]],registry=registry).iter_errors(obj):
  erros.append(dict(arquivo=str(p.relative_to(BASE)),caminho="/".join(map(str,e.absolute_path)),erro=e.message))
# Validação estrutural do modelo sem motor DAX.
m=json.loads((BASE/"powerbi/SupplyChain.SemanticModel/model.bim").read_text(encoding="utf-8"))["model"]
tabs={t["name"]:{c["name"] for c in t["columns"]} for t in m["tables"]}
for r in m["relationships"]:
 if r["fromColumn"] not in tabs[r["fromTable"]] or r["toColumn"] not in tabs[r["toTable"]]:raise ValueError(r)
 if r["fromTable"].startswith("fato_") and r["toTable"].startswith("fato_"):raise ValueError("Relação entre fatos")
rel=dict(arquivos_pbir_validados=n,erros=erros,modelo_estrutura="referências de relações conferidas",
 limite="Sem execução do Power Query/DAX ou renderização no Power BI Desktop.")
(BASE/"resultados/powerbi_validacao.json").write_text(json.dumps(rel,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(rel,ensure_ascii=True,indent=2))
if erros:raise SystemExit(1)
