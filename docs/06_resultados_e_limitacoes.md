# Resultados e limitações — Supply Chain & Inventory Analytics

## 1. Objetivo e escopo

O projeto analisa compras, recebimentos, movimentações e posições diárias de 
estoque da empresa fictícia Nexo Distribuidora, utilizando dados sintéticos de 
2024–2025.
A solução integra Python, SQLite, SQL e Power BI para acompanhar disponibilidade 
de produtos, necessidade de reposição, desempenho de fornecedores e capital 
aplicado em estoque.
A operação contempla 100 produtos, três centros de distribuição e 12 fornecedores. 
As análises de posição final apresentadas neste documento consideram 31/12/2025, 
sem filtros de centro ou categoria.


## 2. Principais resultados

Estoque no fechamento

| Indicador                                      | Resultado       |
| --- | --- |
| Valor do estoque                               | R$ 2.951.164,50 |
| Saldo físico                                   | 34.875 unidades |
| Compras pendentes	                             | 25.637 unidades |
| Combinações de produto e centro em risco	     | 90              |
| Combinações sem saldo e com demanda observada  | 8               |
| Combinações com estoque e sem saída em 90 dias | 6               |
| Combinações a repor	                         | 1               |

Os indicadores evidenciam situações que exigem ações distintas.
As 90 combinações em risco possuem saldo físico inferior à demanda média observada 
multiplicada pelo prazo de reposição. Esse resultado sinaliza possibilidade de 
falta antes da reposição, caso o ritmo de consumo se mantenha.
As 18 combinações sem saldo e com demanda observada representam indisponibilidade 
física no fechamento. As seis combinações com estoque e sem saída em 90 dias merecem 
investigação sobre demanda e destinação do saldo.
A existência de apenas uma combinação a repor não contradiz os demais alertas. 
O indicador de reposição considera saldo físico mais compras pendentes, enquanto o 
risco considera a disponibilidade física durante o prazo de reposição. Uma compra 
emitida pode reduzir a necessidade de um novo pedido sem resolver a indisponibilidade 
imediata.

Compras e recebimentos no período

| Indicador	          | Resultado            |
| --- | --- |
| Pedidos emitidos	  | 4.421                |
| Itens de compra	  | 6.821                |
| Valor comprado	  | R$ 105.248.309,80    |
| Valor recebido	  | R$ 103.237.368,91    |
| Unidades expedidas  | 1.238.829            |


Compras e recebimentos representam eventos diferentes. A diferença entre seus 
valores não deve ser interpretada automaticamente como atraso: parte dos itens 
ainda pode estar dentro do prazo previsto no fechamento.

Desempenho dos fornecedores

| Indicador	                                   | Resultado |
| --- | --- |
| Itens com prazo previsto até o fechamento    | 6.720     |
| Itens integralmente recebidos no prazo       | 1.832     |
| Pontualidade                                 | 27,26     |
| Itens pendentes atrasados                    | 26        |
| Prazo médio de entrega dos itens concluídos  | 13,14     |

A pontualidade foi calculada por:
Itens integralmente recebidos no prazo ÷ itens com prazo previsto até o fechamento.
Recebimentos parciais somente atendem ao critério quando a quantidade total do 
item é recebida até o prazo original. Itens vencidos ainda pendentes permanecem no 
denominador.
Os 26 itens pendentes atrasados representam o saldo de itens vencidos ainda abertos. 
Eles não representam todos os atrasos históricos, pois itens entregues com atraso 
também reduzem a pontualidade.

Na exploração do Power BI, o Fornecedor fictício 12 apresentou:

| Indicador	                                 | Resultado      |
| --- | --- |
| Itens com prazo previsto até o fechamento  | 599            |
| Itens integralmente recebidos no prazo     | 64             |
| Pontualidade                               | 10,68%         |
| Itens pendentes atrasados                  | 4              |
| Prazo médio dos itens concluídos           | 15,11 dia      |
        
A pontualidade do Fornecedor fictício 12 ficou 16,58 pontos percentuais abaixo do 
resultado geral. O resultado justifica priorizar a investigação de seus prazos, 
considerando também os produtos e centros atendidos.

Ajustes de estoque: Foram registradas 1.450 unidades em ajustes, considerando a 
soma das quantidades dos ajustes positivos e negativos. O efeito financeiro 
líquido foi de R$ 4.937,35 positivos.
O valor líquido pode ocultar compensações entre entradas e saídas. Por isso, 
deve ser analisado junto com o volume e os motivos dos ajustes.

## 3. Recomendações de negócio

| Situação identificada	                   | Ação proposta                                                             |
| --- | --- |
| Saldo zero com demanda observada         | Conferir recebimentos previstos e avaliar antecipações ou transferências  |
| Cobertura inferior ao prazo de reposição | Acompanhar compras pendentes antes de ocorrer falta                       |
| Baixa pontualidade de fornecedores       | Comparar prazos prometidos e realizados por item e acompanhar recorrência |
| Estoque sem saída por 90 dias            | Investigar demanda, cadastro e alternativas de destinação                 |
| Ajustes positivos e negativos            | Analisar motivos e recorrência por produto e centro                       |

Essas ações são propostas analíticas. 
O projeto não mede resultados posteriores à sua implementação.

## 4. Validação realizada

A validação ocorreu em duas frentes:
- Dados e regras: execução da DDL, testes de restrições e regressão, conferência 
de integridade referencial e reconciliação de saldos, custos, valores e compras 
pendentes. Os testes executados não identificaram divergências nos critérios 
verificados.
- Power BI Desktop: Conferência dos principais indicadores, testes visuais de 
filtros e seleções e revisão da apresentação das quatro páginas.

As capturas demonstram os comportamentos observados durante a revisão. Elas não 
substituem uma auditoria exaustiva de todas as medidas e combinações possíveis de 
filtros.

## 5. Limitações e cuidados de interpretação

- Dados sintéticos. Os resultados descrevem uma operação simulada e não representam 
o desempenho de uma empresa real.
- Demanda baseada em expedições atendidas. A média utiliza saídas realizadas nos 
últimos 90 dias corridos, incluindo dias sem saída. Em períodos de falta, ela pode 
subestimar a demanda real. Não há registro de pedidos não atendidos ou vendas perdidas.
- Risco é um sinal, não uma previsão garantida. O cálculo depende da continuidade 
da demanda observada e dos parâmetros de reposição. Não incorpora uma previsão 
probabilística da demanda ou dos atrasos.
- Compras pendentes não equivalem a disponibilidade física. O indicador de reposição 
considera suas quantidades, mas a chegada precisa ocorrer a tempo para evitar falta.
- Pontualidade por item de compra. O indicador exige recebimento integral até o prazo 
original. Não mede pontualidade por parcela, por pedido completo ou todos os componentes 
de OTIF (On-Time In-Full).
- Prazo médio somente dos itens concluídos. Itens ainda abertos não participam dessa 
média, que deve ser interpretada junto com as pendências atrasadas.
- Corte final de fornecedores. A página de fornecedores representa a avaliação em 
31/12/2025; não oferece reconstrução dinâmica desse status para qualquer data histórica.
- Estoque não pode ser somado entre datas. A posição diária é um retrato do saldo. 
Somar posições de dias diferentes duplicaria a interpretação do estoque disponível.
- Arredondamento do ponto de reposição. A simulação compara o ponto calculado em 
decimal; a camada analítica utiliza seu arredondamento para cima. Isso pode alterar 
classificações próximas ao limite em menos de uma unidade.
- Causalidade e impacto não comprovados. A baixa pontualidade e os riscos de falta 
justificam investigação conjunta, mas não demonstram, isoladamente, relação causal. 
Também não foram comprovadas reduções de custos, rupturas ou capital empregado.

## 6. Contribuição do projeto

O projeto demonstra a construção de uma solução analítica desde as regras de negócio 
e a modelagem dimensional até a simulação operacional, validação dos dados, consultas 
SQL e apresentação no Power BI.
Seu principal resultado é permitir distinguir necessidade de comprar, necessidade de 
agilizar uma compra existente e necessidade de investigar estoque sem movimentação, 
apoiando decisões específicas para cada situação.
