# Tech Challenge Fase 1 — Plano de Projeto

## Grupo

  | Integrante                         | Contato                         |
| ---------------------------------- | ------------------------------- |
| Alan Araujo Soares                 | aalan.araujo@hotmail.com        |
| Igor da Costa Silveira Pestana     | igor.pestana@alura.com.br       |
| Emídio Dias Maciel e Souza         | emidiodmsouza@gmail.com         |
| Caê Moreira Euphrasio              | caedeminas@gmail.com            |

**Tema escolhido:** Segurança e Saúde da Mulher (Documento B)

**Entrega:** 05/05/2026

**Entregáveis:** PDF com link do repositório Git, relatório técnico, gráficos/prints, e vídeo de até 15 min no YouTube/Vimeo.

---

## Dataset — decisão e escopo

**Escolha do grupo:** **SINASC / DATASUS (Opção B)** — dados reais de nascidos vivos, com foco em **Minas Gerais**, Declarações de Nascido Vivo (**DN**), anos **2020, 2021 e 2022**, obtidos via biblioteca **[PySUS](https://pypi.org/project/pysus/)** (`pysus` no projeto).

**Problema de modelagem (alvo):** classificar risco de **prematuridade** (gestação abaixo de 37 semanas) e/ou **baixo peso ao nascer** (abaixo de 2500 g), alinhado ao tema de saúde materno-infantil no SUS.

**O que já está no EDA (`01_eda.ipynb`):**

- Carga e inspeção via `SINASC` (grupos, metadados, download `.dbc` → parquet em `data/`).
- Concatenação dos anos e tratamento inicial de tipos e sentinelas do DATASUS.
- **Merge com tabela de municípios do IBGE** para **latitude e longitude** a partir de `CODMUNRES` (join alinhando código IBGE 6/7 dígitos conforme documentado no notebook).

**Enriquecimento adicional (opcional / relatório):** IDH municipal, PIB per capita, cobertura e-SUS, taxa de urbanização — fontes em [IBGE — cidades e estados](https://www.ibge.gov.br/cidades-e-estados). Não estão obrigatoriamente no código atual; podem entrar como evolução do feature engineering se couber no prazo.

**Alternativas não adotadas como eixo principal:** Breast Cancer Wisconsin (Opção A) e combinação A+B (Opção C) ficam como referência bibliográfica se o relatório quiser comparar abordagens; o repositório segue **apenas SINASC**.

**Extra (opcional, bônus):** CNN em mamografias ([CBIS-DDSM](https://www.kaggle.com/datasets/awsaf49/cbis-ddsm-breast-cancer-image-dataset)). Só após os itens obrigatórios estarem sólidos.

---

## Estado atual do repositório (alinhado ao código)

| Artefato | Status |
| -------- | ------ |
| `notebooks/01_eda.ipynb` | Em andamento avançado: SINASC MG, PySUS, merge IBGE (lat/lng). |
| `notebooks/02_preprocessing.ipynb` | Esqueleto: falta implementar pipeline de limpeza/encoding/salvamento. |
| `notebooks/03_modeling.ipynb` | Esqueleto: falta modelos, métricas e validação cruzada. |
| `notebooks/04_interpretability.ipynb` | Esqueleto: falta RF importance, SHAP e discussão. |
| `src/pipeline.py` | Stub (`NotImplementedError`): orquestração CLI/Docker pendente. |
| `Dockerfile` | Presente: comando padrão `uv run python -m pipeline`. |
| `compose.yaml` / `compose.dev.yaml` | Presentes: Jupyter Lab com volumes para `notebooks/`, `data/`, `results/`, `src/`. |
| `README.md` | Instruções de uv, Docker e Compose. |
| `docs/relatorio.pdf` | A produzir na entrega. |

---

## Estrutura do repositório

```
tech-challenge-fase-1/
├── README.md
├── Dockerfile
├── compose.yaml               # Jupyter (token variável)
├── compose.dev.yaml           # Jupyter (token fixo de dev)
├── pyproject.toml
├── uv.lock
├── .python-version            # 3.12.x
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_modeling.ipynb
│   └── 04_interpretability.ipynb
├── src/
│   └── pipeline.py
├── data/
│   └── README.md              # Origem dos dados SINASC / pastas locais
├── results/
│   ├── figures/
│   └── metrics/
└── docs/
    ├── plan.md
    └── relatorio.pdf          # Relatório técnico final (entrega)
```

---

## Divisão de tarefas (pra decidir em grupo)

Os blocos abaixo seguem uma ordem lógica de dependência: cada um usa o resultado do anterior. Sugestão é dividir em duplas/trios, mas quem faz o quê a gente decide junto.

### Bloco 1 — Exploração e Pré-processamento (semana 1: 03/04 a 10/04)

- Carregar o dataset com Pandas (parquet gerado pelo fluxo SINASC)
- Estatísticas descritivas: shape, dtypes, describe(), distribuição do target
- Visualizações: histogramas, boxplots, distribuição do target (matplotlib / seaborn / plotly conforme o notebook)
- Matriz de correlação com heatmap (Seaborn)
- Verificar e tratar valores ausentes e sentinelas DATASUS
- Separar features (X) e target (y)
- Normalização/padronização (StandardScaler) onde fizer sentido
- Encoding de categóricas
- Salvar dados processados para o próximo bloco

**Entrega:** `01_eda.ipynb` e `02_preprocessing.ipynb` funcionando de ponta a ponta.

### Bloco 2 — Modelagem e Avaliação (semana 2: 10/04 a 17/04)

- Train/test split (80/20 ou 70/30, estratificado)
- Pelo menos 2 modelos de classificação:
  - Regressão Logística (baseline linear)
  - Random Forest (baseline ensemble)
  - Terceiro opcional: SVM ou Gradient Boosting
- Métricas: accuracy, precision, recall, F1-score, matriz de confusão
- Discussão da métrica mais relevante (em saúde, recall costuma pesar contra falsos negativos)
- Comparação entre modelos em tabela
- Cross-validation (5-fold) para robustez

**Entrega:** `03_modeling.ipynb` funcionando.

### Bloco 3 — Interpretabilidade e Discussão (semana 3: 17/04 a 24/04)

- Feature importance do Random Forest
- SHAP (summary plot, force plot em casos individuais)
- Discussão crítica: uso prático como apoio à triagem (não substitui decisão clínica), features mais preditivas, limitações de viés e representatividade

**Entrega:** `04_interpretability.ipynb` funcionando.

### Bloco 4 — Integração e Entrega (semana 4: 24/04 a 03/05)

- `pipeline.py` reproduzindo o fluxo principal (para Docker e `uv run python -m pipeline`)
- README revisado
- Relatório técnico em PDF cobrindo:
  - Discussões da análise exploratória
  - Estratégias de pré-processamento
  - Modelos usados e justificativa
  - Resultados e interpretação
- Vídeo (até 15 min)
- Revisão final e upload

---

## Cronograma resumido

| Semana | Período       | Atividade                    | Responsáveis |
| ------ | ------------- | ---------------------------- | ------------ |
| 1      | 03/04 — 10/04 | EDA + Pré-processamento      | a definir    |
| 2      | 10/04 — 17/04 | Modelagem + Avaliação        | a definir    |
| 3      | 17/04 — 24/04 | Interpretabilidade + SHAP    | a definir    |
| 4      | 24/04 — 03/05 | Integração, relatório, vídeo | Todos        |
| —      | 05/05         | **Entrega**                  | —            |

---

## Stack técnica

- **Python 3.12** (ver `.python-version`)
- **JupyterLab** para os notebooks
- **Núcleo de análise e ML:** pandas, numpy, matplotlib, seaborn, **plotly**, scikit-learn, shap
- **Dados SUS:** **pysus** (download e leitura SINASC)
- **Reprodutibilidade:** **uv** (`pyproject.toml`, `uv.lock`), **Docker** e **Docker Compose** (ver `README.md`)
- **Ferramentas de desenvolvimento no projeto:** jupyterlab-lsp, python-lsp-server, nbstripout (limpeza de outputs em notebooks, se adotado pelo grupo)
- **Git/GitHub** para versionamento

### Setup (uv)

```bash
git clone <repo-url>
cd tech-challenge-fase-1
uv sync
uv run jupyter lab
```

Para adicionar dependências: `uv add <pacote>`.

---

## Critérios de avaliação (extraídos do enunciado)

O enunciado pede explicitamente os seguintes itens. Cada um precisa estar coberto:

1. **Discussão do problema** — por que esse dataset? qual o impacto clínico?
2. **Exploração de dados** — estatísticas descritivas e visualizações com discussão
3. **Pré-processamento** — pipeline documentado em Python
4. **Análise de correlação** — heatmap e interpretação
5. **Dois ou mais modelos de classificação** — com justificativa da escolha
6. **Separação treino/teste** — clara e estratificada
7. **Métricas** — accuracy, recall, F1-score com discussão de qual é mais relevante
8. **Interpretabilidade** — feature importance e SHAP
9. **Discussão crítica** — o modelo funciona na prática? como? limitações?
10. **Código organizado** — notebooks ou scripts estruturados e documentados
11. **Repositório Git** — com README e instruções de execução
12. **Relatório técnico** — PDF cobrindo todos os pontos acima
13. **Vídeo** — até 15 min demonstrando o sistema

---

## Notas importantes

- O Tech Challenge vale **90% da nota** de todas as disciplinas da fase. É o que importa.
- O enunciado diz "em princípio, deve ser desenvolvida em grupo" — ou seja, é grupo mesmo.
- **Sem frontend.** O enunciado não pede interface (nem Streamlit, nem Gradio, nem dashboard). Pede notebooks, código documentado, relatório em PDF e vídeo. Todo o tempo do grupo deve ir pra qualidade dos dados, da modelagem e da análise. Fazer frontend seria investir em algo que não é avaliado e tirar foco do que é.
- O item EXTRA (CNN com imagens de mamografia) **não é obrigatório**. Só investir nisso se todos os itens obrigatórios estiverem cobertos com qualidade.
- Cada membro deve entender o projeto inteiro, não só sua parte. No vídeo, qualquer um pode ser questionado sobre qualquer parte.

