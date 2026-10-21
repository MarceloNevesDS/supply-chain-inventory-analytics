-- Indicadores por produto, centro e fechamento. Janela inclui dias sem saída.
CREATE VIEW IF NOT EXISTS vw_estoque_analitico AS
WITH expedicoes AS (
 SELECT id_data_movimento,id_produto,id_centro_distribuicao,
        SUM(qt_movimento) qt_expedida_dia
 FROM fato_movimento_estoque WHERE id_tipo_movimento=3 GROUP BY 1,2,3
), janela AS (
 SELECT e.*,d.dt_data dt_estoque,COALESCE(x.qt_expedida_dia,0) qt_expedida_dia,
   SUM(COALESCE(x.qt_expedida_dia,0)) OVER (
     PARTITION BY e.id_produto,e.id_centro_distribuicao ORDER BY e.id_data_estoque
     ROWS BETWEEN 89 PRECEDING AND CURRENT ROW) qt_expedida_90d,
   COUNT(*) OVER (
     PARTITION BY e.id_produto,e.id_centro_distribuicao ORDER BY e.id_data_estoque
     ROWS BETWEEN 89 PRECEDING AND CURRENT ROW) nr_dias_observados
 FROM fato_estoque_diario e JOIN dim_data d ON d.id_data=e.id_data_estoque
 LEFT JOIN expedicoes x ON x.id_data_movimento=e.id_data_estoque
   AND x.id_produto=e.id_produto AND x.id_centro_distribuicao=e.id_centro_distribuicao
), medias AS (
 SELECT *,1.0*qt_expedida_90d/nr_dias_observados qt_demanda_media_dia,
   qt_saldo_final+qt_compra_pendente qt_posicao_estoque FROM janela
), calculos AS (
 SELECT *,
   CAST(qt_demanda_media_dia*nr_dias_seguranca AS INT)
    +(qt_demanda_media_dia*nr_dias_seguranca>CAST(qt_demanda_media_dia*nr_dias_seguranca AS INT)) qt_estoque_seguranca,
   CAST(qt_demanda_media_dia*(nr_dias_reposicao+nr_dias_seguranca) AS INT)
    +(qt_demanda_media_dia*(nr_dias_reposicao+nr_dias_seguranca)>
      CAST(qt_demanda_media_dia*(nr_dias_reposicao+nr_dias_seguranca) AS INT)) qt_ponto_reposicao,
   CASE WHEN qt_demanda_media_dia>0 THEN qt_saldo_final/qt_demanda_media_dia END nr_dias_cobertura
 FROM medias
)
SELECT *,
 CASE WHEN qt_demanda_media_dia>0 AND qt_posicao_estoque<=qt_ponto_reposicao THEN 1 ELSE 0 END in_reposicao,
 CASE WHEN qt_demanda_media_dia>0 AND qt_saldo_final<qt_demanda_media_dia*nr_dias_reposicao THEN 1 ELSE 0 END in_risco_espera,
 CASE WHEN nr_dias_cobertura>90 THEN 1 ELSE 0 END in_cobertura_elevada,
 CASE WHEN nr_dias_observados=90 AND qt_expedida_90d=0 AND qt_saldo_final>0 THEN 1 ELSE 0 END in_sem_saida,
 CASE WHEN qt_saldo_final=0 AND qt_demanda_media_dia>0 THEN 1 ELSE 0 END in_indisponivel,
 CASE
  WHEN qt_saldo_final=0 AND qt_demanda_media_dia>0 THEN 'Sem saldo'
  WHEN nr_dias_observados=90 AND qt_expedida_90d=0 AND qt_saldo_final>0 THEN 'Sem saída em 90 dias'
  WHEN qt_demanda_media_dia>0 AND qt_saldo_final<qt_demanda_media_dia*nr_dias_reposicao THEN 'Risco na espera'
  WHEN qt_demanda_media_dia>0 AND qt_posicao_estoque<=qt_ponto_reposicao THEN 'Repor'
  WHEN nr_dias_cobertura>90 THEN 'Cobertura elevada'
  WHEN qt_demanda_media_dia=0 THEN 'Sem demanda observada'
  ELSE 'Regular'
 END tx_situacao_estoque
FROM calculos;

-- Posição de compras na última data carregada: não é um status histórico.
CREATE VIEW IF NOT EXISTS vw_compras_posicao_final AS
WITH ref AS (SELECT MAX(id_data_estoque) id_data_referencia FROM fato_estoque_diario),
rec AS (
 SELECT r.id_item_compra,SUM(r.qt_recebida) qt_recebida,
 SUM(CASE WHEN r.id_data_recebimento<=i.id_data_prevista THEN r.qt_recebida ELSE 0 END) qt_recebida_no_prazo,
 MAX(r.id_data_recebimento) id_data_ultimo_recebimento
 FROM fato_recebimento r JOIN fato_item_compra i USING(id_item_compra),ref
 WHERE r.id_data_recebimento<=ref.id_data_referencia GROUP BY 1
)
SELECT i.*,ref.id_data_referencia,
 COALESCE(r.qt_recebida,0) qt_recebida,
 i.qt_pedida-COALESCE(r.qt_recebida,0) qt_pendente,
 COALESCE(r.qt_recebida_no_prazo,0) qt_recebida_no_prazo,
 CASE WHEN COALESCE(r.qt_recebida,0)=i.qt_pedida THEN r.id_data_ultimo_recebimento END id_data_conclusao,
 CASE WHEN i.id_data_prevista<=ref.id_data_referencia THEN 1 ELSE 0 END in_vencido_ate_referencia,
 CASE WHEN i.id_data_prevista<=ref.id_data_referencia AND COALESCE(r.qt_recebida_no_prazo,0)=i.qt_pedida THEN 1 ELSE 0 END in_integral_no_prazo,
 CASE WHEN COALESCE(r.qt_recebida,0)=0 THEN 'Em aberto'
      WHEN r.qt_recebida<i.qt_pedida THEN 'Parcialmente recebido' ELSE 'Concluído' END tx_status,
 CASE WHEN COALESCE(r.qt_recebida,0)=i.qt_pedida THEN
   CAST(julianday(dc.dt_data)-julianday(de.dt_data) AS INT) END nr_dias_entrega_completa,
 CASE WHEN i.id_data_prevista<ref.id_data_referencia AND COALESCE(r.qt_recebida,0)<i.qt_pedida THEN 1 ELSE 0 END in_pendente_atrasado
FROM fato_item_compra i CROSS JOIN ref
LEFT JOIN rec r USING(id_item_compra)
JOIN dim_data de ON de.id_data=i.id_data_emissao
LEFT JOIN dim_data dc ON dc.id_data=r.id_data_ultimo_recebimento
WHERE i.id_data_emissao<=ref.id_data_referencia;
