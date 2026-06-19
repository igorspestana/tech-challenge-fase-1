"""
scalability.py
==============
Utilitários de escalabilidade para execução paralela do pipeline de ML
e do Algoritmo Genético.

O módulo detecta automaticamente os recursos computacionais disponíveis (CPUs)
e configura o nível de paralelismo adequado — tanto para ambiente local
quanto para execução via Docker.

Uso básico
----------
    from scalability import parallel_evaluate, get_n_jobs, ResourceMonitor

    # Avaliação paralela de uma população do AG
    fitnesses = parallel_evaluate(evaluate_fn, population, X_train, y_train)

    # Monitorar uso de recursos durante o AG
    with ResourceMonitor("ag_exp2") as monitor:
        run_genetic_algorithm(...)
    monitor.report()
"""

import logging
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Detecção automática de recursos disponíveis
# ---------------------------------------------------------------------------

def get_n_jobs(max_fraction: float = 0.8) -> int:
    """
    Retorna o número de workers paralelos a usar, respeitando o limite
    configurado via variável de ambiente N_JOBS (definida no compose.yaml).

    Lógica de decisão:
      - Se N_JOBS=-1 (padrão Docker): usa 80% dos CPUs disponíveis
      - Se N_JOBS=N explícito: usa exatamente N
      - Mínimo sempre 1

    Parâmetros
    ----------
    max_fraction : float
        Fração máxima dos CPUs a usar quando N_JOBS=-1. Default: 0.8.

    Retorna
    -------
    int
        Número de workers recomendado.
    """
    env_val = os.environ.get("N_JOBS", "-1")

    if env_val == "-1":
        total_cpus = os.cpu_count() or 1
        n_jobs = max(1, int(total_cpus * max_fraction))
    else:
        n_jobs = max(1, int(env_val))

    logger.info(f"Paralelismo configurado: {n_jobs} workers (CPUs disponíveis: {os.cpu_count()})")
    return n_jobs


# ---------------------------------------------------------------------------
# Avaliação paralela de população do AG
# ---------------------------------------------------------------------------

def _evaluate_individual(args: tuple) -> tuple[int, float]:
    """
    Função auxiliar para avaliação de um indivíduo em processo separado.
    Retorna (índice, fitness) para reordenação após coleta paralela.
    """
    idx, evaluate_fn, individual, X_train, y_train = args
    fitness = evaluate_fn(individual, X_train, y_train)
    return idx, fitness


def parallel_evaluate(
    evaluate_fn: Callable,
    population: list[dict[str, Any]],
    X_train: Any,
    y_train: Any,
    n_jobs: int | None = None,
) -> list[float]:
    """
    Avalia uma população do AG em paralelo usando ProcessPoolExecutor.

    Substitui o loop sequencial:
        fitnesses = [evaluate(ind, X_train, y_train) for ind in population]

    por execução paralela, reduzindo o tempo de cada geração.

    Parâmetros
    ----------
    evaluate_fn : Callable
        Função de avaliação de um indivíduo. Assinatura:
        evaluate_fn(individual: dict, X_train, y_train) -> float
    population : list[dict]
        Lista de indivíduos (hiperparâmetros) da geração atual.
    X_train, y_train
        Dados de treino passados para cada avaliação.
    n_jobs : int, opcional
        Número de workers. Se None, usa get_n_jobs().

    Retorna
    -------
    list[float]
        Lista de fitness na mesma ordem da população de entrada.
    """
    if n_jobs is None:
        n_jobs = get_n_jobs()

    # Para populações pequenas (exp1: pop_size=10), paralelismo pode ter
    # overhead maior que o ganho — usa sequencial abaixo de 4 indivíduos
    if len(population) < 4:
        logger.debug("População pequena — avaliação sequencial (evita overhead de IPC)")
        return [evaluate_fn(ind, X_train, y_train) for ind in population]

    args_list = [
        (idx, evaluate_fn, ind, X_train, y_train)
        for idx, ind in enumerate(population)
    ]

    results = [None] * len(population)

    logger.debug(f"Avaliando {len(population)} indivíduos com {n_jobs} workers")
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        futures = {executor.submit(_evaluate_individual, args): args[0] for args in args_list}
        for future in as_completed(futures):
            idx, fitness = future.result()
            results[idx] = fitness

    return results


# ---------------------------------------------------------------------------
# Monitor de recursos (CPU e memória) durante execução
# ---------------------------------------------------------------------------

class ResourceMonitor:
    """
    Registra duração e configuração de recursos durante a execução de um bloco.

    Usa apenas a biblioteca padrão do Python (sem psutil) para manter
    compatibilidade com o ambiente Docker do projeto.

    Parâmetros
    ----------
    label : str
        Nome do bloco monitorado (ex: "ag_exp2_standard").

    Exemplo
    -------
        with ResourceMonitor("treinamento_ag") as monitor:
            run_ag(...)
        monitor.report()
    """

    def __init__(self, label: str):
        self.label = label
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.info(f"[ResourceMonitor] Iniciando monitoramento: {self.label}")
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()

    def report(self) -> dict[str, Any]:
        """
        Loga e retorna o relatório de uso de recursos.

        Retorna
        -------
        dict com duration_seconds, n_cpus e n_jobs_configured.
        """
        duration = self.end_time - self.start_time
        report = {
            "label": self.label,
            "duration_seconds": round(duration, 2),
            "n_cpus_available": os.cpu_count(),
            "n_jobs_configured": get_n_jobs(),
        }

        logger.info(
            f"[ResourceMonitor] {self.label} concluído | "
            f"duração={duration:.2f}s | "
            f"CPUs disponíveis={report['n_cpus_available']} | "
            f"workers={report['n_jobs_configured']}"
        )
        return report


# ---------------------------------------------------------------------------
# Configuração de paralelismo no scikit-learn
# ---------------------------------------------------------------------------

def configure_sklearn_parallelism() -> int:
    """
    Configura o número de jobs para estimadores do scikit-learn
    (HistGradientBoostingClassifier, cross_val_score, etc.).

    Deve ser chamada uma vez no início do notebook/script.

    Retorna
    -------
    int
        Valor de n_jobs a passar para os estimadores sklearn.

    Exemplo
    -------
        n_jobs = configure_sklearn_parallelism()
        model = HistGradientBoostingClassifier(**params, random_state=42)
        scores = cross_val_score(model, X, y, cv=5, n_jobs=n_jobs, scoring=scorer)
    """
    n_jobs = get_n_jobs()
    logger.info(f"scikit-learn configurado com n_jobs={n_jobs}")
    return n_jobs
