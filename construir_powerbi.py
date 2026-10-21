"""Gera projeto PBIP editável (modelo TMSL, relatório PBIR) a partir dos CSV."""
import csv,json,uuid
from pathlib import Path
BASE=Path(__file__).resolve().parent
PBI=BASE/"powerbi"
MODEL=PBI/"SupplyChain.SemanticModel"
REPORT=PBI/"SupplyChain.Report"
SCHEMA="https://developer.microsoft.com/json-schemas/fabric/"
def gravar(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
def lit(value):
 if isinstance(value,bool):v=str(value).lower()
 elif isinstance(value,(int,float)):v=str(value)
 else:v="'"+value.replace("'","''")+"'"
 return {"expr":{"Literal":{"Value":v}}}

medidas=[]
def medida(nome,dax,formato="#,0",pasta="Operação"):
 medidas.append(dict(name=nome,expression=dax,formatString=formato,displayFolder=pasta))
medida("Data de referência","VAR Primeira = MIN(dim_data[dt_data])\nVAR Selecionada = MAX(dim_data[dt_data])\nVAR Carga = CALCULATE(MAX(fato_estoque_diario[dt_estoque]), REMOVEFILTERS())\nRETURN IF(Primeira > Carga, BLANK(), MIN(Selecionada, Carga))","dd/MM/yyyy","Estoque")
def snapshot(nome,col,formato="#,0"):
 medida(nome,"VAR Ref = [Data de referência]\nRETURN IF(ISBLANK(Ref), BLANK(), CALCULATE(SUM(fato_estoque_diario["+col+"]), REMOVEFILTERS(dim_data), dim_data[dt_data] = Ref))",formato,"Estoque")
snapshot("Valor do estoque","vl_estoque_final","R$ #,0.00")
snapshot("Saldo em unidades","qt_saldo_final")
snapshot("Compra pendente em unidades","qt_compra_pendente")
snapshot("Combinações em risco","in_risco_espera")
snapshot("Combinações sem saída","in_sem_saida")
snapshot("Combinações com cobertura elevada","in_cobertura_elevada")
snapshot("Combinações sem saldo","in_indisponivel")
snapshot("Combinações para repor","in_reposicao")
snapshot("Demanda média diária","qt_demanda_media_dia","#,0.00")
snapshot("Ponto de reposição","qt_ponto_reposicao")
medida("Cobertura em dias","IF(HASONEVALUE(dim_produto[id_produto]) && HASONEVALUE(dim_centro_distribuicao[id_centro_distribuicao]), DIVIDE([Saldo em unidades], [Demanda média diária]))","#,0.0","Estoque")
medida("Situação do estoque","VAR Ref = [Data de referência]\nRETURN IF(HASONEVALUE(dim_produto[id_produto]) && HASONEVALUE(dim_centro_distribuicao[id_centro_distribuicao]), CALCULATE(SELECTEDVALUE(fato_estoque_diario[tx_situacao_estoque]), REMOVEFILTERS(dim_data), dim_data[dt_data] = Ref))","","Estoque")
medida("Unidades expedidas","CALCULATE(SUM(fato_movimento_estoque[qt_movimento]), dim_tipo_movimento[cd_tipo_movimento] = \"EXPEDICAO\")")
medida("Custo das expedições","-CALCULATE(SUM(fato_movimento_estoque[vl_movimento_assinado]), dim_tipo_movimento[cd_tipo_movimento] = \"EXPEDICAO\")","R$ #,0.00")
medida("Valor comprado","SUM(fato_item_compra[vl_total_item])","R$ #,0.00","Compras")
medida("Pedidos emitidos","DISTINCTCOUNT(fato_item_compra[nr_pedido])","#,0","Compras")
medida("Valor recebido","SUM(fato_recebimento[vl_total_recebido])","R$ #,0.00","Compras")
medida("Unidades recebidas","SUM(fato_recebimento[qt_recebida])","#,0","Compras")
medida("Itens vencidos no corte final","SUM(fato_item_compra[in_vencido_ate_referencia])","#,0","Fornecedores • posição final")
medida("Itens integrais no prazo","SUM(fato_item_compra[in_integral_no_prazo])","#,0","Fornecedores • posição final")
medida("Pontualidade no corte final","DIVIDE([Itens integrais no prazo], [Itens vencidos no corte final])","0.0%","Fornecedores • posição final")
medida("Itens pendentes atrasados","SUM(fato_item_compra[in_pendente_atrasado])","#,0","Fornecedores • posição final")
medida("Prazo médio realizado","AVERAGE(fato_item_compra[nr_dias_entrega_completa])","#,0.0","Fornecedores • posição final")
medida("Unidades ajustadas","CALCULATE(SUM(fato_movimento_estoque[qt_movimento]), dim_tipo_movimento[cd_tipo_movimento] IN {\"AJUSTE_POSITIVO\", \"AJUSTE_NEGATIVO\"})")
medida("Valor líquido dos ajustes","CALCULATE(SUM(fato_movimento_estoque[vl_movimento_assinado]), dim_tipo_movimento[cd_tipo_movimento] IN {\"AJUSTE_POSITIVO\", \"AJUSTE_NEGATIVO\"})","R$ #,0.00")
medida("Quantidade movimentada","SUM(fato_movimento_estoque[qt_movimento])")
medida("Valor líquido movimentado","SUM(fato_movimento_estoque[vl_movimento_assinado])","R$ #,0.00")

tipos={};tabelas=[];consultas={}
for arquivo in sorted((PBI/"dados").glob("*.csv")):
 nome=arquivo.stem
 with arquivo.open(encoding="utf-8",newline="") as f:campos=next(csv.reader(f))
 colunas=[];mtypes=[]
 for col in campos:
  if col.startswith("dt_"):
   tipo="dateTime";mtype="type datetime" if col in ("dt_movimento","dt_recebimento") else "type date"
  elif col in ("nr_pedido",):tipo="string";mtype="type text"
  elif col in ("qt_demanda_media_dia","nr_dias_cobertura") or col.startswith("vl_"):
   tipo="double";mtype="type number"
  elif col.startswith(("id_","nr_","qt_","in_")):tipo="int64";mtype="Int64.Type"
  else:tipo="string";mtype="type text"
  tipos[nome,col]=tipo
  c=dict(name=col,dataType=tipo,sourceColumn=col,summarizeBy="none")
  if col.startswith("id_"):c["isHidden"]=True
  if tipo=="dateTime":c["formatString"]="dd/MM/yyyy"
  colunas.append(c);mtypes.append('{'+json.dumps(col)+', '+mtype+'}')
 source=[
  "let",
  '  Fonte = Csv.Document(File.Contents(pPastaDados & "/'+nome+'.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
  '  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),',
  '  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),',
  '  Tipos = Table.TransformColumnTypes(Nulos, {'+', '.join(mtypes)+'}, "en-US")',
  "in","  Tipos"]
 consultas[nome]="\n".join(source)
 table=dict(name=nome,columns=colunas,partitions=[dict(name=nome,mode="import",source=dict(type="m",expression=source))])
 if nome=="dim_data":
  table["dataCategory"]="Time"
  next(c for c in colunas if c["name"]=="dt_data")["isKey"]=True
  for texto,numero in [("nm_mes","nr_mes"),("nm_dia_semana","nr_dia_semana"),("nm_bimestre","nr_bimestre"),("nm_trimestre","nr_trimestre"),("nm_semestre","nr_semestre")]:
   next(c for c in colunas if c["name"]==texto)["sortByColumn"]=numero
 if nome=="fato_estoque_diario":table["measures"]=medidas
 tabelas.append(table)
rel=[]
for table in tabelas:
 nome=table["name"]
 if not nome.startswith("fato_"):continue
 campos={c["name"] for c in table["columns"]}
 pares=[("id_produto","dim_produto","id_produto"),("id_centro_distribuicao","dim_centro_distribuicao","id_centro_distribuicao")]
 if "id_fornecedor" in campos:pares.append(("id_fornecedor","dim_fornecedor","id_fornecedor"))
 if "id_tipo_movimento" in campos:pares.append(("id_tipo_movimento","dim_tipo_movimento","id_tipo_movimento"))
 data={"fato_estoque_diario":"id_data_estoque","fato_item_compra":"id_data_emissao","fato_recebimento":"id_data_recebimento","fato_movimento_estoque":"id_data_movimento"}[nome]
 pares.append((data,"dim_data","id_data"))
 if nome=="fato_item_compra":pares.append(("id_data_prevista","dim_data","id_data"))
 for col,dest,col_dest in pares:
  rel.append(dict(name=str(uuid.uuid5(uuid.NAMESPACE_DNS,nome+"."+col)),fromTable=nome,fromColumn=col,
    fromCardinality="many",toTable=dest,toColumn=col_dest,toCardinality="one",
    crossFilteringBehavior="oneDirection",isActive=(col!="id_data_prevista")))
model=dict(name="SupplyChain",compatibilityLevel=1600,model=dict(culture="pt-BR",sourceQueryCulture="en-US",
 defaultPowerBIDataSourceVersion="powerBI_V3",tables=tabelas,relationships=rel,
 expressions=[dict(name="pPastaDados",kind="m",
 expression='\"D:/Portifólio BI/2 - Supply Chain & Inventory Analytics/powerbi/dados\" meta [IsParameterQuery=true, Type=\"Text\", IsParameterQueryRequired=true]')],
 annotations=[dict(name="PBI_QueryOrder",value=json.dumps(list(consultas))),
 dict(name="__PBI_TimeIntelligenceEnabled",value="0")]))
gravar(MODEL/"model.bim",model)
gravar(MODEL/"definition.pbism",{"$schema":SCHEMA+"item/semanticModel/definitionProperties/1.0.0/schema.json","version":"1.0","settings":{}})
gravar(REPORT/"definition.pbir",{"$schema":SCHEMA+"item/report/definitionProperties/2.0.0/schema.json","version":"4.0","datasetReference":{"byPath":{"path":"../SupplyChain.SemanticModel"}}})
gravar(PBI/"SupplyChain.pbip",{"$schema":SCHEMA+"pbip/pbipProperties/1.0.0/schema.json","version":"1.0","artifacts":[{"report":{"path":"SupplyChain.Report"}}],"settings":{"enableAutoRecovery":True}})
gravar(REPORT/"definition/version.json",{"$schema":SCHEMA+"item/report/definition/versionMetadata/1.0.0/schema.json","version":"2.0.0"})
gravar(REPORT/"definition/report.json",{"$schema":SCHEMA+"item/report/definition/report/3.1.0/schema.json","themeCollection":{},"settings":{"useStylableVisualContainerHeader":True}})
# Tema independente, importável também pelo menu do Desktop.
gravar(PBI/"tema_nexo.json",{"name":"Nexo Supply Chain","dataColors":["#147D92","#E09B36","#435A78","#D65D5D","#65A88D"],"background":"#F4F7FA","foreground":"#18344A","tableAccent":"#147D92"})

def campo(tabela,coluna,med=False):
 return {("Measure" if med else "Column"):{"Expression":{"SourceRef":{"Entity":tabela}},"Property":coluna}}
def proj(t,c,med=False):
 return dict(field=campo(t,c,med),queryRef=t+"."+c,nativeQueryRef=c)
def medida_proj(nome):return proj("fato_estoque_diario",nome,True)
paginas=[];visual_count=0
def pagina(nome,titulo):
 ident=nome;paginas.append(ident)
 obj={"$schema":SCHEMA+"item/report/definition/page/2.0.0/schema.json","name":ident,"displayName":titulo,
 "displayOption":"FitToPage","height":900,"width":1440}
 gravar(REPORT/f"definition/pages/{ident}/page.json",obj)
 return ident
def visual(pg,ident,tipo,x,y,w,h,roles,titulo):
 global visual_count
 visual_count+=1
 obj={"$schema":SCHEMA+"item/report/definition/visualContainer/2.1.0/schema.json","name":ident,
 "position":{"x":x,"y":y,"width":w,"height":h,"z":visual_count,"tabOrder":visual_count},
 "visual":{"visualType":tipo,"query":{"queryState":{r:{"projections":p} for r,p in roles.items()}},
 "visualContainerObjects":{"title":[{"properties":{"show":lit(True),"text":lit(titulo),"fontSize":lit(12)}}],
 "background":[{"properties":{"show":lit(True),"color":{"solid":{"color":lit("#FFFFFF")}},"transparency":lit(0)}}]}}}
 gravar(REPORT/f"definition/pages/{pg}/visuals/{ident}/visual.json",obj)
def cartoes(pg,nomes):
 for i,nome in enumerate(nomes):visual(pg,"card_"+str(i),"card",24+i*350,24,330,110,{"Values":[medida_proj(nome)]},nome)
def filtros(pg,ano=True):
 visual(pg,"filtro_centro","slicer",24,150,400,90,{"Values":[proj("dim_centro_distribuicao","nm_centro_distribuicao")]},"Centro")
 visual(pg,"filtro_categoria","slicer",450,150,450,90,{"Values":[proj("dim_produto","nm_categoria")]},"Categoria")
 if ano:visual(pg,"filtro_ano","slicer",930,150,480,90,{"Values":[proj("dim_data","nr_ano")]},"Ano • estoque usa o último dia selecionado")
pg=pagina("executivo","01 • Visão executiva")
cartoes(pg,["Valor do estoque","Combinações em risco","Unidades expedidas","Valor comprado"]);filtros(pg)
visual(pg,"estoque_mes","lineChart",24,270,850,280,{"Category":[proj("dim_data","nr_ano_mes")],"Y":[medida_proj("Valor do estoque")]},"Estoque no fechamento mensal • R$")
visual(pg,"estoque_cd","clusteredBarChart",900,270,510,280,{"Category":[proj("dim_centro_distribuicao","nm_centro_distribuicao")],"Y":[medida_proj("Valor do estoque")]},"Estoque por centro • último dia selecionado")
visual(pg,"saida_mes","clusteredColumnChart",24,580,850,280,{"Category":[proj("dim_data","nr_ano_mes")],"Y":[medida_proj("Unidades expedidas")]},"Expedições mensais • unidades")
visual(pg,"custo_categoria","clusteredBarChart",900,580,510,280,{"Category":[proj("dim_produto","nm_categoria")],"Y":[medida_proj("Custo das expedições")]},"Custo expedido por categoria • R$")
pg=pagina("estoque","02 • Estoque e reposição")
cartoes(pg,["Saldo em unidades","Combinações sem saldo","Combinações sem saída","Combinações para repor"]);filtros(pg)
visual(pg,"detalhe_estoque","tableEx",24,270,1386,590,{"Values":[proj("dim_produto","nm_produto"),proj("dim_centro_distribuicao","nm_centro_distribuicao")]+[medida_proj(n) for n in ["Saldo em unidades","Compra pendente em unidades","Demanda média diária","Ponto de reposição","Cobertura em dias","Situação do estoque"]]},"Posição por produto e centro • cobertura em dias; demanda zero sem cobertura calculável")
pg=pagina("fornecedores","03 • Fornecedores — corte 31/12/2025")
cartoes(pg,["Pontualidade no corte final","Itens vencidos no corte final","Itens pendentes atrasados","Prazo médio realizado"]);filtros(pg,False)
visual(pg,"pontualidade","clusteredBarChart",24,270,700,570,{"Category":[proj("dim_fornecedor","nm_fornecedor")],"Y":[medida_proj("Pontualidade no corte final")]},"Itens integralmente recebidos no prazo / itens vencidos • 31/12/2025")
visual(pg,"tabela_fornecedor","tableEx",750,270,660,570,{"Values":[proj("dim_fornecedor","nm_fornecedor")]+[medida_proj(n) for n in ["Itens vencidos no corte final","Itens integrais no prazo","Pontualidade no corte final","Prazo médio realizado"]]},"Posição final • prazo médio somente de itens concluídos")
pg=pagina("movimentos","04 • Compras e movimentos")
cartoes(pg,["Pedidos emitidos","Valor recebido","Unidades ajustadas","Valor líquido dos ajustes"]);filtros(pg)
visual(pg,"comprado_recebido","lineChart",24,270,850,280,{"Category":[proj("dim_data","nr_ano_mes")],"Y":[medida_proj("Valor comprado"),medida_proj("Valor recebido")]},"Comprado por emissão e recebido por recebimento • datas distintas")
visual(pg,"movimento_tipo","clusteredBarChart",900,270,510,280,{"Category":[proj("dim_tipo_movimento","tx_tipo_movimento")],"Y":[medida_proj("Quantidade movimentada")]},"Quantidade por tipo de movimento")
visual(pg,"ajustes_mensais","clusteredColumnChart",24,580,1386,280,{"Category":[proj("dim_data","nr_ano_mes")],"Y":[medida_proj("Valor líquido dos ajustes")]},"Valor líquido dos ajustes por mês • R$")
gravar(REPORT/"definition/pages/pages.json",{"$schema":SCHEMA+"item/report/definition/pagesMetadata/1.0.0/schema.json","pageOrder":paginas,"activePageName":paginas[0]})
(PBI/"medidas.dax").write_text("\n\n".join("// "+m["displayFolder"]+"\n"+m["name"]+" =\n"+m["expression"] for m in medidas),encoding="utf-8")
(PBI/"consultas_power_query.m").write_text("\n\n".join("// "+n+"\n"+q for n,q in consultas.items()),encoding="utf-8")
gravar(PBI/"estrutura_modelo.json",dict(tabelas=len(tabelas),relacionamentos=len(rel),medidas=len(medidas),paginas=len(paginas),visuais=visual_count))
print(json.dumps(dict(tabelas=len(tabelas),relacionamentos=len(rel),medidas=len(medidas),paginas=len(paginas),visuais=visual_count)))
