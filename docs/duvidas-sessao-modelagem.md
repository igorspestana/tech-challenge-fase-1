# Dúvidas Esclarecidas na Sessão de Modelagem

## 1. Quando usa `sample_weight=balanced`, o balanceamento é feito em `y` ou em `X` também?

O balanceamento é calculado a partir de `y`.

No `03_modeling.ipynb`, os pesos são criados com `compute_sample_weight(class_weight="balanced", y=y)`. Isso significa que:

- a frequência das classes em `y` define os pesos
- cada linha recebe um peso conforme sua classe
- `X` não é rebalanceado, reamostrado nem transformado por causa disso

Na prática, o `X` influencia o treino com mais ou menos peso por linha, mas o cálculo do balanceamento vem apenas do alvo `y`.

## 2. O tratamento de dados precisa ser igual para todos os modelos?

Não.

O ideal é manter igual o que é regra de qualidade e consistência do dado, e adaptar o que depende do algoritmo.

Etapas que costumam ser comuns:

- limpeza e definição do alvo
- separação treino/teste
- prevenção de leakage
- tratamento básico de valores ausentes

Etapas que podem variar por modelo:

- `scaling`
- encoding
- seleção de variáveis
- tratamento de outliers
- estratégia de balanceamento

Exemplos:

- regressão logística costuma se beneficiar de `scaling`
- modelos de árvore normalmente não precisam de `scaling`

## 3. O `src/pipeline.py` está sendo usado de forma generalista para todos os modelos?

Não no estado atual da branch.

O arquivo `src/pipeline.py` ainda está como placeholder com `NotImplementedError`, então ele não está orquestrando a modelagem nem aplicando preprocessing comum ou específico.

Hoje, a lógica efetiva da modelagem está concentrada em `notebooks/03_modeling.ipynb`.

## 4. Qual é a leitura prática do estado atual?

Hoje o fluxo está assim:

- o preprocessing e os artefatos anteriores vêm da trilha de notebooks
- a modelagem acontece no `03_modeling.ipynb`
- o `pipeline.py` permanece reservado para uma futura produtização por CLI ou Docker

Se a equipe quiser evoluir isso depois, o caminho mais seguro é:

- manter uma base comum de preprocessing para regras do dado
- criar pipelines específicos por modelo para transformações sensíveis ao algoritmo

## 5. Foram criadas variáveis categóricas a partir de variáveis contínuas e a variável contínua foi mantida. Ela deveria ser removida?

Não necessariamente.

No estado atual do projeto, as duas versões da informação foram mantidas:

- `IDADEMAE` continua como variável numérica
- `FAIXAETAMAE` foi criada a partir de `IDADEMAE` com `pd.cut` e depois transformada em dummies

Isso significa que o modelo recebe ao mesmo tempo:

- a informação contínua original
- a informação discretizada em faixas de risco

Isso pode ser útil em alguns casos, mas também pode gerar redundância.

## 6. Isso influencia o pipeline?

Sim.

Como o preprocessing atual é generalista, a mesma matriz final é usada para todos os modelos. Assim:

- a regressão logística recebe tanto a variável contínua quanto as dummies da variável categorizada
- os modelos de árvore também recebem as duas versões

Esse desenho é válido para comparação inicial, mas não é o ideal para uma arquitetura final, porque diferentes algoritmos aproveitam essas representações de maneira diferente.

## 7. Para quais modelos faz mais sentido usar a variável categórica criada e para quais faz mais sentido usar a contínua?

Regra prática para este projeto:

- `LogisticRegression`: pode fazer sentido manter as duas versões, porque a contínua captura tendência gradual e a categórica pode capturar faixas clínicas de risco
- `RandomForest`: em geral faz mais sentido começar pela variável contínua e só manter a categórica se houver ganho validado
- `HistGradientBoosting`: também tende a aproveitar melhor a variável contínua, já que o próprio modelo aprende cortes

## 8. Qual recomendação prática para decidir?

O ideal é validar empiricamente, em vez de decidir só por teoria.

Testes recomendados para variáveis como idade materna:

- usar apenas a variável contínua
- usar apenas a versão categorizada
- usar ambas

Sugestão inicial:

- para `LogisticRegression`, começar testando ambas
- para `RandomForest` e `HistGradientBoosting`, começar testando apenas a contínua
- manter a categorizada nas árvores apenas se houver ganho real em validação cruzada e teste

## 9. `KOTELCHUCK` pode ser considerado leakage?

Sim, há forte risco de leakage.

No projeto atual:

- a target é `PREMATURO`
- `SEMAGESTAC` e `GESTACAO` já foram removidas por leakage direto
- `CONSPRENAT` também foi removida por ser uma proxy influenciada pela duração da gestação
- `KOTELCHUCK` permaneceu nas features

O problema é que `KOTELCHUCK` não é uma variável bruta. Ele é um índice derivado do acompanhamento pré-natal e depende da duração da gestação ou de uma expectativa ajustada pela idade gestacional.

Como a idade gestacional é justamente a base da definição de prematuridade, `KOTELCHUCK` carrega parte do mesmo sinal que foi removido em `SEMAGESTAC` e `GESTACAO`.

## 10. Que tipo de leakage seria esse?

Não é leakage direto como usar a própria idade gestacional.

É mais correto tratar `KOTELCHUCK` como:

- variável derivada de uma informação muito próxima da target
- proxy de idade gestacional
- feature de alto risco de vazamento conceitual

Ou seja, mesmo sem ser a própria target, ela pode reintroduzir indiretamente a informação que vocês decidiram tirar.

## 11. Qual a recomendação prática para este projeto?

Se o objetivo é prever prematuridade em um cenário clínico útil, a recomendação é remover `KOTELCHUCK` da modelagem principal.

Justificativa:

- ele depende de informação ligada à duração final da gestação
- isso reduz a validade preditiva real do modelo
- pode inflar artificialmente as métricas

Uma forma segura de validar essa suspeita é fazer uma ablação:

- cenário A: modelo com `KOTELCHUCK`
- cenário B: modelo sem `KOTELCHUCK`

Se houver queda forte de performance ao remover `KOTELCHUCK`, isso reforça a hipótese de que ele estava carregando sinal muito próximo da target.

## 12. Existe uma base melhor do IBGE para enriquecer o SINASC?

Sim.

Os arquivos de IBGE usados atualmente no projeto são basicamente de geografia e regionalização administrativa, com informações como:

- `codigo_ibge`
- `latitude` e `longitude`
- `capital`
- `UF`
- `mesorregiao`
- `microrregiao`
- `regiao imediata`
- `regiao intermediaria`

Essas variáveis ajudam a representar localização e contexto regional, mas não trazem indicadores socioeconômicos mais fortes.

Por isso, elas têm utilidade limitada para enriquecer a modelagem de prematuridade.

Se a ideia for usar uma base melhor do IBGE, a recomendação é buscar indicadores municipais derivados de:

- `Censo Demográfico 2022`
- `SIDRA`
- `Cidades e Estados`

Essas fontes podem trazer variáveis mais úteis para contexto territorial e social, como:

- renda
- escolaridade
- saneamento
- urbanização
- características domiciliares
- densidade populacional

Resumo prático:

- o `IBGE` atual do projeto serve mais para localização
- um `IBGE` melhor para enriquecimento seria baseado em indicadores municipais do `Censo 2022` e do `SIDRA`
- o join continuaria sendo por `codigo_ibge`

## 13. A ordenação dos melhores modelos pode ser revista?

Sim.

Hoje existe uma pequena inconsistência entre o ranking exibido e a regra final de seleção.

Atualmente, a tabela comparativa é ordenada por:

- `cv_recall_mean`
- `cv_f2_mean`

Mas a seleção final do melhor modelo já considera a lógica:

- primeiro verificar se `cv_recall_mean >= MIN_RECALL_THRESHOLD`
- entre os elegíveis, escolher o maior `cv_f2_mean`
- usar `cv_recall_mean` como desempate

Do ponto de vista de boas práticas, quando já existe um limiar mínimo de recall definido por requisito clínico, o mais coerente é:

- tratar `recall` como critério de elegibilidade
- tratar `F2` como critério principal de ranking entre os elegíveis

Isso faz sentido porque o `F2` já favorece recall, mas ainda preserva alguma penalização para perda de precisão.

Assim, a sugestão é revisar a ordenação para algo mais alinhado com a política final do projeto, por exemplo:

- `meets_min_recall`
- `cv_f2_mean`
- `cv_recall_mean`

Se for desejada uma mudança mínima, entre as duas opções discutidas, a recomendação é preferir:

- `comparison_df.sort_values(["cv_f2_mean", "cv_recall_mean"], ascending=False)`

Resumo prático:

- se o projeto já usa `MIN_RECALL_THRESHOLD`, faz mais sentido usar `F2` como critério principal de ordenação
- o `recall` continua prioritário, mas como restrição mínima e não necessariamente como primeiro campo do ranking bruto

## 14. Faz mais sentido usar `GRAVIDEZ` categórica ou uma variável binária de gestação múltipla?

Para este projeto, é bastante defensável que uma variável binária de gestação múltipla seja melhor como representação principal.

Exemplo:

- `GESTACAO_MULTIPLA = 0` para gestação única
- `GESTACAO_MULTIPLA = 1` para gestação dupla ou tripla e mais

Justificativas:

- melhora a interpretabilidade
- reduz a fragmentação em categorias raras
- evita leituras confusas de dummies como `GRAVIDEZ_UNICA`
- representa de forma mais direta o conhecimento de domínio, já que o principal contraste clínico costuma ser entre gestação única e não única

Do ponto de vista médico-científico, o sinal mais relevante costuma ser justamente o aumento de risco associado à gestação múltipla.

A principal desvantagem dessa simplificação é perder a distinção entre:

- `DUPLA`
- `TRIPMAIS`

Se houver volume suficiente nessas categorias, pode existir sinal adicional nessa separação. Mesmo assim, como primeira representação, a versão binária tende a ser mais estável e mais fácil de interpretar.

Recomendação prática:

- usar `GESTACAO_MULTIPLA` como representação principal em testes futuros
- manter a versão categórica apenas se ela demonstrar ganho real e consistente em validação

Forma segura de validar:

- cenário A: `GRAVIDEZ` categórica
- cenário B: `GESTACAO_MULTIPLA` binária

Se o desempenho ficar igual ou muito próximo, a preferência tende a ser pela variável binária, por simplicidade e clareza.

## 15. A imputação atual pode prejudicar os modelos? Vale a pena manter variáveis como `IDADEPAI`?

A imputação atual do projeto, como baseline, é tecnicamente defensável.

Hoje a estratégia é:

- preservar sinais importantes antes da imputação
- calcular a mediana apenas na base de treino
- aplicar a mediana do treino em treino e teste

Isso evita leakage e mantém o pipeline simples e robusto.

As colunas numéricas atualmente imputadas por mediana são:

- `IDADEMAE`
- `IDADEPAI`
- `QTDFILVIVO`
- `QTDFILMORT`
- `CONSPRENAT`
- `MESPRENAT`
- `QTDGESTANT`
- `QTDPARTNOR`
- `QTDPARTCES`
- `LATITUDE`
- `LONGITUDE`

Sobre substituir essa estratégia por imputação por KNN:

- não é automaticamente melhor
- pode aumentar complexidade sem ganho real
- pode suavizar ou distorcer sinais quando o missing não é aleatório
- em bases grandes e heterogêneas, tende a ser mais sensível a escala, codificação e dimensionalidade

Por isso, a recomendação é:

- manter a imputação por mediana como baseline principal
- testar `KNNImputer` apenas como experimento controlado
- só adotar outra estratégia se houver ganho consistente em validação

Sobre `IDADEPAI`, a manutenção é defensável, mas com ressalvas.

O principal valor dessa informação no projeto pode não estar apenas na idade do pai em si, mas no fato de que seu missing parece carregar informação social. Por isso, faz mais sentido interpretar a combinação:

- `PAI_AUSENTE`
- `IDADEPAI` imputada

Do ponto de vista prático:

- `PAI_AUSENTE` pode ser mais informativa que `IDADEPAI` bruta
- `IDADEPAI` vale ser mantida se agregar sinal incremental
- se não houver ganho consistente, pode ser removida em ablação futura

As variáveis que merecem maior cautela entre as imputadas são:

- `CONSPRENAT`
- `MESPRENAT`

Isso porque estão ligadas ao pré-natal e podem ter missing não aleatório, além de `CONSPRENAT` já ser suspeita no projeto por proximidade conceitual com a duração da gestação.

Resumo prático:

- a imputação por mediana não é, por si só, um problema
- `KNN` não deve ser adotado apenas por parecer mais sofisticado
- `IDADEPAI` pode ser mantida, mas deve ser avaliada junto com `PAI_AUSENTE`
- `CONSPRENAT` e, em menor grau, `MESPRENAT` merecem revisão mais crítica

## 16. A identificação de sentinelas por análise exploratória foi necessária?

Parcialmente, mas provavelmente houve esforço redundante.

Os códigos sentinela do SINASC já estão em grande parte documentados no dicionário de dados. Portanto, a estratégia principal de tratamento poderia ter sido guiada diretamente por essa documentação, em vez de depender primeiro de histogramas, box plots e inspeção manual de frequências para descobrir o que já estava definido.

Isso vale especialmente para variáveis como:

- `ESTCIVMAE`
- `ESCMAE` / `ESCMAE2010`
- `GESTACAO`
- `GRAVIDEZ`
- `PARTO`
- `CONSULTAS`
- `SEXO`
- `IDANOMAL`
- `TPMETESTIM`
- `STTRABPART`
- `STCESPARTO`
- `TPNASCASSI`

Assim, do ponto de vista metodológico, o fluxo mais objetivo seria:

- usar o dicionário de dados como fonte primária para mapear sentinelas
- usar análise exploratória apenas como validação complementar

A análise exploratória ainda pode ser útil para:

- confirmar se os códigos aparecem na base exatamente como descritos no dicionário
- identificar diferenças introduzidas pela extração ou transformação dos dados
- detectar sujeiras adicionais não previstas na documentação, como strings vazias, tipos inconsistentes ou códigos inesperados

Há também um ponto importante: o dado processado pode não chegar no mesmo formato literal do dicionário. Por isso, a inspeção empírica continua tendo valor secundário de validação, mas não deveria ser a principal fonte de decisão para códigos já documentados.

Recomendação prática:

- simplificar a narrativa do notebook, deixando claro que o tratamento de sentinelas foi orientado pelo dicionário de dados
- manter a checagem exploratória apenas como confirmação de aderência da base ao dicionário
- referenciar explicitamente o dicionário de dados nos comentários em markdown do notebook, para justificar as substituições realizadas

Resumo:

- houve valor na validação empírica
- mas a descoberta dos sentinelas não precisava depender dela
- o dicionário de dados deve aparecer como referência explícita da regra adotada

## 17. Existem outras colunas em `X` que merecem revisão de representação?

Sim.

Além de `ESCMAE2010`, há outras colunas no conjunto de features que podem ser revistas quanto à forma de representação, seja por natureza ordinal, redundância ou simplificação interpretativa.

As principais candidatas são:

- `ESCMAE2010`
- `GRAVIDEZ`
- `MESPRENAT`
- `FAIXAETAMAE`

### `ESCMAE2010`

`ESCMAE2010` tem natureza ordinal. Portanto, há uma boa justificativa para testar uma representação ordinal, em vez de tratá-la apenas como variável categórica nominal via dummies.

Também é recomendável separar a ausência de preenchimento da escala educacional em si, por exemplo com:

- uma variável ordinal para os níveis válidos
- uma flag específica para `IGNORADO`

### `GRAVIDEZ`

Em vez de usar a variável categórica expandida em dummies, pode ser mais simples e interpretável testar:

- `GESTACAO_MULTIPLA = 0` para gestação única
- `GESTACAO_MULTIPLA = 1` para gestação dupla ou tripla e mais

Essa abordagem tende a representar melhor o principal contraste clínico de risco.

### `MESPRENAT`

`MESPRENAT` tem natureza ordinal/temporal e pode fazer mais sentido como variável numérica ou ordinal, em vez de depender apenas de transformações derivadas.

Também vale revisar possível redundância com `PNTARDIO`, já que ambas podem estar carregando parte do mesmo sinal.

### `FAIXAETAMAE`

Como `IDADEMAE` já está presente como variável numérica, `FAIXAETAMAE` pode ser redundante.

Por isso, faz sentido comparar:

- apenas `IDADEMAE`
- apenas `FAIXAETAMAE`
- ambas

para verificar se a versão categorizada realmente agrega sinal.

### Colunas que parecem adequadas na forma atual

- `RACACORMAE`: natureza nominal, dummies fazem sentido
- `SEXO`: natureza binária/categórica, abordagem atual é adequada
- `PAI_AUSENTE`: feature derivada útil
- `IDADEPAI_INVALIDA`: flag útil de qualidade/inconsistência

No caso de `SEXO`, existe sim a categoria de não preenchimento/ignorado, e ela já está sendo preservada na modelagem como `SEXO_IGNORADO`.

### Colunas que merecem revisão mais conceitual

- `KOTELCHUCK`
- `LATITUDE`
- `LONGITUDE`

`KOTELCHUCK` já é uma candidata forte à remoção por risco de leakage conceitual. `LATITUDE` e `LONGITUDE` não têm exatamente problema de codificação, mas podem futuramente ser substituídas por representações espaciais mais interpretáveis.

Resumo prático:

- as revisões mais prioritárias são `ESCMAE2010`, `GRAVIDEZ`, `MESPRENAT` e `FAIXAETAMAE`
- `SEXO` já contempla categoria de ignorado via `SEXO_IGNORADO`
- algumas colunas merecem revisão por encoding e outras por significado conceitual

## 18. A escolaridade materna merece revisão de representação?

Sim.

`ESCMAE2010` merece revisão porque sua natureza é ordinal, e não apenas categórica nominal.

Há uma progressão natural entre os níveis de escolaridade, e tratar essa variável somente com dummies pode desperdiçar essa informação de ordenação.

Por isso, uma alternativa metodologicamente mais adequada é testar:

- uma variável ordinal para os níveis válidos de escolaridade
- uma flag separada para `IGNORADO`

Essa separação é importante porque `IGNORADO` não representa um nível real de escolaridade e não deveria ser colocado dentro da escala ordinal como se fosse uma categoria educacional válida.

Exemplo conceitual:

- `ESCMAE2010_ORDINAL`
- `ESCMAE2010_IGNORADO`

Vantagens dessa revisão:

- preserva a ordem natural da escolaridade
- melhora a interpretabilidade
- evita tratar ausência de preenchimento como nível educacional real
- pode capturar melhor gradientes de vulnerabilidade social

Recomendação prática:

- testar `ESCMAE2010` em formato ordinal
- manter `IGNORADO` como flag separada
- comparar essa abordagem com a codificação atual por dummies

Tratamentos possíveis para `ESCMAE2010`:

- manter como dummies, como está hoje
  - vantagem: simples e compatível com todos os modelos
  - desvantagem: perde a informação de ordem entre níveis

- converter para variável ordinal
  - vantagem: preserva a progressão natural da escolaridade
  - desvantagem: pode induzir relação aproximadamente monotônica que nem sempre será perfeita

- usar variável ordinal + flag de `IGNORADO`
  - vantagem: preserva ordem sem confundir ausência de preenchimento com nível educacional
  - desvantagem: exige um pouco mais de cuidado no pipeline

- agrupar níveis em faixas mais amplas
  - exemplo: `baixa`, `média`, `alta escolaridade`
  - vantagem: reduz sparsidade e simplifica interpretação
  - desvantagem: perde granularidade

- manter dummies, mas agrupar categorias raras
  - vantagem: reduz fragmentação mantendo abordagem categórica
  - desvantagem: continua sem explorar explicitamente a ordinalidade

- testar representação híbrida
  - exemplo: variável ordinal principal + uma ou duas flags derivadas, como `baixa_escolaridade`
  - vantagem: combina ordem com recortes de risco social
  - desvantagem: aumenta a complexidade e pode introduzir redundância

Sugestão de comparação prática:

- cenário A: dummies atuais
- cenário B: ordinal simples
- cenário C: ordinal + flag `IGNORADO`
- cenário D: faixas agregadas

Se o desempenho for semelhante, a tendência é preferir a representação mais simples e interpretável.

Resumo:

- a escolaridade materna merece revisão específica
- a principal hipótese é que a representação ordinal seja mais adequada do que a nominal pura
- a ausência de preenchimento deve ser tratada separadamente da escala de escolaridade

## Seção final. Organização das dúvidas em planejamento experimental

O conjunto de dúvidas levantadas pode ser reorganizado em poucos blocos de planejamento, com foco em criar condições objetivas para responder duas perguntas centrais:

- qual modelo apresenta melhor desempenho
- em quais condições de preprocessing, seleção de variáveis e representação esse melhor desempenho acontece

Em vez de tratar cada dúvida isoladamente, faz mais sentido transformá-las em frentes únicas de experimento.

### 1. Frente de integridade e validade dos dados

Objetivo:

- garantir que a base usada na modelagem esteja coerente com o dicionário de dados e com regras mínimas de plausibilidade

Principais dúvidas absorvidas:

- tratamento de sentinelas
- necessidade de referenciar o dicionário de dados
- identificação de valores biologicamente improváveis
- revisão de imputação e missing informativo

Decisões a consolidar:

- usar o dicionário de dados como fonte primária para sentinelas
- manter checagem exploratória como validação complementar
- definir regras explícitas para valores extremos suspeitos
- manter a imputação por mediana como baseline, com testes controlados de alternativas apenas se necessário

Entregável esperado:

- uma versão consolidada do preprocessing de integridade, com regras documentadas e reproduzíveis

### 2. Frente de revisão conceitual de features

Objetivo:

- revisar se as features mantidas são coerentes com um cenário preditivo realista e sem vazamento conceitual

Principais dúvidas absorvidas:

- risco de leakage em `KOTELCHUCK`
- risco conceitual em variáveis associadas à duração final da gestação
- valor real de `IDADEPAI`
- valor e limite de joins externos, especialmente `IBGE`

Decisões a consolidar:

- definir uma lista principal de features permitidas
- definir uma lista de features de risco para ablação
- separar baseline principal de análises de sensibilidade

Entregável esperado:

- uma matriz clara com:
  - features mantidas no baseline
  - features removidas por leakage
  - features candidatas a teste em ablação

### 3. Frente de representação e engenharia de variáveis

Objetivo:

- testar representações alternativas para variáveis que podem estar mal codificadas ou redundantes

Principais dúvidas absorvidas:

- `IDADEMAE` contínua vs categorizada
- `ESCMAE2010` nominal vs ordinal
- `GRAVIDEZ` categórica vs `GESTACAO_MULTIPLA`
- redundância entre `MESPRENAT` e `PNTARDIO`
- redundância entre `IDADEMAE` e `FAIXAETAMAE`

Decisões a consolidar:

- definir quais representações serão comparadas
- limitar o número de combinações a cenários interpretáveis e reproduzíveis

Entregável esperado:

- um conjunto pequeno de estratégias de preprocessing concorrentes, por exemplo:
  - cenário A: representação atual
  - cenário B: escolaridade ordinal + gestação múltipla binária
  - cenário C: revisão adicional de idade materna e início do pré-natal

### 4. Frente de arquitetura experimental

Objetivo:

- estruturar experimentos de forma que preprocessing e modelo sejam comparados juntos, sem confusão entre etapas

Principais dúvidas absorvidas:

- possibilidade de criar diversas combinações de pipelines
- necessidade de saber qual modelo vence em qual condição

Decisões a consolidar:

- representar os cenários como pipelines distintos
- combinar cada pipeline com múltiplos modelos
- evitar depender de vários datasets intermediários estáticos como base principal da comparação

Entregável esperado:

- grade experimental organizada como combinação entre:
  - estratégias de preprocessing
  - modelos candidatos
  - regra fixa de seleção

Exemplo conceitual:

- `pipeline A + LogisticRegression`
- `pipeline A + RandomForest`
- `pipeline A + HistGradientBoosting`
- `pipeline B + LogisticRegression`
- `pipeline B + RandomForest`
- `pipeline B + HistGradientBoosting`

### 5. Frente de critério de seleção do melhor modelo

Objetivo:

- garantir que a escolha final do melhor modelo seja coerente com o objetivo clínico do projeto

Principais dúvidas absorvidas:

- ordenação de modelos por `recall` vs `F2`
- uso do `MIN_RECALL_THRESHOLD`

Decisões a consolidar:

- tratar `recall >= MIN_RECALL_THRESHOLD` como critério de elegibilidade
- usar `F2` como principal métrica de ranking entre os modelos elegíveis
- usar `recall` como desempate ou métrica de apoio

Entregável esperado:

- uma regra final única de seleção, aplicada igualmente a todos os cenários

### 6. Sequência sugerida de execução

Para transformar as dúvidas em plano executável, a ordem mais lógica é:

1. consolidar regras de limpeza, sentinelas, extremos e imputação
2. congelar um baseline único e rastreável
3. definir um conjunto pequeno de cenários de representação de features
4. combinar esses cenários com os modelos candidatos
5. avaliar todos sob a mesma validação cruzada e a mesma política de seleção
6. escolher o melhor modelo dentro das condições testadas
7. fazer ablação final das features mais sensíveis, como `KOTELCHUCK`, `IDADEPAI` e representações alternativas

### 7. Pergunta final que o planejamento deve responder

Ao final, o planejamento precisa produzir uma resposta clara e defensável:

- qual modelo foi o melhor
- com qual conjunto de features
- com qual estratégia de preprocessing
- com qual representação das variáveis mais sensíveis
- sob qual regra de seleção baseada em `recall` mínimo e `F2`

Resumo final:

- as dúvidas não precisam virar dezenas de tarefas separadas
- elas podem ser agrupadas em poucas frentes experimentais
- o objetivo principal não é apenas melhorar o preprocessing, mas criar um desenho comparável que permita identificar, de forma reprodutível, qual modelo funciona melhor e em quais condições
