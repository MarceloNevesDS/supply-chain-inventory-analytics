"""Ajusta a origem CSV ao local onde este pacote foi extraído."""
import json
from pathlib import Path
base=Path(__file__).resolve().parent
arquivo=base/"powerbi/SupplyChain.SemanticModel/model.bim"
obj=json.loads(arquivo.read_text(encoding="utf-8"))
param=next(x for x in obj["model"]["expressions"] if x["name"]=="pPastaDados")
param["expression"]=json.dumps((base/"powerbi/dados").as_posix(),ensure_ascii=False)+' meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
arquivo.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
print("Origem Power BI configurada:",base/"powerbi/dados")