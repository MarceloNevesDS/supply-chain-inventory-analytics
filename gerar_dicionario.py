import json,sqlite3,csv
from pathlib import Path
BASE=Path(__file__).resolve().parent
con=sqlite3.connect(BASE/"dados/supply_chain_2024_2025.sqlite")
grains={
"dim_data":"Um dia","dim_produto":"Um produto","dim_fornecedor":"Um fornecedor",
"dim_centro_distribuicao":"Um centro","dim_tipo_movimento":"Um tipo",
"fato_item_compra":"Um item de pedido","fato_recebimento":"Uma parcela recebida de um item",
"fato_movimento_estoque":"Um evento de um produto/centro",
"fato_estoque_diario":"Um produto/centro/data","aux_produto_centro":"Uma vigência de produto/centro"}
parts=["# Dicionário e modelo de dados","\nPrefixos: id identificador; cd código; dt data/instante; nm nome; vl valor; nr número; sg sigla; tx descrição; qt quantidade; in indicador.\n"]
for table in grains:
 fk={r[3]:r[2]+"."+r[4] for r in con.execute(f"pragma foreign_key_list({table})")}
 parts+=["\n## "+table,"Granularidade: "+grains[table]+".","\n| Coluna | Tipo SQLite | Obrigatória | PK | Referência |","|---|---|---|---|---|"]
 for _,name,typ,nn,default,pk in con.execute(f"pragma table_info({table})"):
  parts.append(f"| {name} | {typ} | {'Sim' if nn or pk else 'Não'} | {pk or '—'} | {fk.get(name,'—')} |")
parts+=["\n## Camada analítica do Power BI",
"CSV fato_estoque_diario deriva de vw_estoque_analitico; fato_item_compra deriva de vw_compras_posicao_final.",
"Essas exportações incluem as colunas originais e atributos calculados; a DDL original não foi modificada.",
"\n| Atributo derivado | Significado |","|---|---|",
"| dt_estoque | Data do fechamento |",
"| qt_expedida_dia | Saídas do dia, apenas expedições |",
"| qt_expedida_90d | Saídas da janela de até 90 dias |",
"| nr_dias_observados | Quantidade de dias da janela |",
"| qt_demanda_media_dia | Média das expedições na janela |",
"| qt_posicao_estoque | Saldo físico + compra pendente |",
"| qt_estoque_seguranca | Média × dias de segurança, arredondada para cima |",
"| qt_ponto_reposicao | Média × (prazo + segurança), arredondada para cima |",
"| nr_dias_cobertura | Saldo / média; nulo sem demanda |",
"| in_reposicao | Posição <= ponto e demanda positiva |",
"| in_risco_espera | Saldo < demanda esperada no prazo |",
"| in_cobertura_elevada | Cobertura > 90 dias |",
"| in_sem_saida | Saldo positivo, janela completa e zero saída |",
"| in_indisponivel | Saldo zero e demanda observada positiva |",
"| tx_situacao_estoque | Classificação priorizada; flags podem coexistir |",
"| id_data_referencia | Corte da posição de compras |",
"| qt_recebida / qt_pendente | Recebimentos e saldo contratado até o corte |",
"| qt_recebida_no_prazo | Quantidade recebida até a previsão original |",
"| id_data_conclusao | Data da entrega integral, se concluído |",
"| in_vencido_ate_referencia | Previsão até o corte, inclusive |",
"| in_integral_no_prazo | Toda a quantidade recebida até a previsão |",
"| tx_status | Em aberto, parcialmente recebido, concluído |",
"| nr_dias_entrega_completa | Dias corridos emissão → conclusão |",
"| in_pendente_atrasado | Quantidade pendente e previsão anterior ao corte |"]
m=json.loads((BASE/"powerbi/SupplyChain.SemanticModel/model.bim").read_text(encoding="utf-8"))
parts+=["\n## Relações no Power BI","\n| Origem (N) | Destino (1) | Ativa |","|---|---|---|"]
for r in m["model"]["relationships"]:
 parts.append(f'| {r["fromTable"]}.{r["fromColumn"]} | {r["toTable"]}.{r["toColumn"]} | {"Sim" if r["isActive"] else "Não"} |')
(BASE/"docs/03_dicionario_de_dados.md").write_text("\n".join(parts),encoding="utf-8")
con.close()
print("Dicionário gerado.")
