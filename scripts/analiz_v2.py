# -*- coding: utf-8 -*-
"""
analiz_v2.py
Tez analizi - AŞAMA 1 + AŞAMA 2
AŞAMA 3 kullanıcı onayından sonra eklenecektir.

Colab/Jupyter/VS Code kullanımında yalnız INPUT_FILE ve OUTPUT_ROOT alanlarını düzenleyin.
"""

# ============================================================
# 0) KULLANICI AYARLARI
# ============================================================
INPUT_FILE = "/content/Veri_Seti_Son_duzeltilmis_v3_agac_farklari_eklendi.xlsx"
OUTPUT_ROOT = "/content/analiz_v2_ciktilari"
SHEET_NAME = "Tam veri seti"

# ============================================================
# 1) KÜTÜPHANELER
# ============================================================
import math
import platform
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.stats import t as student_t
import sklearn
from sklearn.model_selection import RepeatedKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.dummy import DummyRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

OUT_ROOT = Path(OUTPUT_ROOT)
OUT1 = OUT_ROOT / "asama1_sonuclari"
OUT2 = OUT_ROOT / "asama2_sonuclari"
OUT1.mkdir(parents=True, exist_ok=True)
OUT2.mkdir(parents=True, exist_ok=True)

print("Python:", platform.python_version())
print("pandas:", pd.__version__)
print("NumPy:", np.__version__)
print("Matplotlib:", matplotlib.__version__)
print("scikit-learn:", sklearn.__version__)

# ============================================================
# 2) DEĞİŞKEN TANIMLARI
# ============================================================
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
FULL = [TREE, LAG] + METEO
FORBIDDEN = [
    "AGAC_BASI_VERIM_KG_AGAC",
    "FELAKET_YILI_UZMAN",
    "FELAKET_YILI_KURAL",
    "FELAKET_NOTU",
]

# ============================================================
# 3) VERİYİ OKU VE KONTROL ET
# ============================================================
input_path = Path(INPUT_FILE)
if not input_path.exists():
    raise FileNotFoundError(
        f"Girdi dosyası bulunamadı: {INPUT_FILE}\n"
        "Scriptin başındaki INPUT_FILE satırını gerçek dosya yoluna göre değiştirin."
    )
try:
    df = pd.read_excel(input_path, sheet_name=SHEET_NAME)
except Exception:
    df = pd.read_excel(input_path)
df.columns = [str(c).strip() for c in df.columns]
df = df.sort_values(YEAR).reset_index(drop=True)
required = [YEAR, TARGET, TREE] + METEO
missing_cols = [c for c in required if c not in df.columns]
if missing_cols:
    raise ValueError(f"Eksik gerekli sütunlar: {missing_cols}")
for c in required:
    df[c] = pd.to_numeric(df[c], errors="coerce")
if df[required].isna().any().any():
    raise ValueError("Gerekli alanlarda eksik/sayısala çevrilemeyen değer var. Varsayım yapılmadan durduruldu.")
if TARGET in FULL or YEAR in FULL or any(c in FULL for c in FORBIDDEN):
    raise RuntimeError("Yasaklı/hedef/yıl alanı model özellik listesine girmiş.")

# ============================================================
# AŞAMA 1 - VERİ DENETİMİ
# ============================================================
audit = df[[YEAR, TARGET, TREE]].copy()
audit["Önceki_Kayıt_Yılı"] = audit[YEAR].shift(1)
audit["Yıl_Farkı"] = audit[YEAR] - audit["Önceki_Kayıt_Yılı"]
audit["Üretim_Değişim_%"] = audit[TARGET].pct_change(fill_method=None) * 100
audit["Ağaç_Sayısı_Değişim_%"] = audit[TREE].pct_change(fill_method=None) * 100
audit["Üretimde_>%50_Kırılma"] = np.where(audit["Üretim_Değişim_%"].abs() > 50, "EVET", "")
audit["Ağaç_Sayısında_>%50_Kırılma"] = np.where(audit["Ağaç_Sayısı_Değişim_%"].abs() > 50, "EVET", "")
audit["kaynak"] = ""
audit["coğrafi düzey (Malatya / Türkiye / belirsiz)"] = ""
audit.to_csv(OUT1 / "veri_denetimi.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
audit[(audit["Üretimde_>%50_Kırılma"] == "EVET") | (audit["Ağaç_Sayısında_>%50_Kırılma"] == "EVET")].to_csv(
    OUT1 / "ani_kirilmalar.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig"
)

# TAM 57 gözlem
TAM = df[[YEAR, TARGET, TREE] + METEO].copy()
TAM[LAG] = TAM[TREE].shift(1)
TAM = TAM.dropna(subset=[LAG]).reset_index(drop=True)
TAM = TAM[[YEAR, TARGET, TREE, LAG] + METEO]

# MALATYA: 1982-2024 kesintisiz dönem, gerçek t-1 lag -> 1983-2024
expected = set(range(1982, 2025))
missing_years = sorted(expected - set(df[YEAR].astype(int)))
if missing_years:
    raise ValueError(f"1982–2024 dönemi kesintisiz değil. Eksik yıllar: {missing_years}")
mb = df[(df[YEAR] >= 1982) & (df[YEAR] <= 2024)][[YEAR, TARGET, TREE] + METEO].copy()
mb[LAG] = mb[TREE].shift(1)
MALATYA = mb.dropna(subset=[LAG]).reset_index(drop=True)
MALATYA = MALATYA[[YEAR, TARGET, TREE, LAG] + METEO]
if len(TAM) != 57 or len(MALATYA) != 42 or int(MALATYA[YEAR].min()) != 1983:
    raise ValueError("Beklenen TAM=57 veya MALATYA=42 veri yapısı oluşmadı.")
TAM.to_csv(OUT1 / "model_seti_TAM.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
MALATYA.to_csv(OUT1 / "model_seti_MALATYA.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")

def descriptive(data):
    rows = []
    for c in [TARGET] + FULL:
        s = data[c].astype(float)
        rows.append({"Değişken": c, "N": s.count(), "Ortalama": s.mean(), "Standart_Sapma": s.std(ddof=1),
                     "Minimum": s.min(), "Q1": s.quantile(.25), "Medyan": s.median(), "Q3": s.quantile(.75), "Maksimum": s.max()})
    return pd.DataFrame(rows)
descriptive(TAM).to_csv(OUT1 / "tanimlayici_TAM.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
descriptive(MALATYA).to_csv(OUT1 / "tanimlayici_MALATYA.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")

def detrend(s, years):
    y = np.asarray(s, float); x = np.asarray(years, float)
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta

def corr_outputs(data, label):
    cols = [TARGET] + FULL
    raw = data[cols].corr(method="pearson")
    det = pd.DataFrame({c: detrend(data[c], data[YEAR]) for c in cols}).corr(method="pearson")
    raw.to_csv(OUT1 / f"korelasyon_matrisi_ham_{label}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    det.to_csv(OUT1 / f"korelasyon_matrisi_detrend_{label}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    t = pd.DataFrame([{"Değişken": c, "Ham_Pearson_r": raw.loc[TARGET,c],
                       "Doğrusal_Eğilimden_Arındırılmış_r": det.loc[TARGET,c],
                       "Fark_(Detrend-Ham)": det.loc[TARGET,c]-raw.loc[TARGET,c]} for c in FULL])
    t.to_csv(OUT1 / f"korelasyon_hedef_{label}.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")

corr_outputs(TAM, "TAM")
corr_outputs(MALATYA, "MALATYA")

def tr_axis(x, pos=None):
    s = f"{x:,.1f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def production_plot(data, label):
    fig, ax = plt.subplots(figsize=(11,6)); ax.plot(data[YEAR], data[TARGET], marker="o", markersize=3.5, linewidth=1.4)
    ax.set_xlabel("Yıl"); ax.set_ylabel("Toplam yaş kayısı üretimi (ton)")
    ax.set_title(f"{label} veri setinde toplam yaş kayısı üretiminin yıllara göre değişimi")
    ax.yaxis.set_major_formatter(FuncFormatter(tr_axis)); ax.grid(alpha=.25); fig.tight_layout()
    fig.savefig(OUT1 / f"uretim_{label}.png", dpi=200, bbox_inches="tight"); plt.close(fig)
production_plot(TAM, "TAM"); production_plot(MALATYA, "MALATYA")

# ============================================================
# AŞAMA 2 - 10x5 TEKRARLI K-KATLI ÇAPRAZ DOĞRULAMA
# ============================================================

def build_model(name):
    if name == "Extra Trees":
        return Pipeline([("imputer", SimpleImputer(strategy="median")),
                         ("model", ExtraTreesRegressor(n_estimators=500, max_depth=6, random_state=42, n_jobs=-1))])
    if name == "Random Forest":
        return Pipeline([("imputer", SimpleImputer(strategy="median")),
                         ("model", RandomForestRegressor(n_estimators=300, max_depth=5, random_state=42, n_jobs=-1))])
    if name == "Doğrusal SVR":
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler()),
                         ("model", SVR(kernel="linear", C=5000, epsilon=0.5))])
    if name == "Eğitim Ortalaması":
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", DummyRegressor(strategy="mean"))])
    if name in ["OLS - Ağaç Sayısı", "Doğrusal Trend"]:
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", LinearRegression())])
    raise ValueError(name)

def metrics(y, pred):
    return {"R2": r2_score(y,pred), "RMSE": np.sqrt(mean_squared_error(y,pred)), "MAE": mean_absolute_error(y,pred)}

def ci95(values):
    a = np.asarray(values, float); n = len(a); m = a.mean(); sd = a.std(ddof=1)
    h = student_t.ppf(.975, n-1) * sd / math.sqrt(n)
    return float(m), float(sd), float(m-h), float(m+h)

def eval_combo(dset_name, data, experiment, setting, model_name, cols, splits):
    X = data[cols].reset_index(drop=True); y = data[TARGET].reset_index(drop=True)
    fold_rows=[]; by_repeat={r:{"y":[],"p":[]} for r in range(1,11)}
    for si,(tr,te) in enumerate(splits):
        repeat=si//5+1; fold=si%5+1
        model=build_model(model_name); model.fit(X.iloc[tr], y.iloc[tr])
        p_train=model.predict(X.iloc[tr]); p_test=model.predict(X.iloc[te])
        mt=metrics(y.iloc[tr],p_train); ms=metrics(y.iloc[te],p_test)
        fold_rows.append({"deney":experiment,"veri_seti":dset_name,"ayar":setting,"model":model_name,"tekrar":repeat,"kat":fold,
                          "n_egitim":len(tr),"n_test":len(te),"train_R2":mt["R2"],"train_RMSE":mt["RMSE"],"train_MAE":mt["MAE"],
                          "test_R2":ms["R2"],"test_RMSE":ms["RMSE"],"test_MAE":ms["MAE"],
                          "R2_farki_train_minus_test":mt["R2"]-ms["R2"],
                          "RMSE_farki_test_minus_train":ms["RMSE"]-mt["RMSE"],
                          "MAE_farki_test_minus_train":ms["MAE"]-mt["MAE"]})
        by_repeat[repeat]["y"].extend(y.iloc[te].tolist()); by_repeat[repeat]["p"].extend(np.asarray(p_test).tolist())
    oof_rows=[]
    for repeat in range(1,11):
        mm=metrics(by_repeat[repeat]["y"], by_repeat[repeat]["p"])
        oof_rows.append({"deney":experiment,"veri_seti":dset_name,"ayar":setting,"model":model_name,"tekrar":repeat,
                         "oof_R2":mm["R2"],"oof_RMSE":mm["RMSE"],"oof_MAE":mm["MAE"]})
    return fold_rows, oof_rows

fold_all=[]; oof_all=[]
MAIN=["Extra Trees","Random Forest","Doğrusal SVR"]
for dset_name,data in [("TAM",TAM),("MALATYA",MALATYA)]:
    splits=list(RepeatedKFold(n_splits=5,n_repeats=10,random_state=42).split(np.arange(len(data))))
    # Ana karşılaştırma
    for m in MAIN:
        a,b=eval_combo(dset_name,data,"Ana model karşılaştırması","Birleşik / kıyas",m,FULL,splits); fold_all += a; oof_all += b
    for m,cols in [("Eğitim Ortalaması",FULL),("OLS - Ağaç Sayısı",[TREE]),("Doğrusal Trend",[YEAR])]:
        a,b=eval_combo(dset_name,data,"Ana model karşılaştırması","Birleşik / kıyas",m,cols,splits); fold_all += a; oof_all += b
    # Değişken grupları
    for setting,cols in [("Kapasite",[TREE,LAG]),("Meteoroloji",METEO),("Birleşik",FULL)]:
        for m in MAIN:
            a,b=eval_combo(dset_name,data,"Değişken grubu",setting,m,cols,splits); fold_all += a; oof_all += b
    # L1
    for setting,cols in [("L1 Var",FULL),("L1 Yok",[TREE]+METEO)]:
        for m in MAIN:
            a,b=eval_combo(dset_name,data,"L1 duyarlılığı",setting,m,cols,splits); fold_all += a; oof_all += b

fold_df=pd.DataFrame(fold_all); oof_df=pd.DataFrame(oof_all)
summary_rows=[]
for (experiment,dset,setting,model),g in fold_df.groupby(["deney","veri_seti","ayar","model"],sort=False):
    o=oof_df[(oof_df.deney==experiment)&(oof_df.veri_seti==dset)&(oof_df.ayar==setting)&(oof_df.model==model)]
    r={"deney":experiment,"veri_seti":dset,"ayar":setting,"model":model,"kat_sayisi":len(g),"tekrar_sayisi":len(o)}
    for c in ["train_R2","train_RMSE","train_MAE","test_R2","test_RMSE","test_MAE","R2_farki_train_minus_test","RMSE_farki_test_minus_train","MAE_farki_test_minus_train"]:
        m,sd,lo,hi=ci95(g[c]); r[c+"_ortalama"]=m; r[c+"_ss"]=sd; r[c+"_GA95_alt"]=lo; r[c+"_GA95_ust"]=hi
    for c in ["oof_R2","oof_RMSE","oof_MAE"]:
        m,sd,lo,hi=ci95(o[c]); r[c+"_ortalama"]=m; r[c+"_ss"]=sd; r[c+"_GA95_alt"]=lo; r[c+"_GA95_ust"]=hi
    summary_rows.append(r)
summary_df=pd.DataFrame(summary_rows)
fold_df.to_csv(OUT2 / "cv_katlar.csv",sep=";",decimal=",",index=False,encoding="utf-8-sig")
oof_df.to_csv(OUT2 / "cv_oof_tekrar.csv",sep=";",decimal=",",index=False,encoding="utf-8-sig")
summary_df.to_csv(OUT2 / "cv_sonuclari.csv",sep=";",decimal=",",index=False,encoding="utf-8-sig")
summary_df[summary_df.deney=="Ana model karşılaştırması"].to_csv(OUT2 / "cv_ana_model_sonuclari.csv",sep=";",decimal=",",index=False,encoding="utf-8-sig")
summary_df[summary_df.deney=="Değişken grubu"].to_csv(OUT2 / "cv_degiskengruplari_sonuclari.csv",sep=";",decimal=",",index=False,encoding="utf-8-sig")
summary_df[summary_df.deney=="L1 duyarlılığı"].to_csv(OUT2 / "cv_l1_sonuclari.csv",sep=";",decimal=",",index=False,encoding="utf-8-sig")

# RMSE kutu grafikleri
for dset in ["TAM","MALATYA"]:
    g=fold_df[(fold_df.deney=="Ana model karşılaştırması")&(fold_df.veri_seti==dset)]
    order=["Extra Trees","Random Forest","Doğrusal SVR","Eğitim Ortalaması","OLS - Ağaç Sayısı","Doğrusal Trend"]
    fig,ax=plt.subplots(figsize=(12,6)); ax.boxplot([g[g.model==m].test_RMSE.to_numpy() for m in order],tick_labels=order,showmeans=True)
    ax.set_xlabel("Model"); ax.set_ylabel("Test RMSE (ton)"); ax.set_title(f"{dset} veri setinde test RMSE dağılımı (10×5 RepeatedKFold)")
    ax.yaxis.set_major_formatter(FuncFormatter(tr_axis)); ax.tick_params(axis="x",rotation=20); ax.grid(axis="y",alpha=.25); fig.tight_layout()
    fig.savefig(OUT2 / f"cv_rmse_kutu_{dset}.png",dpi=200,bbox_inches="tight"); plt.close(fig)

with open(OUT_ROOT / "surumler.txt","w",encoding="utf-8") as f:
    f.write(f"Python: {platform.python_version()}\npandas: {pd.__version__}\nNumPy: {np.__version__}\nMatplotlib: {matplotlib.__version__}\nscikit-learn: {sklearn.__version__}\n")

print("AŞAMA 1 ve AŞAMA 2 tamamlandı.")
print("TAM:", len(TAM), "gözlem | MALATYA:", len(MALATYA), "gözlem")
print("AŞAMA 1 ve AŞAMA 2 tamamlandı. AŞAMA 3 başlatılıyor.")

# ============================================================
# AŞAMA 3 - ZAMANA GÖRE (KRONOLOJİK) DOĞRULAMA
# ============================================================

OUT3 = OUT_ROOT / "asama3_sonuclari"
OUT3.mkdir(parents=True, exist_ok=True)

# 1982-2024 kesintisiz taban veri
chrono_base = df[(df[YEAR] >= 1982) & (df[YEAR] <= 2024)][
    [YEAR, TARGET, TREE] + METEO
].copy()

expected_years = list(range(1982, 2025))
if chrono_base[YEAR].astype(int).tolist() != expected_years:
    missing = sorted(set(expected_years) - set(chrono_base[YEAR].astype(int)))
    raise ValueError(f"1982–2024 dönemi kesintisiz değil. Eksik yıllar: {missing}")

# Ana MALATYA seti (1983-2024): gerçek yıllık ağaç gecikmesi
chrono_main = chrono_base.copy()
chrono_main[LAG] = chrono_main[TREE].shift(1)
chrono_main = chrono_main.dropna(subset=[LAG]).reset_index(drop=True)

# Yalnız t-1 değişkenleri duyarlılık seti
lagged_predictors = []
chrono_lag = chrono_base.copy()
for c in [TREE] + METEO:
    new_c = f"{c}__L1"
    chrono_lag[new_c] = chrono_lag[c].shift(1)
    lagged_predictors.append(new_c)
chrono_lag = chrono_lag.dropna(subset=lagged_predictors).reset_index(drop=True)

if len(chrono_main) != 42 or len(chrono_lag) != 42:
    raise ValueError("Kronolojik setler beklenen 42 gözlem yapısında değil.")

def chrono_mape(y_true, y_pred):
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    if np.any(y_true == 0):
        raise ValueError("MAPE için sıfır gerçek değer bulundu.")
    return float(np.mean(np.abs((y_true-y_pred)/y_true))*100.0)

forecast_years = list(range(2003, 2025))
chrono_rows = []

for test_year in forecast_years:
    train = chrono_main[chrono_main[YEAR] < test_year].copy()
    test = chrono_main[chrono_main[YEAR] == test_year].copy()

    if len(test) != 1 or int(train[YEAR].max()) != test_year - 1:
        raise ValueError(f"{test_year} kronolojik penceresinde hata.")

    y_train = train[TARGET]
    y_true = float(test[TARGET].iloc[0])

    row = {
        "YIL": test_year,
        "Gercek_Ton": y_true,
        "Egitim_Ilk_Yil": int(train[YEAR].min()),
        "Egitim_Son_Yil": int(train[YEAR].max()),
        "Egitim_Gozlem_Sayisi": len(train),
    }

    for m in ["Extra Trees", "Random Forest", "Doğrusal SVR"]:
        model = build_model(m)
        model.fit(train[FULL], y_train)
        col = {
            "Extra Trees": "Tahmin_Extra_Trees",
            "Random Forest": "Tahmin_Random_Forest",
            "Doğrusal SVR": "Tahmin_Dogrusal_SVR",
        }[m]
        row[col] = float(model.predict(test[FULL])[0])

    prev = chrono_main.loc[chrono_main[YEAR] == test_year-1, TARGET]
    if len(prev) != 1:
        raise ValueError(f"{test_year} naif t-1 üretim değeri yok.")
    row["Tahmin_Naif_t_1_Uretim"] = float(prev.iloc[0])

    trend = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", LinearRegression())
    ])
    trend.fit(train[[YEAR]], y_train)
    row["Tahmin_Dogrusal_Trend"] = float(
        trend.predict(pd.DataFrame({YEAR:[test_year]}))[0]
    )

    ols = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", LinearRegression())
    ])
    ols.fit(train[[TREE]], y_train)
    row["Tahmin_OLS_Cari_Agac"] = float(ols.predict(test[[TREE]])[0])

    train_lag = chrono_lag[chrono_lag[YEAR] < test_year].copy()
    test_lag = chrono_lag[chrono_lag[YEAR] == test_year].copy()

    for m in ["Extra Trees", "Random Forest", "Doğrusal SVR"]:
        model = build_model(m)
        model.fit(train_lag[lagged_predictors], train_lag[TARGET])
        col = {
            "Extra Trees": "Tahmin_LagOnly_Extra_Trees",
            "Random Forest": "Tahmin_LagOnly_Random_Forest",
            "Doğrusal SVR": "Tahmin_LagOnly_Dogrusal_SVR",
        }[m]
        row[col] = float(model.predict(test_lag[lagged_predictors])[0])

    chrono_rows.append(row)

chrono_pred = pd.DataFrame(chrono_rows)

if len(chrono_pred) != 22:
    raise ValueError(f"Beklenen 22 tahmin yerine {len(chrono_pred)} üretildi.")

y_chrono = chrono_pred["Gercek_Ton"].to_numpy(float)
naive_chrono = chrono_pred["Tahmin_Naif_t_1_Uretim"].to_numpy(float)
naive_rmse = float(np.sqrt(mean_squared_error(y_chrono, naive_chrono)))

def chrono_metric_row(scenario, model, pred_col):
    pred = chrono_pred[pred_col].to_numpy(float)
    rmse = float(np.sqrt(mean_squared_error(y_chrono, pred)))
    return {
        "Senaryo": scenario,
        "Model": model,
        "Tahmin_Sayisi": len(y_chrono),
        "Tahmin_Baslangic_Yili": int(chrono_pred[YEAR].min()),
        "Tahmin_Bitis_Yili": int(chrono_pred[YEAR].max()),
        "RMSE_Ton": rmse,
        "MAE_Ton": float(mean_absolute_error(y_chrono, pred)),
        "MAPE_Yuzde": chrono_mape(y_chrono, pred),
        "R2": float(r2_score(y_chrono, pred)),
        "Naife_Gore_Beceri_Skoru": float(1-rmse/naive_rmse),
    }

chrono_result_rows = []
for model,col in [
    ("Extra Trees","Tahmin_Extra_Trees"),
    ("Random Forest","Tahmin_Random_Forest"),
    ("Doğrusal SVR","Tahmin_Dogrusal_SVR"),
    ("Naif t-1 üretim","Tahmin_Naif_t_1_Uretim"),
    ("Doğrusal Trend","Tahmin_Dogrusal_Trend"),
    ("OLS - Cari Ağaç Sayısı","Tahmin_OLS_Cari_Agac"),
]:
    chrono_result_rows.append(
        chrono_metric_row("Ana kronolojik doğrulama",model,col)
    )

for model,col in [
    ("Lag-only Extra Trees","Tahmin_LagOnly_Extra_Trees"),
    ("Lag-only Random Forest","Tahmin_LagOnly_Random_Forest"),
    ("Lag-only Doğrusal SVR","Tahmin_LagOnly_Dogrusal_SVR"),
]:
    chrono_result_rows.append(
        chrono_metric_row("Yalnız t-1 değişkenleri duyarlılığı",model,col)
    )

chrono_results = pd.DataFrame(chrono_result_rows)

chrono_pred.to_csv(
    OUT3/"kronolojik_tahminler.csv",
    sep=";",decimal=",",index=False,encoding="utf-8-sig"
)
chrono_results.to_csv(
    OUT3/"kronolojik_sonuclar.csv",
    sep=";",decimal=",",index=False,encoding="utf-8-sig"
)

timing_note = """Ana kronolojik model cari yıl ağaç sayısı ile cari Haziran-Temmuz
meteorolojik göstergelerini kullanmaktadır. Veri dosyasında cari yıl ağaç
sayısının ölçüm/yayın tarihi bulunmadığından bu girdinin hasat öncesinde
kesin olarak bilindiği varsayılmamıştır. Haziran-Temmuz meteorolojisi ilgili
aylar tamamlanmadan tam olarak bilinemeyeceği için ana senaryo sezon öncesi
tahmin olarak yorumlanmamalıdır. Bu nedenle ayrıca yalnız t-1 yılındaki ağaç
sayısı ve meteorolojik değişkenleri kullanan duyarlılık senaryosu raporlanmıştır.
"""
(OUT3/"tahmin_zamanlamasi.txt").write_text(timing_note,encoding="utf-8")

fig,ax=plt.subplots(figsize=(13,7))
ax.plot(chrono_pred[YEAR],chrono_pred["Gercek_Ton"],marker="o",linewidth=2.2,label="Gerçek")
ax.plot(chrono_pred[YEAR],chrono_pred["Tahmin_Extra_Trees"],linewidth=1.2,label="Extra Trees")
ax.plot(chrono_pred[YEAR],chrono_pred["Tahmin_Random_Forest"],linewidth=1.2,label="Random Forest")
ax.plot(chrono_pred[YEAR],chrono_pred["Tahmin_Dogrusal_SVR"],linewidth=1.2,label="Doğrusal SVR")
ax.plot(chrono_pred[YEAR],chrono_pred["Tahmin_Naif_t_1_Uretim"],linestyle="--",linewidth=1.2,label="Naif t-1")
ax.plot(chrono_pred[YEAR],chrono_pred["Tahmin_Dogrusal_Trend"],linestyle="--",linewidth=1.2,label="Doğrusal trend")
ax.plot(chrono_pred[YEAR],chrono_pred["Tahmin_OLS_Cari_Agac"],linestyle="--",linewidth=1.2,label="OLS - cari ağaç")
ax.set_xlabel("Tahmin yılı")
ax.set_ylabel("Toplam yaş kayısı üretimi (ton)")
ax.set_title("2003–2024 genişleyen pencere doğrulamasında gerçek ve tahmin edilen üretim")
ax.yaxis.set_major_formatter(FuncFormatter(tr_axis))
ax.set_xticks(chrono_pred[YEAR]); ax.tick_params(axis="x",rotation=45)
ax.grid(alpha=.25); ax.legend(ncol=2); fig.tight_layout()
fig.savefig(OUT3/"kronolojik_tahmin_grafigi.png",dpi=200,bbox_inches="tight")
plt.close(fig)

print("AŞAMA 3 tamamlandı:", OUT3)

