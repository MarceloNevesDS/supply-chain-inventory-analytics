// dim_centro_distribuicao
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/dim_centro_distribuicao.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_centro_distribuicao", Int64.Type}, {"cd_centro_distribuicao", type text}, {"nm_centro_distribuicao", type text}, {"nm_cidade", type text}, {"sg_uf", type text}, {"nm_regiao", type text}}, "en-US")
in
  Tipos

// dim_data
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/dim_data.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_data", Int64.Type}, {"dt_data", type date}, {"nr_dia_mes", Int64.Type}, {"nr_dia_semana", Int64.Type}, {"nm_dia_semana", type text}, {"nr_mes", Int64.Type}, {"nm_mes", type text}, {"nr_bimestre", Int64.Type}, {"nm_bimestre", type text}, {"nr_trimestre", Int64.Type}, {"nm_trimestre", type text}, {"nr_semestre", Int64.Type}, {"nm_semestre", type text}, {"nr_ano", Int64.Type}, {"nr_ano_mes", Int64.Type}, {"in_fim_semana", Int64.Type}, {"in_feriado_nacional", Int64.Type}, {"nm_feriado_nacional", type text}}, "en-US")
in
  Tipos

// dim_fornecedor
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/dim_fornecedor.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_fornecedor", Int64.Type}, {"cd_fornecedor", type text}, {"nm_fornecedor", type text}, {"nm_cidade", type text}, {"sg_uf", type text}, {"nm_regiao", type text}}, "en-US")
in
  Tipos

// dim_produto
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/dim_produto.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_produto", Int64.Type}, {"cd_produto", type text}, {"nm_produto", type text}, {"nm_categoria", type text}, {"nm_marca", type text}, {"sg_unidade_medida", type text}}, "en-US")
in
  Tipos

// dim_tipo_movimento
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/dim_tipo_movimento.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_tipo_movimento", Int64.Type}, {"cd_tipo_movimento", type text}, {"tx_tipo_movimento", type text}, {"nr_sinal", Int64.Type}}, "en-US")
in
  Tipos

// fato_estoque_diario
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/fato_estoque_diario.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_data_estoque", Int64.Type}, {"id_produto", Int64.Type}, {"id_centro_distribuicao", Int64.Type}, {"qt_saldo_final", Int64.Type}, {"vl_custo_medio", type number}, {"vl_estoque_final", type number}, {"qt_compra_pendente", Int64.Type}, {"nr_dias_reposicao", Int64.Type}, {"nr_dias_seguranca", Int64.Type}, {"dt_estoque", type date}, {"qt_expedida_dia", Int64.Type}, {"qt_expedida_90d", Int64.Type}, {"nr_dias_observados", Int64.Type}, {"qt_demanda_media_dia", type number}, {"qt_posicao_estoque", Int64.Type}, {"qt_estoque_seguranca", Int64.Type}, {"qt_ponto_reposicao", Int64.Type}, {"nr_dias_cobertura", type number}, {"in_reposicao", Int64.Type}, {"in_risco_espera", Int64.Type}, {"in_cobertura_elevada", Int64.Type}, {"in_sem_saida", Int64.Type}, {"in_indisponivel", Int64.Type}, {"tx_situacao_estoque", type text}}, "en-US")
in
  Tipos

// fato_item_compra
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/fato_item_compra.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_item_compra", Int64.Type}, {"nr_pedido", type text}, {"nr_item", Int64.Type}, {"id_produto", Int64.Type}, {"id_fornecedor", Int64.Type}, {"id_centro_distribuicao", Int64.Type}, {"id_data_emissao", Int64.Type}, {"id_data_prevista", Int64.Type}, {"qt_pedida", Int64.Type}, {"vl_custo_unitario_pedido", type number}, {"vl_total_item", type number}, {"id_data_referencia", Int64.Type}, {"qt_recebida", Int64.Type}, {"qt_pendente", Int64.Type}, {"qt_recebida_no_prazo", Int64.Type}, {"id_data_conclusao", Int64.Type}, {"in_vencido_ate_referencia", Int64.Type}, {"in_integral_no_prazo", Int64.Type}, {"tx_status", type text}, {"nr_dias_entrega_completa", Int64.Type}, {"in_pendente_atrasado", Int64.Type}}, "en-US")
in
  Tipos

// fato_movimento_estoque
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/fato_movimento_estoque.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_movimento_estoque", Int64.Type}, {"id_produto", Int64.Type}, {"id_centro_distribuicao", Int64.Type}, {"id_tipo_movimento", Int64.Type}, {"id_data_movimento", Int64.Type}, {"id_recebimento", Int64.Type}, {"dt_movimento", type datetime}, {"qt_movimento", Int64.Type}, {"qt_movimento_assinada", Int64.Type}, {"vl_custo_unitario_movimento", type number}, {"vl_movimento_assinado", type number}, {"tx_motivo_ajuste", type text}}, "en-US")
in
  Tipos

// fato_recebimento
let
  Fonte = Csv.Document(File.Contents(pPastaDados & "/fato_recebimento.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
  Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
  Tipos = Table.TransformColumnTypes(Nulos, {{"id_recebimento", Int64.Type}, {"id_item_compra", Int64.Type}, {"id_produto", Int64.Type}, {"id_fornecedor", Int64.Type}, {"id_centro_distribuicao", Int64.Type}, {"id_data_recebimento", Int64.Type}, {"dt_recebimento", type datetime}, {"qt_recebida", Int64.Type}, {"vl_custo_unitario_recebido", type number}, {"vl_total_recebido", type number}}, "en-US")
in
  Tipos