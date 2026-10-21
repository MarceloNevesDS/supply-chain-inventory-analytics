"""Testes de regressão: fórmulas e detecção de corrupção, sem alterar o banco entregue."""
import json
from pathlib import Path
import sqlite3
from decimal import Decimal as D
from simular_operacao import custo_apos_entrada, validar_operacao

base=Path(__file__).resolve().parent
aprovados=[]
for saldo,custo,qtd,entrada,esperado in [
    (10,D(20),10,D(30),D(25)),
    (0,D(99),5,D(12),D(12)),
    (10,D(25),5,D(25),D(25)),
    (3,D(10),2,D(11),D("10.4"))]:
    if custo_apos_entrada(saldo,custo,qtd,entrada)!=esperado:
        raise AssertionError("Custo médio incorreto")
    aprovados.append(f"Custo médio {saldo}@{custo} + {qtd}@{entrada} = {esperado}")

# Uma cópia em memória recebe alterações inválidas.
origem=sqlite3.connect(f"file:{(base/'dados'/'supply_chain_2024_2025.sqlite').as_posix()}?mode=ro",uri=True)
con=sqlite3.connect(":memory:")
origem.backup(con)
origem.close()
con.execute("pragma foreign_keys=on")
casos=[
  ("Recebimento acima do pedido","update fato_recebimento set qt_recebida=999999,vl_total_recebido=999999*vl_custo_unitario_recebido where id_recebimento=1","excesso_recebido"),
  ("Produto divergente na origem","update fato_recebimento set id_produto=case when id_produto=1 then 2 else 1 end where id_recebimento=1","origem_recebimento"),
  ("Pendência diária adulterada","update fato_estoque_diario set qt_compra_pendente=qt_compra_pendente+1 where id_data_estoque=20241231 and id_produto=1 and id_centro_distribuicao=1","pendencia_diaria"),
  ("Valor do fechamento adulterado","update fato_estoque_diario set vl_estoque_final=vl_estoque_final+1 where id_data_estoque=20241231 and id_produto=1 and id_centro_distribuicao=1","Valor diário divergente"),
]
for nome,sql,mensagem in casos:
    con.execute("savepoint caso")
    try:
        con.execute(sql)
        try:
            validar_operacao(con)
        except ValueError as e:
            if mensagem not in str(e):
                raise
            aprovados.append(nome)
        else:
            raise AssertionError(f"Auditoria aceitou corrupção: {nome}")
    finally:
        con.execute("rollback to caso")
        con.execute("release caso")
con.close()
relatorio=dict(testes_aprovados=len(aprovados),casos=aprovados)
(base/"testes_operacao.json").write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(relatorio,ensure_ascii=True,indent=2))
