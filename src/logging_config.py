"""
logging_config.py
=================
Configuração centralizada de logging e monitoramento para o Tech Challenge.

Uso básico
----------
    from logging_config import get_logger, ContextTimer, MetricsLogger

    logger = get_logger(__name__)

    # Log simples
    logger.info("Iniciando pré-processamento")

    # Medir tempo de qualquer bloco
    with ContextTimer("treinamento do modelo", logger):
        model.fit(X_train, y_train)

    # Monitorar métricas do AG por geração
    ml = MetricsLogger(experiment_name="exp2_standard")
    ml.log_generation(gen=1, best_fitness=0.38, mean_fitness=0.35, params={...})
    ml.save_summary()
"""

import json
import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Diretório de logs
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).resolve().parent.parent / "results" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Configuração do logger raiz do projeto
# ---------------------------------------------------------------------------

def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Retorna um logger configurado com dois handlers:
      - StreamHandler  → console (INFO e acima)
      - FileHandler    → results/logs/pipeline.log (DEBUG e acima)

    Parâmetros
    ----------
    name : str
        Nome do logger, geralmente __name__ do módulo chamador.
    level : int
        Nível mínimo capturado pelo logger raiz (default: DEBUG).

    Retorna
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Evita adicionar handlers duplicados em reexecuções de célula no Jupyter
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler 1: console — só INFO e acima para não poluir o notebook
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)

    # Handler 2: arquivo — tudo (DEBUG incluso) para rastreabilidade completa
    log_file = LOG_DIR / "pipeline.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# ---------------------------------------------------------------------------
# Context manager para medir tempo de execução
# ---------------------------------------------------------------------------

@contextmanager
def ContextTimer(label: str, logger: logging.Logger | None = None):
    """
    Mede o tempo de execução de um bloco e loga o resultado.

    Parâmetros
    ----------
    label : str
        Descrição da etapa sendo medida (ex: "treinamento", "SHAP").
    logger : logging.Logger, opcional
        Logger a usar. Se None, usa print() como fallback.

    Exemplo
    -------
        with ContextTimer("pré-processamento", logger):
            df = preprocess(df_raw)
    """
    _log = logger.info if logger else print
    _log(f"▶ Iniciando: {label}")
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        _log(f"✔ Concluído: {label} — {elapsed:.2f}s")


# ---------------------------------------------------------------------------
# Logger de métricas para o Algoritmo Genético
# ---------------------------------------------------------------------------

class MetricsLogger:
    """
    Registra e persiste métricas de desempenho do Algoritmo Genético.

    Cada geração é logada com: número da geração, melhor fitness,
    fitness médio e melhores hiperparâmetros encontrados até ali.

    Ao final, `save_summary()` grava um JSON em results/logs/ com
    o histórico completo e os melhores parâmetros globais.

    Parâmetros
    ----------
    experiment_name : str
        Identificador do experimento (ex: "exp1_conservador").
    logger : logging.Logger, opcional
        Logger a usar. Se None, cria um interno.

    Exemplo
    -------
        ml = MetricsLogger("exp2_standard")
        for gen, pop in enumerate(generations):
            best = max(pop, key=lambda x: x.fitness)
            ml.log_generation(
                gen=gen + 1,
                best_fitness=best.fitness,
                mean_fitness=mean([p.fitness for p in pop]),
                params=best.params,
            )
        ml.save_summary()
    """

    def __init__(self, experiment_name: str, logger: logging.Logger | None = None):
        self.experiment_name = experiment_name
        self.logger = logger or get_logger(f"metrics.{experiment_name}")
        self.history: list[dict[str, Any]] = []
        self.start_time = datetime.now()

        self.logger.info(
            f"MetricsLogger iniciado | experimento={experiment_name} | "
            f"início={self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def log_generation(
        self,
        gen: int,
        best_fitness: float,
        mean_fitness: float,
        params: dict[str, Any],
    ) -> None:
        """
        Registra métricas de uma geração do AG.

        Parâmetros
        ----------
        gen : int
            Número da geração (começa em 1).
        best_fitness : float
            Melhor valor de fitness (F2-score) na geração.
        mean_fitness : float
            Fitness médio da população.
        params : dict
            Hiperparâmetros do melhor indivíduo da geração.
        """
        record = {
            "generation": gen,
            "best_fitness": round(best_fitness, 6),
            "mean_fitness": round(mean_fitness, 6),
            "best_params": params,
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(record)

        self.logger.info(
            f"Geração {gen:>3} | "
            f"best_F2={best_fitness:.4f} | "
            f"mean_F2={mean_fitness:.4f} | "
            f"params={params}"
        )

    def log_pipeline_step(self, step: str, metrics: dict[str, Any]) -> None:
        """
        Loga métricas de uma etapa genérica do pipeline
        (ex: pré-processamento, avaliação final).

        Parâmetros
        ----------
        step : str
            Nome da etapa.
        metrics : dict
            Dicionário com as métricas a registrar.
        """
        self.logger.info(f"[{step}] " + " | ".join(f"{k}={v}" for k, v in metrics.items()))

    def save_summary(self) -> Path:
        """
        Salva o histórico completo em JSON em results/logs/.

        O arquivo inclui: nome do experimento, timestamps de início/fim,
        duração total, melhor fitness global e todo o histórico por geração.

        Retorna
        -------
        Path
            Caminho do arquivo salvo.
        """
        if not self.history:
            self.logger.warning("Nenhuma geração registrada — summary não salvo.")
            return Path()

        end_time = datetime.now()
        best_record = max(self.history, key=lambda r: r["best_fitness"])

        summary = {
            "experiment": self.experiment_name,
            "started_at": self.start_time.isoformat(),
            "finished_at": end_time.isoformat(),
            "duration_seconds": round((end_time - self.start_time).total_seconds(), 2),
            "total_generations": len(self.history),
            "best_fitness_overall": best_record["best_fitness"],
            "best_params_overall": best_record["best_params"],
            "best_at_generation": best_record["generation"],
            "history": self.history,
        }

        filename = (
            LOG_DIR
            / f"ag_metrics_{self.experiment_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        )
        filename.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

        self.logger.info(
            f"Summary salvo em: {filename} | "
            f"melhor F2={best_record['best_fitness']:.4f} "
            f"(geração {best_record['generation']})"
        )
        return filename
