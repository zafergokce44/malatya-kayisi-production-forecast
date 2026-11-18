#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nested CV reconstruction for Zafer Gokce's 2026 master's thesis.

RECONSTRUCTION, not an original historical experiment source file.
Source basis: nested_yontem_notu.txt, nested_arama_uzayi.csv,
nested_outer_katlar.csv and analiz_v2.py. Original hyperparameters and
split design were recovered independently and are validated against saved
per-fold predictions by the optional --reference-outer argument.

Never publish input data or derived row-level predictions without reviewing
source-data licensing, especially Turkish MGM meteorological data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

YEAR = "YIL"
TARGET = "TOPLAM ÜRETİM(YAŞ KAYISI/TON)"
TREE = "TOPLAM MEYVE VEREN AĞAÇ SAYISI"
LAG = "AGAC_SAYISI_L1"
METEO = [
    "Haziran ayı ortalama sıcaklık",
    "Temmuz ayı sıcaklık ortalaması",
    "Haziran max sıcaklık",
    "Temmuz ayı max sıcaklık",
    "Haziran ayı rüzgar hızı ortalaması",
    "Temmuz ayı rüzgar hızı ortalaması",
]
FEATURES = [TREE, LAG] + METEO
NESTED_SEED = 42
MODELS = ("Extra Trees", "Random Forest", "Doğrusal SVR")


def load_data(path: Path, sheet: str) -> dict[str, pd.DataFrame]:
    """Read the *locally licensed* original data; no file is bundled."""
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, encoding="utf-8-sig")
    elif path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path, sheet_name=sheet)
    else:
        raise ValueError("Input must be a .csv or Excel .xlsx/.xls file")
    df.columns = df.columns.astype(str).str.strip()
    required = [YEAR, TARGET, TREE] + METEO
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required input columns are missing: {missing}")
    df = df.sort_values(YEAR).reset_index(drop=True)
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="raise")
    if df[required].isna().any().any():
        raise ValueError("Required input columns have missing values")
    if df[YEAR].duplicated().any():
        raise ValueError("Duplicate years are not supported")
    # This target-leakage guard is intentionally strict; only explicit features above are used.
    if TARGET in FEATURES or YEAR in FEATURES or len(FEATURES) != 8:
        raise AssertionError("Feature definition error")

    tam = df[[YEAR, TARGET, TREE] + METEO].copy()
    tam[LAG] = tam[TREE].shift(1)
    tam = tam.dropna(subset=[LAG]).reset_index(drop=True)
    tam = tam[[YEAR, TARGET] + FEATURES]

    years = set(df[YEAR].astype(int))
    missing_years = set(range(1982, 2025)) - years
    if missing_years:
        raise ValueError(f"MALATYA continuous subset missing years: {sorted(missing_years)}")
    malatya = df[(df[YEAR] >= 1982) & (df[YEAR] <= 2024)][[YEAR, TARGET, TREE] + METEO].copy()
    malatya[LAG] = malatya[TREE].shift(1)
    malatya = malatya.dropna(subset=[LAG]).reset_index(drop=True)
    malatya = malatya[[YEAR, TARGET] + FEATURES]

    if len(tam) != 57 or len(malatya) != 42 or int(malatya[YEAR].min()) != 1983:
        raise ValueError(f"Unexpected samples: TAM={len(tam)}, MALATYA={len(malatya)}")
    return {"TAM": tam, "MALATYA": malatya}


def pipeline_and_search_space(model_name: str) -> tuple[Pipeline, dict[str, list]]:
    if model_name == "Extra Trees":
        estimator = ExtraTreesRegressor(n_estimators=500, max_depth=6,
                                       min_samples_leaf=1, random_state=NESTED_SEED,
                                       n_jobs=-1)
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", estimator)]), {
            "model__n_estimators": [300, 500],
            "model__max_depth": [6, None],
            "model__min_samples_leaf": [1, 2],
        }
    if model_name == "Random Forest":
        estimator = RandomForestRegressor(n_estimators=300, max_depth=5,
                                          min_samples_leaf=1, random_state=NESTED_SEED,
                                          n_jobs=-1)
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", estimator)]), {
            "model__n_estimators": [200, 300],
            "model__max_depth": [5, None],
            "model__min_samples_leaf": [1, 2],
        }
    if model_name == "Doğrusal SVR":
        estimator = SVR(kernel="linear", C=5000, epsilon=0.5, gamma="scale")
        return Pipeline([("imputer", SimpleImputer(strategy="median")),
                         ("scaler", StandardScaler()),
                         ("model", estimator)]), {
            "model__C": [1000, 5000, 10000],
            "model__epsilon": [0.5, 5000, 10000],
        }
    raise ValueError(f"Unknown model: {model_name}")


def measures(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {"R2": float(r2_score(y_true, y_pred)),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "MAE": float(mean_absolute_error(y_true, y_pred))}


def to_json_array(arr) -> str:
    return json.dumps([float(v) for v in arr], ensure_ascii=False)


def calculate(datasets: dict, *, print_progress: bool = True, select_datasets=None, select_models=None, select_folds=None) -> pd.DataFrame:
    all_rows = []
    outer = KFold(n_splits=5, shuffle=True, random_state=NESTED_SEED)
    inner = KFold(n_splits=3, shuffle=True, random_state=NESTED_SEED)
    for dataset_name, data in datasets.items():
        if select_datasets and dataset_name not in select_datasets:
            continue
        X, y = data[FEATURES], data[TARGET]
        for fold_no, (tr, te) in enumerate(outer.split(X), start=1):
            if select_folds and fold_no not in select_folds:
                continue
            for model_name in MODELS:
                if select_models and model_name not in select_models:
                    continue
                fixed, param_grid = pipeline_and_search_space(model_name)
                search = GridSearchCV(
                    estimator=pipeline_and_search_space(model_name)[0],
                    param_grid=param_grid,
                    scoring="neg_root_mean_squared_error", cv=inner,
                    n_jobs=1, refit=True, error_score="raise"
                )
                search.fit(X.iloc[tr], y.iloc[tr])
                fixed.fit(X.iloc[tr], y.iloc[tr])
                tuned_test = search.predict(X.iloc[te]); fixed_test = fixed.predict(X.iloc[te])
                mt = measures(y.iloc[te].to_numpy(), tuned_test)
                mf = measures(y.iloc[te].to_numpy(), fixed_test)
                tuned_train_r2 = float(r2_score(y.iloc[tr], search.predict(X.iloc[tr])))
                fixed_train_r2 = float(r2_score(y.iloc[tr], fixed.predict(X.iloc[tr])))
                row = {
                    "Veri_Seti": dataset_name, "Model": model_name, "Outer_Kat": fold_no,
                    "N_Egitim": len(tr), "N_Test": len(te),
                    "Test_Index_JSON": json.dumps([int(v) for v in te]),
                    "Tuned_Test_Pred_JSON": to_json_array(tuned_test),
                    "Fixed_Test_Pred_JSON": to_json_array(fixed_test),
                    "Inner_Best_RMSE": float(-search.best_score_),
                    "Best_Params_JSON": json.dumps(search.best_params_, ensure_ascii=False),
                    "Grid_Kombinasyon_Sayisi": len(search.cv_results_["params"]),
                    "Tuned_Test_RMSE": mt["RMSE"], "Tuned_Test_MAE": mt["MAE"],
                    "Tuned_Test_R2": mt["R2"], "Tuned_Train_R2": tuned_train_r2,
                    "Fixed_Test_RMSE": mf["RMSE"], "Fixed_Test_MAE": mf["MAE"],
                    "Fixed_Test_R2": mf["R2"], "Fixed_Train_R2": fixed_train_r2,
                }
                all_rows.append(row)
                if print_progress:
                    print(f"{dataset_name} | fold {fold_no}/5 | {model_name} | "
                          f"tuned RMSE {mt['RMSE']:.2f} ton", flush=True)
    return pd.DataFrame(all_rows)


def verify_against_historical(rebuilt: pd.DataFrame, original_path: Path, tolerance: float = 1e-6) -> dict:
    original = pd.read_csv(original_path, sep=";", decimal=",", encoding="utf-8-sig")
    cols = ("Veri_Seti", "Model", "Outer_Kat")
    merged = rebuilt.merge(original, on=list(cols), how="outer", suffixes=("_new", "_original"),
                           indicator=True, validate="one_to_one")
    if (merged["_merge"] == "left_only").any():
        raise AssertionError("Reconstructed experiment rows have no matching original record")
    merged = merged[merged["_merge"] == "both"].copy()
    errors = []
    max_diff = 0.0
    for _, row in merged.iterrows():
        key = " / ".join(str(row[k]) for k in cols)
        for field in ["N_Egitim", "N_Test", "Grid_Kombinasyon_Sayisi"]:
            if row[field+"_new"] != row[field+"_original"]:
                errors.append(f"{key}: {field} mismatch")
        idx_new = json.loads(row["Test_Index_JSON_new"])
        idx_old = json.loads(row["Test_Index_JSON_original"])
        if idx_new != idx_old:
            errors.append(f"{key}: indices mismatch")
        for field in ["Best_Params_JSON"]:
            if json.loads(row[field+"_new"]) != json.loads(row[field+"_original"]):
                errors.append(f"{key}: selected parameters mismatch")
        for field in ["Tuned_Test_Pred_JSON", "Fixed_Test_Pred_JSON"]:
            a = np.array(json.loads(row[field+"_new"]), float)
            b = np.array(json.loads(row[field+"_original"]), float)
            delta = float(np.max(np.abs(a-b)))
            max_diff = max(delta, max_diff)
            if delta > tolerance:
                errors.append(f"{key}: {field} max delta {delta}")
        for field in ["Inner_Best_RMSE", "Tuned_Test_RMSE", "Tuned_Test_MAE", "Tuned_Test_R2", "Tuned_Train_R2", "Fixed_Test_RMSE", "Fixed_Test_MAE", "Fixed_Test_R2", "Fixed_Train_R2"]:
            a, b = float(row[field+"_new"]), float(row[field+"_original"])
            delta = abs(a-b)
            max_diff = max(delta, max_diff)
            if delta > tolerance:
                errors.append(f"{key}: {field} delta {delta}")
    return {"historical_experiment_rows": len(original),
            "reconstructed_rows": len(rebuilt),
            "coverage": "all" if len(rebuilt) == len(original) else "selected_subset",
            "max_absolute_numeric_difference": max_diff,
            "tolerance": tolerance,
            "matched": len(errors) == 0,
            "differences": errors[:100]}


def main():
    parser = argparse.ArgumentParser(description="Reconstruct 5x3 nested CV from preserved method/output records")
    parser.add_argument("--input", required=True, type=Path,
                        help="Locally authorized 58-record input dataset (.xlsx or .csv)")
    parser.add_argument("--sheet", default="Tam veri seti", help="Excel sheet name")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--reference-outer", type=Path,
                        help="Saved nested_outer_katlar.csv to validate every outer-fold prediction")
    parser.add_argument("--datasets", nargs="+", choices=["TAM", "MALATYA"],
                        help="Optional dataset selection for a targeted verification run")
    parser.add_argument("--models", nargs="+", choices=MODELS,
                        help="Optional model selection for a targeted verification run")
    parser.add_argument("--folds", nargs="+", type=int, choices=range(1, 6),
                        help="Optional 1-based outer folds for a targeted verification run")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Input not found: {args.input}")
    datasets = load_data(args.input, args.sheet)
    rebuilt = calculate(datasets, select_datasets=args.datasets, select_models=args.models, select_folds=args.folds)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = args.output_dir / "nested_outer_katlar_yeniden_uretim.csv"
    rebuilt.to_csv(out_csv, sep=";", decimal=",", index=False, encoding="utf-8-sig")
    print("Saved:", out_csv)
    if args.reference_outer:
        report = verify_against_historical(rebuilt, args.reference_outer)
        report_path = args.output_dir / "nested_yeniden_uretim_dogrulama.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Validation:", json.dumps(report, ensure_ascii=False))
        if not report["matched"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
