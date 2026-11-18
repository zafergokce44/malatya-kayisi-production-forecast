#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""İlkbahar minimum sıcaklık duyarlılık analizi: kayıtlı deneyden yeniden oluşturma.

Kaynak: Zafer Gökçe yüksek lisans tezi, v3(2), 2.8.4 ve 3.8.5.
Bu betik 8 ve 11 öznitelik düzenini, 10x5 RepeatedKFold ve 2003–2024
kronolojik genişleyen pencereyi aynı veri bölmeleriyle karşılaştırır.

Yayımlanan paket ham veriyi içermez. Çalıştırma için kullanıcı tarafından yasal
olarak erişilen Excel verisi ayrıca sağlanmalıdır.

Örnek:
  python scripts/ilkbahar_min_reconstruction.py --input /path/to/veri.xlsx \
      --output /path/to/outputs \
      --validate-dir results/05_ilkbahar_sonuclar
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RepeatedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

YEAR = "YIL"
TARGET = "TOPLAM ÜRETİM(YAŞ KAYISI/TON)"
TREE = "TOPLAM MEYVE VEREN AĞAÇ SAYISI"
LAG = "AGAC_SAYISI_L1"
METEOROLOGY = [
    "Haziran ayı ortalama sıcaklık",
    "Temmuz ayı sıcaklık ortalaması",
    "Haziran max sıcaklık",
    "Temmuz ayı max sıcaklık",
    "Haziran ayı rüzgar hızı ortalaması",
    "Temmuz ayı rüzgar hızı ortalaması",
]
FROST = [
    "Şubat ayı minimum sıcaklık ortalaması",
    "Mart ayı minimum sıcaklık ortalaması",
    "Nisan ayı minimum sıcaklık ortalaması",
]
FEATURES = {
    "Temel_8": [TREE, LAG] + METEOROLOGY,
    "Ilkbahar_11": [TREE, LAG] + METEOROLOGY + FROST,
}
MODELS = ["Extra Trees", "Random Forest", "Doğrusal SVR"]
DATASETS = ["TAM", "MALATYA"]


def model_for(name: str) -> Pipeline:
    """v3(2), Ek 2 Tablo 15 ve özgün analiz_v2.py referans parametreleri."""
    if name == "Extra Trees":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", ExtraTreesRegressor(n_estimators=500, max_depth=6, random_state=42, n_jobs=-1)),
        ])
    if name == "Random Forest":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(n_estimators=300, max_depth=5, random_state=42, n_jobs=-1)),
        ])
    if name == "Doğrusal SVR":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", SVR(kernel="linear", C=5000, epsilon=0.5, gamma="scale")),
        ])
    raise ValueError(f"Bilinmeyen model: {name}")


def load_data(path: Path, sheet_name: str) -> dict[str, pd.DataFrame]:
    if not path.is_file():
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {path}")
    raw = pd.read_excel(path, sheet_name=sheet_name)
    raw.columns = [str(c).strip() for c in raw.columns]
    needed = [YEAR, TARGET, TREE] + METEOROLOGY + FROST
    missing = [c for c in needed if c not in raw.columns]
    if missing:
        raise ValueError(f"Eksik sütunlar: {missing}")
    raw = raw[needed].copy()
    for col in needed:
        raw[col] = pd.to_numeric(raw[col], errors="raise")
    if raw[needed].isna().any().any():
        raise ValueError("Gerekli sütunlarda eksik gözlemler bulundu.")
    raw = raw.sort_values(YEAR).reset_index(drop=True)
    if raw[YEAR].duplicated().any():
        raise ValueError("YIL sütununda tekrar eden kayıt var.")
    if len(raw) != 58 or raw[YEAR].iloc[0] != 1934 or raw[YEAR].iloc[-1] != 2024:
        raise ValueError("Beklenen 1934–2024 aralığına ait 58 tarihsel gözlem yok.")

    # TAM'daki L1: önceki mevcut kronolojik gözlem (her zaman önceki takvim yılı değil).
    full = raw.copy()
    full[LAG] = full[TREE].shift(1)
    full = full.dropna(subset=[LAG]).reset_index(drop=True)

    # Kesintisiz MALATYA: ilk L1 için 1982 kullanılır; model yılları 1983–2024.
    mb = raw[(raw[YEAR] >= 1982) & (raw[YEAR] <= 2024)].copy()
    if mb[YEAR].astype(int).tolist() != list(range(1982, 2025)):
        raise ValueError("MALATYA tabanında 1982–2024 kesintisiz gözlemler bulunamadı.")
    mb[LAG] = mb[TREE].shift(1)
    mb = mb.dropna(subset=[LAG]).reset_index(drop=True)
    if len(full) != 57 or len(mb) != 42:
        raise ValueError(f"Beklenen TAM=57, MALATYA=42; elde edilen {len(full)}, {len(mb)}")
    return {"TAM": full, "MALATYA": mb}


def metrics(y: Any, pred: Any) -> tuple[float, float, float]:
    return (
        float(r2_score(y, pred)),
        float(np.sqrt(mean_squared_error(y, pred))),
        float(mean_absolute_error(y, pred)),
    )


def mean_ci(values: Any) -> tuple[float, float, float, float]:
    v = np.asarray(list(values), float)
    n = len(v)
    if n < 2:
        raise ValueError("Güven aralığı için en az 2 değer gerekiyor.")
    avg, sd = float(v.mean()), float(v.std(ddof=1))
    h = float(student_t.ppf(0.975, n - 1) * sd / math.sqrt(n))
    return avg, sd, avg - h, avg + h


def csv_write(df: pd.DataFrame, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False, sep=";", decimal=",", encoding="utf-8-sig", float_format="%.14g")


def repeated_cv(data: dict[str, pd.DataFrame], output: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_folds: list[dict[str, Any]] = []
    all_oof: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for ds_name in DATASETS:
        ds = data[ds_name]
        y = ds[TARGET].reset_index(drop=True)
        split_list = list(RepeatedKFold(n_splits=5, n_repeats=10, random_state=42).split(ds))
        for feature_name in FEATURES:
            X = ds[FEATURES[feature_name]].reset_index(drop=True)
            for name in MODELS:
                fold_rows: list[dict[str, Any]] = []
                oof_rows: list[dict[str, Any]] = []
                for fold_idx, (tr, te) in enumerate(split_list):
                    repeat, fold = fold_idx // 5 + 1, fold_idx % 5 + 1
                    mdl = model_for(name)
                    mdl.fit(X.iloc[tr], y.iloc[tr])
                    train_pred = mdl.predict(X.iloc[tr])
                    test_pred = mdl.predict(X.iloc[te])
                    train_r2, _, _ = metrics(y.iloc[tr], train_pred)
                    test_r2, test_rmse, test_mae = metrics(y.iloc[te], test_pred)
                    fold_rows.append({
                        "Veri_Seti": ds_name, "Ozellik_Seti": feature_name, "Model": name,
                        "Tekrar": repeat, "Kat": fold, "Train_R2": train_r2,
                        "Test_R2": test_r2, "Test_RMSE": test_rmse, "Test_MAE": test_mae,
                    })
                    # OOF tahminleri, her tekrar için her gözlemi tam bir kez içerecek biçimde toplanır.
                    if fold == 1:
                        p_repeat = np.full(len(ds), np.nan)
                    p_repeat[te] = test_pred
                    if fold == 5:
                        if np.isnan(p_repeat).any():
                            raise AssertionError("OOF tahminleri eksik.")
                        oof_r2, oof_rmse, oof_mae = metrics(y, p_repeat)
                        oof_rows.append({
                            "Veri_Seti": ds_name, "Ozellik_Seti": feature_name,
                            "Model": name, "Tekrar": repeat,
                            "OOF_R2": oof_r2, "OOF_RMSE": oof_rmse, "OOF_MAE": oof_mae,
                        })
                all_folds.extend(fold_rows)
                all_oof.extend(oof_rows)
                g = pd.DataFrame(fold_rows)
                o = pd.DataFrame(oof_rows)
                d: dict[str, Any] = {"Veri_Seti": ds_name, "Ozellik_Seti": feature_name, "Model": name, "Kat_Sayisi": len(g)}
                for field in ["Test_RMSE", "Test_MAE", "Test_R2", "Train_R2"]:
                    avg, sd, lo, hi = mean_ci(g[field])
                    d.update({f"{field}_Ort": avg, f"{field}_SS": sd,
                              f"{field}_GA95_Alt": lo, f"{field}_GA95_Ust": hi})
                avg, sd, _, _ = mean_ci(o["OOF_R2"])
                d.update({"OOF_R2_Ort": avg, "OOF_R2_SS": sd,
                          "Train_Test_R2_Farki": d["Train_R2_Ort"] - d["Test_R2_Ort"]})
                rows.append(d)
                print(f"CV {ds_name:7s} {feature_name:11s} {name:14s}: RMSE {d['Test_RMSE_Ort']:.2f}", flush=True)
    fold_df, oof_df, summary = pd.DataFrame(all_folds), pd.DataFrame(all_oof), pd.DataFrame(rows)
    csv_write(fold_df[fold_df.Ozellik_Seti == "Ilkbahar_11"], output / "ilkbahar11_cv_katlar.csv")
    csv_write(oof_df[oof_df.Ozellik_Seti == "Ilkbahar_11"], output / "ilkbahar11_oof_tekrar.csv")
    csv_write(summary[summary.Ozellik_Seti == "Ilkbahar_11"], output / "ilkbahar11_cv_ozet.csv")
    summary_all = summary.copy()
    summary_all["__feature_order"] = summary_all["Ozellik_Seti"].map({"Temel_8": 0, "Ilkbahar_11": 1})
    summary_all["__ds_order"] = summary_all["Veri_Seti"].map({"TAM": 0, "MALATYA": 1})
    summary_all["__model_order"] = summary_all["Model"].map({name: i for i, name in enumerate(MODELS)})
    summary_all = summary_all.sort_values(["__feature_order", "__ds_order", "__model_order"]).drop(columns=["__feature_order", "__ds_order", "__model_order"])
    csv_write(summary_all, output / "ilkbahar_min_karsilastirma.csv")
    paired: list[dict[str, Any]] = []
    for ds_name in DATASETS:
        for name in MODELS:
            f8 = fold_df[(fold_df.Veri_Seti == ds_name)&(fold_df.Ozellik_Seti == "Temel_8")&(fold_df.Model == name)].sort_values(["Tekrar", "Kat"])
            f11 = fold_df[(fold_df.Veri_Seti == ds_name)&(fold_df.Ozellik_Seti == "Ilkbahar_11")&(fold_df.Model == name)].sort_values(["Tekrar", "Kat"])
            if not np.array_equal(f8[["Tekrar", "Kat"]].to_numpy(), f11[["Tekrar", "Kat"]].to_numpy()):
                raise AssertionError("Eşleştirilmiş kat indeksleri uyuşmuyor.")
            dr = f11["Test_RMSE"].to_numpy() - f8["Test_RMSE"].to_numpy()
            d2 = f11["Test_R2"].to_numpy() - f8["Test_R2"].to_numpy()
            mr, _, lr, ur = mean_ci(dr)
            m2, _, l2, u2 = mean_ci(d2)
            paired.append({"Veri_Seti": ds_name, "Model": name,
                           "RMSE_Fark_Ilkbahar11_Eksi_Temel8_Ort": mr,
                           "RMSE_Fark_GA95_Alt": lr, "RMSE_Fark_GA95_Ust": ur,
                           "R2_Fark_Ilkbahar11_Eksi_Temel8_Ort": m2,
                           "R2_Fark_GA95_Alt": l2, "R2_Fark_GA95_Ust": u2,
                           "Ilkbahar11_RMSE_Daha_Iyi_Kat_Sayisi": int(np.sum(dr < 0)),
                           "Toplam_Kat": len(dr)})
    csv_write(pd.DataFrame(paired), output / "ilkbahar_min_eslesik_kat_farklari.csv")
    return summary, fold_df


def chronological(data: dict[str, pd.DataFrame], output: Path) -> None:
    ds = data["MALATYA"]
    rows: list[dict[str, Any]] = []
    for feature_name in FEATURES:
        predictions: list[dict[str, Any]] = []
        for year in range(2003, 2025):
            tr = ds[ds[YEAR] < year]
            te = ds[ds[YEAR] == year]
            if len(te) != 1 or int(tr[YEAR].max()) != year-1:
                raise ValueError(f"Eksik veya yanlış kronolojik pencere: {year}")
            row: dict[str, Any] = {"YIL": year, "Gercek_Ton": float(te[TARGET].iloc[0])}
            for name in MODELS:
                mdl = model_for(name)
                cols = FEATURES[feature_name]
                mdl.fit(tr[cols], tr[TARGET])
                row[name] = float(mdl.predict(te[cols])[0])
            predictions.append(row)
        pred = pd.DataFrame(predictions)
        if len(pred) != 22:
            raise AssertionError("Kronolojik tahmin sayısı 22 değil")
        if feature_name == "Ilkbahar_11":
            csv_write(pred, output / "ilkbahar11_kronolojik_tahminler.csv")
        for name in MODELS:
            actual = pred["Gercek_Ton"].to_numpy(float)
            forecast = pred[name].to_numpy(float)
            r2, rmse, mae = metrics(actual, forecast)
            mape = float(np.mean(np.abs((actual-forecast)/actual))*100.0)
            rows.append({"Ozellik_Seti": feature_name, "Model": name,
                         "Tahmin_Sayisi": len(actual), "RMSE_Ton": rmse,
                         "MAE_Ton": mae, "MAPE_Yuzde": mape, "R2": r2,
                         "_actual": actual, "_pred": forecast})
        print(f"Kronolojik doğrulama tamamlandı: {feature_name}", flush=True)
    compact = [{k:v for k,v in row.items() if not k.startswith('_')} for row in rows]
    csv_write(pd.DataFrame(compact), output / "ilkbahar_min_kronolojik_ozet.csv")
    diff = []
    for name in MODELS:
        a = next(r for r in rows if r["Ozellik_Seti"] == "Temel_8" and r["Model"] == name)
        b = next(r for r in rows if r["Ozellik_Seti"] == "Ilkbahar_11" and r["Model"] == name)
        diff.append({
            "Model": name,
            "RMSE_Fark_Ilkbahar11_Eksi_Temel8": b["RMSE_Ton"]-a["RMSE_Ton"],
            "MAE_Fark_Ilkbahar11_Eksi_Temel8": b["MAE_Ton"]-a["MAE_Ton"],
            "Ilkbahar11_Daha_Dusuk_Mutlak_Hata_Yil_Sayisi": int(np.sum(np.abs(b["_actual"]-b["_pred"]) < np.abs(a["_actual"]-a["_pred"]))),
            "Toplam_Yil": 22,
        })
    csv_write(pd.DataFrame(diff), output / "ilkbahar_min_kronolojik_fark.csv")


def validate(produced: Path, original: Path) -> dict[str, Any]:
    """Özgün çıktılarla satır/sütun bazında sayısal eşleşme kontrolü (yeniden hesaplama dışında)."""
    report: dict[str, Any] = {"files": {}, "all_numeric_matches_within_tolerance": True, "tolerance_absolute": 1e-5}
    names = [
        "ilkbahar11_cv_katlar.csv", "ilkbahar11_cv_ozet.csv", "ilkbahar_min_karsilastirma.csv",
        "ilkbahar11_oof_tekrar.csv", "ilkbahar_min_eslesik_kat_farklari.csv",
        "ilkbahar11_kronolojik_tahminler.csv", "ilkbahar_min_kronolojik_ozet.csv",
        "ilkbahar_min_kronolojik_fark.csv",
    ]
    for fname in names:
        a_path, b_path = produced / fname, original / fname
        if not b_path.exists():
            report["files"][fname] = {"status": "original_missing"}
            report["all_numeric_matches_within_tolerance"] = False
            continue
        actual = pd.read_csv(a_path, sep=";", decimal=",")
        expected = pd.read_csv(b_path, sep=";", decimal=",")
        if actual.shape != expected.shape or list(actual.columns) != list(expected.columns):
            report["files"][fname] = {"status": "schema_mismatch", "generated_shape": actual.shape, "recorded_shape": expected.shape}
            report["all_numeric_matches_within_tolerance"] = False
            continue
        numeric = [c for c in actual if pd.api.types.is_numeric_dtype(actual[c]) and pd.api.types.is_numeric_dtype(expected[c])]
        non_numeric = [c for c in actual if c not in numeric]
        # Aynı kayıt sırası bekleniyor; CSV'lerde özgün dosya sıralaması korunmuştur.
        mismatch_text = sum(int((actual[c].fillna('<NA>').astype(str) != expected[c].fillna('<NA>').astype(str)).sum()) for c in non_numeric)
        max_diff = max((float(np.max(np.abs(actual[c].to_numpy(float) - expected[c].to_numpy(float)))) for c in numeric), default=0.0)
        ok = mismatch_text == 0 and max_diff <= report["tolerance_absolute"]
        report["files"][fname] = {"status": "matched" if ok else "different", "rows": len(actual),
                                   "numeric_columns": len(numeric), "max_absolute_numeric_difference": max_diff,
                                   "non_numeric_mismatched_cells": mismatch_text}
        report["all_numeric_matches_within_tolerance"] = report["all_numeric_matches_within_tolerance"] and ok
    (produced / "spring_validation_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2), encoding="utf-8")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True, help="Özgün, izinli Excel veri dosyası")
    ap.add_argument("--sheet", default="Tam veri seti", help="Excel sayfa adı")
    ap.add_argument("--output", type=Path, required=True, help="Özel yerel sonuç klasörü")
    ap.add_argument("--validate-dir", type=Path, default=None, help="Arşivdeki özgün CSV sonuçlarının bulunduğu klasör")
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    ds = load_data(args.input, args.sheet)
    repeated_cv(ds, args.output)
    chronological(ds, args.output)
    if args.validate_dir:
        rep = validate(args.output, args.validate_dir)
        print("Özgün CSV eşleşmesi:", rep["all_numeric_matches_within_tolerance"], flush=True)
        if not rep["all_numeric_matches_within_tolerance"]:
            print("Ayrıntılar için spring_validation_report.json dosyasını kontrol ediniz.", flush=True)

if __name__ == "__main__":
    main()
