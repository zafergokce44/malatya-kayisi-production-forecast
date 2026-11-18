# Malatya Yaş Kayısı Üretim Tahmini — Tez Analiz Kodları

**Araştırmacı:** Zafer Gökçe  
**Tez:** *İklim Değişikliğinin Malatya Kayısı Üretimi Üzerindeki Etkisinin Yapay Zekâ Modelleri ile Tahmini*  
**Kurum:** Bayburt Üniversitesi, Lisansüstü Eğitim Enstitüsü, Endüstri Mühendisliği Ana Bilim Dalı (2026)  
**Arşiv durumu:** **0.4.0 geliştirme/ön yayın sürümü**. Zenodo DOI'si henüz alınmadı.  
**Depo:** https://github.com/zafergokce44/malatya-kayisi-production-forecast

## Araştırmanın çerçevesi

Tarımsal kapasite ve meteorolojik göstergelerle Malatya yaş kayısı üretiminin tahmini için Extra Trees, Random Forest ve doğrusal çekirdekli SVR kullanılmıştır. Modellemeye ait iki veri yapısı vardır: mevcut 1934–2024 kayıtlarından gecikme sonrasında oluşturulan **TAM (57 gözlem)** ve 1983–2024 dönemine ait kesintisiz **MALATYA (42 gözlem)** alt örneklemi. Nihai giriş matrisi cari/gecikmeli meyve veren ağaç sayısı ile Haziran–Temmuz ortalama sıcaklık, maksimum sıcaklık ve ortalama rüzgâr göstergelerinden oluşan sekiz açıklayıcı değişkeni içerir.

**Seed 42 referans testi rassal eğitim/test ayrımıdır; geleceğe yönelik tahmin doğrulaması değildir.** Genişleyen pencere analizi, 1983–2002 ilk eğitim dönemiyle 2003–2024 için 22 ardışık tek adımlı sınama içerir. Bulgular, iklim değişikliğinin nedensel etkisini belirlemek için yeterli değildir.

## Dosya yapısı

```text
scripts/
  tezfinal.py                      # Referans Seed 42 / beş-seed ön değerlendirmeler
  analiz_v2.py                     # 10×5 CV, değişken grupları, L1 ve kronolojik değerlendirme
  nested_cv_reconstruction.py      # İç içe CV: sonradan yeniden oluşturulan kod (kısmi doğrulama)
  ilkbahar_min_reconstruction.py   # İlkbahar 8/11 değişken duyarlılığı (çıktılarla eşleşti)
notebooks/tezfinal.ipynb           # Temizlenmiş not defteri
results/02_tekrarli_cv/            # Tekrarlı CV sonuçları
results/03_kronolojik/             # Kronolojik sonuçlar
results/04_nested_cv_sonuclar/     # Nested CV sonuçları
results/05_ilkbahar_sonuclar/      # İlkbahar duyarlılık sonuçları
docs/                              # Yöntem, kaynak eşleme, doğrulama ve çalıştırma notları
data/README.md                     # Ham veri yayımlanmıyor
tools/verify_repository.py         # Dosya bütünlüğü ve Python sözdizimi denetimi
README_EN.md · CITATION.cff · LICENSE · DATA_AVAILABILITY.md
requirements.txt · checksums.sha256 · .gitignore
```

## Kod–deney eşleştirmesi ve doğrulama durumu

| Tezdeki analiz | Kod | Kayıtlı sonuçlar | Bu arşivde doğrulanma durumu |
|---|---|---|---|
| Seed 42 referans karşılaştırması, ilk beş-seed denemeleri | `scripts/tezfinal.py` | Çalıştırmayla üretilir | Orijinal kod kopyası; bu sürümde tam sayısal yeniden çalışma belgelenmedi |
| 10 tekrarlı 5-katlı CV, değişken grupları ve L1 | `scripts/analiz_v2.py` | `results/02_tekrarli_cv/` | Kod ve özgün çıktı kayıtları var; tam bağımsız eşleşme bu sürümde belgelenmedi |
| 2003–2024 genişleyen pencere | `scripts/analiz_v2.py` | `results/03_kronolojik/` | Kod ve özgün çıktı kayıtları var; tam bağımsız eşleşme bu sürümde belgelenmedi |
| İç içe çapraz doğrulama (Tablo 8) | `scripts/nested_cv_reconstruction.py` | `results/04_nested_cv_sonuclar/` | **Yeniden oluşturulan betik**; yalnız seçili dış katlar birebir doğrulandı, 30/30 kontrol tamamlanmadı |
| İlkbahar minimum sıcaklıkları (Tablo 12) | `scripts/ilkbahar_min_reconstruction.py` | `results/05_ilkbahar_sonuclar/` | **Yeniden oluşturulan betik**; kayıtlı sekiz sonuç CSV'sinin tamamıyla 1×10⁻⁵ toleransta eşleşti |

Kaynak ve çıktı ilişkisini ayrıntılı gösteren belge: [`docs/DENEY_ESLESTIRME.md`](docs/DENEY_ESLESTIRME.md). Nested CV ve ilkbahar analizlerinin doğrulama kayıtları ayrıca [`docs/NESTED_CV_KOD_DOGRULAMA.md`](docs/NESTED_CV_KOD_DOGRULAMA.md) ve [`docs/ILKBAHAR_MIN_KOD_DOGRULAMA.md`](docs/ILKBAHAR_MIN_KOD_DOGRULAMA.md) dosyalarındadır. Betiklerin *orijinal* kaynak oldukları iddia edilmemektedir.

## Çalıştırma ve bütünlük kontrolü

Python sürümleri, yerel veri dosyası kullanımı ve doğrulama komutları için [`docs/CALISTIRMA.md`](docs/CALISTIRMA.md) belgesine bakınız. GitHub deposu ham veri olmadan tüm model sonuçlarını sıfırdan hesaplayamaz.

```bash
python -m pip install -r requirements.txt
python tools/verify_repository.py
```

Statik kontrol SHA-256 karmalarını, kaynak dosya sözdizimini ve arşivde yanlışlıkla eklenmiş kaynak veri dosyalarını tarar. **Model eğitimi veya yeniden hesaplama yerine geçmez.** Dosyalar değiştirildiğinde `checksums.sha256` dosyasının yeni sürüme göre güncellenmesi gerekir.

## Veri paylaşımı ve lisans

Ham MGM meteoroloji verileri veya bu verileri içeren kaynak Excel çalışma kitapları depoda **yoktur**. Bazı kayıtlı sonuç dosyaları yıl, gerçek üretim veya gözlem bazında tahmin içerir; bu kayıtların açık yayım koşulları ayrıca denetlenmelidir. Bkz. [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md).

Yayınlama hakkı araştırmacıya ait kodlar [`LICENSE`](LICENSE) dosyasındaki **MIT Lisansı** kapsamındadır. MIT lisansı kaynak veri veya üçüncü taraf materyallerin yeniden dağıtım izni değildir.

## Atıf ve kalıcı arşiv

Geçici atıf bilgileri [`CITATION.cff`](CITATION.cff) dosyasındadır. **DOI henüz yoktur**; Zenodo tarafından verilen gerçek tanımlayıcı, yayımlanan sürüm doğrulandıktan sonra eklenir. Arşivin hazırlık durumu için [`docs/ARSIV_DENETIMI_v0.4.0.md`](docs/ARSIV_DENETIMI_v0.4.0.md) belgesine bakınız.
