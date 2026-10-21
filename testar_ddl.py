"""Testes isolados em memória: nunca modifica o banco de demonstração."""
from pathlib import Path
import json
import sqlite3
from gerar_projeto import carregar, inserir, validar

base=Path(__file__).resolve().parent
con=sqlite3.connect(':memory:')
con.executescript((base/'modelo.sql').read_text(encoding='utf-8-sig'))
carregar(con)
validar(con)
inserir(con,'fato_item_compra',id_item_compra=1,nr_pedido='TESTE',nr_item=1,id_produto=1,
    id_fornecedor=1,id_centro_distribuicao=1,id_data_emissao=20240101,id_data_prevista=20240110,
    qt_pedida=10,vl_custo_unitario_pedido=10,vl_total_item=100)
inserir(con,'fato_recebimento',id_recebimento=1,id_item_compra=1,id_produto=1,id_fornecedor=1,
    id_centro_distribuicao=1,id_data_recebimento=20240110,dt_recebimento='2024-01-10 08:00:00',
    qt_recebida=5,vl_custo_unitario_recebido=10,vl_total_recebido=50)
inserir(con,'fato_movimento_estoque',id_produto=1,id_centro_distribuicao=1,id_tipo_movimento=2,
    id_data_movimento=20240110,id_recebimento=1,dt_movimento='2024-01-10 08:00:00',
    qt_movimento=5,qt_movimento_assinada=5,vl_custo_unitario_movimento=10,vl_movimento_assinado=50)
con.commit()
resultados=[]
def rejeitar(nome,sql,parametros=()):
    con.execute('savepoint caso')
    try:
        con.execute(sql,parametros)
    except sqlite3.IntegrityError:
        resultados.append(nome)
    else:
        raise AssertionError('Dado inválido foi aceito: '+nome)
    finally:
        con.execute('rollback to caso')
        con.execute('release caso')

# Testa cada FK, cada NOT NULL explícito e cada PK.
tabelas=[r[0] for r in con.execute("select name from sqlite_master where type='table'")]
for tabela in tabelas:
    for _,_,pai,coluna,*_ in con.execute(f'pragma foreign_key_list({tabela})').fetchall():
        rejeitar(f'FK {tabela}.{coluna}',f'update {tabela} set {coluna}=99999999 where rowid=(select min(rowid) from {tabela})')
    for _,coluna,tipo,obrigatorio,padrao,pk in con.execute(f'pragma table_info({tabela})').fetchall():
        if obrigatorio:
            rejeitar(f'NOT NULL {tabela}.{coluna}',f'update {tabela} set {coluna}=null where rowid=(select min(rowid) from {tabela})')
    rejeitar(f'PK {tabela}',f'insert into {tabela} select * from {tabela} limit 1')

casos=[('dim_data','nr_dia_mes',0),('dim_data','nr_dia_semana',8),('dim_data','nr_mes',13),
 ('dim_data','nr_bimestre',7),('dim_data','nr_trimestre',5),('dim_data','nr_semestre',3),
 ('dim_data','in_fim_semana',2),('dim_data','in_feriado_nacional',2),('dim_tipo_movimento','nr_sinal',0),
 ('fato_item_compra','nr_item',0),('fato_item_compra','qt_pedida',0),
 ('fato_item_compra','vl_custo_unitario_pedido',0),('fato_item_compra','vl_total_item',0),
 ('fato_item_compra','id_data_prevista',20240101),
 ('fato_recebimento','qt_recebida',0),('fato_recebimento','vl_custo_unitario_recebido',0),('fato_recebimento','vl_total_recebido',0),
 ('fato_movimento_estoque','qt_movimento',0),('fato_movimento_estoque','qt_movimento_assinada',9999),
 ('fato_movimento_estoque','vl_custo_unitario_movimento',0),('fato_movimento_estoque','vl_movimento_assinado',-1),
 ('fato_estoque_diario','qt_saldo_final',-1),('fato_estoque_diario','vl_custo_medio',-1),
 ('fato_estoque_diario','vl_estoque_final',-1),('fato_estoque_diario','qt_compra_pendente',-1),
 ('fato_estoque_diario','nr_dias_reposicao',0),('fato_estoque_diario','nr_dias_seguranca',-1),
 ('aux_produto_centro','nr_dias_reposicao',0),('aux_produto_centro','nr_dias_seguranca',-1),
 ('aux_produto_centro','dt_fim_vigencia','2023-12-31')]
# Ajuste da emissão permite testar previsão anterior usando uma data existente.
con.execute('update fato_item_compra set id_data_emissao=20240102')
con.commit()
for tabela,coluna,valor in casos:
    rejeitar(f'CHECK {tabela}.{coluna}',f'update {tabela} set {coluna}=? where rowid=(select min(rowid) from {tabela})',(valor,))
for tabela,coluna in [('dim_data','dt_data'),('dim_produto','cd_produto'),
 ('dim_centro_distribuicao','cd_centro_distribuicao'),('dim_fornecedor','cd_fornecedor'),('dim_tipo_movimento','cd_tipo_movimento')]:
    rejeitar(f'UNIQUE {tabela}.{coluna}',f'update {tabela} set {coluna}=(select {coluna} from {tabela} order by rowid limit 1) where rowid=(select max(rowid) from {tabela})')
rejeitar('UNIQUE pedido/item',"insert into fato_item_compra select 2,nr_pedido,nr_item,id_produto,id_fornecedor,id_centro_distribuicao,id_data_emissao,id_data_prevista,qt_pedida,vl_custo_unitario_pedido,vl_total_item from fato_item_compra where id_item_compra=1")
rejeitar('UNIQUE origem recebimento','insert into fato_movimento_estoque select 999999,id_produto,id_centro_distribuicao,id_tipo_movimento,id_data_movimento,id_recebimento,dt_movimento,qt_movimento,qt_movimento_assinada,vl_custo_unitario_movimento,vl_movimento_assinado,tx_motivo_ajuste from fato_movimento_estoque where id_recebimento=1')
rejeitar('UNIQUE início vigência','insert into aux_produto_centro select 999999,id_produto,id_centro_distribuicao,dt_inicio_vigencia,dt_fim_vigencia,nr_dias_reposicao,nr_dias_seguranca from aux_produto_centro limit 1')
rejeitar('Saldo positivo sem custo','update fato_estoque_diario set qt_saldo_final=1,vl_custo_medio=0 where rowid=(select min(rowid) from fato_estoque_diario)')
rejeitar('Saldo zero com valor','update fato_estoque_diario set qt_saldo_final=0,vl_estoque_final=10 where rowid=(select min(rowid) from fato_estoque_diario)')
relatorio=dict(ddl='10 tabelas criadas em banco vazio',testes_rejeicao_aprovados=len(resultados),casos=resultados,
    observacao='Testes de restrições declaradas; regras entre registros serão implementadas na próxima etapa da carga.')
(base/'testes_ddl.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(resultados)} testes de rejeição aprovados.')
con.close()
