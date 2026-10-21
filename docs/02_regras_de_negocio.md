# Regras e decisões
## Estoque
Controle por produto/centro. Aberturas positivas em 01/01/2024 às 00h; combinações
com abertura zero não geram movimento. Recebimentos às 08h, expedições às 16h,
ajustes às 17h e compras após essas operações. Ordenação por instante e ID.

Quantidades de eventos são positivas; o tipo do evento determina o sinal. Nenhum 
evento pode deixar saldo negativo. Ajustes exigem motivo. Aberturas e ajustes não
são demanda.

## Compras e recebimentos
Um pedido tem um fornecedor, centro de distribuição e data de emissão. Itens podem 
ter previsões distintas. Pedido/item é único. Cada recebimento pertence a um item 
comprado; quantidade acumulada não supera o pedido. Custo recebido é o custo 
contratado. Cada recebimento tem exatamente um movimento correspondente, sem 
duplicação.

Emitir compra aumenta pendência, não o saldo físico. Status e pendência históricos
consideram apenas compras e recebimentos até a data da análise. A view de compras
final é explicitamente uma posição em 31/12/2025.

## Valorização
Custo médio ponderado móvel por produto/centro, calculado com Decimal e oito casas.
Recebimentos atualizam a média; saídas e ajustes usam a média anterior.
Com saldo zero, o custo conhecido é preservado; próximo recebimento estabelece a
nova média. Sem custo conhecido não se gera ajuste positivo.

Valor diário = saldo × custo médio, arredondado HALF_UP (para cima) a centavos. 
Movimentos individualmente arredondados podem apresentar resíduo ao serem somados.
SQLite NUMERIC pode armazenar ponto flutuante: auditoria utiliza tolerâncias.

## Reposição e cobertura
Média observada = expedições da janela de 90 dias / dias observados (máximo 90).
A janela inclui hoje e dias sem saída. No começo, divide pelos dias decorridos.
Segurança = média × dias de segurança. Ponto = média × (prazo + segurança).
Posição = saldo físico + compras pendentes. Cobertura = saldo / média.

A camada analítica apresenta segurança e ponto arredondados para cima; a flag
de reposição compara a posição inteira com o ponto arredondado. O gerador
original compara com o ponto decimal antes de arredondar a quantidade comprada:
em fronteiras fracionárias, a indicação analítica pode antecipar a compra em
menos de uma unidade. Essa distinção está preservada, sem reescrever a simulação.

Risco durante espera: saldo < média × prazo. Cobertura elevada: mais de 90 dias.
Sem saída: saldo positivo e expedição zero em uma janela completa de 90 dias.
Demanda zero resulta em cobertura nula, não infinita nem automaticamente excesso.
Sem saldo com demanda observada sinaliza indisponibilidade, não venda perdida.

Compra simulada busca prazo + segurança + 30 dias, mínimo 20 unidades.
Exceção de implantação no primeiro dia para saldo zero com demanda simulada
positiva. Parâmetros alterados em 01/07/2025 para produtos múltiplos de dez.
Vigências são início inclusivo e fim exclusivo, sem sobreposição ou lacunas.

## Fornecedores
Pontualidade = itens integralmente recebidos até a previsão / itens cujo
vencimento ocorreu até o corte. Itens vencidos em aberto entram no denominador.
Parcela pontual não equivale a item integral pontual.
Prazo realizado = conclusão integral menos emissão, somente para itens concluídos.
Não confundir com OTD (On-Time Delivery) por entrega e/ou OTIF (On-Time In-Full) 
completo ou taxa de atendimento.

## Agregação
Compras, recebimentos e movimentos são fluxos. Estoque e pendência são posições:
somar entre produtos/centros na mesma data, não entre vários dias.
Custo unitário e cobertura não devem ser somados. Power BI mostra cobertura
somente na granularidade de um produto e um centro.