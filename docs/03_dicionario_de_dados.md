# Dicionário e modelo de dados

Termos natureza:
     id --> identificador; 
     cd --> código; 
     dt --> data/instante; 
     nm --> nome; 
     vl --> valor; 
     nr --> número; 
     sg --> sigla; 
     tx --> descrição; 
     qt --> quantidade; 
     in --> indicador.

## dim_data
Granularidade: Um dia.

+-------------------------------------------------------------------+
| Coluna              | Tipo SQLite | Obrigatória | PK | Referência |
|---------------------+-------------+-------------+----+------------|
| id_data             | INTEGER     | Sim         | 1  | —          |
| dt_data             | TEXT        | Sim         | —  | —          |
| nr_dia_mes          | INTEGER     | Sim         | —  | —          |
| nr_dia_semana       | INTEGER     | Sim         | —  | —          |
| nm_dia_semana       | TEXT        | Sim         | —  | —          |
| nr_mes              | INTEGER     | Sim         | —  | —          |
| nm_mes              | TEXT        | Sim         | —  | —          |
| nr_bimestre         | INTEGER     | Sim         | —  | —          |
| nm_bimestre         | TEXT        | Sim         | —  | —          |
| nr_trimestre        | INTEGER     | Sim         | —  | —          |
| nm_trimestre        | TEXT        | Sim         | —  | —          |
| nr_semestre         | INTEGER     | Sim         | —  | —          |
| nm_semestre         | TEXT        | Sim         | —  | —          |
| nr_ano              | INTEGER     | Sim         | —  | —          |
| nr_ano_mes          | INTEGER     | Sim         | —  | —          |
| in_fim_semana       | INTEGER     | Sim         | —  | —          |
| in_feriado_nacional | INTEGER     | Sim         | —  | —          |
| nm_feriado_nacional | TEXT        | Não         | —  | —          |
+-------------------------------------------------------------------+

## dim_produto
Granularidade: Um produto.

+-----------------------------------------------------------------+
| Coluna            | Tipo SQLite | Obrigatória | PK | Referência |
|-------------------+-------------+-------------+----+------------|
| id_produto        | INTEGER     | Sim         | 1  | —          |
| cd_produto        | TEXT        | Sim         | —  | —          |
| nm_produto        | TEXT        | Sim         | —  | —          |
| nm_categoria      | TEXT        | Sim         | —  | —          |
| nm_marca          | TEXT        | Sim         | —  | —          |
| sg_unidade_medida | TEXT        | Sim         | —  | —          |
+-----------------------------------------------------------------+

## dim_fornecedor
Granularidade: Um fornecedor.

+-------------------------------------------------------------+
| Coluna        | Tipo SQLite | Obrigatória | PK | Referência |
|---------------+-------------+-------------+----+------------|
| id_fornecedor | INTEGER     | Sim         | 1  | —          |
| cd_fornecedor | TEXT        | Sim         | —  | —          |
| nm_fornecedor | TEXT        | Sim         | —  | —          |
| nm_cidade     | TEXT        | Sim         | —  | —          |
| sg_uf         | TEXT        | Sim         | —  | —          |
| nm_regiao     | TEXT        | Sim         | —  | —          |
+-------------------------------------------------------------+

## dim_centro_distribuicao
Granularidade: Um centro.

+----------------------------------------------------------------------+
| Coluna                 | Tipo SQLite | Obrigatória | PK | Referência |
|------------------------+-------------+-------------+----+------------|
| id_centro_distribuicao | INTEGER     | Sim         | 1  | —          |
| cd_centro_distribuicao | TEXT        | Sim         | —  | —          |
| nm_centro_distribuicao | TEXT        | Sim         | —  | —          |
| nm_cidade              | TEXT        | Sim         | —  | —          |
| sg_uf                  | TEXT        | Sim         | —  | —          |
| nm_regiao              | TEXT        | Sim         | —  | —          |
+----------------------------------------------------------------------+

## dim_tipo_movimento
Granularidade: Um tipo.

+-----------------------------------------------------------------+
| Coluna            | Tipo SQLite | Obrigatória | PK | Referência |
|-------------------+-------------+-------------+----+------------|
| id_tipo_movimento | INTEGER     | Sim         | 1  | —          |
| cd_tipo_movimento | TEXT        | Sim         | —  | —          |
| tx_tipo_movimento | TEXT        | Sim         | —  | —          |
| nr_sinal          | INTEGER     | Sim         | —  | —          |
+-----------------------------------------------------------------+

## fato_item_compra
Granularidade: Um item de pedido.

+-------------------------------------------------------------------------------------+
| Coluna                   | Tipo SQLite | Obrigatória | PK | Referência              |
|--------------------------+-------------+-------------+----+-------------------------|
| id_item_compra           | INTEGER     | Sim         | 1  | —                       |
| nr_pedido                | TEXT        | Sim         | —  | —                       |
| nr_item                  | INTEGER     | Sim         | —  | —                       |
| id_produto               | INTEGER     | Sim         | —  | dim_produto             |
| id_fornecedor            | INTEGER     | Sim         | —  | dim_fornecedor          |
| id_centro_distribuicao   | INTEGER     | Sim         | —  | dim_centro_distribuicao |
| id_data_emissao          | INTEGER     | Sim         | —  | dim_data                |
| id_data_prevista         | INTEGER     | Sim         | —  | dim_data                |
| qt_pedida                | INTEGER     | Sim         | —  | —                       |
| vl_custo_unitario_pedido | numeric     | Sim         | —  | —                       |
| vl_total_item            | numeric     | Sim         | —  | —                       |
+-------------------------------------------------------------------------------------+

## fato_recebimento
Granularidade: Uma parcela recebida de um item.

+---------------------------------------------------------------------------------------+
| Coluna                     | Tipo SQLite | Obrigatória | PK | Referência              |
|----------------------------+-------------+-------------+----+-------------------------|
| id_recebimento             | INTEGER     | Sim         | 1  | —                       |
| id_item_compra             | INTEGER     | Sim         | —  | fato_item_compra        |
| id_produto                 | INTEGER     | Sim         | —  | dim_produto             |
| id_fornecedor              | INTEGER     | Sim         | —  | dim_fornecedor          |
| id_centro_distribuicao     | INTEGER     | Sim         | —  | dim_centro_distribuicao |
| id_data_recebimento        | INTEGER     | Sim         | —  | dim_data                |
| dt_recebimento             | TEXT        | Sim         | —  | —                       |
| qt_recebida                | INTEGER     | Sim         | —  | —                       |
| vl_custo_unitario_recebido | numeric     | Sim         | —  | —                       |
| vl_total_recebido          | numeric     | Sim         | —  | —                       |
+---------------------------------------------------------------------------------------+

## fato_movimento_estoque
Granularidade: Um evento de um produto/centro.

+----------------------------------------------------------------------------------------+
| Coluna                      | Tipo SQLite | Obrigatória | PK | Referência              |
|-----------------------------+-------------+-------------+----+-------------------------|
| id_movimento_estoque        | INTEGER     | Sim         | 1  | —                       |
| id_produto                  | INTEGER     | Sim         | —  | dim_produto             |
| id_centro_distribuicao      | INTEGER     | Sim         | —  | dim_centro_distribuicao |
| id_tipo_movimento           | INTEGER     | Sim         | —  | dim_tipo_movimento      |
| id_data_movimento           | INTEGER     | Sim         | —  | dim_data                |
| id_recebimento              | INTEGER     | Não         | —  | fato_recebimento        |
| dt_movimento                | TEXT        | Sim         | —  | —                       |
| qt_movimento                | INTEGER     | Sim         | —  | —                       |
| qt_movimento_assinada       | INTEGER     | Sim         | —  | —                       |
| vl_custo_unitario_movimento | numeric     | Sim         | —  | —                       |
| vl_movimento_assinado       | numeric     | Sim         | —  | —                       |
| tx_motivo_ajuste            | TEXT        | Não         | —  | —                       |
+----------------------------------------------------------------------------------------+

## fato_estoque_diario
Granularidade: Um produto/centro/data.

+-----------------------------------------------------------------------------------+
| Coluna                 | Tipo SQLite | Obrigatória | PK | Referência              |
|------------------------+-------------+-------------+----+-------------------------|
| id_data_estoque        | INTEGER     | Sim         | 1  | dim_data                |
| id_produto             | INTEGER     | Sim         | 2  | dim_produto             |
| id_centro_distribuicao | INTEGER     | Sim         | 3  | dim_centro_distribuicao |
| qt_saldo_final         | INTEGER     | Sim         | —  | —                       |
| vl_custo_medio         | numeric     | Sim         | —  | —                       |
| vl_estoque_final       | numeric     | Sim         | —  | —                       |
| qt_compra_pendente     | INTEGER     | Sim         | —  | —                       |
| nr_dias_reposicao      | INTEGER     | Sim         | —  | —                       |
| nr_dias_seguranca      | INTEGER     | Sim         | —  | —                       |
+-----------------------------------------------------------------------------------+

## aux_produto_centro
Granularidade: Uma vigência de produto/centro.

+-----------------------------------------------------------------------------------+
| Coluna                 | Tipo SQLite | Obrigatória | PK | Referência              |
|------------------------+-------------+-------------+----+-------------------------|
| id_produto_centro      | INTEGER     | Sim         | 1  | —                       |
| id_produto             | INTEGER     | Sim         | —  | dim_produto             |
| id_centro_distribuicao | INTEGER     | Sim         | —  | dim_centro_distribuicao |
| dt_inicio_vigencia     | TEXT        | Sim         | —  | —                       |
| dt_fim_vigencia        | TEXT        | Não         | —  | —                       |
| nr_dias_reposicao      | INTEGER     | Sim         | —  | —                       |
| nr_dias_seguranca      | INTEGER     | Sim         | —  | —                       |
+-----------------------------------------------------------------------------------+

## Camada analítica do Power BI
CSV fato_estoque_diario deriva de vw_estoque_analitico; fato_item_compra deriva de vw_compras_posicao_final.
Essas exportações incluem as colunas originais e atributos calculados; 

+--------------------------------------------------------------------------------+
| Atributo derivado         | Significado                                        |
|---------------------------+----------------------------------------------------|
| dt_estoque                | Data do fechamento                                 |
| qt_expedida_dia           | Saídas do dia, apenas expedições                   |
| qt_expedida_90d           | Saídas da janela de até 90 dias                    |
| nr_dias_observados        | Quantidade de dias da janela                       |
| qt_demanda_media_dia      | Média das expedições na janela                     |
| qt_posicao_estoque        | Saldo físico + compra pendente                     |
| qt_estoque_seguranca      | Média × dias de segurança, arredondada para cima   |
| qt_ponto_reposicao        | Média × (prazo + segurança), arredondada para cima |
| nr_dias_cobertura         | Saldo / média; nulo sem demanda                    |
| in_reposicao              | Posição <= ponto e demanda positiva                |
| in_risco_espera           | Saldo < demanda esperada no prazo                  |
| in_cobertura_elevada      | Cobertura > 90 dias                                |
| in_sem_saida              | Saldo positivo, janela completa e zero saída       |
| in_indisponivel           | Saldo zero e demanda observada positiva            |
| tx_situacao_estoque       | Classificação priorizada; flags podem coexistir    |
| id_data_referencia        | Corte da posição de compras                        |
| qt_recebida / qt_pendente | Recebimentos e saldo contratado até o corte        |
| qt_recebida_no_prazo      | Quantidade recebida até a previsão original        |
| id_data_conclusao         | Data da entrega integral, se concluído             |
| in_vencido_ate_referencia | Previsão até o corte, inclusive                    |
| in_integral_no_prazo      | Toda a quantidade recebida até a previsão          |
| tx_status                 | Em aberto, parcialmente recebido, concluído        |
| nr_dias_entrega_completa  | Dias corridos emissão → conclusão                  |
| in_pendente_atrasado      | Quantidade pendente e previsão anterior ao corte   |
+--------------------------------------------------------------------------------+

## Relações no Power BI

+--------------------------------------------------------------------------------------------------------+
| Origem (N)                                    | Destino (1)                                    | Ativa |
|-----------------------------------------------+------------------------------------------------+-------|
| fato_estoque_diario.id_produto                | dim_produto.id_produto                         | Sim   |
| fato_estoque_diario.id_centro_distribuicao    | dim_centro_distribuicao.id_centro_distribuicao | Sim   |
| fato_estoque_diario.id_data_estoque           | dim_data.id_data                               | Sim   |
| fato_item_compra.id_produto                   | dim_produto.id_produto                         | Sim   |
| fato_item_compra.id_centro_distribuicao       | dim_centro_distribuicao.id_centro_distribuicao | Sim   |
| fato_item_compra.id_fornecedor                | dim_fornecedor.id_fornecedor                   | Sim   |
| fato_item_compra.id_data_emissao              | dim_data.id_data                               | Sim   |
| fato_item_compra.id_data_prevista             | dim_data.id_data                               | Não   |
| fato_movimento_estoque.id_produto             | dim_produto.id_produto                         | Sim   |
| fato_movimento_estoque.id_centro_distribuicao | dim_centro_distribuicao.id_centro_distribuicao | Sim   |
| fato_movimento_estoque.id_tipo_movimento      | dim_tipo_movimento.id_tipo_movimento           | Sim   |
| fato_movimento_estoque.id_data_movimento      | dim_data.id_data                               | Sim   |
| fato_recebimento.id_produto                   | dim_produto.id_produto                         | Sim   |
| fato_recebimento.id_centro_distribuicao       | dim_centro_distribuicao.id_centro_distribuicao | Sim   |
| fato_recebimento.id_fornecedor                | dim_fornecedor.id_fornecedor                   | Sim   |
| fato_recebimento.id_data_recebimento          | dim_data.id_data                               | Sim   |
+--------------------------------------------------------------------------------------------------------+