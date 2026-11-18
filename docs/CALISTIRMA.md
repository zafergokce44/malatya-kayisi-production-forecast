# Tez kaynak kodlarını çalıştırma

Bu klasörde **iki tarihsel/orijinal betik** (`tezfinal.py`, `analiz_v2.py`) ve **iki sonradan oluşturulmuş betik** (`nested_cv_reconstruction.py`, `ilkbahar_min_reconstruction.py`) bulunur. İkinci gruptakiler özgün betik olarak sunulmamalıdır. Sayısal doğrulama kayıtları ilgili `docs/` belgelerinde yer alır.

## Ortam

- Kayıtlı Aşama 2/3 ve ilkbahar doğrulama ortamı: Python **3.13.5**, NumPy **2.3.5**, pandas **2.2.3**, scikit-learn **1.8.0**, SciPy **1.17.0**, openpyxl **3.1.5** (matplotlib **3.10.8**).
- `python -m pip install -r requirements.txt`
- Orijinal betikler Google Colab'a özel `/content/` yolları kullanabilir; kaynak veriyi kendi yerel/özel ortamında edinip uygun yolları ayarlamalısın.

## Statik kontrol

```bash
python tools/verify_repository.py
```

Bu komut SHA-256, Python sözdizimi, notebook JSON yapısı ve yanlışlıkla eklenen Excel dosyaları açısından kontrol yapar. **Makine öğrenmesi modellerini eğitmez.**

## Orijinal kodlar

- `scripts/tezfinal.py`: Seed 42 ve önceki beş-seed rassal ayrımlar, gruplar ve gecikmeli değişken duyarlılığı.
- `scripts/analiz_v2.py`: 10×5 tekrarlı CV ve genişleyen pencere kronolojik doğrulama; çıktılar varsayılan olarak `/content/analiz_v2_ciktilari` altında oluşturulur.
- Bu iki betikteki `INPUT_FILE`, `FILE_PATH`, `SHEET_NAME` ve çıktı yollarını **özgün veri üzerinde** çalıştırmadan önce kontrol et. Kaynak çalışma sayfası: `Tam veri seti`. Kaynak Excel dosyalarının otomatik keşfedilmesi yanlış sürümü seçebilir.

## Yeniden oluşturulmuş Nested CV

```bash
python scripts/nested_cv_reconstruction.py --input "C:\\ozel_veri\\Veri_Seti_Son_duzeltilmis_v3_agac_farklari_eklendi.xlsx" --output-dir "C:\\ozel_sonuclar\\nested" --reference-outer "results/04_nested_cv_sonuclar/nested_outer_katlar.csv"
```

`--reference-outer` verilirse kaydedilmiş dış kat verileriyle eşleşme kontrol edilir. 30 dış katın tamamı için kapsamlı doğrulama henüz tamamlanmamıştır. Bkz. [`NESTED_CV_KOD_DOGRULAMA.md`](NESTED_CV_KOD_DOGRULAMA.md).

## Yeniden oluşturulmuş ilkbahar duyarlılığı

```bash
python scripts/ilkbahar_min_reconstruction.py --input "C:\\ozel_veri\\Veri_Seti_Son_duzeltilmis_v3_agac_farklari_eklendi.xlsx" --output "C:\\ozel_sonuclar\\ilkbahar" --validate-dir "results/05_ilkbahar_sonuclar"
```

Kayıtlı sekiz sonuç CSV'si ile eşleşme doğrulandı. Bkz. [`ILKBAHAR_MIN_KOD_DOGRULAMA.md`](ILKBAHAR_MIN_KOD_DOGRULAMA.md).

## Veri kaynağı ve dağıtım

Depoda MGM ham verileri veya kaynak Excel çalışma kitapları yer almaz; bu dosyalar yalnız yetkili yerel ortamda kullanılmalıdır. Kayıtlı sonuçların bazıları yıl/üretim/tahmin alanları içerir; açık paylaşım hakları ayrıca değerlendirilmelidir. [`DATA_AVAILABILITY.md`](../DATA_AVAILABILITY.md).
