# Tech Challenge - Fase 1

Este repositório contém o projeto do **Tech Challenge da Fase 1** da **Post Tech IA para Devs (FIAP)**.

O Tech Challenge é o projeto que engloba os conhecimentos obtidos em todas as disciplinas dessa fase.

## Estrutura do repositório

```
tech-challenge-fase-1/
├── README.md
├── Dockerfile
├── compose.yaml
├── compose.dev.yaml
├── pyproject.toml
├── uv.lock
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_modeling.ipynb
│   └── 04_interpretability.ipynb
├── src/
│   └── pipeline.py
├── data/
│   └── README.md
├── results/
│   ├── figures/
│   └── metrics/
└── docs/
    ├── plan.md
    └── relatorio.pdf   # relatório técnico final (adicionar na entrega)
```

## Como executar

**Requisito:** Python 3.12.

### Ambiente local (uv)

Instale o [uv](https://docs.astral.sh/uv/) e, na raiz do repositório:

```bash
uv sync
uv run jupyter lab
```

Por padrão o Jupyter gera um token novo a cada subida; em geral basta abrir pelo link que o comando imprime (já inclui `?token=...`) ou confiar no cookie do navegador após o primeiro acesso.

Para rodar o script do pipeline (após implementar `src/pipeline.py`):

```bash
uv run python -m pipeline
```

Dependências ficam em `pyproject.toml` e `uv.lock`. Para adicionar pacotes: `uv add <pacote>`.

### Docker

Build e execução do pipeline (comando padrão do `Dockerfile`):

```bash
docker build -t tech-challenge-fase-1 .
docker run --rm tech-challenge-fase-1
```

O comando padrão do container executa `python -m pipeline`. Para Jupyter dentro do container, sobrescreva o comando (por exemplo `uv run jupyter lab --ip=0.0.0.0`).

### Docker Compose (Jupyter Lab)

Na raiz do repositório, sobe o Jupyter Lab na porta **8888**, com `notebooks/`, `data/`, `results/` e `src/` montados do host.

**Produção (token aleatório):** use só `compose.yaml`. O Jupyter gera um token novo a cada subida; copie do log:

```bash
docker compose up --build
docker compose logs -f jupyter   # procure ?token=... ou "token is:"
```

**Desenvolvimento local (token fixo):** use `compose.dev.yaml`. O padrão é **`local-dev-token`** (não precisa de `.env`):

```bash
docker compose -f compose.dev.yaml up --build
```

No login do Jupyter, use `local-dev-token`.

Em segundo plano: `docker compose up -d --build` (produção) ou `docker compose -f compose.dev.yaml up -d --build` (dev).

Para encerrar: `docker compose down` (ou `docker compose -f compose.dev.yaml down`).

Para rodar o pipeline na mesma imagem (one-shot), sem subir o Jupyter:

```bash
docker compose run --rm jupyter uv run python -m pipeline
```

Com override de dev:

```bash
docker compose -f compose.dev.yaml run --rm jupyter uv run python -m pipeline
```

## Integrantes do grupo

- **Alan Araujo Soares** - aalan.araujo@hotmail.com
- **Igor da Costa Silveira Pestana** - igor.pestana@alura.com.br
- **Emídio Dias Maciel e Souza** - emidiodmsouza@gmail.com
- **Caê Moreira Euphrasio** - caedeminas@gmail.com
