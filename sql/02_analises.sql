-- 01. Estoque por centro no fechamento final (não soma datas).
SELECT c.nm_centro_distribuicao,SUM(e.vl_estoque_final) vl_estoque,
 SUM(e.qt_saldo_final) qt_unidades,SUM(e.qt_compra_pendente) qt_pendente
FROM fato_estoque_diario e JOIN dim_centro_distribuicao c USING(id_centro_distribuicao)
WHERE e.id_data_estoque=(SELECT MAX(id_data_estoque) FROM fato_estoque_diario)
GROUP BY 1;

-- 02. Fechamentos mensais: um dia por mês.
WITH ultimo AS (
 SELECT d.nr_ano_mes,MAX(e.id_data_estoque) id_data FROM fato_estoque_diario e
 JOIN dim_data d ON d.id_data=e.id_data_estoque GROUP BY 1)
SELECT u.nr_ano_mes,SUM(e.vl_estoque_final) vl_estoque
FROM ultimo u JOIN fato_estoque_diario e ON e.id_data_estoque=u.id_data GROUP BY 1 ORDER BY 1;

-- 03. Itens prioritários no corte final.
SELECT p.nm_produto,c.nm_centro_distribuicao,e.qt_saldo_final,e.qt_compra_pendente,
 e.qt_demanda_media_dia,e.qt_ponto_reposicao,e.nr_dias_cobertura,e.tx_situacao_estoque
FROM vw_estoque_analitico e JOIN dim_produto p USING(id_produto)
JOIN dim_centro_distribuicao c USING(id_centro_distribuicao)
WHERE e.id_data_estoque=(SELECT MAX(id_data_estoque) FROM fato_estoque_diario)
ORDER BY e.in_indisponivel DESC,e.in_risco_espera DESC,e.vl_estoque_final DESC;

-- 04. Pontualidade por fornecedor, corte final, por item integral.
SELECT f.nm_fornecedor,COUNT(*) nr_itens,
 SUM(v.in_vencido_ate_referencia) nr_itens_vencimento_ate_corte,
 SUM(v.in_integral_no_prazo) nr_itens_integrais_prazo,
 ROUND(100.0*SUM(v.in_integral_no_prazo)/NULLIF(SUM(v.in_vencido_ate_referencia),0),2) pc_pontualidade,
 ROUND(AVG(v.nr_dias_entrega_completa),2) nr_dias_entrega_media,
 SUM(v.qt_pendente) qt_pendente
FROM vw_compras_posicao_final v JOIN dim_fornecedor f USING(id_fornecedor) GROUP BY 1;

-- 05. Expedição mensal por categoria (fluxo aditivo).
SELECT d.nr_ano_mes,p.nm_categoria,SUM(m.qt_movimento) qt_expedida,
 ROUND(-SUM(m.vl_movimento_assinado),2) vl_custo_expedido
FROM fato_movimento_estoque m JOIN dim_data d ON d.id_data=m.id_data_movimento
JOIN dim_produto p USING(id_produto) WHERE m.id_tipo_movimento=3 GROUP BY 1,2 ORDER BY 1,2;

-- 06. Produtos sem saída e estoque positivo após janela completa.
SELECT p.nm_produto,c.nm_centro_distribuicao,e.qt_saldo_final,e.vl_estoque_final
FROM vw_estoque_analitico e JOIN dim_produto p USING(id_produto)
JOIN dim_centro_distribuicao c USING(id_centro_distribuicao)
WHERE e.id_data_estoque=20251231 AND e.in_sem_saida=1 ORDER BY e.vl_estoque_final DESC;

-- 07. Reconciliação de quantidades por produto e centro.
SELECT id_produto,id_centro_distribuicao,SUM(qt_movimento_assinada) qt_saldo_reconstruido
FROM fato_movimento_estoque GROUP BY 1,2;

-- 08. Compras com recebimentos parciais (agrega antes de juntar).
WITH recebimentos AS (
 SELECT id_item_compra,COUNT(*) nr_parcelas,SUM(qt_recebida) qt_recebida FROM fato_recebimento GROUP BY 1)
SELECT i.nr_pedido,i.nr_item,i.qt_pedida,r.nr_parcelas,r.qt_recebida
FROM fato_item_compra i JOIN recebimentos r USING(id_item_compra) WHERE r.nr_parcelas>1;

-- 09. Custo de ajustes por motivo.
SELECT tx_motivo_ajuste,COUNT(*) nr_movimentos,SUM(qt_movimento) qt_ajustada,
 ROUND(SUM(vl_movimento_assinado),2) vl_ajuste_assinado
FROM fato_movimento_estoque WHERE id_tipo_movimento IN (4,5) GROUP BY 1;

-- 10. Posição histórica de compras. Alterar a data apenas neste CTE.
WITH parametros AS (SELECT 20240630 id_corte),
recebido AS (
 SELECT id_item_compra,SUM(qt_recebida) qt_recebida FROM fato_recebimento,parametros
 WHERE id_data_recebimento<=id_corte GROUP BY 1)
SELECT i.nr_pedido,i.nr_item,i.qt_pedida,COALESCE(r.qt_recebida,0) qt_recebida,
 i.qt_pedida-COALESCE(r.qt_recebida,0) qt_pendente
FROM fato_item_compra i CROSS JOIN parametros p LEFT JOIN recebido r USING(id_item_compra)
WHERE i.id_data_emissao<=p.id_corte;
