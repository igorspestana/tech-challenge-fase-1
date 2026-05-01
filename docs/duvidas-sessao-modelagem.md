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
