# Plano de Melhoria Incremental — Predição de Prematuridade (SINASC)

## Resumo
O resultado atual indica limite de separação entre classes (`ROC-AUC ~0.66`, `AP ~0.27`), com ganho de recall via threshold mas forte queda de precisão.
Objetivo travado para as próximas iterações: **manter recall clínico alto (>= 0.80)** usando **apenas os dados atuais**, enquanto aumentamos precisão/F2 e robustez de validação.

## Mudanças-chave (por etapas)

### 1. Etapa 1 — Diagnóstico técnico e baseline reprodutível
- Congelar baseline único com split/cv fixos, mesma lista de features e versão de dados para comparação justa.
- Auditar vazamento e variáveis proxy do alvo (ex.: campos potencialmente pós-desfecho ou fortemente derivados do parto).
- Medir performance por subgrupos (faixa etária, escolaridade, tipo de gestação, município) para identificar onde o modelo falha.
- Entregáveis: tabela única de baseline + relatório curto de riscos de leakage e qualidade de features.

### 2. Etapa 2 — Reforço de validação e estratégia de decisão
- Trocar seleção de modelo para **nested CV** (ou CV interna de tuning + holdout final realmente cego).
- Definir seleção por função-objetivo alinhada ao negócio: `max F2` sujeito a `recall >= 0.80`.
- Incluir intervalos de confiança (bootstrap) para métricas principais no teste.
- Entregáveis: `model_comparison` com incerteza e critério explícito de escolha do melhor modelo.

### 3. Etapa 3 — Engenharia de atributos orientada a risco clínico
- Reestruturar encoding/imputação em `Pipeline/ColumnTransformer` para evitar inconsistência entre treino/teste.
- Criar features clínicas de maior sinal (interações e bins): idade materna por faixas de risco, extremos de pré-natal, histórico obstétrico agregado, e combinações relevantes entre variáveis maternas/gestacionais.
- Tratar raridade de categorias (grouping de categorias raras) para reduzir ruído.
- Entregáveis: ablação de features (baseline vs +blocos de engenharia) com impacto em recall/F2/AP.

### 4. Etapa 4 — Modelagem avançada para tabular desbalanceado
- Expandir candidatos além dos atuais: `XGBoost/LightGBM/CatBoost` (ou equivalente disponível), mantendo RF/LogReg como controle.
- Otimizar hiperparâmetros com busca bayesiana/aleatória mais ampla e orçamento controlado.
- Comparar estratégias de desbalanceamento: `class_weight`, under/over-sampling (somente dentro do fold), e ajuste de loss.
- Entregáveis: ranking de modelos por métrica-alvo com custo computacional e estabilidade.

### 5. Etapa 5 — Calibração e política de threshold operacional
- Calibrar probabilidades (`Platt` ou isotônica) e validar com Brier/reliability curve.
- Selecionar threshold em validação (não no teste) com regra operacional fixa: `recall >= 0.80` e melhor precisão/F2 possível.
- Produzir matriz de confusão final e curva Precision-Recall na configuração operacional.
- Entregáveis: pacote final de métricas operacionais e threshold recomendado para uso.

### 6. Etapa 6 — Produtização mínima e governança
- Migrar lógica crítica dos notebooks para `src/pipeline.py` (carga, preprocess, treino, avaliação, artefatos).
- Versionar artefatos de experimento (config + métricas + modelo + threshold) para rastreabilidade.
- Definir checklist de re-treino e critérios de aceite para futuras iterações.
- Entregáveis: pipeline reproduzível por CLI/Docker e documentação técnica atualizada.

## Mudanças em interfaces/artefatos públicos
- Padronizar `results/metrics/model_comparison_cv_test.csv` para incluir: métrica de seleção, intervalo de confiança, estratégia de desbalanceamento, calibração e threshold final.
- Adicionar artefato de configuração do experimento (ex.: `results/metrics/experiment_config.json`) com seeds, features, filtros e busca de hiperparâmetros.
- Consolidar saída final operacional em CSV único (ex.: `best_model_operational_metrics.csv`) com regra de decisão utilizada.

## Testes e cenários de validação
- Reprodutibilidade: mesma configuração deve reproduzir métricas dentro de tolerância pequena.
- Anti-leakage: remover features suspeitas não pode causar “colapso inesperado” de generalização no holdout.
- Critério de negócio: modelo só é aceito se `recall >= 0.80` no teste cego e ganho de precisão/F2 sobre baseline.
- Robustez: métricas consistentes entre folds e sem degradação extrema em subgrupos críticos.
- Calibração: probabilidades calibradas devem reduzir erro de probabilidade (Brier) sem perda material de recall.

## Assumptions e defaults
- Prioridade de negócio: **recall mínimo de 0.80**.
- Escopo de dados na fase atual: **somente dataset atual** (sem novas fontes externas).
- Melhorias serão entregues incrementalmente, com “gate” de aceitação por etapa antes de avançar para a próxima.
