"""Primeira etapa da carga: dimensões, parâmetros e abertura em 01/01/2024.
Python 3.10+, sem dependências externas. Caminhos relativos a este script.
Compras, recebimentos e simulação diária serão a próxima etapa.
"""
import argparse
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import random
import sqlite3

BASE = Path(__file__).resolve().parent

def inserir(con, tabela, **valores):
    dados = [str(v) if isinstance(v, Decimal) else v for v in valores.values()]
    return con.execute(f"INSERT INTO {tabela} ({','.join(valores)}) VALUES ({','.join('?' for _ in valores)})", dados).lastrowid

def carregar(con, semente=404):
    rng = random.Random(semente)
    meses = 'Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro'.split()
    semana = ['Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo']
    feriados = {(1,1):'Confraternização Universal',(4,21):'Tiradentes',(5,1):'Dia do Trabalho',
        (9,7):'Independência do Brasil',(10,12):'Nossa Senhora Aparecida',(11,2):'Finados',
        (11,15):'Proclamação da República',(11,20):'Consciência Negra',(12,25):'Natal'}
    # Extensão até março/2026 permite previsões posteriores ao período analítico.
    dia = date(2024,1,1)
    while dia <= date(2026,3,1):
        bi,tri,sem = (dia.month-1)//2+1,(dia.month-1)//3+1,(dia.month-1)//6+1
        nome=feriados.get((dia.month,dia.day))
        inserir(con,'dim_data',id_data=int(dia.strftime('%Y%m%d')),dt_data=str(dia),
            nr_dia_mes=dia.day,nr_dia_semana=dia.isoweekday(),nm_dia_semana=semana[dia.weekday()],
            nr_mes=dia.month,nm_mes=meses[dia.month-1],nr_bimestre=bi,nm_bimestre=f'{bi}º Bimestre',
            nr_trimestre=tri,nm_trimestre=f'{tri}º Trimestre',nr_semestre=sem,nm_semestre=f'{sem}º Semestre',
            nr_ano=dia.year,nr_ano_mes=dia.year*100+dia.month,in_fim_semana=int(dia.weekday()>=5),
            in_feriado_nacional=int(nome is not None),nm_feriado_nacional=nome)
        dia+=timedelta(days=1)
    centros=[('BSB','Brasília','DF','Centro-Oeste'),('SPO','São Paulo','SP','Sudeste'),('CWB','Curitiba','PR','Sul')]
    for i,(sigla,cidade,uf,regiao) in enumerate(centros,1):
        inserir(con,'dim_centro_distribuicao',id_centro_distribuicao=i,cd_centro_distribuicao=f'CD_{sigla}',
            nm_centro_distribuicao=f'CD {cidade}',nm_cidade=cidade,sg_uf=uf,nm_regiao=regiao)
    produtos=[('Papel A4','Papelaria'),('Caderno','Papelaria'),('Pasta','Organização'),('Organizador','Organização'),
        ('Teclado USB','Periféricos'),('Mouse USB','Periféricos'),('Headset','Periféricos'),
        ('Cabo HDMI','Acessórios de informática'),('Hub USB','Acessórios de informática'),('Suporte notebook','Acessórios de informática')]
    for p in range(1,101):
        nome,categoria=produtos[(p-1)%10]
        inserir(con,'dim_produto',id_produto=p,cd_produto=f'PRD{p:04}',nm_produto=f'{nome} - modelo {(p-1)//10+1}',
            nm_categoria=categoria,nm_marca=f'Marca {(p-1)%5+1}',sg_unidade_medida='UN')
    for f in range(1,13):
        _,cidade,uf,regiao=centros[(f-1)%3]
        inserir(con,'dim_fornecedor',id_fornecedor=f,cd_fornecedor=f'FOR{f:03}',
            nm_fornecedor=f'Fornecedor fictício {f:02}',nm_cidade=cidade,sg_uf=uf,nm_regiao=regiao)
    tipos=[('ABERTURA','Saldo inicial',1),('RECEBIMENTO_COMPRA','Recebimento de compra',1),
        ('EXPEDICAO','Expedição para cliente',-1),('AJUSTE_POSITIVO','Ajuste positivo de inventário',1),
        ('AJUSTE_NEGATIVO','Ajuste negativo de inventário',-1)]
    for i,(codigo,descricao,sinal) in enumerate(tipos,1):
        inserir(con,'dim_tipo_movimento',id_tipo_movimento=i,cd_tipo_movimento=codigo,tx_tipo_movimento=descricao,nr_sinal=sinal)
    for p in range(1,101):
        for c in range(1,4):
            prazo,seguranca=rng.randint(5,15),rng.randint(3,8)
            qtd=rng.choice([0, rng.randint(20,200)])
            custo=Decimal(rng.randint(500,20000))/100 if qtd else Decimal(0)
            valor=(qtd*custo).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
            inserir(con,'aux_produto_centro',id_produto=p,id_centro_distribuicao=c,
                dt_inicio_vigencia='2024-01-01',dt_fim_vigencia=None,nr_dias_reposicao=prazo,nr_dias_seguranca=seguranca)
            if qtd:
                inserir(con,'fato_movimento_estoque',id_produto=p,id_centro_distribuicao=c,id_tipo_movimento=1,
                    id_data_movimento=20240101,id_recebimento=None,dt_movimento='2024-01-01 00:00:00',
                    qt_movimento=qtd,qt_movimento_assinada=qtd,vl_custo_unitario_movimento=custo,
                    vl_movimento_assinado=valor,tx_motivo_ajuste=None)
            inserir(con,'fato_estoque_diario',id_data_estoque=20240101,id_produto=p,id_centro_distribuicao=c,
                qt_saldo_final=qtd,vl_custo_medio=custo,vl_estoque_final=valor,qt_compra_pendente=0,
                nr_dias_reposicao=prazo,nr_dias_seguranca=seguranca)

def validar(con):
    assert con.execute('pragma foreign_keys').fetchone()[0]==1
    assert not con.execute('pragma foreign_key_check').fetchall()
    assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
    divergencias=con.execute('''select count(*) from fato_estoque_diario e left join
        (select id_produto,id_centro_distribuicao,sum(qt_movimento_assinada) saldo from fato_movimento_estoque
        group by 1,2) m using(id_produto,id_centro_distribuicao)
        where e.qt_saldo_final<>coalesce(m.saldo,0) or abs(e.vl_estoque_final-round(e.qt_saldo_final*e.vl_custo_medio,2))>0.001''').fetchone()[0]
    assert divergencias==0
    assert con.execute('select count(*) from fato_estoque_diario').fetchone()[0]==300
    return {t:con.execute(f'select count(*) from {t}').fetchone()[0]
        for (t,) in con.execute("select name from sqlite_master where type='table' order by name")}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--banco',type=Path,default=BASE/'dados'/'supply_chain.sqlite')
    parser.add_argument('--semente',type=int,default=404)
    args=parser.parse_args()
    if args.banco.exists():
        parser.error('Banco já existe. Use --banco com outro nome. Nenhum arquivo foi substituído.')
    args.banco.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(args.banco)
    try:
        con.execute('pragma foreign_keys=on')
        con.executescript((BASE/'modelo.sql').read_text(encoding='utf-8-sig'))
        with con:
            carregar(con,args.semente)
            contagens=validar(con)
        relatorio=dict(etapa='Carga inicial e abertura; simulação de compras e dias seguintes ainda não implementada',
            semente=args.semente,integridade='ok',divergencias_abertura=0,contagens=contagens)
        args.banco.with_suffix('.validacao.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(relatorio,ensure_ascii=True,indent=2))
    finally:
        con.close()

if __name__=='__main__':
    main()
