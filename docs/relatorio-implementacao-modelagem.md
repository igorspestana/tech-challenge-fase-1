# Relatório de Implementação do Plano de Melhorias de Modelagem

## Contexto de execução
- Plano implementado: `docs/plano-melhorias-modelagem.md`
- Implementação principal: `src/pipeline.py`
- Observação: o dataset principal do SINASC não está versionado no repositório. A validação técnica de execução foi feita com dataset sintético (`/tmp/sinasc_sintetico.csv`) para testar fluxo completo e critérios por fase.

## Fase 1 — Diagnóstico técnico e baseline
- Entregas implementadas:
  - baseline reprodutível com split estratificado fixo por seed
  - auditoria de leakage (`phase1_leakage_audit.csv`)
  - avaliação por subgrupos (`phase1_subgroup_performance.csv`)
  - resumo do baseline (`phase1_baseline_summary.json`)
- Resultado obtido (execução validada):
  - 2500 linhas, 28 features elegíveis
  - prevalência do alvo: 30.56%
  - split: 2000 treino / 500 teste

## Fase 2 — Reforço de validação e decisão
- Entregas implementadas:
  - seleção de modelo com CV aninhada (outer/inner)
  - critério explícito: `max F2` sujeito a `recall >= 0.80`
  - comparação consolidada em `model_comparison_cv_test.csv`
  - IC 95% via bootstrap no teste
- Resultado obtido (CV):
  - melhor candidato por regra de negócio: `rf_balanced`
  - CV (OOF): recall 0.9493, precisão 0.3446, F2 0.7027

## Fase 3 — Engenharia de atributos clínicos
- Entregas implementadas:
  - features de risco materno/obstétrico (`IDADEMAE_RISCO`, `PN_EXTREMO`, `OBS_HISTORICO_AGG`, `PRIMIPARA`, `HISTPERDAFETAL`, etc.)
  - faixa etária materna (`FAIXAETAMAE`)
  - tratamento de raridade categórica via `RareCategoryGrouper`
  - pipeline consistente em `ColumnTransformer`
- Resultado obtido:
  - engenharia integrada ao fluxo de treino/validação/teste sem inconsistência entre conjuntos

## Fase 4 — Modelagem avançada desbalanceada
- Entregas implementadas:
  - candidatos: `LogisticRegression (balanced)`, `RandomForest (balanced_subsample)`, `HistGradientBoosting`
  - tuning controlado por grid em CV interna
  - ranking com estabilidade por métrica-alvo
- Resultado obtido (CV):
  - `rf_balanced`: F2=0.7027 (melhor)
  - `logreg_balanced`: F2=0.6976
  - `hgb`: F2=0.6919

## Fase 5 — Calibração e threshold operacional
- Entregas implementadas:
  - calibração sigmoide (Platt)
  - escolha de threshold em validação dedicada (não no teste)
  - curva de busca em `threshold_search_curve.csv`
  - métricas default vs operacional
- Correção aplicada durante implementação:
  - inicialmente o threshold era selecionado no mesmo conjunto de ajuste do calibrador; corrigido para usar split de validação separado.
- Resultado obtido (teste):
  - threshold operacional: 0.1923
  - recall: 0.9673 (atinge critério >=0.80)
  - precisão: 0.3474
  - F2: 0.7129
  - baseline default (0.5): recall 0.0, F2 0.0

## Fase 6 — Produtização mínima e governança
- Entregas implementadas:
  - CLI (`--data-path`, `--data-glob`, `--seed`, `--min-recall`)
  - artefatos versionáveis:
    - `experiment_config.json`
    - `best_model_operational_metrics.json`
    - `retraining_checklist.json`
    - `artifacts/best_model_calibrated.pkl`
  - política de aceite/re-treino formalizada

## Mapeamento de commits
- Commit 1: implementação completa do pipeline incremental em fases 1-6 em `src/pipeline.py`
- Commit 2: relatório final de implementação com resultados por fase em `docs/relatorio-implementacao-modelagem.md`

## Observações finais
- A implementação está pronta para execução com dado real SINASC assim que o arquivo parquet/csv for disponibilizado localmente (`--data-path`).
- Os resultados quantitativos acima refletem a validação técnica com dados sintéticos para garantir o comportamento do pipeline e o cumprimento das regras de decisão.
