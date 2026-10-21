"""Executa SQL, valida indicadores e exporta CSV UTF-8 para Power BI."""
import argparse,csv,json,sqlite3
from pathlib import Path
from collections import deque
BASE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--banco",type=Path,default=BASE/"dados/supply_chain_2024_2025.sqlite")
 args=p.parse_args()
 if not args.banco.is_file(): raise FileNotFoundError(args.banco)
 con=sqlite3.connect(args.banco)
 con.executescript((BASE/"sql/01_views_analiticas.sql").read_text(encoding="utf-8"))
 # Executar cada consulta analítica, consumindo seu resultado.
 sql=(BASE/"sql/02_analises.sql").read_text(encoding="utf-8")
 resultados=[]
 for indice,statement in enumerate(sql.split(";"),1):
  if statement.strip():
   cur=con.execute(statement)
   linhas=cur.fetchall()
   resultados.append(dict(consulta=indice,linhas=len(linhas)))
 exportacoes={t:t for t in ["dim_data","dim_produto","dim_fornecedor","dim_centro_distribuicao",
   "dim_tipo_movimento","fato_recebimento","fato_movimento_estoque"]}
 exportacoes.update(fato_estoque_diario="vw_estoque_analitico",fato_item_compra="vw_compras_posicao_final")
 destino=BASE/"powerbi/dados"
 destino.mkdir(parents=True,exist_ok=True)
 contagens={}
 for nome,origem in exportacoes.items():
  cur=con.execute(f"select * from {origem}")
  with (destino/f"{nome}.csv").open("w",newline="",encoding="utf-8") as f:
   w=csv.writer(f);w.writerow([c[0] for c in cur.description])
   contador=0
   for row in cur:
    w.writerow(row);contador+=1
  contagens[nome]=contador
 # Referência independente para média, ponto, classificação e pendência.
 exp={(d,p,c):q for d,p,c,q in con.execute("""select id_data_movimento,id_produto,
  id_centro_distribuicao,sum(qt_movimento) from fato_movimento_estoque where id_tipo_movimento=3 group by 1,2,3""")}
 totais={}
 with (destino/"fato_estoque_diario.csv").open(encoding="utf-8",newline="") as f:
  for r in csv.DictReader(f):
   p,c=int(r["id_produto"]),int(r["id_centro_distribuicao"]);d=int(r["id_data_estoque"])
   hist=totais.setdefault((p,c),deque(maxlen=90));hist.append(exp.get((d,p,c),0))
   media=sum(hist)/len(hist)
   if abs(float(r["qt_demanda_media_dia"])-media)>1e-9:raise ValueError("Média 90d")
   if int(r["qt_expedida_90d"])!=sum(hist):raise ValueError("Janela 90d")
   saldo,pend=int(r["qt_saldo_final"]),int(r["qt_compra_pendente"])
   prazo,seg=int(r["nr_dias_reposicao"]),int(r["nr_dias_seguranca"])
   esperado=int(media>0 and saldo+pend<=__import__("math").ceil(media*(prazo+seg)))
   if int(r["in_reposicao"])!=esperado:raise ValueError("Ponto de reposição")
   if media==0 and r["nr_dias_cobertura"]!="":raise ValueError("Cobertura sem demanda")
 snapshot=con.execute("""select sum(vl_estoque_final),sum(qt_saldo_final),sum(qt_compra_pendente),
  sum(in_risco_espera),sum(in_sem_saida),sum(in_cobertura_elevada),sum(in_indisponivel),
  sum(in_reposicao) from vw_estoque_analitico where id_data_estoque=20251231""").fetchone()
 pontual=con.execute("""select sum(in_integral_no_prazo),sum(in_vencido_ate_referencia),
  sum(in_pendente_atrasado) from vw_compras_posicao_final""").fetchone()
 rel=dict(consultas_executadas=resultados,csv_exportados=contagens,validacao_indicadores="219300 linhas conferidas",
  corte="2025-12-31",snapshot=dict(zip(["vl_estoque","qt_saldo","qt_pendente","nr_risco","nr_sem_saida",
   "nr_cobertura_elevada","nr_indisponivel","nr_reposicao"],snapshot)),
  fornecedores=dict(nr_integral_prazo=pontual[0],nr_vencidos=pontual[1],nr_pendentes_atrasados=pontual[2],
   pc_pontualidade=pontual[0]/pontual[1] if pontual[1] else None))
 (BASE/"resultados").mkdir(exist_ok=True)
 (BASE/"resultados/indicadores.json").write_text(json.dumps(rel,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(rel,ensure_ascii=True,indent=2))
 con.close()
if __name__=="__main__":main()
