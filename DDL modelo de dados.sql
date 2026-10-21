pragma foreign_keys=ON;
create table dim_data (
   id_data             integer primary key,
   dt_data             text    not null unique,
   nr_dia_mes          integer not null check (nr_dia_mes BETWEEN 1 AND 31),
   nr_dia_semana       integer not null check (nr_dia_semana BETWEEN 1 AND 7),
   nm_dia_semana       text    not null,
   nr_mes              integer not null check (nr_mes BETWEEN 1 AND 12),
   nm_mes              text    not null,
   nr_bimestre         integer not null check (nr_bimestre BETWEEN 1 AND 6),
   nm_bimestre         text    not null,
   nr_trimestre        integer not null check (nr_trimestre BETWEEN 1 AND 4),
   nm_trimestre        text    not null,
   nr_semestre         integer not null check (nr_semestre BETWEEN 1 AND 2),
   nm_semestre         text    not null,
   nr_ano              integer not null,
   nr_ano_mes          integer not null,
   in_fim_semana       integer not null check (in_fim_semana in (0, 1)),
   in_feriado_nacional integer not null default 0 check (in_feriado_nacional IN (0, 1)),
   nm_feriado_nacional text
);
create table dim_produto (
   id_produto        integer primary key,
   cd_produto        text not null unique,
   nm_produto        text not null,
   nm_categoria      text not null,
   nm_marca          text not null,
   sg_unidade_medida text not null
);
create table dim_centro_distribuicao (
   id_centro_distribuicao  integer primary key,
   cd_centro_distribuicao  text not null unique,
   nm_centro_distribuicao  text not null,
   nm_cidade               text not null,
   sg_uf                   text not null,
   nm_regiao               text not null
);
create table dim_fornecedor (
   id_fornecedor   integer primary key,
   cd_fornecedor   text not null unique,
   nm_fornecedor   text not null,
   nm_cidade       text not null,
   sg_uf           text not null,
   nm_regiao       text not null
);
create table dim_tipo_movimento (
   id_tipo_movimento  integer primary key,
   cd_tipo_movimento  text    not null unique,
   tx_tipo_movimento  text    not null,
   nr_sinal           integer not null check (nr_sinal in (-1, 1))
);
create table fato_item_compra (
   id_item_compra      integer primary key,
   nr_pedido           text not null,
   nr_item             integer not null check (nr_item > 0),
   id_produto          integer not null
      references dim_produto ( id_produto ),
   id_fornecedor       integer not null
      references dim_fornecedor ( id_fornecedor ),
   id_centro_distribuicao integer not null
      references dim_centro_distribuicao ( id_centro_distribuicao ),
   id_data_emissao     integer not null
      references dim_data ( id_data ),
   id_data_prevista    integer not null
      references dim_data ( id_data ),
   qt_pedida           integer not null check (qt_pedida > 0),
   vl_custo_unitario_pedido numeric not null check (vl_custo_unitario_pedido > 0),
   vl_total_item       numeric not null check (vl_total_item > 0),
   unique ( nr_pedido, nr_item ),
   check (id_data_prevista >= id_data_emissao)
);
create table fato_recebimento (
   id_recebimento integer primary key,
   id_item_compra integer not null
      references fato_item_compra (id_item_compra),
   id_produto integer not null
      references dim_produto (id_produto),
   id_fornecedor integer not null
      references dim_fornecedor (id_fornecedor),
   id_centro_distribuicao integer not null
      references dim_centro_distribuicao (id_centro_distribuicao),
   id_data_recebimento integer not null
      references dim_data (id_data),
   dt_recebimento text not null,
   qt_recebida integer not null
      check (qt_recebida > 0),
   vl_custo_unitario_recebido numeric not null
      check (vl_custo_unitario_recebido > 0),
   vl_total_recebido numeric not null
      check (vl_total_recebido > 0)
);
create table fato_movimento_estoque (
   id_movimento_estoque integer primary key,
   id_produto integer not null
      references dim_produto (id_produto),
   id_centro_distribuicao integer not null
      references dim_centro_distribuicao (id_centro_distribuicao),
   id_tipo_movimento integer not null
      references dim_tipo_movimento (id_tipo_movimento),
   id_data_movimento integer not null
      references dim_data (id_data),
   id_recebimento integer unique
      references fato_recebimento (id_recebimento),
   dt_movimento text not null,
   qt_movimento integer not null
      check (qt_movimento > 0),
   qt_movimento_assinada integer not null
      check (
         qt_movimento_assinada = qt_movimento
         or qt_movimento_assinada = -qt_movimento
      ),
   vl_custo_unitario_movimento numeric not null
      check (vl_custo_unitario_movimento > 0),
   vl_movimento_assinado numeric not null
      check (
         (qt_movimento_assinada > 0
            and vl_movimento_assinado >= 0)
         or
         (qt_movimento_assinada < 0
            and vl_movimento_assinado <= 0)
      ),
   tx_motivo_ajuste text
);
create table fato_estoque_diario (
   id_data_estoque integer not null
      references dim_data (id_data),
   id_produto integer not null
      references dim_produto (id_produto),
   id_centro_distribuicao integer not null
      references dim_centro_distribuicao (id_centro_distribuicao),
   qt_saldo_final integer not null
      check (qt_saldo_final >= 0),
   vl_custo_medio numeric not null
      check (vl_custo_medio >= 0),
   vl_estoque_final numeric not null
      check (vl_estoque_final >= 0),
   qt_compra_pendente integer not null
      check (qt_compra_pendente >= 0),
   nr_dias_reposicao integer not null
      check (nr_dias_reposicao > 0),
   nr_dias_seguranca integer not null
      check (nr_dias_seguranca >= 0),
   primary key (
      id_data_estoque,
      id_produto,
      id_centro_distribuicao
   ),
   check (
      qt_saldo_final = 0
      or vl_custo_medio > 0
   ),
   check (
      qt_saldo_final <> 0
      or vl_estoque_final = 0
   )
);
create table aux_produto_centro (
   id_produto_centro integer primary key,
   id_produto integer not null
      references dim_produto (id_produto),
   id_centro_distribuicao integer not null
      references dim_centro_distribuicao (id_centro_distribuicao),
   dt_inicio_vigencia text not null,
   dt_fim_vigencia text,
   nr_dias_reposicao integer not null
      check (nr_dias_reposicao > 0),
   nr_dias_seguranca integer not null
      check (nr_dias_seguranca >= 0),
   unique (
      id_produto,
      id_centro_distribuicao,
      dt_inicio_vigencia
   ),
   check (
      dt_fim_vigencia is null
      or dt_fim_vigencia > dt_inicio_vigencia
   )
);