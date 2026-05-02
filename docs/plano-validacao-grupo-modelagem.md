# Plano Conciso para Validar com o Grupo

## Resumo

Objetivo: organizar as dúvidas de modelagem em um plano experimental curto e validável pelo grupo, para depois executar de forma reproduzível e descobrir qual modelo performa melhor e em quais condições.

Durante toda a execução futura, o arquivo [duvidas-sessao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/duvidas-sessao-modelagem.md) deve ser consultado como referência central de contexto, decisões em aberto, justificativas e hipóteses já levantadas.

A resposta final que o plano precisa produzir é:

- qual foi o melhor modelo
- com quais features
- com qual preprocessing
- com qual representação das variáveis mais sensíveis
- sob qual critério de seleção

## Frentes de trabalho

### 1. Consolidar baseline e estado atual

- Tratar o pipeline atual generalista como baseline inicial de comparação.
- Registrar a leitura prática do estado atual antes de introduzir mudanças.
- Deixar explícito que `sample_weight` é decisão de treino/modelagem e não transformação de `X`.
- Consultar o arquivo de dúvidas para garantir aderência às decisões já discutidas.

### 2. Consolidar integridade da base e preprocessing

- Confirmar regras de sentinelas com base no dicionário de dados.
- Revisar tratamento de extremos, missing e imputação.
- Manter a imputação atual como baseline, com alternativas testadas apenas de forma controlada.
- Validar se o preprocessing atual deve continuar único ou se passará a variar por família de modelo.

### 3. Definir baseline de features e features de risco

- Separar features do baseline principal.
- Separar features suspeitas para teste de remoção controlada, especialmente `KOTELCHUCK` e `IDADEPAI`.
- Registrar o que sai por leakage e o que fica para teste controlado.
- Validar cada decisão contra o arquivo de dúvidas antes de executar mudanças.

Teste de remoção controlada significa comparar o desempenho do modelo com e sem uma variável específica, para verificar se ela realmente agrega valor ou se está introduzindo ruído, redundância ou leakage.

### 4. Comparar representações de variáveis

- Testar poucos cenários reproduzíveis, por exemplo:
  - atual
  - `ESCMAE2010` ordinal + flag de ignorado
  - `GRAVIDEZ` como `GESTACAO_MULTIPLA`
  - revisão de `IDADEMAE` / `FAIXAETAMAE`
  - revisão de `MESPRENAT` / `PNTARDIO`
- Usar o arquivo de dúvidas como guia para montar os cenários e evitar combinações sem justificativa.

### 5. Comparar preprocessing + modelo juntos

- Estruturar os testes como combinações entre pipelines e modelos.
- Permitir que diferentes modelos usem preprocessamentos diferentes, se isso melhorar aderência metodológica.
- Comparar pelo menos:
  - `LogisticRegression`
  - `RandomForest`
  - `HistGradientBoosting`

### 6. Fixar regra única de seleção

- `recall >= MIN_RECALL_THRESHOLD` como critério de elegibilidade.
- `F2` como critério principal de ranking entre elegíveis.
- `recall` como desempate ou métrica de apoio.

## Sequência de execução

1. Consultar o arquivo de dúvidas e congelar baseline de dados, pipeline atual e regra de avaliação.
2. Fechar lista baseline de features e lista de teste de remoção controlada.
3. Definir 2 a 4 cenários de representação de variáveis.
4. Decidir se o preprocessing continuará único ou se haverá pipelines distintos por tipo de modelo.
5. Rodar os mesmos modelos nos cenários definidos.
6. Comparar tudo com a mesma validação cruzada e a mesma regra de seleção.
7. Escolher o melhor conjunto `pipeline + modelo`.
8. Fazer teste final de remoção controlada das variáveis mais sensíveis.
9. Registrar conclusões de volta no arquivo de dúvidas ou em documento derivado.

## Critérios de aceite

O grupo deve validar:

- que o pipeline atual será o baseline inicial
- quais variáveis ficam no baseline
- quais entram só em teste de remoção controlada
- quais cenários de representação serão testados
- se haverá preprocessing único ou específico por modelo
- quais modelos entram na comparação
- que a regra final de escolha será `recall mínimo + ranking por F2`
- que o arquivo de dúvidas será a referência permanente durante a execução

## Assumptions

- O objetivo principal continua sendo triagem com prioridade clínica para sensibilidade.
- O baseline deve evitar leakage conceitual.
- O plano será executado mais tarde, então aqui o foco é fechar decisões, não implementar.
- O arquivo de dúvidas é a principal fonte de contexto para orientar a execução futura.
