# Guia dos scripts Python

## Visão geral

Os scripts implementam a geração dos dados simulados, os testes,
a preparação analítica e a geração dos artefatos do projeto.

| Etapa | Scripts |
|---|---|
| Carga inicial | `gerar_projeto.py` |
| Simulação e auditoria | `simular_operacao.py` |
| Testes | `testar_ddl.py`, `testar_operacao.py` |
| SQL e exportação | `preparar_analytics.py` |
| Geração e configuração do Power BI | `construir_powerbi.py`, `configurar_powerbi.py` |
| Validação estrutural do Power BI | `validar_powerbi_schema.py` |
| Documentação e imagem de apoio | `gerar_dicionario.py`, `gerar_resumo_visual.py` |
| Orquestração | `executar_pipeline.py` |
| Distribuição | `empacotar_entrega.py` |

Os caminhos internos são, em geral, resolvidos a partir da localização dos scripts. Para os exemplos de execução, considere o terminal aberto na raiz do projeto.

## 1. gerar_projeto.py

**Finalidade:** criar a base inicial, com dimensões, parâmetros de reposição e abertura do estoque em 01/01/2024.

**Principais atividades:**

- Executa a estrutura definida em `modelo.sql`.
- Carrega calendário, produtos, fornecedores, centros e tipos de movimento.
- Define os parâmetros iniciais de cada combinação de produto e centro.
- Registra movimentos de abertura para os saldos positivos.
- Grava as 300 posições iniciais de estoque.
- Confere integridade referencial, saldos e valores da abertura.

**Entradas:** `modelo.sql`, caminho do banco e semente aleatória.

**Saídas padrão:**

- `dados/supply_chain.sqlite`
- `dados/supply_chain.validacao.json`

**Exemplo:**

```powershell
python gerar_projeto.py --banco dados/abertura_exemplo.sqlite --semente 404
```

**Cuidados:** recusa substituir um banco existente. Sua execução isolada produz a abertura; a operação completa pertence ao simulador. As funções `inserir`, `carregar` e `validar` também são utilizadas por outros scripts.
O calendário identifica os feriados de datas fixas cadastrados no código; não constitui um calendário completo de feriados móveis, estaduais e municipais.

## 2. simular_operacao.py

**Finalidade:** gerar e auditar a operação completa de 2024–2025.

**Principais atividades:**

- Reutiliza a carga inicial de `gerar_projeto.py`.
- Simula recebimentos, expedições, ajustes e emissão de compras.
- Atualiza saldo, compras pendentes e custo médio ponderado.
- Aplica os parâmetros de reposição vigentes.
- Grava o fechamento diário por produto e centro.
- Audita os dados por consultas SQL e reconstrução cronológica dos movimentos.

A sequência diária é: recebimentos às 08h, expedições às 16h, ajustes às 17h, compras às 18h e fechamento.

**Entradas:** `modelo.sql`, funções da carga inicial, semente e caminho de destino.

**Saídas padrão:**

- `dados/supply_chain_2024_2025.sqlite`
- `dados/supply_chain_2024_2025.validacao.json`

**Exemplo:**

```powershell
python simular_operacao.py --banco dados/simulacao_exemplo.sqlite --semente 404
```

**Cuidados:** gera os dados em banco temporário e somente disponibiliza o banco final após a validação. Recusa substituir um destino existente. O período está fixado no código; a semente pode ser informada pela linha de comando.

## 3. testar_ddl.py

**Finalidade:** verificar se as restrições declaradas no banco
rejeitam dados inválidos.

**Principais atividades:**

- Cria um banco SQLite em memória.
- Executa a DDL e prepara dados para os testes.
- Testa chaves primárias, estrangeiras, obrigatoriedade e unicidade.
- Testa limites e consistências implementados por `CHECK`.
- Desfaz cada alteração de teste utilizando pontos de salvamento.

**Entradas:** `modelo.sql` e funções de `gerar_projeto.py`.

**Saída:** `testes_ddl.json`, com os casos aprovados.

**Execução:**

```powershell
python testar_ddl.py
```

**Cuidados:** não altera os bancos de demonstração.

## 4. testar_operacao.py

**Finalidade:** testar o cálculo de custo médio e a capacidade da auditoria de detectar inconsistências.

**Principais atividades:**

- Confere quatro exemplos de custo médio, incluindo entrada após saldo zero.
- Copia o banco operacional para a memória.
- Introduz quatro inconsistências deliberadas nessa cópia.
- Verifica a detecção de recebimento excedente, produto divergente, pendência adulterada e valor de fechamento adulterado.

**Entradas:** banco operacional padrão e funções de `simular_operacao.py`.

**Saída:** `testes_operacao.json`, com oito casos aprovados quando todos os testes passam.

**Execução:**

```powershell
python testar_operacao.py
```

**Cuidados:** lê o banco original em modo somente leitura. As alterações deliberadas ocorrem exclusivamente na cópia em memória. Utiliza o caminho padrão do banco, sem argumento para selecionar outro arquivo.

## 5. preparar_analytics.py

**Finalidade:** transformar o banco operacional na camada analítica consumida pelo Power BI.

**Principais atividades:**

- Executa `sql/01_views_analiticas.sql`.
- Executa e consome os resultados das consultas de `sql/02_analises.sql`.
- Exporta cinco dimensões e quatro fatos para CSV.
- Enriquece estoque e compras com atributos das views analíticas.
- Confere a janela de expedições, a demanda média, a classificação de reposição e a cobertura sem demanda.
- Consolida indicadores do fechamento e dos fornecedores.

**Entradas:** banco operacional e os dois arquivos SQL.

**Saídas:**

- Nove arquivos CSV em `powerbi/dados/`.
- `resultados/indicadores.json`.

**Execução:**

```powershell
python preparar_analytics.py
```

**Cuidados:** cria ou atualiza views no banco selecionado e sobrescreve os CSVs e o relatório de indicadores. O resumo final utiliza o corte de 31/12/2025. A mensagem de validação contém uma contagem fixa de 219.300 linhas, que precisa ser revista se o escopo mudar.

## 6. construir_powerbi.py

**Finalidade:** gerar a estrutura inicial editável do projeto Power BI a partir dos CSVs.

**Principais atividades:**

- Lê os cabeçalhos dos arquivos exportados.
- Define tipos de dados e consultas Power Query.
- Cria relacionamentos, medidas DAX e ordenações do calendário.
- Gera quatro páginas com cartões, gráficos, tabelas e filtros.
- Produz o tema visual e arquivos auxiliares de consultas e medidas.

**Entradas:** arquivos em `powerbi/dados/`.

**Principais saídas:**

- `powerbi/SupplyChain.pbip`
- Estrutura do relatório PBIR.
- Modelo semântico inicial em `model.bim`.
- `powerbi/medidas.dax`
- `powerbi/consultas_power_query.m`
- `powerbi/tema_nexo.json`
- `powerbi/estrutura_modelo.json`

**Cuidados:** recria arquivos do projeto e pode sobrescrever ajustes posteriores. A versão final salva pelo Desktop utiliza TMDL; o gerador continua produzindo `model.bim`. Deve ser executado em uma cópia destinada à regeneração, após avaliar a compatibilidade com a estrutura atual.
A geração dos arquivos não executa Power Query nem medidas DAX.

## 7. configurar_powerbi.py

**Finalidade:** ajustar o parâmetro `pPastaDados` ao local da pasta de CSVs.

**Funcionamento:** abre o `model.bim`, localiza a expressão do parâmetro e grava o caminho absoluto de `powerbi/dados/`.

**Entrada e saída:** modifica diretamente `powerbi/SupplyChain.SemanticModel/model.bim`.

**Cuidados:** a implementação atual depende de `model.bim` e precisa ser adaptada para configurar a versão final em TMDL. Nessa versão, o parâmetro pode ser ajustado pelo Power Query no Desktop.

## 8. validar_powerbi_schema.py

**Finalidade:** validar a estrutura dos arquivos do Power BI e conferir referências dos relacionamentos.

**Principais atividades:**

- Carrega os esquemas armazenados em `powerbi/schemas/registry.json`.
- Valida arquivos JSON, PBIP, PBIR e PBISM que declaram `$schema`.
- Confere se as colunas dos relacionamentos existem no modelo.
- Rejeita relacionamentos diretos entre tabelas fato.

**Saída:** `resultados/powerbi_validacao.json`.

**Dependências externas:** `jsonschema` e `referencing`.

**Cuidados:** a verificação do modelo depende de `model.bim` e precisa ser adaptada para TMDL. Não executa Power Query, DAX ou renderização no Desktop. O relatório gerado descreve validação estrutural.

## 9. gerar_dicionario.py

**Finalidade:** gerar a documentação da estrutura do banco e dos relacionamentos do Power BI.

**Principais atividades:**

- Consulta os metadados SQLite com `PRAGMA`.
- Documenta colunas, tipos, obrigatoriedade, chaves primárias e referências.
- Acrescenta a granularidade das tabelas.
- Documenta os atributos derivados da camada analítica.
- Lê os relacionamentos do modelo semântico.

**Entradas:** banco operacional padrão e `model.bim`.

**Saída:** `docs/03_dicionario_de_dados.md`.

**Cuidados:** sobrescreve o documento, incluindo eventuais edições manuais. A leitura dos relacionamentos depende de `model.bim`; é necessária adaptação para a versão em TMDL. O código já produz tabelas no formato Markdown.

## 10. gerar_resumo_visual.py

**Finalidade:** produzir uma imagem estática de apoio à conferência dos resultados.

**Principais atividades:**

- Consulta estoque no fechamento mensal.
- Consolida estoque por centro e expedições mensais.
- Calcula pontualidade por fornecedor.
- Desenha os quatro gráficos com Matplotlib.

**Entradas:** banco operacional, views analíticas e `resultados/indicadores.json`.

**Saída:** `resultados/resumo_executivo.png`.

**Dependência externa:** `matplotlib`.

**Cuidados:** a imagem é uma figura estática, distinta das capturas do Power BI. Os indicadores destacados no cabeçalho estão fixados no código; precisam ser atualizados ou calculados dinamicamente se os dados mudarem. O JSON é carregado, mas seus valores não alimentam esses destaques.

## 11. executar_pipeline.py

**Finalidade:** coordenar as principais etapas automáticas em uma sequência única.

**Sequência executada:**

1. Localiza o banco padrão ou gera uma nova simulação.
2. Executa os testes da DDL.
3. Executa os testes operacionais quando o banco padrão existe.
4. Prepara a camada analítica e exporta os CSVs.
5. Recria o projeto Power BI.
6. Configura a origem dos CSVs.

Utiliza o mesmo interpretador Python da execução principal e interrompe a sequência quando um subprocesso falha.

**Cuidados:** inclui a execução de `construir_powerbi.py`, podendo sobrescrever ajustes do relatório. Também herda a dependência de `model.bim` dos scripts chamados.
Quando recebe `--nova-base`, os testes operacionais continuam usando o banco padrão, se ele existir. A nova base passa pela auditoria executada pelo próprio simulador.
O pipeline não chama automaticamente os scripts de dicionário, resumo visual, validação de esquema ou empacotamento.

## 12. empacotar_entrega.py

**Finalidade:** reunir os arquivos do projeto em um ZIP e gerar um manifesto de integridade.

**Principais atividades:**

- Percorre os arquivos da pasta do projeto.
- Exclui alguns caches, arquivos temporários, logs e bytecode.
- Calcula o SHA-256 dos arquivos selecionados.
- Gera o manifesto e o pacote compactado.
- Confere a integridade interna do ZIP.

**Saídas:**

- `manifesto_sha256.json`, na raiz do projeto.
- `Supply_Chain_Entrega_Final.zip`, na pasta imediatamente acima do projeto.

**Cuidados:** o script não utiliza as regras do `.gitignore` e não exclui explicitamente `.git`, `.pbi`, `.venv` ou arquivos `.pbix`. Sua seleção precisa ser ajustada antes de empacotar a pasta atual do repositório. Uma execução também substitui o ZIP anterior com o mesmo nome.

## Cuidados gerais de manutenção

A versão final do Power BI foi salva em TMDL. Os scripts `configurar_powerbi.py`, `validar_powerbi_schema.py` e `gerar_dicionario.py` ainda leem `model.bim`; `construir_powerbi.py` gera esse formato inicial.

Antes de executar esses utilitários sobre a entrega final, é necessário adaptar a leitura do modelo e proteger os ajustes realizados no Desktop.
Vários utilitários executam suas atividades diretamente ao serem importados. Para reutilização como módulos Python, recomenda-se organizar sua execução em uma função `main()` protegida por `if __name__ == "__main__":`.