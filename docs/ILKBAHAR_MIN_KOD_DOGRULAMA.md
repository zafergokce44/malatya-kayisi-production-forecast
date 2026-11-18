# İlkbahar minimum sıcaklık duyarlılık analizi — kod ve doğrulama kaydı

**İlgili tez sürümü:** `Zafer Gökçe Tez - Düzeltilmiş Sürüm (v3)(2).docx`  
**İlgili bölümler:** 2.8.4 (yöntem), 3.8.5 (bulgular), Tablo 12 ve Ek 2 (referans parametreleri).

## Deneyin tanımı

Araştırmanın 8 açıklayıcı değişkenli temel yapısına Şubat, Mart ve Nisan ayı **minimum sıcaklık ortalamaları** eklenerek 11 değişkenli alternatif yapı sınanır. Hedef, `TOPLAM ÜRETİM(YAŞ KAYISI/TON)` sütunudur.

- **TAM:** 1934–2024 dönemindeki mevcut kayıtlardan türetilen **57 modelleme gözlemi**; `AGAC_SAYISI_L1` önceki *mevcut* kronolojik kayıttır.
- **MALATYA:** 1982'deki gözlemin yalnız L1 değişkeni için kullanılmasıyla elde edilen **1983–2024 / 42 gözlem**; L1 gerçek bir yıllık gecikmedir.
- **Çapraz doğrulama:** `RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)`; aynı veri setindeki iki özellik kümesi için aynı 50 eğitim-test katı.
- **Kronolojik doğrulama:** İlk eğitim penceresi 1983–2002; 2003–2024 yıllarında **22 tek-adım-ileri tahmin**.
- **Model parametreleri:** Extra Trees `n_estimators=500`, `max_depth=6`, `random_state=42`; Random Forest `n_estimators=300`, `max_depth=5`, `random_state=42`; doğrusal SVR `kernel=linear`, `C=5000`, `epsilon=0.5`, eğitim katı içinde `StandardScaler`.
- **Metrikler:** Eğitim/test R²; test RMSE ve MAE; tekrarlara göre OOF R²; aynı katlardaki eşleştirilmiş farklar; kronolojik R²/RMSE/MAE/MAPE.

## Kaynak dosya ve yeniden oluşturma yaklaşımı

`scripts/ilkbahar_min_reconstruction.py`, tezde belgelenen yöntem, `scripts/analiz_v2.py` içindeki referans modeller ve `results/05_ilkbahar_sonuclar/` altındaki kayıtlı deney çıktıları kullanılarak **sonradan yeniden oluşturulmuştur**. Korunmuş özgün betiğin birebir kopyası olduğu iddia edilmez.

Excel kaynağı GitHub paketine eklenmez; kullanıcı tarafından yerel çalışma ortamına ayrıca sağlanır. Gerekli özgün Excel sayfası: `Tam veri seti`.

```bash
python scripts/ilkbahar_min_reconstruction.py --input "Veri_Seti_Son_duzeltilmis_v3_agac_farklari_eklendi.xlsx" --output "ilkbahar_yeniden_hesaplama" --validate-dir "results/05_ilkbahar_sonuclar"
```

`--validate-dir` isteğe bağlıdır. Kaynak CSV dosyaları aynı klasörde tutulduğunda özgün ve yeni sonuçları karşılaştıran `spring_validation_report.json` üretilir. Yalnız kodu çalıştırmak için `--input` ve `--output` yeterlidir.

## Tam sayısal doğrulama sonucu

**Sekiz CSV çıktı dosyasının sekizi de eşleşti.** Kullanılan tolerans mutlak **1×10⁻⁵**; en büyük mutlak sayısal fark yaklaşık **3,12×10⁻⁶**. Bu fark, test hata değerlerinin tezdeki iki ondalıklı gösterimini değiştirmez. İnceleme, 300 katlık ilkbahar CV, 60 OOF kaydı, 12 satırlık 8/11 karşılaştırması, 6 eşleştirilmiş kat özeti, 22 yıllık kronolojik tahmin ve kronolojik performans özetlerini kapsar.

| Veri seti | Model | Temel 8 RMSE (ton) | İlkbahar 11 RMSE (ton) |
|---|---|---:|---:|
| TAM | Extra Trees | 115.822,86 | 115.720,72 |
| TAM | Random Forest | 118.348,14 | 117.768,15 |
| TAM | Doğrusal SVR | 101.449,76 | 102.759,62 |
| MALATYA | Extra Trees | 133.890,25 | 134.906,66 |
| MALATYA | Random Forest | 135.426,57 | 136.151,59 |
| MALATYA | Doğrusal SVR | 116.779,34 | 118.805,20 |

Değerler tezdeki **Tablo 12** ile eşleşir; tezin sonuçlarında değişiklik yapılmamıştır.

**Doğrulama ortamı:** Python 3.13.5; NumPy 2.3.5; pandas 2.2.3; scikit-learn 1.8.0; SciPy 1.17.0; openpyxl 3.1.5.

**Makine tarafından okunabilir eşleşme kaydı:** `docs/ILKBAHAR_MIN_DOGRULAMA_DURUMU.json`.
