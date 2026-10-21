import os
from pathlib import Path
BASE=Path(__file__).resolve().parent
os.environ["MPLCONFIGDIR"]=str(BASE/"resultados/matplotlib_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sqlite3,json
con=sqlite3.connect(BASE/"dados/supply_chain_2024_2025.sqlite")
dados=json.loads((BASE/"resultados/indicadores.json").read_text(encoding="utf-8"))
mensal=con.execute("""with ult as (select d.nr_ano_mes,max(e.id_data_estoque) id
 from fato_estoque_diario e join dim_data d on d.id_data=e.id_data_estoque group by 1)
 select u.nr_ano_mes,sum(e.vl_estoque_final) from ult u join fato_estoque_diario e on e.id_data_estoque=u.id group by 1 order by 1""").fetchall()
cd=con.execute("""select c.nm_cidade,sum(e.vl_estoque_final) from fato_estoque_diario e
 join dim_centro_distribuicao c using(id_centro_distribuicao) where id_data_estoque=20251231 group by 1""").fetchall()
forn=con.execute("""select f.cd_fornecedor,100.0*sum(v.in_integral_no_prazo)/sum(v.in_vencido_ate_referencia)
 from vw_compras_posicao_final v join dim_fornecedor f using(id_fornecedor) group by 1 order by 2""").fetchall()
exp=con.execute("""select d.nr_ano_mes,sum(m.qt_movimento) from fato_movimento_estoque m
 join dim_data d on d.id_data=m.id_data_movimento where id_tipo_movimento=3 group by 1 order by 1""").fetchall()
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,"axes.spines.right":False})
fig,axs=plt.subplots(2,2,figsize=(15,10))
fig.patch.set_facecolor("#F4F7FA")
fig.suptitle("NEXO  |  Supply Chain & Inventory Analytics",x=.06,ha="left",fontsize=23,color="#18344A",fontweight="bold",y=.97)
fig.text(.06,.91,"Estoque final: R$ 2.951.164,50     •     90 combinações em risco     •     Pontualidade: 27,26%",fontsize=13,color="#147D92")
fig.text(.06,.88,"Dados fictícios • 2024–2025 • posições em 31/12/2025 • figura estática de conferência, não captura do Power BI",fontsize=10,color="#435A78")
x=list(range(len(mensal)))
axs[0,0].plot(x,[v/1e6 for _,v in mensal],color="#147D92",lw=2.5)
axs[0,0].set(title="Estoque no fechamento mensal",ylabel="R$ milhões")
axs[0,0].set_xticks(x[::3],[str(d)[:4]+"-"+str(d)[4:] for d,_ in mensal][::3],rotation=20)
axs[0,1].barh([r[0] for r in cd],[r[1]/1e6 for r in cd],color="#147D92")
axs[0,1].set(title="Estoque por centro • corte final",xlabel="R$ milhões")
axs[1,0].bar(x,[v/1000 for _,v in exp],color="#435A78")
axs[1,0].set(title="Expedições mensais",ylabel="Mil unidades")
axs[1,0].set_xticks(x[::3],[str(d)[:4]+"-"+str(d)[4:] for d,_ in exp][::3],rotation=20)
axs[1,1].barh([r[0] for r in forn],[r[1] for r in forn],color="#E09B36")
axs[1,1].set(title="Itens integralmente no prazo • corte final",xlabel="% dos itens com vencimento até o corte",xlim=(0,100))
for ax in axs.flat:
 ax.grid(axis="x" if ax in [axs[0,1],axs[1,1]] else "y",alpha=.15);ax.set_axisbelow(True)
fig.tight_layout(rect=(.03,.03,.98,.85),h_pad=3,w_pad=3)
fig.savefig(BASE/"resultados/resumo_executivo.png",dpi=150,facecolor=fig.get_facecolor())
con.close()
print("Resumo visual gerado.")
