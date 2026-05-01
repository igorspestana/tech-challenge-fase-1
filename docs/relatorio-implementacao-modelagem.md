# Relatório de Implementação do Plano de Melhorias de Modelagem

## Contexto de execução
- Plano implementado: `docs/plano-melhorias-modelagem.md`
- Implementação principal nesta branch: `notebooks/03_modeling.ipynb`
- `src/pipeline.py` permanece como placeholder para futura orquestração por CLI/Docker.
- Observação: o dataset principal do SINASC não está versionado no repositório. A validação técnica completa depende da execução do notebook com os artefatos gerados por `02_preprocessing.ipynb`.

## Fase 1 — Diagnóstico técnico e baseline
- Entregas mantidas na trilha de notebooks:
  - split estratificado fixo por seed no `02_preprocessing.ipynb`
  - remoção explícita de colunas com leakage direto (`SEMAGESTAC`, `GESTACAO`, `PREMATURO`, `CONSPRENAT`) antes da modelagem
  - geração dos artefatos `X_train`, `X_test`, `y_train` e `y_test` consumidos pelo `03_modeling.ipynb`
- Observação:
  - auditoria detalhada de leakage e análise por subgrupos não ficam mais centralizadas em `src/pipeline.py`; a branch volta a priorizar execução e documentação em notebook.

## Fase 2 — Reforço de validação e decisão
- Entregas implementadas:
  - comparação consolidada em `model_comparison_cv_test.csv`
  - critério explícito de escolha com `recall >= 0.80` e `F2` como desempate
  - IC 95% via bootstrap no teste registrado em `best_model_operational_metrics.json`

## Fase 3 — Engenharia de atributos clínicos
- Entregas implementadas:
  - features de risco materno/obstétrico e encoding preparados no `02_preprocessing.ipynb`
  - consumo desses artefatos prontos no `03_modeling.ipynb`

## Fase 4 — Modelagem avançada desbalanceada
- Entregas implementadas:
  - candidatos: `LogisticRegression`, `RandomForest`, `HistGradientBoosting` e `HistGB_Balanced`
  - variante `HistGB_Balanced` treinada com `sample_weight=balanced` para comparar o impacto do balanceamento no `HistGradientBoostingClassifier`
  - tuning controlado com `RandomizedSearchCV`
  - ranking salvo em `model_comparison_cv_test.csv`

## Fase 5 — Calibração e threshold operacional
- Entregas implementadas:
  - calibração sigmoide (Platt)
  - escolha de threshold em validação dedicada (não no teste)
  - curva de busca em `threshold_search_curve.csv`
  - métricas default vs operacional em CSV e JSON

## Fase 6 — Produtização mínima e governança
- Entregas implementadas:
  - artefatos versionáveis gerados pelo notebook:
    - `experiment_config.json`
    - `best_model_operational_metrics.json`
    - `retraining_checklist.json`
    - `artifacts/best_model_calibrated.pkl`
  - política de aceite/re-treino formalizada sem mover a implementação para `src/pipeline.py`

## Mapeamento de commits
- Commit 1: implementação operacional consolidada em `notebooks/03_modeling.ipynb`
- Commit 2: atualização do relatório técnico e restauração de `src/pipeline.py` como placeholder

## Observações finais
- A execução principal da modelagem volta a acontecer pela sequência `02_preprocessing.ipynb` -> `03_modeling.ipynb`.
- `src/pipeline.py` continua reservado para uma futura etapa de produtização, quando fizer sentido transformar a lógica do notebook em fluxo de CLI/Docker.
