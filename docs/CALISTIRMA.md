# Çalıştırma yönergeleri — orijinal kodun beklediği ortam

**Not:** Bu talimatlar, mevcut kaynak betiklerin kullandığı dosya yollarına göre yazılmıştır. Kodlar arşiv oluşturulurken veri üzerinde çalıştırılmamıştır. Analiz sonuçlarını doğrulanmış yeniden üretim sonucu olarak raporlamayın.

## 1. Önerilen ortam

- Python **3.13** (kayıtlı Aşama 2–3 çalıştırmaları Python 3.13.5).
- `pip install -r requirements.txt`
- Google Colab'da: depoyu ZIP olarak yükleyip açabilir veya GitHub'dan klonlayabilirsiniz.

## 2. Veri erişimi

1. Yasal olarak kullanma hakkınız bulunan Excel veri dosyasını kendi özel Colab ortamınıza yükleyin.
2. `scripts/tezfinal.py` ve `scripts/analiz_v2.py` dosyalarında yer alan `INPUT_FILE`, `FILE_PATH`, `SHEET_NAME` ve çıktı yollarını kontrol edin.
3. Orijinal Aşama 1–3 betiği Colab'da şu girdi yolunu kullanıyor:

   `/content/Veri_Seti_Son_duzeltilmis_v3_agac_farklari_eklendi.xlsx`

4. Her iki betik varsayılan olarak **`Tam veri seti`** çalışma sayfasını bekler. `tezfinal.py`, sayfa adı bulunmazsa ilk sayfayı okumaya çalışır; **bu, yanlış veriyle analiz yapma riski doğurur**. Doğru sayfayı çalıştırmadan önce manuel kontrol edin.

## 3. Referans analiz

Colab'da, dosyalar `repo` dizinindeyse:

```bash
python repo/scripts/tezfinal.py
```

Betik sonuçları `/content/` altına yazacak şekilde özgün hâlinde korunmuştur. Seed 42 ve diğer seed sonuçları, kullanılan veri seti sürümüyle birlikte doğrulanmalıdır. Rassal veri ayrımı kronolojik tahmin değildir.

## 4. Tekrarlı CV ve kronolojik doğrulama

```bash
python repo/scripts/analiz_v2.py
```

Bu betik Aşama 1 (veri denetimi), Aşama 2 (10 tekrarlı 5-katlı CV) ve Aşama 3 (genişleyen pencere 2003–2024 kronolojik test) kodlarını birlikte içerir. Çıktıların varsayılan kök yolu `/content/analiz_v2_ciktilari` şeklindedir.

## 5. Nested CV ve ilkbahar duyarlılığı

Bu iki deneyin **kayıtlı çıktı dosyaları** `results/` altında mevcuttur. Ancak bunlara karşılık gelen, kesin sürümü doğrulanmış *çalıştırılabilir betikler* henüz bu pakete dahil edilmemiştir. Kodu bulup deney sonuçlarıyla eşleştirene kadar bu aşamaların bağımsız yeniden çalıştırılabildiği iddia edilmemelidir.

## 6. Dosya bütünlüğü

```bash
python tools/verify_repository.py
```

Bu komut dosyaların SHA-256 karmalarını ve Python sözdizimini kontrol eder. Model metriklerini **yeniden hesaplamaz**.
