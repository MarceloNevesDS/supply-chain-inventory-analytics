Se desejar baixar os objetos deste projeto para sua máquina local, siga os
passos abaixo:

# Power BI — abertura, modelo e validação

## Abrir (iniciar o projeto)
1. Extraia os objetos na raiz do projeto (Supply Chain & Inventory Analytics).
2. Configure o parâmetro `pPastaDados` conforme as instruções da seção Modelo semântico.
3. Abra `powerbi/SupplyChain.pbip` no Power BI Desktop.
4. Se a versão solicitar habilitação de projetos PBIP/PBIR, siga as opções
   indicadas pelo próprio Desktop e reinicie o aplicativo quando necessário.
5. Atualize os dados. São nove arquivos CSV UTF-8, com números no padrão en-US.
6. Se solicitado, confirme o acesso à pasta de dados local.
7. Confira as quatro páginas e os resultados abaixo.
8. Se desejar um arquivo único com dados carregados, salve como PBIX.

O projeto usa importação de CSV para não depender de driver SQLite/ODBC.
O SQLite permanece como base de auditoria e origem do processamento Python.
Os arquivos CSV são gerados por preparar_analytics.py.

## Modelo semântico
O escopo das tabelas contempla cinco dimensões e quatro fatos, com relacionamemtos 
muitos-para-um e filtro unidirecional das dimensões para fatos; sem ligações 
diretas entre fatos. Compras usam emissão como data ativa e previsão como relação 
inativa. Os IDs ficam ocultos. A dimensão calendário tem dia, mês, bimestre, 
trimestre, semestre e nomes. Os textos de calendário são ordenados pelos atributos 
numéricos.

O modelo semântico da versão final está no formato TMDL, na pasta
`powerbi/SupplyChain.SemanticModel/definition/`.

Para configurar a origem dos dados em outra máquina:

1. Abra `powerbi/SupplyChain.pbip` no Power BI Desktop.
2. No Power Query, localize o parâmetro `pPastaDados` em Gerenciar parâmetros.
3. Informe o caminho absoluto da pasta `powerbi/dados` da sua cópia do projeto.
4. Aplique as alterações e atualize os dados.

O script `configurar_powerbi.py` foi desenvolvido para a estrutura inicial
em `model.bim` e precisa ser adaptado antes de configurar a versão em TMDL.

O script `construir_powerbi.py` recria o projeto. Sua execução pode sobrescrever
os ajustes de modelo e apresentação feitos posteriormente no Power BI Desktop.

## Páginas de relatório

| Página                    | Leitura                                                |
| --- | --- |
| 01 • Visão executiva      | Estoque no fechamento, risco, fluxos e tendência       |
| 02 • Estoque e reposição  | Posição de produto/centro, pendências e cobertura      |
| 03 • Fornecedores         | Posição final em 31/12/2025, pontualidade por item     |
| 04 • Compras e movimentos | Compras por emissão, recebimentos por chegada, ajustes |

Há quatro páginas e 37 visuais definidos, incluindo segmentadores.  O tema utilizado 
está em tema_nexo.json e pode ser importado em Design → Importar tema.

## Comportamento das medidas
Estoque usa o último dia do contexto, limitado ao último dia carregado. Em meses
inteiramente posteriores à carga, retorna vazio. Para um ano selecionado, usa
o fechamento desse ano; para todo o período, usa 31/12/2025.

Os fluxos respeitam o período selecionado. Gráfico de valor comprado por mês usa
emissão; valor recebido usa recebimento. 

Fornecedores usa flags de posição final: a página não tem segmentador de ano.
Se adicionar filtro de data, ele filtrará coortes por emissão; não transformará
automaticamente o status final em status histórico. Para isso use a consulta SQL
histórica ou construa um indicador DAX específico.

## Conferência sem filtros aplicados

| Indicador                     | Esperado        |
| --- | --- |
| Valor do estoque              | R$ 2.951.164,50 |
| Saldo em unidades             | 34.875          |
| Compra pendente               | 25.637          |
| Combinações em risco          | 90              |
| Combinações sem saldo         | 18              |
| Combinações sem saída         | 6               |
| Combinações para repor        | 1               |
| Itens vencidos no corte final | 6.720           |
| Itens integrais no prazo      | 1.832           |
| Pontualidade                  | 27,26%          |
| Itens pendentes atrasados     | 26              |
| Pedidos emitidos              | 4.421           |
| Unidades expedidas            | 1.238.829       |

## Critérios para concluir a homologação na sua máquina local
- Atualização das nove tabelas sem erro de Power Query.
- Medidas sem erro de DAX.
- Cartões conferidos com a tabela acima.
- Selecionar 2024: estoque deve usar 31/12/2024, não a soma dos dias.
- Selecionar um centro e categoria: fatos devem respeitar as dimensões.

Estado desta entrega: definições validadas contra os esquemas oficiais e
referências estruturais conferidas. Power Query, DAX e renderização no Desktop
devem ser executados no seu ambiente. A validação de esquema não substitui
essa homologação.

## Fontes oficiais consultadas neste projeto
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset
- https://developer.microsoft.com/json-schemas/fabric/
