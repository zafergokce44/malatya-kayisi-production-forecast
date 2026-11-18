# Nested CV — kaynak kod yeniden oluşturma kaydı (18 Kasım 2026)

## Durum: Yeniden oluşturulmuş betik; özgün kaynak betiği değildir

`scripts/nested_cv_reconstruction.py`, özgün `.py` dosyası arşivde bulunamadığından korunmuş **deney yöntem notu**, **arama uzayı**, **dış kat tahminleri** ve `analiz_v2.py` içindeki veri hazırlama yönteminden hareketle yeniden oluşturuldu. Özgün çalışmanın bütün sayısal sonuçları doğrulanıncaya kadar tam yeniden üretilebilirlik iddia edilmemelidir.

### Doğrulanabilen deney tasarımı

- Veri yapıları: 57 gözlemli **TAM** ve 42 gözlemli **MALATYA**; model girdileri yalnız sekiz nihai açıklayıcı değişken.
- Dış katlar: `KFold(n_splits=5, shuffle=True, random_state=42)`.
- İç katlar: `KFold(n_splits=3, shuffle=True, random_state=42)`.
- Hiperparametre seçimi: `GridSearchCV(scoring="neg_root_mean_squared_error")`, eğitim verisinde; dış test katı arama dışında.
- Extra Trees: `n_estimators` 300/500, `max_depth` 6/None, `min_samples_leaf` 1/2.
- Random Forest: `n_estimators` 200/300, `max_depth` 5/None, `min_samples_leaf` 1/2.
- Doğrusal SVR: `C` 1000/5000/10000, `epsilon` 0.5/5000/10000, `kernel="linear"`; yalnız SVR için `StandardScaler`.
- Ön işleme, her doğrulama katının eğitim bölümünde öğrenilecek şekilde `Pipeline` içindedir.
- Fixed karşılaştırmaları: referans hiperparametreli modeller aynı dış eğitim/test katlarında eğitilir ve test edilir.

## Yerel çalıştırma — kamuya açık veriyi arşive eklemeyin

Depo kök dizininde:

```powershell
python -m pip install -r requirements.txt
python scripts/nested_cv_reconstruction.py --input "C:\\ozel_veri\\Veri_Seti_Son_duzeltilmis_v3_agac_farklari_eklendi.xlsx" --output-dir "C:\\ozel_sonuclar\\nested" --reference-outer "results/04_nested_cv_sonuclar/nested_outer_katlar.csv"
```

Kısa bir doğrulama, yalnız SVR ve dış katlar 1–2 için:

```powershell
python scripts/nested_cv_reconstruction.py --input "C:\\ozel_veri\\Veri_Seti_Son_duzeltilmis_v3_agac_farklari_eklendi.xlsx" --output-dir "C:\\ozel_sonuclar\\nested_kisa" --reference-outer "results/04_nested_cv_sonuclar/nested_outer_katlar.csv" --datasets TAM --models "Doğrusal SVR" --folds 1 2
```

- Çıktı dizini **GitHub deposu dışında** tutulmalı; tahminlerin veya ham verilerin paylaşım koşulları bağımsız değerlendirilmelidir.
- Kaynak karşılaştırma dosyası her 5 dış katı ve her üç modelin test tahminlerini içerir; `--reference-outer` verildiğinde test indeksleri, seçilen parametreler ve tahminler karşılaştırılır. Kısa çalıştırmada `coverage=selected_subset` doğaldır.
- Tüm 30 dış katın çalıştırılması model aramalarından dolayı uzun sürebilir; betik işlemin tamamlanmasını bekler, kesintiye karşı otomatik devam etme özelliği yoktur.
- Çıktı dosyası `nested_outer_katlar_yeniden_uretim.csv` olarak adlandırılır; özgün kayıtlı CSV'leri değiştirmez.

## Mevcut bağımsız kontrollerin durumu

| Kontrol | Sonuç |
|---|---|
| MALATYA / Extra Trees / dış kat 1: test indeksleri, seçilen parametreler, fixed+tuned tahminleri | **Eşleşti**; maksimum fark yaklaşık `5.9e-11` |
| TAM / Doğrusal SVR / dış kat 1 ve 2: bütün kaydedilmiş metrik, indeks, parametre ve tahmin alanları | **Eşleşti**; maksimum fark `1.46e-11` |
| TAM ve MALATYA / Random Forest / dış kat 1: fixed tahminler | **Eşleşti**; maksimum fark `5.9e-11` |
| Bütün veri setleri, modeller ve 5 dış kat (toplam 30 deney satırı) | **Henüz tam doğrulanmadı** |

İlk tam çalışma denemesi hesaplama süresi sınırına takıldı. Bu yüzden yalnızca üstte açıkça tanımlanan kontroller doğrulanmış sayılmalıdır. `nested_cv_ozet.csv` dosyasındaki bütün ortalama ve güven aralığı özetleri bu aşamada ayrıca yeniden hesaplanıp karşılaştırılmamıştır.

## Kaynak dosyalar

- `results/04_nested_cv_sonuclar/nested_yontem_notu.txt`
- `results/04_nested_cv_sonuclar/nested_arama_uzayi.csv`
- `results/04_nested_cv_sonuclar/nested_outer_katlar.csv`
- `results/04_nested_cv_sonuclar/nested_cv_ozet.csv`
- `scripts/analiz_v2.py`

ÖNEMLİ: Bu kodun MIT lisansı altında yayımlanması, kaynağı dış kurumlardan alınan verilerin yeniden dağıtım haklarını vermez.
