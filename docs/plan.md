# Tech Challenge Fase 1 — Plano de Projeto

## Grupo


| Integrante   | Perfil                   |
| ------------ | ------------------------ |
| Emídio Souza | Python / AI / Backend    |
| Alan Araújo  | PHP / Backend            |
| Caê          | JS / Python / Front      |
| Igor Pestana | JS / Python / Full Stack |
| Isa Santiago | Início em ML             |


**Tema escolhido:** Segurança e Saúde da Mulher (Documento B)

**Entrega:** 05/05/2026

**Entregáveis:** PDF com link do repositório Git, relatório técnico, gráficos/prints, e vídeo de até 15 min no YouTube/Vimeo.

---

## Dataset — pra debater no grupo

Temos duas opções realistas pro nosso Tech Challenge. Cada uma tem vantagens e riscos diferentes, e vale a gente decidir junto com base no tempo disponível e no nível de conforto de cada um com Python e dados.

### Opção A — Breast Cancer Wisconsin (caminho seguro)

Fonte: [https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data](https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data)

São 569 amostras com 30 features numéricas extraídas de imagens de biópsia. O target é binário: maligno ou benigno. Não tem valores faltantes, tudo já vem numérico, e é uma das sugestões do próprio enunciado.

**Prós:** Dataset limpo, pronto pra usar, amplamente documentado na internet. Permite focar 100% no que o enunciado avalia (pipeline, modelagem, métricas, SHAP) sem perder tempo com limpeza. Baixo risco de atraso.

**Contras:** Todo mundo vai entregar esse dataset. Não tem identidade brasileira. A exploração de dados fica mais superficial porque não tem muito o que limpar ou transformar, o que pode enfraquecer a seção de pré-processamento do relatório.

### Opção B — SINASC / DATASUS (caminho diferenciado)

Fonte: OpenDataSUS / FTP DATASUS (acessível via biblioteca Python PySUS)

O SINASC (Sistema de Informações sobre Nascidos Vivos) registra todos os partos no Brasil. Cada linha é um nascimento com dezenas de variáveis: idade da mãe, escolaridade, semanas de gestação, tipo de parto, número de consultas pré-natal, peso do recém-nascido, APGAR, presença de anomalias congênitas, município, raça/cor. Dá pra filtrar por Minas Gerais ou até por Belo Horizonte.

O problema clínico seria classificar risco de prematuridade (abaixo de 37 semanas) ou baixo peso ao nascer (abaixo de 2500g), ambos problemas reais e relevantes de saúde materno-infantil no SUS.

**Enriquecimento com dados do IBGE:** O SINASC não tem latitude/longitude, mas tem código do município IBGE (6 dígitos) tanto do nascimento (`CODMUNNASC`) quanto da residência da mãe (`CODMUNRES`). Dá pra cruzar com dados públicos do IBGE pra adicionar variáveis geográficas e socioeconômicas por município:

- **Coordenadas geográficas** (lat/lng do centroide do município) — permite fazer mapas e usar localização como feature
- **IDH municipal** — proxy forte de condição socioeconômica
- **PIB per capita municipal**
- **Cobertura da atenção primária (e-SUS)** — disponível no DATASUS/e-Gestor AB
- **Taxa de urbanização**

Fonte das tabelas auxiliares: [https://www.ibge.gov.br/cidades-e-estados](https://www.ibge.gov.br/cidades-e-estados) (API IBGE ou download CSV). O merge é simples: um left join pelo código IBGE do município. Isso adiciona contexto territorial ao modelo e enriquece muito a análise exploratória, permitindo visualizações geográficas (mapas de calor de prematuridade por região de MG, por exemplo).

**Prós:** Dados reais brasileiros do SUS, com relevância direta pro tema de saúde da mulher. Diferencia o grupo de todos que vão entregar o breast cancer. A limpeza de dados reais (valores codificados, missing values de verdade, variáveis categóricas) enriquece muito a seção de pré-processamento do relatório. Volume enorme, o que mostra maturidade no recorte e tratamento. O enriquecimento com IBGE adiciona uma etapa de feature engineering com dados externos, que demonstra maturidade analítica.

**Contras:** Os dados vêm codificados (ex: "1" = vaginal, "2" = cesárea) e exigem consulta ao dicionário de dados do DATASUS. Tem valores faltantes reais que precisam de tratamento. Consome mais tempo no pré-processamento. Se o grupo travar na limpeza, pode comprometer o prazo.

### Opção C — Combinar as duas

Usar o Breast Cancer Wisconsin como entrega principal garantida, e incluir o SINASC como análise complementar no relatório, mostrando que o grupo sabe lidar com dados reais brasileiros. Isso cobre a segurança da nota e adiciona um diferencial.

### Pra discussão no dia 03/04

Perguntas pra gente responder juntos:

1. Quanto tempo cada um tem disponível por semana até 05/05?
2. Alguém já tem experiência com Pandas e limpeza de dados sujos, ou estamos todos aprendendo?
3. A gente quer se diferenciar (Opção B ou C) ou quer segurança máxima (Opção A)?
4. Quem já tem o uv instalado e o ambiente testado?
5. **Dataset brasileiro:** a Opção B (SINASC) usa dados reais do SUS, o que dá identidade ao projeto e mostra que sabemos trabalhar com dados do mundo real. Mas exige mais esforço de limpeza. O grupo topa esse esforço extra, sabendo que o resultado final fica mais forte? Ou preferimos o caminho seguro e garantir a nota sem risco de atraso?

**Extra (opcional, pra pontos bônus):** Detecção de câncer de mama em mamografias com CNN

Fonte: [https://www.kaggle.com/datasets/awsaf49/cbis-ddsm-breast-cancer-image-dataset](https://www.kaggle.com/datasets/awsaf49/cbis-ddsm-breast-cancer-image-dataset)

Só vale a pena investir nisso se todos os itens obrigatórios estiverem cobertos com qualidade. Não comprometer o essencial pelo bônus.

---

## Estrutura do repositório

```
tech-challenge-fase1/
├── README.md                  # Instruções de execução
├── Dockerfile                 # Ambiente reproduzível (opcional no doc B)
├── pyproject.toml             # Dependências
├── uv.lock                    # Lock exato
├── notebooks/
│   ├── 01_eda.ipynb           # Exploração e análise descritiva
│   ├── 02_preprocessing.ipynb # Limpeza e transformação
│   ├── 03_modeling.ipynb      # Treino e avaliação dos modelos
│   └── 04_interpretability.ipynb  # SHAP e feature importance
├── src/
│   └── pipeline.py            # Pipeline completo em script (pra Dockerfile)
├── data/
│   └── README.md              # Link pro download do dataset
├── results/
│   ├── figures/               # Gráficos exportados
│   └── metrics/               # Tabelas de métricas
└── docs/
    └── relatorio.pdf          # Relatório técnico final
```

---

## Divisão de tarefas (pra decidir em grupo)

Os blocos abaixo seguem uma ordem lógica de dependência: cada um usa o resultado do anterior. Sugestão é dividir em duplas/trios, mas quem faz o quê a gente decide junto.

### Bloco 1 — Exploração e Pré-processamento (semana 1: 03/04 a 10/04)

Esse bloco é ideal pra quem está começando em ML, porque é o primeiro contato prático com os dados e usa conceitos fundamentais.

- Carregar o dataset com Pandas
- Estatísticas descritivas: shape, dtypes, describe(), value_counts() do target
- Visualizações: histogramas das features, boxplots, distribuição do target
- Matriz de correlação com heatmap (Seaborn)
- Verificar e tratar valores ausentes
- Separar features (X) e target (y)
- Normalização/padronização (StandardScaler)
- Conversão de variáveis se necessário
- Salvar dados processados pra próximo bloco

**Entrega:** notebooks 01_eda.ipynb e 02_preprocessing.ipynb funcionando

### Bloco 2 — Modelagem e Avaliação (semana 2: 10/04 a 17/04)

- Train/test split (80/20 ou 70/30, estratificado)
- Implementar no mínimo 2 modelos de classificação:
  - Regressão Logística (baseline linear)
  - Random Forest (baseline ensemble)
  - Sugestão de terceiro: SVM ou Gradient Boosting
- Métricas: accuracy, precision, recall, F1-score, matriz de confusão
- Discussão da escolha da métrica (em diagnóstico médico, recall é mais importante que accuracy — um falso negativo significa deixar de diagnosticar um caso de risco)
- Comparação entre modelos com tabela de métricas
- Cross-validation (5-fold) pra robustez

**Entrega:** notebook 03_modeling.ipynb funcionando

### Bloco 3 — Interpretabilidade e Discussão (semana 3: 17/04 a 24/04)

- Feature importance do Random Forest
- SHAP values (summary plot, force plot pra casos individuais)
- Discussão crítica:
  - O modelo pode ser usado na prática? (Sim, como ferramenta de triagem, nunca como substituto do médico)
  - Quais features são mais preditivas?
  - Limitações: viés de seleção, representatividade dos dados, etc.
  - O médico sempre tem a palavra final

**Entrega:** notebook 04_interpretability.ipynb funcionando

### Bloco 4 — Integração e Entrega (semana 4: 24/04 a 03/05)

Esse bloco é de todos.

- Dockerfile funcional
- README.md com instruções claras de execução
- Relatório técnico em PDF cobrindo:
  - Discussões da análise exploratória
  - Estratégias de pré-processamento
  - Modelos usados e justificativa
  - Resultados e interpretação
- Gravação do vídeo de demonstração (até 15 min)
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

- **Python 3.12**
- **JupyterLab** pra desenvolvimento dos notebooks
- **Bibliotecas principais:** pandas, numpy, matplotlib, seaborn, scikit-learn, shap
- **Git/GitHub** pra versionamento
- **Docker** (opcional no doc B) pra reprodutibilidade

### Setup (uv)

O uv gerencia pacotes e ambientes via `pyproject.toml` e `uv.lock`, garantindo o mesmo ambiente para todo mundo.

```bash
git clone <repo-url>
cd tech-challenge-fase1
uv sync              # instala tudo do pyproject.toml
uv run jupyter lab   # roda o Jupyter no ambiente do projeto
```

Pra adicionar dependências: `uv add pandas scikit-learn shap` (atualiza o `pyproject.toml` e o lock automaticamente).

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

