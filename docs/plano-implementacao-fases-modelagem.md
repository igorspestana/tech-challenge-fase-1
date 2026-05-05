# Plano de Implementação por Fases da Modelagem

## Objetivo do plano

Organizar a evolução da modelagem em fases executáveis, rastreáveis e reavaliáveis, usando [docs/duvidas-sessao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/duvidas-sessao-modelagem.md) como referência conceitual principal.

Este plano reflete o estado atual do projeto:

- a execução principal continua centrada em `notebooks/02_preprocessing.ipynb` e `notebooks/03_modeling.ipynb`
- `src/pipeline.py` segue como placeholder para uma fase final de produtização
- o relatório [docs/relatorio-implementacao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/relatorio-implementacao-modelagem.md) é usado como evidência inicial, mas não substitui este acompanhamento

## Contexto atual do projeto

Evidências já disponíveis no repositório nesta branch:

- `results/metrics/experiment_config.json` registra `random_state=42`, `cv_splits=3`, `min_recall_threshold=0.8`, modelos testados e dimensionalidade do experimento atual
- `results/metrics/model_comparison_cv_test.csv` consolida comparação entre `LogReg`, `RandomForest`, `HistGB` e `HistGB_Balanced`
- `results/metrics/threshold_search_curve.csv` registra a busca de threshold com coluna `meets_min_recall`
- `results/metrics/best_model_operational_metrics.json` registra a decisão operacional final, o threshold ajustado e IC 95% via bootstrap
- `results/metrics/retraining_checklist.json` formaliza critérios de aceite e reexecução
- `docs/relatorio-implementacao-modelagem.md` resume o que já foi consolidado na trilha de notebooks
- `src/pipeline.py` ainda contém `NotImplementedError`

Leitura prática do estado inicial:

- já existe uma baseline operacional de modelagem com artefatos de governança suficientes para rastrear configuração, seleção e métricas operacionais
- já existe comparação entre modelos
- ainda não existe um plano único de acompanhamento por fases com fechamento formal de cada etapa
- algumas decisões centrais das dúvidas ainda não foram convertidas em matriz operacional explícita de features, cenários e comparações de sensibilidade

## Convenção de status

- `Não iniciada`: fase ainda não começou ou não possui evidência suficiente
- `Em andamento`: há entregas parciais ou evidências incompletas
- `Concluída`: critérios de conclusão atendidos com evidências verificáveis
- `Bloqueada`: fase depende de decisão ou artefato ausente

## Tabela-resumo das fases

| Fase | Nome | Status inicial | Síntese do status |
| --- | --- | --- | --- |
| 1 | Consolidar baseline e regra de avaliação | `Concluída` | A baseline está bem evidenciada por configuração, comparação CV, decisão por fallback, threshold operacional e métricas com bootstrap. |
| 2 | Consolidar integridade de dados e preprocessing comum | `Em andamento` | O checklist operacional já está definido, mas ainda precisa ser convertido em execução rastreável fora da leitura documental do notebook. |
| 3 | Definir baseline de features e features de risco | `Em andamento` | A matriz de decisão por feature já foi fechada, mas ainda falta transformá-la em alterações executadas e verificadas no fluxo experimental. |
| 4 | Testar representações alternativas de variáveis | `Em andamento` | Os cenários já foram definidos, mas ainda não foram materializados como execuções comparativas reproduzíveis. |
| 5 | Comparar pipelines experimentais e modelos | `Em andamento` | A grade experimental está congelada, mas ainda falta executar as combinações previstas e consolidar o artefato comparativo final. |
| 6 | Comparação final de sensibilidade e decisão de modelo | `Em andamento` | O protocolo final está definido, mas ainda depende do vencedor real da fase comparativa e das comparações executadas com `KOTELCHUCK` e `IDADEPAI`. |
| 7 | Produtização mínima | `Em andamento` | O alvo mínimo de produtização foi fechado: o pipeline deve orquestrar artefatos já gerados pelos notebooks antes de absorver lógica interna de preprocessing e modelagem. |

## Fases detalhadas

### Fase 1 — Consolidar baseline e regra de avaliação

**Objetivo**

Fixar a baseline oficial do experimento atual e tornar explícita a regra de escolha do melhor modelo.

**Escopo**

- documentar a baseline derivada do fluxo atual de notebooks
- registrar dados, modelos comparados, métrica principal e política de seleção
- alinhar o ranking exibido com a regra efetiva de decisão

**Entradas**

- [docs/duvidas-sessao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/duvidas-sessao-modelagem.md)
- [docs/relatorio-implementacao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/relatorio-implementacao-modelagem.md)
- [results/metrics/experiment_config.json](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/results/metrics/experiment_config.json)
- [results/metrics/model_comparison_cv_test.csv](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/results/metrics/model_comparison_cv_test.csv)
- [results/metrics/threshold_search_curve.csv](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/results/metrics/threshold_search_curve.csv)
- [results/metrics/best_model_test_metrics_default_threshold.csv](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/results/metrics/best_model_test_metrics_default_threshold.csv)
- [results/metrics/best_model_test_metrics_tuned_threshold.csv](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/results/metrics/best_model_test_metrics_tuned_threshold.csv)
- [results/metrics/best_model_operational_metrics.json](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/results/metrics/best_model_operational_metrics.json)

**Atividades**

- registrar a baseline oficial com os modelos, métricas e artefatos disponíveis nesta branch
- formalizar a política principal: elegibilidade por `recall >= MIN_RECALL_THRESHOLD` e ranking por `cv_f2_mean`, com `cv_recall_mean` como desempate
- registrar explicitamente a regra prática observada quando nenhum modelo atingir o recall mínimo na comparação CV
- revisar se a ordenação exibida nos artefatos acompanha essa política

**Entregáveis esperados**

- baseline oficial documentada
- regra única de seleção documentada
- observação explícita sobre fallback

**Critérios de conclusão**

- baseline documentada com artefatos verificáveis
- regra principal e fallback descritos sem ambiguidade
- coerência entre ranking exibido, regra de seleção e conclusão final

**Evidências a verificar**

- `model_comparison_cv_test.csv` com ranking de `cv_f2_mean` e `cv_recall_mean`
- `threshold_search_curve.csv` com coluna `meets_min_recall`
- `experiment_config.json` com `min_recall_threshold=0.8`
- `best_model_operational_metrics.json` com `selection_rule=fallback: max CV F2 (nenhum modelo atingiu recall mínimo)`
- `best_model_operational_metrics.json` com `model=HistGB_Balanced`, `threshold=0.37999999999999995` e `recall=0.835174717368962`

**Análise pós-implementação**

Fase revalidada após o rebase em `origin/main`. A baseline está completamente rastreável: `experiment_config.json` fixa `random_state=42`, `cv_splits=3` e `min_recall_threshold=0.8`; `model_comparison_cv_test.csv` mostra que nenhum modelo atingiu o piso de recall na comparação CV e que `HistGB_Balanced` lidera em `cv_f2_mean`; `best_model_operational_metrics.json` documenta explicitamente a regra de fallback e o threshold final de `0.38`, com `recall=0.835174717368962` e IC 95% via bootstrap. A leitura prática correta desta branch deixou de ser a versão simplificada da etapa anterior: o candidato principal não é `RandomForest`, mas `HistGB_Balanced`, e os artefatos de governança já são suficientes para considerar a Fase 1 fechada com boa rastreabilidade.

**Status**

`Concluída`

### Fase 2 — Consolidar integridade de dados e preprocessing comum

**Objetivo**

Traduzir as decisões conceituais de integridade em regras operacionais verificáveis de preprocessing.

**Escopo**

- sentinelas guiados pelo dicionário
- revisão de missing e imputação baseline
- tratamento de extremos plausíveis
- manutenção da execução centrada em notebooks nesta fase

**Entradas**

- [docs/duvidas-sessao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/duvidas-sessao-modelagem.md)
- `notebooks/01_eda.ipynb`
- `notebooks/02_preprocessing.ipynb`

**Atividades**

- consolidar lista de regras de sentinelas orientadas pelo dicionário
- documentar imputação baseline por mediana e limites do experimento com KNN
- registrar tratamento de missing informativo e revisão de extremos suspeitos
- separar o que é regra comum de dado do que pode variar por modelo

**Checklist operacional consolidado**

- Converter para numérico, com `errors='coerce'`, as colunas usadas no mapeamento cirúrgico de sentinelas: `ESTCIVMAE`, `KOTELCHUCK`, `ESCMAE2010`, `GRAVIDEZ`, `SEXO`, `MESPRENAT` e `CONSPRENAT`.
- Aplicar mapeamento de sentinelas para `NaN` com as seguintes regras:
  - `ESTCIVMAE`: `9`
  - `KOTELCHUCK`: `9`
  - `ESCMAE2010`: `9`
  - `GRAVIDEZ`: `9`
  - `SEXO`: `0` e `9`
  - `MESPRENAT`: `99`
  - `CONSPRENAT`: `99`
- Converter strings vazias ou compostas apenas por espaços em `NaN` para capturar missing disfarçado, com destaque para casos como `RACACORMAE`.
- Tratar valores extremos plausíveis de contagem como dados válidos quando a distribuição e a semântica sustentarem o valor.
  - Exemplo documentado no notebook: `QTDGESTANT`, `QTDPARTNOR` e `QTDFILVIVO` mantêm valores altos raros, como `9`, por serem biologicamente possíveis e clinicamente informativos.
- Fazer feature engineering antes da imputação para preservar missing informativo e evitar distorção de regras de negócio.
  - `PAI_AUSENTE` deve ser derivada antes de imputar `IDADEPAI`.
  - `PNTARDIO` deve distinguir `MESPRENAT` ausente de início tardio real.
  - `PRIMIPARA` e `HISTPERDAFETAL` devem ser calculadas antes de preencher contagens com a mediana.
- Preencher nulos categóricos antes do split numérico final usando:
  - `IGNORADO` para colunas categóricas originadas por `pd.cut`, como `FAIXAETAMAE`
  - `-1` para demais categóricas codificadas, como `RACACORMAE`, `GRAVIDEZ`, `SEXO`, `ESTCIVMAE`, `KOTELCHUCK` e `ESCMAE2010`
- Remover colunas com leakage direto ou proxy já assumido no baseline antes da modelagem:
  - `SEMAGESTAC`
  - `GESTACAO`
  - `PREMATURO`
  - `CONSPRENAT`
- Fazer split estratificado com `train_test_split(..., test_size=0.2, random_state=42, stratify=y)`.
- Imputar colunas numéricas somente após o split, calculando a mediana apenas na base de treino e aplicando o mesmo valor em treino e teste.
  - Colunas numéricas explicitamente imputadas no notebook: `IDADEMAE`, `IDADEPAI`, `QTDFILVIVO`, `QTDFILMORT`, `CONSPRENAT`, `MESPRENAT`, `QTDGESTANT`, `QTDPARTNOR`, `QTDPARTCES`, `LATITUDE`, `LONGITUDE`
- Manter registrado que `KNNImputer` não faz parte da baseline operacional atual; qualquer uso futuro deve entrar apenas como experimento controlado.
- Distinguir o que é regra comum de dado do que é transformação sensível ao modelo.
  - Regras comuns nesta branch: limpeza, sentinelas, missing, features derivadas pré-imputação, split anti-leakage e imputação por mediana.
  - Transformações sensíveis ao modelo ainda não foram separadas em pipelines específicos; o encoding atual permanece generalista para comparação inicial.

**Entregáveis esperados**

- checklist de integridade e preprocessing comum
- narrativa alinhada entre documento de dúvidas e notebook de preprocessing

**Critérios de conclusão**

- regras operacionais descritas de forma verificável
- aderência entre documentação e fluxo real do notebook
- distinção explícita entre regras comuns e transformações sensíveis ao modelo

**Evidências a verificar**

- markdown e células do `02_preprocessing.ipynb`
- referência explícita a regras de sentinelas e imputação baseline
- bloco de mapeamento `sentinels_mapping`
- bloco de imputação com mediana calculada apenas em `X_train`
- bloco de remoção de `SEMAGESTAC`, `GESTACAO`, `PREMATURO` e `CONSPRENAT`

**Análise pós-implementação**

Fase em andamento. O `02_preprocessing.ipynb` já forneceu o conteúdo necessário para fechar o checklist operacional, mas isso ainda representa uma consolidação documental e não uma nova execução controlada desta fase fora do notebook. O ganho principal até aqui foi transformar decisões dispersas em uma especificação rastreável; o que permanece pendente é executar essa especificação como parte do fluxo reprodutível que será usado nas próximas fases.

**Status**

`Em andamento`

### Fase 3 — Definir baseline de features e features de risco

**Objetivo**

Estabelecer uma matriz única que separe features do baseline, features removidas por leakage e features reservadas para comparação de sensibilidade.

**Escopo**

- baseline principal de features
- remoções por leakage direto ou conceitual
- features de risco para teste controlado

**Entradas**

- [docs/duvidas-sessao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/duvidas-sessao-modelagem.md)
- [docs/relatorio-implementacao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/relatorio-implementacao-modelagem.md)
- `notebooks/02_preprocessing.ipynb`
- `results/metrics/experiment_config.json`

**Atividades**

- listar features mantidas no baseline principal
- listar features removidas por leakage, incluindo justificativa
- listar features candidatas a comparação de sensibilidade, com prioridade para `KOTELCHUCK` e `IDADEPAI`
- registrar o papel de `PAI_AUSENTE`, `MESPRENAT`, `PNTARDIO`, `LATITUDE` e `LONGITUDE`

**Matriz operacional de decisão por feature**

| Feature ou grupo | Decisão atual | Status na baseline | Justificativa operacional |
| --- | --- | --- | --- |
| `SEMAGESTAC` | remover | fora da baseline | leakage direto por carregar a idade gestacional usada na definição de prematuridade |
| `GESTACAO` | remover | fora da baseline | proxy direta da duração gestacional e já removida no notebook |
| `PREMATURO` | remover | fora da baseline | alvo da modelagem |
| `CONSPRENAT` | remover | fora da baseline | proxy influenciada pela duração final da gestação; já removida como leakage conceitual no baseline |
| `KOTELCHUCK_*` | manter apenas na baseline atual, com revisão obrigatória | dentro da baseline atual | o notebook atual mantém a variável e suas dummies, mas o documento de dúvidas a trata como candidata prioritária à remoção por alto risco de vazamento conceitual |
| `IDADEPAI` | manter com ressalva | dentro da baseline atual | pode agregar sinal incremental, mas só faz sentido junto com o missing informativo capturado em `PAI_AUSENTE` |
| `PAI_AUSENTE` | manter | dentro da baseline atual | feature derivada útil e potencialmente mais informativa do que `IDADEPAI` isolada |
| `IDADEPAI_INVALIDA` | manter | dentro da baseline atual | flag de qualidade e inconsistência considerada útil na forma atual |
| `MESPRENAT` | manter com revisão futura | dentro da baseline atual | variável temporal relevante, mas com possível redundância conceitual com `PNTARDIO` |
| `PNTARDIO` | manter com revisão futura | dentro da baseline atual | feature derivada útil para risco, porém precisa ser avaliada em conjunto com `MESPRENAT` |
| `LATITUDE` / `LONGITUDE` | manter com ressalva | dentro da baseline atual | não apresentam problema de leakage, mas são candidatas a substituição futura por representação espacial mais interpretável |
| `IDADEMAE` | manter | dentro da baseline atual | variável contínua principal para risco materno |
| `FAIXAETAMAE_*` | manter na baseline atual, revisar depois | dentro da baseline atual | hoje convive com `IDADEMAE`; a redundância será tratada na fase de cenários |
| `ESCMAE2010_*` | manter na baseline atual, revisar depois | dentro da baseline atual | atualmente codificada por dummies; a revisão ordinal fica para a fase de cenários |
| `GRAVIDEZ_*` | manter na baseline atual, revisar depois | dentro da baseline atual | atualmente em dummies; a hipótese de `GESTACAO_MULTIPLA` fica para a fase de cenários |

**Leitura prática da baseline atual**

- A baseline efetivamente usada na modelagem já exclui `SEMAGESTAC`, `GESTACAO`, `PREMATURO` e `CONSPRENAT`.
- A baseline ainda inclui `KOTELCHUCK`, `IDADEPAI`, `PAI_AUSENTE`, `IDADEPAI_INVALIDA`, `MESPRENAT`, `PNTARDIO`, `LATITUDE` e `LONGITUDE`.
- No `X_train` atual, as dummies de `KOTELCHUCK` permanecem ativas, incluindo `KOTELCHUCK_IGNORADO`, `KOTELCHUCK_INADEQUADO`, `KOTELCHUCK_INTERMEDIARIO`, `KOTELCHUCK_MAIS_QUE_ADEQUADO` e `KOTELCHUCK_SEM_PRENATAL`.
- Isso confirma que a matriz desta fase não descreve uma hipótese futura: ela documenta a baseline real que já está sendo usada e aponta quais partes dela exigem comparação de sensibilidade depois.

**Entregáveis esperados**

- matriz de decisão por feature
- distinção explícita entre baseline e sensibilidade

**Critérios de conclusão**

- toda feature sensível com decisão registrada
- baseline e ablações futuras definidos sem ambiguidade

**Evidências a verificar**

- documentação de remoção de `SEMAGESTAC`, `GESTACAO`, `PREMATURO` e `CONSPRENAT`
- tabela ou seção dedicada a `KOTELCHUCK`, `IDADEPAI` e correlatas
- verificação em `X_train.parquet` da presença de `KOTELCHUCK_*`, `IDADEPAI`, `PAI_AUSENTE`, `IDADEPAI_INVALIDA`, `MESPRENAT`, `PNTARDIO`, `LATITUDE` e `LONGITUDE`

**Análise pós-implementação**

Fase em andamento. A matriz de decisão por feature já foi consolidada com base no `02_preprocessing.ipynb`, no `X_train.parquet` e no documento de dúvidas, mas ela ainda precisa ser convertida em mudanças executadas e verificadas no fluxo experimental. O ponto mais sensível continua sendo `KOTELCHUCK`: a baseline atual o mantém, mas a próxima etapa precisa transformar essa leitura em teste real e não apenas em orientação metodológica.

**Status**

`Em andamento`

### Fase 4 — Testar representações alternativas de variáveis

**Objetivo**

Fechar um conjunto pequeno e reproduzível de cenários de representação para as variáveis mais sensíveis.

**Escopo**

- `ESCMAE2010` nominal vs ordinal
- `GRAVIDEZ` categórica vs `GESTACAO_MULTIPLA`
- `IDADEMAE` vs `FAIXAETAMAE`
- revisão de `MESPRENAT` quando aplicável

**Entradas**

- [docs/duvidas-sessao-modelagem.md](/home/emidiosouza/FiapCode/fase1/tech-challenge-fase-1/docs/duvidas-sessao-modelagem.md)
- baseline definida nas fases 1 a 3

**Atividades**

- definir de 3 a 4 cenários totais
- garantir que os cenários sejam comparáveis e não redundantes
- documentar a justificativa metodológica de cada cenário

**Catálogo fixo de cenários**

**Cenário A — Baseline atual**

- Manter a representação já materializada no `X_train` atual.
- Permanecer com:
  - `IDADEMAE` contínua + dummies de `FAIXAETAMAE`
  - `ESCMAE2010` em dummies
  - `GRAVIDEZ` em dummies
  - `MESPRENAT` numérica + `PNTARDIO`
- Objetivo: servir como referência única de comparação para todos os demais cenários.

**Cenário B — Escolaridade ordinal e gestação múltipla binária**

- Substituir `ESCMAE2010_*` por:
  - `ESCMAE2010_ORDINAL`
  - `ESCMAE2010_IGNORADO`
- Substituir `GRAVIDEZ_*` por:
  - `GESTACAO_MULTIPLA`
  - manter sinal separado de ignorado, se necessário, como `GRAVIDEZ_IGNORADO` ou flag equivalente
- Manter sem mudança:
  - `IDADEMAE` + `FAIXAETAMAE`
  - `MESPRENAT` + `PNTARDIO`
- Objetivo: testar a hipótese de que escolaridade ordinal e gestação múltipla binária são representações mais estáveis e interpretáveis.

**Cenário C — Simplificação de idade materna**

- Partir do Cenário B.
- Remover as dummies de `FAIXAETAMAE`.
- Manter apenas `IDADEMAE` contínua como representação principal da idade materna.
- Manter sem mudança:
  - `ESCMAE2010_ORDINAL` + `ESCMAE2010_IGNORADO`
  - `GESTACAO_MULTIPLA`
  - `MESPRENAT` + `PNTARDIO`
- Objetivo: testar se a discretização da idade é redundante quando a variável contínua já está presente.

**Cenário D — Simplificação de início do pré-natal**

- Partir do Cenário C.
- Remover `PNTARDIO`.
- Manter apenas `MESPRENAT` como variável temporal principal de início do pré-natal.
- Manter sem mudança:
  - `IDADEMAE`
  - `ESCMAE2010_ORDINAL` + `ESCMAE2010_IGNORADO`
  - `GESTACAO_MULTIPLA`
- Objetivo: testar se `PNTARDIO` está apenas reproduzindo sinal já contido em `MESPRENAT`.

**Regras de construção dos cenários**

- Não criar mais de 4 cenários nesta fase.
- Alterar apenas as variáveis sob hipótese em cada cenário.
- Manter inalteradas todas as demais features da baseline, inclusive `KOTELCHUCK`, `IDADEPAI`, `PAI_AUSENTE`, `IDADEPAI_INVALIDA`, `LATITUDE` e `LONGITUDE`.
- Não misturar nesta fase a comparação de sensibilidade de `KOTELCHUCK` ou `IDADEPAI`; isso fica reservado para a Fase 6.
- Aplicar os mesmos modelos e a mesma política de seleção a todos os cenários.

**Entregáveis esperados**

- catálogo fixo de cenários experimentais
- definição clara do cenário atual e dos alternativos

**Critérios de conclusão**

- cenários fechados, limitados e rastreáveis
- justificativa explícita para cada representação escolhida

**Evidências a verificar**

- seção com cenários A, B, C e opcionalmente D
- regras de comparação sem explosão combinatória
- aderência entre cada cenário e as hipóteses levantadas em `docs/duvidas-sessao-modelagem.md`

**Análise pós-implementação**

Fase em andamento. Os quatro cenários já estão definidos e controlados, o que elimina ambiguidade de desenho, mas eles ainda não foram implementados como execuções reproduzíveis. O próximo avanço real desta fase não é mais discutir combinações, e sim materializar esses cenários no fluxo experimental.

**Status**

`Em andamento`

### Fase 5 — Comparar pipelines experimentais e modelos

**Objetivo**

Comparar os modelos principais do projeto nos cenários definidos, sob a mesma política de validação e seleção.

**Escopo**

- `LogisticRegression`
- `RandomForest`
- `HistGradientBoosting`
- eventual diferenciação de preprocessing por família de modelo

**Entradas**

- `results/metrics/model_comparison_cv_test.csv`
- cenários definidos na fase 4
- regras consolidadas nas fases 1 a 3

**Atividades**

- reaproveitar a baseline comparativa atual
- expandir a comparação para os cenários definidos
- manter critério de avaliação único
- registrar o melhor conjunto `cenário + modelo`

**Grade experimental fechada**

As combinações obrigatórias desta fase são:

| Cenário | Modelo | Observação |
| --- | --- | --- |
| A | `LogisticRegression` | controle linear sobre a baseline atual |
| A | `RandomForest` | controle ensemble sobre a baseline atual |
| A | `HistGradientBoosting` | controle boosting sobre a baseline atual |
| B | `LogisticRegression` | mede impacto de escolaridade ordinal e gestação múltipla binária em modelo linear |
| B | `RandomForest` | mede o mesmo cenário em ensemble de árvores |
| B | `HistGradientBoosting` | mede o mesmo cenário em boosting |
| C | `LogisticRegression` | testa simplificação de idade materna em modelo linear |
| C | `RandomForest` | testa simplificação de idade materna em ensemble |
| C | `HistGradientBoosting` | testa simplificação de idade materna em boosting |
| D | `LogisticRegression` | testa simplificação do sinal de início do pré-natal em modelo linear |
| D | `RandomForest` | testa simplificação do sinal de início do pré-natal em ensemble |
| D | `HistGradientBoosting` | testa simplificação do sinal de início do pré-natal em boosting |

**Regra de execução da grade**

- Executar os 12 testes com a mesma base de treino e teste já definida na Fase 1.
- Manter `random_state=42`, `cv_splits=3` e `min_recall_threshold=0.8` conforme `experiment_config.json`.
- Aplicar a mesma lógica de tuning controlado usada na baseline atual para os três modelos principais.
- Não incluir `HistGB_Balanced` como linha obrigatória da grade principal.
  - Motivo: nesta fase o objetivo é isolar o impacto das representações de variáveis nos três modelos principais acordados com o grupo.
  - Se necessário, `HistGB_Balanced` pode ser executado depois como extensão dirigida, não como parte da grade mínima obrigatória.
- Avaliar todos os resultados com os mesmos indicadores de CV e teste já utilizados na baseline:
  - `cv_recall_mean`
  - `cv_f2_mean`
  - `cv_f1_mean`
  - `cv_precision_mean`
  - `cv_roc_auc_mean`
  - `cv_average_precision_mean`
  - métricas de teste com threshold padrão
- Manter o ajuste de threshold e a avaliação operacional fora desta fase.
  - Nesta etapa, o objetivo é escolher o melhor conjunto `cenário + modelo` no regime comparável de baseline.
  - O ajuste de threshold operacional continua sendo aplicado depois, sobre o vencedor da grade.

**Artefato-alvo da fase**

- Consolidar uma tabela única com, no mínimo, estas colunas:
  - `scenario`
  - `model`
  - `selection_metric`
  - `min_recall_threshold`
  - `cv_recall_mean`
  - `cv_recall_std`
  - `cv_f2_mean`
  - `cv_f2_std`
  - `cv_f1_mean`
  - `cv_precision_mean`
  - `cv_roc_auc_mean`
  - `cv_average_precision_mean`
  - `test_recall_default`
  - `test_f2_default`
  - `test_f1_default`
  - `test_precision_default`
  - `test_accuracy_default`
  - `best_params`

**Regra de escolha dentro da fase**

- Primeiro verificar elegibilidade por `cv_recall_mean >= MIN_RECALL_THRESHOLD`.
- Se houver elegíveis, ordenar por:
  - `cv_f2_mean`
  - `cv_recall_mean`
- Se não houver elegíveis, aplicar o mesmo fallback já usado na baseline:
  - escolher o maior `cv_f2_mean`
- O vencedor desta fase deve ser registrado como:
  - melhor `cenário + modelo` antes da comparação final de sensibilidade

**Entregáveis esperados**

- tabela comparativa única entre cenários e modelos
- seleção rastreável do melhor conjunto experimental

**Critérios de conclusão**

- comparação consolidada entre todos os cenários previstos
- decisão final reproduzível sobre o melhor conjunto

**Evidências a verificar**

- comparação atual em `model_comparison_cv_test.csv`
- artefato futuro consolidando cenário, modelo, métrica e decisão
- lista fechada de 12 combinações obrigatórias
- regra explícita de exclusão de `HistGB_Balanced` da grade mínima principal
- regra única de seleção consistente com a Fase 1

**Análise pós-implementação**

Fase em andamento. A grade experimental está completamente fechada no papel, mas ainda falta executá-la e consolidar o artefato comparativo resultante. O plano já impede deriva metodológica, mas a fase só poderá ser considerada concluída depois que as 12 combinações forem rodadas e comparadas sob a mesma regra.

**Status**

`Em andamento`

### Fase 6 — Comparação final de sensibilidade e decisão de modelo

**Objetivo**

Executar as comparações mais sensíveis e consolidar a resposta final do experimento.

**Escopo**

- comparação com e sem `KOTELCHUCK`
- comparação com e sem `IDADEPAI`
- revisão de features cuja utilidade dependa do cenário final

**Entradas**

- resultados da fase 5
- matriz de features da fase 3
- hipóteses do documento de dúvidas

**Atividades**

- comparar desempenho com e sem features críticas
- verificar indícios de leakage conceitual ou redundância
- fechar o pacote final: melhor modelo, melhor cenário, features finais e regra de seleção

**Ordem obrigatória de execução**

1. Selecionar o vencedor da Fase 5 como ponto de partida.
2. Rodar a comparação de sensibilidade de `KOTELCHUCK` sobre esse vencedor.
3. Escolher a versão com ou sem `KOTELCHUCK` usando a regra desta fase.
4. Sobre a versão vencedora do passo anterior, rodar a comparação de sensibilidade de `IDADEPAI`.
5. Escolher a versão com ou sem `IDADEPAI` usando a mesma regra.
6. Consolidar o melhor conjunto final:
   - cenário
   - modelo
   - lista final de features
   - threshold operacional
   - regra final de seleção

**Comparações obrigatórias**

**Bloco 1 — `KOTELCHUCK`**

- Cenário 1A: melhor `cenário + modelo` da Fase 5, mantendo `KOTELCHUCK`
- Cenário 1B: melhor `cenário + modelo` da Fase 5, removendo todas as colunas derivadas de `KOTELCHUCK`
  - `KOTELCHUCK_IGNORADO`
  - `KOTELCHUCK_INADEQUADO`
  - `KOTELCHUCK_INTERMEDIARIO`
  - `KOTELCHUCK_MAIS_QUE_ADEQUADO`
  - `KOTELCHUCK_SEM_PRENATAL`

**Bloco 2 — `IDADEPAI`**

- Cenário 2A: versão vencedora do Bloco 1, mantendo `IDADEPAI`
- Cenário 2B: versão vencedora do Bloco 1, removendo apenas `IDADEPAI`
- `PAI_AUSENTE` e `IDADEPAI_INVALIDA` devem permanecer nos dois lados da comparação.
  - Motivo: a hipótese do projeto não é remover o sinal de ausência paterna, mas testar o ganho incremental da idade imputada do pai.

**Regra de decisão dentro da fase**

- Aplicar exatamente a mesma política de seleção da Fase 1:
  - primeiro verificar se `cv_recall_mean >= MIN_RECALL_THRESHOLD`
  - entre os elegíveis, escolher maior `cv_f2_mean`
  - usar `cv_recall_mean` como desempate
- Se nenhuma das duas variantes atingir o piso de recall na CV, usar o mesmo fallback:
  - escolher a maior `cv_f2_mean`
- Além da regra principal, registrar obrigatoriamente a diferença absoluta em:
  - `cv_recall_mean`
  - `cv_f2_mean`
  - `test_recall_default`
  - `test_f2_default`
  - `test_average_precision`

**Critério interpretativo da comparação**

- Para `KOTELCHUCK`:
  - se a remoção causar queda pequena ou irrelevante em `F2` e `recall`, preferir remover
  - se a remoção causar queda forte, registrar explicitamente que a variável carregava sinal muito dominante e tratar isso como evidência de risco de vazamento conceitual, não como justificativa automática para mantê-la
- Para `IDADEPAI`:
  - se a remoção não causar perda consistente, preferir remover `IDADEPAI`
  - se houver ganho consistente ao manter `IDADEPAI`, manter apenas em conjunto com `PAI_AUSENTE`

**Pacote final de decisão**

Ao fim da fase, a resposta final do experimento deve ser documentada neste formato:

- melhor cenário de representação: `A`, `B`, `C` ou `D`
- melhor modelo: `LogisticRegression`, `RandomForest` ou `HistGradientBoosting`
- status de `KOTELCHUCK`: mantido ou removido
- status de `IDADEPAI`: mantida ou removida
- status de `PAI_AUSENTE`: mantido
- regra de seleção aplicada:
  - `recall >= MIN_RECALL_THRESHOLD` como elegibilidade
  - `cv_f2_mean` como critério principal
  - fallback por maior `cv_f2_mean`, se nenhum elegível
- threshold operacional final
- métricas finais operacionais:
  - `recall`
  - `f2`
  - `precision`
  - `average_precision`
  - `brier`

**Entregáveis esperados**

- relatório curto de comparação de sensibilidade
- decisão final defendida por evidências

**Critérios de conclusão**

- comparações de sensibilidade executadas e analisadas
- resposta final do experimento documentada

**Evidências a verificar**

- métricas comparativas por comparação de sensibilidade
- decisão final com justificativa explícita
- comparação com e sem `KOTELCHUCK` registrada separadamente
- comparação com e sem `IDADEPAI` registrada separadamente
- justificativa explícita caso `KOTELCHUCK` permaneça no conjunto final
- artefato final apontando cenário, modelo e conjunto de features vencedores

**Análise pós-implementação**

Fase em andamento. O protocolo decisório agora está fechado, o que reduz incerteza, mas ainda não houve a execução das comparações de sensibilidade que encerrariam de fato a escolha final. Em termos práticos, esta fase continua dependente do vencedor real da Fase 5 e da comparação efetiva com e sem `KOTELCHUCK` e `IDADEPAI`.

**Status**

`Em andamento`

### Fase 7 — Produtização mínima

**Objetivo**

Migrar a lógica crítica estabilizada para um pipeline reproduzível por CLI ou Docker.

**Escopo**

- implementar `src/pipeline.py`
- padronizar geração de artefatos
- manter rastreabilidade de configuração e métricas

**Entradas**

- `src/pipeline.py`
- artefatos e decisões consolidadas das fases anteriores

**Atividades**

- portar a lógica principal dos notebooks para pipeline reproduzível
- gerar artefatos versionáveis de configuração, métricas e modelo
- alinhar documentação técnica com o novo fluxo

**Escopo mínimo executável desta fase**

Nesta branch, a produtização mínima não deve começar tentando reimplementar toda a lógica de `02_preprocessing.ipynb` e `03_modeling.ipynb` dentro de `src/pipeline.py`. O alvo inicial mais seguro é um pipeline fino de orquestração, que valide entradas, chame etapas já estabilizadas e consolide artefatos.

**Passo 1 — Pipeline de leitura e validação**

- Implementar em `src/pipeline.py` uma CLI mínima capaz de:
  - verificar existência de `data/X_train.parquet`, `data/X_test.parquet`, `data/y_train.parquet` e `data/y_test.parquet`
  - verificar existência do diretório `results/metrics`
  - falhar com mensagem clara quando os artefatos-base não existirem
- Objetivo: substituir o `NotImplementedError` por uma checagem reproduzível do estado mínimo necessário para a modelagem.

**Passo 2 — Pipeline de consolidação de artefatos**

- Fazer o script expor, no mínimo, um fluxo que:
  - leia `results/metrics/experiment_config.json`
  - leia `results/metrics/model_comparison_cv_test.csv`
  - leia `results/metrics/best_model_operational_metrics.json`
  - imprima ou grave um resumo curto da execução atual
- Objetivo: transformar a baseline atual em um ponto de entrada executável por CLI, mesmo antes da migração integral da lógica dos notebooks.

**Passo 3 — Gancho explícito para futura migração**

- Estruturar `src/pipeline.py` com funções separadas, por exemplo:
  - `validate_inputs()`
  - `load_existing_artifacts()`
  - `summarize_current_baseline()`
  - `main()`
- Objetivo: deixar preparado um esqueleto limpo para, no futuro, absorver partes de preprocessing, treino, avaliação e exportação sem recomeçar do zero.

**Passo 4 — Critério de não escopo nesta branch**

- Não migrar nesta fase:
  - engenharia completa de features do `02_preprocessing.ipynb`
  - treino completo dos modelos do `03_modeling.ipynb`
  - busca de threshold
  - bootstrap
- Motivo: a prioridade desta branch continua sendo fechar o desenho experimental e a rastreabilidade decisória, não duplicar prematuramente a implementação do notebook.

**Entregáveis esperados**

- `src/pipeline.py` deixando de ser placeholder
- CLI mínima funcional para validação e leitura dos artefatos atuais
- documentação técnica alinhada com esse escopo reduzido

**Critérios de conclusão**

- `src/pipeline.py` deixa de lançar `NotImplementedError`
- o script executa por CLI e valida corretamente a presença dos artefatos esperados
- o script consegue consolidar a baseline atual a partir dos artefatos já gerados
- a documentação deixa explícito que a execução principal ainda depende dos notebooks para geração dos dados e métricas

**Evidências a verificar**

- implementação real em `src/pipeline.py`
- mensagem de execução bem-sucedida por CLI
- documentação de execução atualizada
- ausência de `NotImplementedError` no arquivo

**Análise pós-implementação**

Fase reclassificada para `Em andamento`. A implementação ainda não começou, mas o escopo mínimo agora está fechado de forma compatível com a realidade desta branch. Em vez de prometer uma migração completa e precoce dos notebooks, o plano passa a exigir primeiro uma CLI fina de validação e consolidação dos artefatos já existentes. Isso reduz risco, evita duplicação prematura e cria uma ponte mais honesta entre a execução centrada em notebook e a futura produtização.

**Status**

`Em andamento`

## Regra de atualização após cada fase

Sempre que uma fase for implementada, executar esta rotina:

1. comparar o que foi entregue com os critérios de conclusão da fase
2. listar evidências verificáveis
3. escrever uma análise curta do que mudou, do que ficou pendente e dos riscos remanescentes
4. atualizar o status da fase
5. ajustar dependências e observações das fases seguintes, se necessário

A análise pós-implementação de cada fase deve responder, no mínimo:

- o objetivo da fase foi atendido integralmente ou parcialmente
- quais artefatos, notebooks ou métricas comprovam isso
- que decisão ficou travada para a próxima fase
- se o status correto é `Concluída`, `Em andamento` ou `Bloqueada`

## Histórico de conclusões

### Execução inicial registrada em 2026-05-02

- Fase 1 marcada como `Concluída` nesta branch porque a baseline foi revalidada após o rebase com configuração explícita, comparação CV, regra de fallback, threshold operacional e métricas com bootstrap.
- Fase 2 marcada como `Em andamento` porque as regras reais do `02_preprocessing.ipynb` já foram convertidas em checklist operacional, mas ainda precisam ser executadas dentro de um fluxo reprodutível de trabalho.
- Fase 3 marcada como `Em andamento` porque a baseline atual e as features sensíveis já foram consolidadas em matriz explícita, mas ainda não foram convertidas em mudanças experimentais executadas.
- Fase 4 marcada como `Em andamento` porque os cenários alternativos já foram congelados em 4 opções reproduzíveis, mas ainda faltam as execuções correspondentes.
- Fase 5 marcada como `Em andamento` porque a grade experimental já foi fechada, mas ainda falta rodar e consolidar as combinações previstas.
- Fase 6 marcada como `Em andamento` porque o protocolo final de comparação de sensibilidade já foi definido, mas ainda depende da execução dos testes finais com `KOTELCHUCK` e `IDADEPAI`.
- Fase 7 marcada como `Em andamento` porque o escopo mínimo de produtização já foi fechado, embora `src/pipeline.py` ainda precise sair do placeholder.

### Revalidação após rebase em `origin/main`

- A revalidação substituiu a leitura temporária que apontava `RandomForest` como candidato principal.
- A baseline válida desta branch passa a ser a consolidada em `best_model_operational_metrics.json`, com `HistGB_Balanced` escolhido por fallback de `max CV F2`.
- Os artefatos `experiment_config.json`, `best_model_operational_metrics.json`, `retraining_checklist.json` e `docs/relatorio-implementacao-modelagem.md` voltam a fazer parte explícita das evidências do plano.

## Validação do próprio plano

- Todas as fases possuem critérios de conclusão observáveis.
- O plano reflete o estado atual do repositório, com notebooks como centro da execução.
- O plano não depende de nova fonte externa para começar.
- A política de seleção está consistente com os artefatos completos desta branch: piso clínico de recall, fallback por `max CV F2` e threshold operacional escolhido fora do teste padrão.
