"""End-to-end ML pipeline for prematurity risk modeling.

Implements the incremental plan in 6 phases:
1) Baseline diagnostic and leakage audit
2) Stronger validation strategy with nested CV and bootstrap CI
3) Clinical feature engineering
4) Advanced tabular models for imbalance
5) Probability calibration + operational threshold policy
6) Minimal production artifacts + governance outputs
"""

from __future__ import annotations

import argparse
import json
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_predict,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


@dataclass
class ExperimentConfig:
    random_state: int = 42
    test_size: float = 0.2
    cv_splits: int = 5
    min_recall: float = 0.80
    bootstrap_rounds: int = 300
    target_column: str = "PREMATURO"
    data_path: str = ""


LEAKAGE_COLUMNS = {
    "SEMAGESTAC",
    "GESTACAO",
    "PESO",
    "APGAR1",
    "APGAR5",
}

CATEGORICAL_COLUMNS = [
    "ESCMAE2010",
    "ESTCIVMAE",
    "RACACORMAE",
    "GRAVIDEZ",
    "PARTO",
    "SEXO",
    "KOTELCHUCK",
    "FAIXAETAMAE",
]

NUMERIC_COLUMNS = [
    "IDADEMAE",
    "QTDGESTANT",
    "QTDPARTNOR",
    "QTDPARTCES",
    "QTDFILVIVO",
    "QTDFILMORT",
    "MESPRENAT",
    "CONSPRENAT",
    "IDADEPAI",
    "LATITUDE",
    "LONGITUDE",
    "PAI_AUSENTE",
    "IDADEPAI_INVALIDA",
    "PNTARDIO",
    "HISTPERDAFETAL",
    "PRIMIPARA",
    "IDADEMAE_RISCO",
    "PN_EXTREMO",
    "OBS_HISTORICO_AGG",
]

SUBGROUP_COLUMNS = ["FAIXAETAMAE", "ESCMAE2010", "GRAVIDEZ", "CODMUNRES"]


class RareCategoryGrouper(BaseEstimator, TransformerMixin):
    """Group rare categories to reduce one-hot noise and instability."""

    def __init__(self, min_freq: float = 0.01, other_label: str = "OUTROS") -> None:
        self.min_freq = min_freq
        self.other_label = other_label
        self.allowed_: dict[str, set[Any]] = {}

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None) -> "RareCategoryGrouper":
        df = pd.DataFrame(X).copy()
        self.allowed_ = {}
        for col in df.columns:
            values = df[col].astype("string").fillna("MISSING")
            freq = values.value_counts(normalize=True)
            allowed = set(freq[freq >= self.min_freq].index.tolist())
            self.allowed_[col] = allowed
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = pd.DataFrame(X).copy()
        for col in df.columns:
            values = df[col].astype("string").fillna("MISSING")
            allowed = self.allowed_.get(col, set())
            df[col] = values.where(values.isin(allowed), self.other_label).astype("string")
        return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SINASC prematurity modeling pipeline")
    parser.add_argument("--data-path", type=str, default="", help="Input file path (.parquet/.csv)")
    parser.add_argument(
        "--data-glob",
        type=str,
        default="data/*.parquet",
        help="Glob pattern used when --data-path is omitted",
    )
    parser.add_argument("--results-dir", type=str, default="results", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--test-size", type=float, default=0.2, help="Holdout test size")
    parser.add_argument("--cv-splits", type=int, default=5, help="CV splits")
    parser.add_argument("--min-recall", type=float, default=0.80, help="Operational recall floor")
    return parser.parse_args()


def load_dataset(data_path: str, data_glob: str) -> pd.DataFrame:
    if data_path:
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de dados nao encontrado: {path}")
        return read_tabular(path)

    candidates = [
        p
        for p in sorted(Path().glob(data_glob))
        if p.is_file() and "municipios" not in p.name.lower()
    ]
    if not candidates:
        raise FileNotFoundError(
            "Nenhum dataset principal encontrado. Forneca --data-path ou coloque parquet em data/."
        )
    frames = [read_tabular(p) for p in candidates]
    return pd.concat(frames, ignore_index=True)


def read_tabular(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Formato nao suportado: {path}")


def to_numeric_if_present(df: pd.DataFrame, cols: list[str]) -> None:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


def prepare_target(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
    frame = df.copy()
    if target_column not in frame.columns:
        if "SEMAGESTAC" not in frame.columns:
            raise ValueError("Nao foi possivel inferir target. Coluna PREMATURO ou SEMAGESTAC ausente.")
        semagestac = pd.to_numeric(frame["SEMAGESTAC"], errors="coerce")
        frame[target_column] = (semagestac < 37).astype("float")
    frame = frame[frame[target_column].notna()].copy()
    frame[target_column] = frame[target_column].astype(int)
    return frame


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "IDADEMAE" in out.columns:
        idade = pd.to_numeric(out["IDADEMAE"], errors="coerce")
        out["IDADEMAE_RISCO"] = (
            ((idade < 18) | (idade >= 35)).astype("float").fillna(0.0)
        )
        out["FAIXAETAMAE"] = pd.cut(
            idade,
            bins=[-np.inf, 17, 24, 34, 44, np.inf],
            labels=["<18", "18-24", "25-34", "35-44", "45+"],
        ).astype("object")

    if "MESPRENAT" in out.columns:
        mes = pd.to_numeric(out["MESPRENAT"], errors="coerce")
        out["PNTARDIO"] = (mes >= 4).astype("float").fillna(0.0)
        out["PN_EXTREMO"] = ((mes <= 1) | (mes >= 7)).astype("float").fillna(0.0)

    if "IDADEPAI" in out.columns:
        idade_pai = pd.to_numeric(out["IDADEPAI"], errors="coerce")
        out["PAI_AUSENTE"] = idade_pai.isna().astype("float")
        out["IDADEPAI_INVALIDA"] = (idade_pai > 80).astype("float").fillna(0.0)

    obst_cols = [c for c in ["QTDGESTANT", "QTDPARTNOR", "QTDPARTCES", "QTDFILMORT"] if c in out.columns]
    if obst_cols:
        for col in obst_cols:
            out[col] = pd.to_numeric(out[col], errors="coerce")
        out["OBS_HISTORICO_AGG"] = out[obst_cols].fillna(0.0).sum(axis=1)

    if "QTDGESTANT" in out.columns:
        qtd = pd.to_numeric(out["QTDGESTANT"], errors="coerce")
        out["PRIMIPARA"] = (qtd <= 1).astype("float").fillna(0.0)
    if "QTDFILMORT" in out.columns and "HISTPERDAFETAL" not in out.columns:
        qfm = pd.to_numeric(out["QTDFILMORT"], errors="coerce")
        out["HISTPERDAFETAL"] = (qfm > 0).astype("float").fillna(0.0)

    return out


def leakage_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for col in sorted(df.columns):
        risk = "baixo"
        rationale = "ok"
        if col in LEAKAGE_COLUMNS:
            risk = "alto"
            rationale = "potencial leakage direto ou derivado do desfecho"
        elif col in {"CONSPRENAT"}:
            risk = "medio"
            rationale = "pode carregar proxy temporal do desfecho"
        rows.append({"feature": col, "leakage_risk": risk, "rationale": rationale})
    return pd.DataFrame(rows)


def select_feature_columns(df: pd.DataFrame, target: str) -> tuple[list[str], list[str]]:
    candidates = [c for c in df.columns if c != target and c not in LEAKAGE_COLUMNS]

    cat_cols = [c for c in CATEGORICAL_COLUMNS if c in candidates]
    num_cols = [c for c in NUMERIC_COLUMNS if c in candidates]

    extra = [c for c in candidates if c not in set(cat_cols + num_cols)]
    for col in extra:
        if pd.api.types.is_numeric_dtype(df[col]):
            num_cols.append(col)
        else:
            cat_cols.append(col)

    return num_cols, cat_cols


def build_preprocessor(num_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    num_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )
    cat_pipe = Pipeline(
        [
            ("rare", RareCategoryGrouper(min_freq=0.01)),
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[("num", num_pipe, num_cols), ("cat", cat_pipe, cat_cols)],
        remainder="drop",
    )


def evaluate_predictions(y_true: np.ndarray, prob: np.ndarray, threshold: float) -> dict[str, float]:
    pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "roc_auc": float(roc_auc_score(y_true, prob)),
        "average_precision": float(average_precision_score(y_true, prob)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "f2": float(fbeta_score(y_true, pred, beta=2, zero_division=0)),
        "brier": float(brier_score_loss(y_true, prob)),
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
    }


def search_operational_threshold(y_true: np.ndarray, prob: np.ndarray, min_recall: float) -> tuple[float, pd.DataFrame]:
    precision, recall, thresholds = precision_recall_curve(y_true, prob)
    rows: list[dict[str, float]] = []
    best_threshold = 0.5
    best_f2 = -1.0

    for idx, thr in enumerate(thresholds):
        p = precision[idx + 1]
        r = recall[idx + 1]
        f2 = (5 * p * r) / (4 * p + r) if (4 * p + r) > 0 else 0.0
        rows.append({"threshold": float(thr), "precision": float(p), "recall": float(r), "f2": float(f2)})
        if r >= min_recall and f2 > best_f2:
            best_f2 = f2
            best_threshold = float(thr)

    curve = pd.DataFrame(rows)
    if best_f2 < 0 and not curve.empty:
        best_threshold = float(curve.sort_values("f2", ascending=False).iloc[0]["threshold"])
    return best_threshold, curve


def bootstrap_ci(
    y_true: np.ndarray,
    prob: np.ndarray,
    threshold: float,
    n_rounds: int,
    seed: int,
) -> dict[str, tuple[float, float]]:
    rng = np.random.default_rng(seed)
    metrics: dict[str, list[float]] = {"roc_auc": [], "average_precision": [], "precision": [], "recall": [], "f2": []}

    n = len(y_true)
    for _ in range(n_rounds):
        idx = rng.integers(0, n, n)
        y_b = y_true[idx]
        p_b = prob[idx]
        if len(np.unique(y_b)) < 2:
            continue
        ev = evaluate_predictions(y_b, p_b, threshold)
        for key in metrics:
            metrics[key].append(ev[key])

    ci: dict[str, tuple[float, float]] = {}
    for key, values in metrics.items():
        if not values:
            ci[key] = (float("nan"), float("nan"))
            continue
        lo, hi = np.percentile(values, [2.5, 97.5])
        ci[key] = (float(lo), float(hi))
    return ci


def subgroup_metrics(
    df: pd.DataFrame,
    y_true: np.ndarray,
    prob: np.ndarray,
    threshold: float,
) -> pd.DataFrame:
    pred = (prob >= threshold).astype(int)
    report: list[dict[str, Any]] = []

    for col in SUBGROUP_COLUMNS:
        if col not in df.columns:
            continue
        groups = df[col].astype("string").fillna("MISSING")
        vc = groups.value_counts()
        top_values = vc.head(15).index.tolist()
        for value in top_values:
            idx = groups == value
            if idx.sum() < 100:
                continue
            yt = y_true[idx.to_numpy()]
            yp = pred[idx.to_numpy()]
            report.append(
                {
                    "subgroup_column": col,
                    "subgroup": str(value),
                    "n": int(idx.sum()),
                    "prevalence": float(np.mean(yt)),
                    "precision": float(precision_score(yt, yp, zero_division=0)),
                    "recall": float(recall_score(yt, yp, zero_division=0)),
                    "f2": float(fbeta_score(yt, yp, beta=2, zero_division=0)),
                }
            )

    return pd.DataFrame(report).sort_values(["subgroup_column", "n"], ascending=[True, False])


def fit_nested_selection(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    preprocessor: ColumnTransformer,
    config: ExperimentConfig,
) -> tuple[pd.DataFrame, str, BaseEstimator, dict[str, Any]]:
    outer_cv = StratifiedKFold(n_splits=config.cv_splits, shuffle=True, random_state=config.random_state)
    inner_cv = StratifiedKFold(n_splits=max(3, config.cv_splits - 1), shuffle=True, random_state=config.random_state)

    models = {
        "logreg_balanced": (
            LogisticRegression(max_iter=1200, class_weight="balanced", solver="liblinear"),
            {"clf__C": [0.2, 1.0, 5.0]},
        ),
        "rf_balanced": (
            RandomForestClassifier(n_estimators=300, random_state=config.random_state, class_weight="balanced_subsample", n_jobs=-1),
            {"clf__max_depth": [None, 8, 16], "clf__min_samples_leaf": [1, 3, 10]},
        ),
        "hgb": (
            HistGradientBoostingClassifier(random_state=config.random_state),
            {"clf__learning_rate": [0.03, 0.08], "clf__max_leaf_nodes": [31, 63]},
        ),
    }

    rows: list[dict[str, Any]] = []
    best_name = ""
    best_score = -1.0
    best_estimator: BaseEstimator | None = None
    best_params: dict[str, Any] = {}

    for name, (clf, grid) in models.items():
        pipe = Pipeline([("prep", clone(preprocessor)), ("clf", clf)])

        search = GridSearchCV(
            estimator=pipe,
            param_grid=grid,
            scoring="average_precision",
            cv=inner_cv,
            n_jobs=-1,
            refit=True,
        )

        oof_prob = cross_val_predict(
            search,
            X_train,
            y_train,
            cv=outer_cv,
            method="predict_proba",
            n_jobs=-1,
        )[:, 1]

        threshold, _ = search_operational_threshold(y_train.to_numpy(), oof_prob, config.min_recall)
        metrics = evaluate_predictions(y_train.to_numpy(), oof_prob, threshold)
        metrics.update({"model": name, "selection_metric": "f2_subject_to_recall_floor", "min_recall": config.min_recall})
        rows.append(metrics)

        if metrics["recall"] >= config.min_recall and metrics["f2"] > best_score:
            best_score = metrics["f2"]
            best_name = name

        search.fit(X_train, y_train)
        if name == best_name or (not best_name and metrics["f2"] > best_score):
            best_estimator = search.best_estimator_
            best_params = search.best_params_

    table = pd.DataFrame(rows).sort_values(["f2", "average_precision"], ascending=False)

    if best_estimator is None:
        top = table.iloc[0]
        best_name = str(top["model"])
        clf, grid = models[best_name]
        pipe = Pipeline([("prep", clone(preprocessor)), ("clf", clf)])
        search = GridSearchCV(pipe, grid, scoring="average_precision", cv=inner_cv, n_jobs=-1, refit=True)
        search.fit(X_train, y_train)
        best_estimator = search.best_estimator_
        best_params = search.best_params_

    return table, best_name, best_estimator, best_params


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
    args = parse_args()
    config = ExperimentConfig(
        random_state=args.seed,
        test_size=args.test_size,
        cv_splits=args.cv_splits,
        min_recall=args.min_recall,
        target_column="PREMATURO",
        data_path=args.data_path,
    )

    results_dir = Path(args.results_dir)
    metrics_dir = results_dir / "metrics"
    artifacts_dir = results_dir / "artifacts"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1: baseline + leakage diagnostic
    raw = load_dataset(args.data_path, args.data_glob)
    frame = prepare_target(raw, config.target_column)
    frame = add_engineered_features(frame)

    leakage = leakage_audit(frame)
    leakage.to_csv(metrics_dir / "phase1_leakage_audit.csv", index=False)

    num_cols, cat_cols = select_feature_columns(frame, config.target_column)
    x = frame[num_cols + cat_cols].copy()
    y = frame[config.target_column].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=y,
    )

    baseline = {
        "n_rows": int(len(frame)),
        "n_features": int(x.shape[1]),
        "target_prevalence": float(y.mean()),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "seed": config.random_state,
    }
    write_json(metrics_dir / "phase1_baseline_summary.json", baseline)

    # Phase 2-4: nested validation + model ranking
    preprocessor = build_preprocessor(num_cols, cat_cols)
    comparison, best_model_name, best_estimator, best_params = fit_nested_selection(
        X_train,
        y_train,
        preprocessor,
        config,
    )
    comparison.to_csv(metrics_dir / "model_comparison_cv_test.csv", index=False)

    # Phase 5: calibration + threshold policy
    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.2,
        random_state=config.random_state,
        stratify=y_train,
    )

    calibrator_for_threshold = CalibratedClassifierCV(clone(best_estimator), method="sigmoid", cv=3)
    calibrator_for_threshold.fit(X_fit, y_fit)
    val_prob = calibrator_for_threshold.predict_proba(X_val)[:, 1]
    op_threshold, thr_curve = search_operational_threshold(y_val.to_numpy(), val_prob, config.min_recall)
    thr_curve.to_csv(metrics_dir / "threshold_search_curve.csv", index=False)

    calibrator = CalibratedClassifierCV(clone(best_estimator), method="sigmoid", cv=3)
    calibrator.fit(X_train, y_train)
    test_prob = calibrator.predict_proba(X_test)[:, 1]
    default_metrics = evaluate_predictions(y_test.to_numpy(), test_prob, threshold=0.5)
    tuned_metrics = evaluate_predictions(y_test.to_numpy(), test_prob, threshold=op_threshold)

    pd.DataFrame([default_metrics]).to_csv(metrics_dir / "best_model_test_metrics_default_threshold.csv", index=False)
    pd.DataFrame([tuned_metrics]).to_csv(metrics_dir / "best_model_test_metrics_tuned_threshold.csv", index=False)

    ci = bootstrap_ci(
        y_true=y_test.to_numpy(),
        prob=test_prob,
        threshold=op_threshold,
        n_rounds=config.bootstrap_rounds,
        seed=config.random_state,
    )

    operational = {
        "model": best_model_name,
        "threshold": op_threshold,
        "selection_rule": f"max f2 with recall >= {config.min_recall:.2f}",
        "metrics": tuned_metrics,
        "metrics_default_threshold": default_metrics,
        "bootstrap_ci_95": {k: {"low": v[0], "high": v[1]} for k, v in ci.items()},
        "best_model_params": best_params,
    }
    write_json(metrics_dir / "best_model_operational_metrics.json", operational)

    subgroup = subgroup_metrics(
        frame.loc[X_test.index],
        y_test.to_numpy(),
        test_prob,
        op_threshold,
    )
    subgroup.to_csv(metrics_dir / "phase1_subgroup_performance.csv", index=False)

    # Phase 6: reproducibility + governance artifacts
    write_json(metrics_dir / "experiment_config.json", asdict(config))
    with (artifacts_dir / "best_model_calibrated.pkl").open("wb") as f:
        pickle.dump(calibrator, f)

    checklist = {
        "acceptance_criteria": {
            "recall_minimum": config.min_recall,
            "must_improve_over_baseline": ["precision", "f2"],
            "calibration_monitor": "brier"
        },
        "retraining_checklist": [
            "Fixar seed e split para comparação justa",
            "Reexecutar auditoria de leakage",
            "Validar nested CV e estabilidade por subgrupo",
            "Selecionar threshold em validação (nunca no teste)",
            "Versionar config, métricas e modelo"
        ]
    }
    write_json(metrics_dir / "retraining_checklist.json", checklist)

    print("Pipeline concluído com sucesso.")
    print(f"Melhor modelo: {best_model_name}")
    print(f"Threshold operacional: {op_threshold:.4f}")


if __name__ == "__main__":
    main()
