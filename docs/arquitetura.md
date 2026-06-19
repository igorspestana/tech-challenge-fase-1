# Documentação de Arquitetura e Decisões de Implementação — Fase 2

**Projeto:** Tech Challenge — Fase 2  
**Curso:** Post Tech IA para Devs — FIAP  
**Grupo:** Alan Araujo Soares · Igor Pestana · Emídio Dias · Caê Euphrasio · Isabella Santiago  

---

## 1. Contexto

A Fase 1 entregou um pipeline de ML para predição de prematuridade (SINASC) com `HistGradientBoostingClassifier`, threshold operacional 0.40 e F2-score baseline de **0.3857**. A Fase 2 tem como objetivo otimizar esse modelo via Algoritmo Genético e adicionar infraestrutura de escalabilidade, monitoramento e logging.

---

## 2. Arquitetura da Fase 2

```
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 2 — Notebooks 05 e 05b                                        │
│                                                                     │
│  05_AG.ipynb               → Algoritmo Genético para busca de      │
│                              hiperparâmetros (threshold 0.5)        │
│                              4 experimentos: conservador, padrão,   │
│                              exploratório, hot start                │
│                                                                     │
│  05b_AG_threshold040.ipynb → Mesmo AG com scorer no threshold       │
│                              operacional (0.40)                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INFRAESTRUTURA (adicionada na Fase 2)                              │
│                                                                     │
│  src/logging_config.py  → Logging estruturado + MetricsLogger AG   │
│  src/scalability.py     → Paralelismo automático + registro de recursos configurados   │
│  compose.scalable.yaml  → Pipeline com recursos e restart policy   │
└─────────────────────────────────────────────────────────────────────┘
```

### Estrutura de diretórios relevante

```
tech-challenge-fase-1/
├── src/
│   ├── pipeline.py
│   ├── logging_config.py        # novo — logging centralizado
│   └── scalability.py           # novo — paralelismo e monitoramento
├── notebooks/
│   ├── 05_AG.ipynb              # novo — AG threshold 0.5
│   └── 05b_AG_threshold040.ipynb # novo — AG threshold 0.40
├── results/
│   └── logs/                    # novo — logs e métricas persistidas
│       ├── pipeline.log
│       └── ag_metrics_<exp>_<timestamp>.json
├── docs/
│   └── arquitetura.md           # este documento
├── compose.scalable.yaml        # novo — escalabilidade Docker
└── pyproject.toml
```

---

## 3. Decisões do Algoritmo Genético

### 3.1 Por que AG em vez de continuar com RandomizedSearchCV?

O `RandomizedSearchCV` da Fase 1 avalia cada configuração de hiperparâmetros de forma independente. O AG explora **interações entre hiperparâmetros** através de crossover e mutação — candidatos promissores combinam características de soluções anteriores, o que pode encontrar regiões do espaço de busca que amostragem aleatória pura não alcançaria.

### 3.2 Estrutura do AG

| Componente | Decisão | Justificativa |
|---|---|---|
| Representação | Dicionário de hiperparâmetros | Mapeamento direto para `HistGradientBoostingClassifier` |
| Fitness | F2-score com cross-validation | Alinhado ao objetivo clínico (recall > precision) |
| Seleção | Torneio | Mantém pressão seletiva sem eliminar diversidade |
| Crossover | Uniforme por parâmetro | Preserva combinações válidas de hiperparâmetros |
| Mutação | Amostragem aleatória do espaço | Evita convergência prematura |

### 3.3 Os 4 experimentos e suas hipóteses

| Experimento | pop_size | n_gen | mutation_rate | Hipótese |
|---|---|---|---|---|
| exp1_conservador | 10 | 8 | 0.10 | Convergência rápida com baixa diversidade |
| exp2_standard | 20 | 15 | 0.20 | Balanço entre exploração e explotação |
| exp3_exploratorio | 20 | 15 | 0.40 | Alta mutação mantém diversidade genética |
| exp4_hot_start | 20 | 15 | 0.20 | Inicializar com melhor resultado da Fase 1 |

### 3.4 Resultado

Nenhum experimento superou o baseline F2=0.3857 da Fase 1. Isso confirma que o gargalo de desempenho está no **poder discriminativo das features administrativas do SINASC**, não nos hiperparâmetros do modelo.

---

## 4. Monitoramento e Logging

### 4.1 Arquitetura

```
src/logging_config.py
       │
       ├── get_logger(name)
       │      ├── StreamHandler → stdout (INFO+)       ← visível no Jupyter
       │      └── FileHandler  → results/logs/pipeline.log (DEBUG+)  ← persistido
       │
       ├── ContextTimer(label, logger)
       │      └── mede tempo de execução de qualquer bloco com `with`
       │
       └── MetricsLogger(experiment_name)
              ├── log_generation(gen, best_fitness, mean_fitness, params)
              └── save_summary() → results/logs/ag_metrics_<exp>_<timestamp>.json
```

### 4.2 O que é monitorado

- **Por geração do AG:** número da geração, melhor F2, F2 médio, melhores hiperparâmetros
- **Por etapa do pipeline:** tempo de execução via `ContextTimer`
- **Por experimento:** JSON completo com histórico, duração total e melhor resultado global

### 4.3 Exemplo de saída de log

```
2026-06-16 14:30:22 | INFO | notebook.ag | ▶ Iniciando: AG completo — exp2_standard
2026-06-16 14:30:23 | INFO | notebook.ag | Geração   1 | best_F2=0.3612 | mean_F2=0.3241 | params={...}
2026-06-16 14:30:25 | INFO | notebook.ag | Geração   2 | best_F2=0.3744 | mean_F2=0.3489 | params={...}
...
2026-06-16 14:35:01 | INFO | notebook.ag | ✔ Concluído: AG completo — exp2_standard — 279.43s
2026-06-16 14:35:01 | INFO | notebook.ag | Summary salvo em: results/logs/ag_metrics_exp2_standard_20260616_143022.json
```

---

## 5. Escalabilidade

### 5.1 Paralelismo no AG

A avaliação de cada indivíduo da população é independente — **embaraçosamente paralelizável**. O módulo `src/scalability.py` implementa:

- `get_n_jobs()`: detecta CPUs disponíveis via variável de ambiente `N_JOBS`
- `parallel_evaluate()`: avalia a população com `ProcessPoolExecutor`, mantendo ordem de retorno
- `configure_sklearn_parallelism()`: propaga `n_jobs` para `cross_val_score` e estimadores sklearn### 5.2 Recursos no Docker (compose.scalable.yaml)

| Serviço | CPU limit | Memory limit | Restart policy |
|---|---|---|---|
| jupyter | 2.0 cores | 4 GB | — |
| pipeline | 4.0 cores | 8 GB | on-failure (3x) |

### 5.3 Controle de paralelismo por variável de ambiente

```yaml
# compose.scalable.yaml
environment:
  - N_JOBS=-1   # usa 80% dos CPUs disponíveis no container
```

Para forçar execução sequencial em debug:
```bash
N_JOBS=1 docker compose -f compose.scalable.yaml run --rm pipeline
```

---

## 6. Como Reproduzir

```bash
# Ambiente interativo
docker compose -f compose.dev.yaml up --build
# acesse: http://localhost:8888 | token: local-dev-token

# Pipeline em batch com escalabilidade
docker compose -f compose.scalable.yaml run --rm pipeline

# Verificar logs gerados
ls results/logs/
# pipeline.log                    ← log contínuo
# ag_metrics_exp2_*.json          ← histórico do AG por experimento
```

---

## 7. Limitações e Próximos Passos

| Limitação | Impacto | Proposta |
|---|---|---|
| AG não supera RandomizedSearch | Hiperparâmetros já próximos do ótimo | Investigar feature engineering |
| Features apenas administrativas | Teto discriminativo próximo de ROC-AUC ~0.65 com SINASC isolado | Integrar dados clínicos (SISPRENATAL/e-SUS APS/SIHSUS) |
| Dados de um estado/período | Generalização incerta | Expandir cobertura geográfica |