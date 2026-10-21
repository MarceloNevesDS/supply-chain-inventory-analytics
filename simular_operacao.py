"""
Simulação Nexo 2024–2025. Biblioteca padrão; não substitui bancos existentes.
Execute: python simular_operacao.py
O fechamento de 01/01 inclui a operação desse dia.
"""
import argparse
from collections import defaultdict, deque
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import random
import sqlite3
import tempfile

from gerar_projeto import carregar, inserir, validar as validar_abertura

BASE = Path(__file__).resolve().parent
INICIO, FIM = date(2024, 1, 1), date(2025, 12, 31)
D = Decimal
PRECISAO_CUSTO = D("0.00000001")


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def arredondar(valor):
    return valor.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def chave(dia):
    return int(dia.strftime("%Y%m%d"))


def custo_apos_entrada(saldo, custo, quantidade, custo_entrada):
    exigir(quantidade > 0 and saldo >= 0, "Quantidade de entrada ou saldo inválido")
    return ((saldo*custo + quantidade*custo_entrada)/(saldo+quantidade)).quantize(
        PRECISAO_CUSTO, rounding=ROUND_HALF_UP)


def movimento(con, dia, hora, p, c, tipo, qtd, custo, recebimento=None, motivo=None):
    sinal = 1 if tipo in (1, 2, 4) else -1
    return inserir(con, "fato_movimento_estoque",
        id_produto=p, id_centro_distribuicao=c, id_tipo_movimento=tipo,
        id_data_movimento=chave(dia), id_recebimento=recebimento,
        dt_movimento=f"{dia} {hora}", qt_movimento=qtd,
        qt_movimento_assinada=qtd*sinal, vl_custo_unitario_movimento=custo,
        vl_movimento_assinado=arredondar(qtd*sinal*custo), tx_motivo_ajuste=motivo)


def simular(con, semente=404):
    """Recebimentos 08h -> expedições 16h -> ajustes 17h -> compras 18h -> fechamento."""
    carregar(con, semente)
    validar_abertura(con)
    # Reconstituímos o fechamento de 01/01 após os eventos operacionais.
    estados = {}
    rng = random.Random(semente+1)
    for p,c,saldo,custo,prazo,seguranca in con.execute("""
        select id_produto,id_centro_distribuicao,qt_saldo_final,
        vl_custo_medio,nr_dias_reposicao,nr_dias_seguranca from fato_estoque_diario
        order by id_produto,id_centro_distribuicao"""):
        base_custo = D(str(custo)) if custo else D(500+p*113)/100
        '''
        Definir perfis sintéticos de demanda: sem saída, baixo giro, regular, alto giro.
        | Condição                   | Perfil                             |
        |----------------------------|------------------------------------|
        | Produto múltiplo de 20     | Demanda zero                       |
        | Ou, Produto múltiplo de 10 | Demanda baixa: 0.35                |
        | Ou, Demais produtos        | Demanda de referência entre 2 e 10 |'''
        demanda = 0 if p%20==0 else (0.35 if p%10==0 else 2+(p%9))
        estados[p,c] = dict(saldo=saldo,custo=D(str(custo)),base=base_custo,
            prazo=prazo,seguranca=seguranca,pendente=0,demanda=demanda,
            historico=deque(maxlen=90))
    con.execute("delete from fato_estoque_diario")
    agenda = defaultdict(list)
    numero_pedido = 0
    dia = INICIO
    while dia <= FIM:
        if dia == date(2025,7,1):
            for (p,c),e in estados.items():
                if p%10==0:
                    con.execute("""update aux_produto_centro set dt_fim_vigencia=?
                        where id_produto=? and id_centro_distribuicao=? and dt_fim_vigencia is null""",
                        (str(dia),p,c))
                    e["prazo"] += 2
                    e["seguranca"] += 1
                    inserir(con,"aux_produto_centro",id_produto=p,id_centro_distribuicao=c,
                        dt_inicio_vigencia=str(dia),dt_fim_vigencia=None,
                        nr_dias_reposicao=e["prazo"],nr_dias_seguranca=e["seguranca"])
        for item,p,c,fornecedor,qtd,custo in agenda.pop(dia, []):
            e=estados[p,c]
            rec=inserir(con,"fato_recebimento",id_item_compra=item,id_produto=p,
                id_fornecedor=fornecedor,id_centro_distribuicao=c,
                id_data_recebimento=chave(dia),dt_recebimento=f"{dia} 08:00:00",
                qt_recebida=qtd,vl_custo_unitario_recebido=custo,
                vl_total_recebido=arredondar(qtd*custo))
            movimento(con,dia,"08:00:00",p,c,2,qtd,custo,recebimento=rec)
            e["custo"]=custo_apos_entrada(e["saldo"],e["custo"],qtd,custo)
            e["saldo"]+=qtd
            e["pendente"]-=qtd
        candidatos=defaultdict(list) # É usada para agrupar produtos que precisam de reposição
        for (p,c),e in estados.items():
            ''' Em novembro e dezembro, a demanda de referência aumenta 35%. Nos demais meses, permanece sem alteração.
            É uma premissa fictícia para gerar um comportamento que depois será identificado nas análises.'''
            sazonal = 1.35 if dia.month in (11,12) else 1
            '''Aqui criamos um dicionário e imediatamente buscamos o valor da chave c (centro de distribuição).
            Centro	        Fator	Efeito
            Brasília — 1	1,00	Demanda de referência
            São Paulo — 2	1,25	Demanda 25% maior
            Curitiba — 3	0,80	Demanda 20% menor
            --> Por exemplo, se c = 2, o resultado da expressão será 1.25.'''
            fator_centro = {1:1.0,2:1.25,3:0.8}[c]
            # Bernoulli preserva saída eventual para produtos de baixo giro.
            media=e["demanda"]*sazonal*fator_centro  # Calcula a demanda média esperada.
            '''
            Para demanda média menor que uma unidade (if media<1):
            rng.random() sorteia um número entre zero e um, sem incluir um.
            Se media = 0.35, existe uma probabilidade de 35% de o resultado ser verdadeiro:
            Assim, o produto terá procura de zero ou uma unidade naquele dia. Se a média for zero, a demanda será sempre zero.
            Para demanda média maior ou igual a uma unidade (else max(0, round(rng.gauss(media, media * 0.4)))):
            Por exemplo, para média de dez unidades, o desvio padrão será quatro. As quantidades irão variar ao redor de dez.
            '''
            demanda = int(rng.random()<media) if media<1 else max(0,round(rng.gauss(media,media*0.4))) # Soteia a demandado do dia
            expedida=min(e["saldo"],demanda)
            if expedida:   # Registrar a saída e reduzir o saldo.
                movimento(con,dia,"16:00:00",p,c,3,expedida,e["custo"])
                e["saldo"]-=expedida
            e["historico"].append(expedida)  # Registrar a saída no histórico diário.
            if dia.day==28 and rng.random()<0.10 and e["custo"]>0:
                tipo=rng.choice([4,5]) # Sorteia o tipo de ajuste: 4-Ajuste positivo ou 5-Ajuste negativo.
                qtd=rng.randint(1,3)   # Sorteia a quantidade que será ajustada.
                if tipo==4 or e["saldo"]>=qtd:
                    '''A função movimento() aplica o sinal e grava o evento na fato_movimento_estoque.'''
                    movimento(con,dia,"17:00:00",p,c,tipo,qtd,e["custo"],
                        motivo="Diferença de contagem" if tipo==4 else "Avaria em inventário")
                    e["saldo"]+=qtd if tipo==4 else -qtd
            # Média observada incluindo hoje; denominador cresce até 90 dias.
            media_observada=D(sum(e["historico"]))/len(e["historico"])
            ponto=media_observada*(e["prazo"]+e["seguranca"])
            # Uma compra de implantação no primeiro dia evita a armadilha:
            # saldo zero -> nenhuma expedição -> média observada zero -> nenhuma compra.
            implantacao = dia==INICIO and e["saldo"]==0 and e["demanda"]>0
            '''No IF abaixo, decide se é necessário comprar, calcula a quantidade e agrupa os produtos por centro e fornecedor. 
            O pedido será gravado mais adiante.'''
            if (media_observada>0 and e["saldo"]+e["pendente"]<=ponto) or implantacao:
                taxa=D(str(e["demanda"]*fator_centro)) if implantacao else media_observada
                alvo=taxa*(e["prazo"]+e["seguranca"]+30)
                qtd=max(20,int((alvo-e["saldo"]-e["pendente"]).to_integral_value(rounding="ROUND_CEILING")))
                fornecedor=(p%4)*3+c
                candidatos[c,fornecedor].append((p,qtd))
        for (c,fornecedor),itens in sorted(candidatos.items()):
            numero_pedido+=1
            for nr_item,(p,qtd) in enumerate(itens,1):
                e=estados[p,c]
                custo=arredondar(e["base"]*D(str(rng.uniform(0.90,1.15))))
                prevista=dia+timedelta(days=e["prazo"])
                item=inserir(con,"fato_item_compra",nr_pedido=f"PC{numero_pedido:06}",nr_item=nr_item,
                    id_produto=p,id_fornecedor=fornecedor,id_centro_distribuicao=c,
                    id_data_emissao=chave(dia),id_data_prevista=chave(prevista),
                    qt_pedida=qtd,vl_custo_unitario_pedido=custo,vl_total_item=arredondar(qtd*custo))
                '''f"PC{numero_pedido:06}" formata o número do pedido com seis posições preenchendo zeros
                Exemplos:
                1   → PC000001
                25  → PC000025
                300 → PC000300 '''
                atraso=rng.choice([-2,0,0,1,3,7])+(2 if fornecedor%4==0 else 0)     # Simula possibilidade de atraso na entrega
                chegada=max(dia+timedelta(days=1),prevista+timedelta(days=atraso))  # Simula a data efetiva de chegada
                partes=[(chegada,qtd)] # Inicialmente haverá uma entrega completa.
                # Decidir se haverá entrega parcial
                if rng.random()<0.35:
                    # Há 35% de chance de dividir o item em duas entregar.
                    primeira=qtd*3//5
                    partes=[(chegada,primeira),(chegada+timedelta(days=3),qtd-primeira)]
                for data_rec,parcial in partes: # Colocar as entregas na agenda
                    agenda[data_rec].append((item,p,c,fornecedor,parcial,custo))
                e["pendente"]+=qtd
        for (p,c),e in estados.items():  # registra como terminou o dia para cada produto e centro.
            inserir(con,"fato_estoque_diario",id_data_estoque=chave(dia),id_produto=p,
                id_centro_distribuicao=c,qt_saldo_final=e["saldo"],vl_custo_medio=e["custo"],
                vl_estoque_final=arredondar(e["saldo"]*e["custo"]),qt_compra_pendente=e["pendente"],
                nr_dias_reposicao=e["prazo"],nr_dias_seguranca=e["seguranca"])
        dia+=timedelta(days=1) # Avança o calendário para repetir a operação para o próximo dia. 


def validar_operacao(con):
    """Auditoria independente: SQL e replay dos eventos, sem usar estados do gerador."""
    exigir(con.execute("pragma foreign_keys").fetchone()[0]==1,"FK desativada")
    exigir(not con.execute("pragma foreign_key_check").fetchall(),"FK inválida")
    exigir(con.execute("pragma integrity_check").fetchone()[0]=="ok","Integridade física")
    sqls={
      "valor_item_compra": "select count(*) from fato_item_compra where abs(vl_total_item-round(qt_pedida*vl_custo_unitario_pedido,2))>0.001",
      "valor_recebimento": "select count(*) from fato_recebimento where abs(vl_total_recebido-round(qt_recebida*vl_custo_unitario_recebido,2))>0.001",
      "origem_recebimento":"""select count(*) from fato_recebimento r join fato_item_compra i using(id_item_compra)
        where r.id_produto<>i.id_produto or r.id_fornecedor<>i.id_fornecedor
        or r.id_centro_distribuicao<>i.id_centro_distribuicao or r.id_data_recebimento<i.id_data_emissao
        or abs(r.vl_custo_unitario_recebido-i.vl_custo_unitario_pedido)>0.000001""",
      "excesso_recebido":"""select count(*) from (select i.id_item_compra from fato_item_compra i
        join fato_recebimento r using(id_item_compra) group by i.id_item_compra having sum(r.qt_recebida)>i.qt_pedida)""",
      "cabecalho_pedido":"""select count(*) from (select nr_pedido from fato_item_compra group by nr_pedido
        having count(distinct id_fornecedor)>1 or count(distinct id_centro_distribuicao)>1
        or count(distinct id_data_emissao)>1)""",
      "espelho_recebimento":"""select count(*) from fato_recebimento r left join fato_movimento_estoque m using(id_recebimento)
        where m.id_movimento_estoque is null or m.id_tipo_movimento<>2 or m.id_produto<>r.id_produto
        or m.id_centro_distribuicao<>r.id_centro_distribuicao or m.dt_movimento<>r.dt_recebimento
        or m.qt_movimento<>r.qt_recebida or abs(m.vl_custo_unitario_movimento-r.vl_custo_unitario_recebido)>0.000001""",
      "sinal_origem_motivo":"""select count(*) from fato_movimento_estoque m join dim_tipo_movimento t using(id_tipo_movimento)
        where m.qt_movimento_assinada<>m.qt_movimento*t.nr_sinal
        or (m.id_tipo_movimento=2)<>(m.id_recebimento is not null)
        or (m.id_tipo_movimento in (4,5) and coalesce(trim(m.tx_motivo_ajuste),'')='')""",
      "data_movimento":"""select count(*) from fato_movimento_estoque m join dim_data d on d.id_data=m.id_data_movimento
        where substr(m.dt_movimento,1,10)<>d.dt_data""",
      "data_recebimento":"""select count(*) from fato_recebimento r join dim_data d on d.id_data=r.id_data_recebimento
        where substr(r.dt_recebimento,1,10)<>d.dt_data""",
      "sobreposicao_vigencia":"""select count(*) from aux_produto_centro a join aux_produto_centro b
        on a.id_produto=b.id_produto and a.id_centro_distribuicao=b.id_centro_distribuicao
        and a.id_produto_centro<b.id_produto_centro
        where a.dt_inicio_vigencia<coalesce(b.dt_fim_vigencia,'9999-12-31')
        and b.dt_inicio_vigencia<coalesce(a.dt_fim_vigencia,'9999-12-31')""",
      "parametros_diarios":"""select count(*) from (select e.id_data_estoque,e.id_produto,e.id_centro_distribuicao
        from fato_estoque_diario e join dim_data d on d.id_data=e.id_data_estoque
        left join aux_produto_centro a on a.id_produto=e.id_produto
        and a.id_centro_distribuicao=e.id_centro_distribuicao and a.dt_inicio_vigencia<=d.dt_data
        and (a.dt_fim_vigencia is null or d.dt_data<a.dt_fim_vigencia)
        group by e.id_data_estoque,e.id_produto,e.id_centro_distribuicao
        having count(a.id_produto_centro)<>1 or max(a.nr_dias_reposicao)<>e.nr_dias_reposicao
        or max(a.nr_dias_seguranca)<>e.nr_dias_seguranca)""",
      "pendencia_diaria":"""with eventos as (
        select id_data_emissao d,id_produto p,id_centro_distribuicao c,qt_pedida q from fato_item_compra
        union all select id_data_recebimento,id_produto,id_centro_distribuicao,-qt_recebida from fato_recebimento
        ), diario as (select d,p,c,sum(q) q from eventos group by d,p,c), calculado as (
        select e.qt_compra_pendente,sum(coalesce(x.q,0)) over
        (partition by e.id_produto,e.id_centro_distribuicao order by e.id_data_estoque rows unbounded preceding) q
        from fato_estoque_diario e left join diario x on x.d=e.id_data_estoque
        and x.p=e.id_produto and x.c=e.id_centro_distribuicao)
        select count(*) from calculado where qt_compra_pendente<>q""",
      "abertura":"""select count(*) from (select id_produto,id_centro_distribuicao from fato_movimento_estoque
        where id_tipo_movimento=1 group by 1,2 having count(*)>1 or min(id_data_movimento)<>20240101)"""
    }
    resultados={nome:con.execute(sql).fetchone()[0] for nome,sql in sqls.items()}
    for nome,n in resultados.items():
        exigir(n==0,f"Validação {nome}: {n} divergências")
    # Auditoria por produto/centro, evitando JOIN cartesiano entre fatos.
    for p,c in con.execute("select id_produto,id_centro_distribuicao from aux_produto_centro group by 1,2"):
        eventos=iter(con.execute("""select id_data_movimento,id_tipo_movimento,qt_movimento,
            qt_movimento_assinada,vl_custo_unitario_movimento,vl_movimento_assinado
            from fato_movimento_estoque where id_produto=? and id_centro_distribuicao=?
            order by dt_movimento,id_movimento_estoque""",(p,c)))
        atual=next(eventos,None)
        saldo,custo=0,D(0)
        registros=0
        for data_id,qtd,custo_db,valor in con.execute("""select id_data_estoque,qt_saldo_final,vl_custo_medio,vl_estoque_final
            from fato_estoque_diario where id_produto=? and id_centro_distribuicao=? order by id_data_estoque""",(p,c)):
            exigir(data_id==chave(INICIO+timedelta(days=registros)),"Calendário diário incompleto")
            while atual is not None and atual[0]<=data_id:
                d,tipo,q,ass,c,v=atual
                c=D(str(c));v=D(str(v))
                if tipo==1:
                    custo=c
                elif tipo==2:
                    custo=custo_apos_entrada(saldo,custo,q,c)
                else:
                    exigir(abs(c-custo)<=D("0.00000002"),"Custo da saída/ajuste divergente")
                exigir(abs(v-arredondar(ass*c))<=D("0.000001"),"Valor do movimento divergente")
                saldo+=ass
                exigir(saldo>=0,"Saldo negativo durante os eventos")
                atual=next(eventos,None)
            exigir(qtd==saldo,f"Saldo diário divergente: {p}/{c}/{data_id}")
            exigir(abs(D(str(custo_db))-custo)<=D("0.00000002"),"Custo médio diário divergente")
            exigir(abs(D(str(valor))-arredondar(saldo*custo))<=D("0.000001"),"Valor diário divergente")
            registros+=1
        exigir(registros==731 and atual is None,"Cobertura temporal inválida")
    resultados["replay_saldo_custo_valor"]=0
    resultados["integridade"]="ok"
    return resultados


def indices(con):
    con.executescript("""
        create index ix_recebimento_item on fato_recebimento(id_item_compra);
        create index ix_movimento_produto_centro_data on fato_movimento_estoque
          (id_produto,id_centro_distribuicao,dt_movimento,id_movimento_estoque);
        create index ix_estoque_produto_centro_data on fato_estoque_diario
          (id_produto,id_centro_distribuicao,id_data_estoque);
    """)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banco",type=Path,default=BASE/"dados"/"supply_chain_2024_2025.sqlite")
    parser.add_argument("--semente",type=int,default=404)
    args=parser.parse_args()
    exigir(not args.banco.exists(),"Banco já existe; escolha outro caminho com --banco.")
    args.banco.parent.mkdir(parents=True,exist_ok=True)
    # Banco só recebe o nome final depois da validação.
    with tempfile.TemporaryDirectory(dir=args.banco.parent) as temp:
        temporario=Path(temp)/"carga.sqlite"
        con=sqlite3.connect(temporario)
        try:
            con.executescript((BASE/"modelo.sql").read_text(encoding="utf-8-sig"))
            indices(con)
            with con:
                simular(con,args.semente)
            validacoes=validar_operacao(con)
            contagens={t:con.execute(f"select count(*) from {t}").fetchone()[0]
                for (t,) in con.execute("select name from sqlite_master where type='table' order by name")}
            exigir(contagens["fato_estoque_diario"]==219300,"Contagem de fechamentos incorreta")
            relatorio=dict(semente=args.semente,periodo=[str(INICIO),str(FIM)],contagens=contagens,validacoes=validacoes)
        finally:
            con.close()
        # link falha se o destino surgir durante a execução, sem sobrescrevê-lo.
        import os
        os.link(temporario,args.banco)
    args.banco.with_suffix(".validacao.json").write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(relatorio,ensure_ascii=True,indent=2))


if __name__=="__main__":
    main()
