"""Executa a verificação, SQL, exportação e geração do projeto Power BI.
Use --nova-base dados/reproducao.sqlite para gerar outra base sem sobrescrever.
"""
import argparse,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--nova-base",type=Path)
args=p.parse_args()
def executar(script,*argumentos):
 print("Executando:",script,flush=True)
 subprocess.run([sys.executable,str(BASE/script),*map(str,argumentos)],cwd=BASE,check=True)
banco=args.nova_base
if banco is not None:
 banco=banco.resolve()
 executar("simular_operacao.py","--banco",banco)
else:
 banco=BASE/"dados/supply_chain_2024_2025.sqlite"
 if not banco.exists():executar("simular_operacao.py")
executar("testar_ddl.py")
# O teste de regressão usa a base padrão entregue, em cópia isolada.
if (BASE/"dados/supply_chain_2024_2025.sqlite").exists():executar("testar_operacao.py")
executar("preparar_analytics.py","--banco",banco)
executar("construir_powerbi.py")
executar("configurar_powerbi.py")
print("Etapas automáticas concluídas. Abra powerbi/SupplyChain.pbip e atualize os dados no Desktop.")
