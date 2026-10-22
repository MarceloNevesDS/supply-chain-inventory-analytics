# Resultados e evidências
Execução dos scripts atuais, com semente 404; 4.421 pedidos, 6.821 itens, 
9.013 recebimentos, 203.550 movimentos, 219.300 fechamentos e 330 configurações 
com vigência.

## Interpretação do corte final
- Estoque de R$ 2,95 milhões: valor de aquisição gerencial, não receita.
- 90 combinações em risco durante a espera: priorizar análise de pendências e
  datas de chegada antes de emitir compras adicionais.
- 18 combinações sem saldo e com demanda observada: investigar indisponibilidade.
  A simulação não grava a demanda não atendida.
- Seis combinações com estoque positivo e sem saída: revisar manutenção do mix.
- Pontualidade de 27,26%: reflete as premissas de atraso e entregas parciais da
  simulação. Não é um benchmark de mercado.
- Nenhuma cobertura acima de 90 dias no corte final. O indicador continua
  implementado; não se fabricaram ocorrências para preencher o relatório.
- Uma combinação sinalizada para reposição no fechamento: a simulação já emitiu
  compras no próprio dia; não significa ausência de risco físico.

## Verificações executadas

| Verificação                                            | Resultado                                  |
| --- | --- |
| DDL, PK, FK, UNIQUE, NOT NULL e CHECK                  | Casos de rejeição aprovados                |
| Regressão de custo e corrupção deliberada              | Oito casos aprovados                       |
| Auditoria cronológica                                  | Sem divergências de saldo, custo ou valor  |
| Pendência por eventos de emissão/recebimento           | Sem divergências                           |
| Consultas SQL                                          | Dez executadas                             |
| Média e janela de 90 dias e classificação de reposição | 219.300 linhas conferidas                  |
| Exportação CSV                                         | Nove tabelas                               |
| Definições PBIR/PBIP/PBISM                             | 47 arquivos validados por JSON Schema      |
| Modelo semântico                                       | 16 relações com colunas existentes         |
| Atualização/renderização no Desktop                    | Finalizada com sucesso                     |

Evidências: JSON na pasta resultados, relatório junto ao banco e arquivos
testes_ddl.json/testes_operacao.json na raiz. O PNG resumo_executivo é uma
figura estática dos dados, não uma captura do Power BI.

O relatório de auditoria não certifica regras não implementadas, integração com
ERP, segurança de produção ou compatibilidade de todas as versões do Desktop.
