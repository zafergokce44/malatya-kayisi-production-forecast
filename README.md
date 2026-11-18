# Malatya Yaş Kayısı Üretim Tahmini — Tez Analiz Kodları

**Araştırmacı:** Zafer Gökçe  
**Tez:** *İklim Değişikliğinin Malatya Kayısı Üretimi Üzerindeki Etkisinin Yapay Zekâ Modelleri ile Tahmini*  
**Kurum:** Bayburt Üniversitesi, Lisansüstü Eğitim Enstitüsü, Endüstri Mühendisliği Ana Bilim Dalı (2026)  
**Arşiv durumu:** **Ön yayın / doğrulama gerektiren araştırma arşivi (v0.1.0)**. Henüz DOI atanmış değildir.

## Amaç ve kapsam

Bu arşiv, tez kapsamında kullanılan **Extra Trees**, **Random Forest** ve **doğrusal SVR** modellerine ilişkin kaynak kodlarını; tekrarlı çapraz doğrulama, kronolojik doğrulama, iç içe çapraz doğrulama ve ilkbahar minimum sıcaklığı duyarlılık deneylerinin **eldeki sonuç çıktılarını** denetlenebilir bir klasör yapısında toplar.

- Tarihsel kaynak veri aralığı **1934–2024**; temel modelleme matrisi **57** gözlem (`TAM`).
- Kesintisiz dönem alt örneklemi **1983–2024**; **42** gözlem (`MALATYA`).
- Referans deneyde `FINAL_SEED = 42`; tekrarlı değerlendirmede 10 tekrarlı 5 kat kullanılmıştır.
- Referans Seed 42 değerlendirmesi **rassal eğitim-test ayrımıdır** ve ileri dönem tahmini olarak yorumlanamaz.
- Kronolojik doğrulama, **1983–2002** başlangıç eğitimiyle **2003–2024** için 22 bir-adım-ileri sınama içerir.

> **Bilimsel sınır:** Bu arşiv nedensel bir iklim değişikliği etkisi kanıtı sunmaz. Verilerle gerçekleştirilen tahmin ve doğrulama çalışmalarını belgeler.

## Dosya yapısı

```text
.
├── README.md
├── README_EN.md
├── CITATION.cff
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── tezfinal.py                 # Seed 42 + 5 seed + değişken grubu + L1
│   └── analiz_v2.py                # 10x5 CV + 2003–2024 kronolojik doğrulama
├── notebooks/
│   └── tezfinal.ipynb              # Çıktıları ve kişisel meta verisi temizlenmiş
├── results/
│   ├── 02_tekrarli_cv/             # Kaydedilmiş aşama 2 sonuçları
│   ├── 03_kronolojik/              # Kaydedilmiş aşama 3 sonuçları
│   ├── 04_nested_cv_sonuclar/      # Nested CV çıktıları (kaynak betik eşleşmesi eksik)
│   └── 05_ilkbahar_sonuclar/       # İlkbahar deney çıktıları (kaynak betik eşleşmesi eksik)
├── data/
│   └── README.md                   # Ham veri bu depoda dağıtılmaz
├── docs/
│   ├── CALISTIRMA.md
│   ├── DENEY_ESLESTIRME.md
│   ├── YAYIN_ONCESI_KONTROL.md
│   ├── KAYNAK_KOKENI.tsv
│   └── kaynak_ortam_surumleri.txt
└── tools/
    └── verify_repository.py
```

## Mevcut kodun kapsamı ve eksikler

| Deney | Kaynak kod | Çıktılar | Durum |
|---|---|---|---|
| Referans Seed 42 ve 5 seed | `scripts/tezfinal.py` | Kod yeniden çalıştırıldığında üretir | Kod mevcut; yeniden çalıştırılmadı |
| 10×5 tekrarlı CV ve değişken grupları | `scripts/analiz_v2.py` | `results/02_tekrarli_cv/` | Kod ve önceden kaydedilmiş sonuçlar mevcut |
| Genişleyen pencere kronolojik test | `scripts/analiz_v2.py` | `results/03_kronolojik/` | Kod ve önceden kaydedilmiş sonuçlar mevcut |
| Nested CV | **Henüz eşleştirilmedi** | `results/04_nested_cv_sonuclar/` | **Sonuç-odaklı arşiv; tam yeniden çalıştırılabilir değil** |
| İlkbahar minimum sıcaklığı deneyi | **Henüz eşleştirilmedi** | `results/05_ilkbahar_sonuclar/` | **Sonuç-odaklı arşiv; tam yeniden çalıştırılabilir değil** |

Kaynak kodlar **mevcut analiz sürümlerinden alınmıştır; model sonuçları bu arşivi hazırlarken yeniden hesaplanmamıştır.** Kodların ve çıktıların birebir yeniden üretilebilirliği, yetkili veri erişimi sağlandıktan sonra ayrıca test edilmelidir.

## Çalıştırma

Colab ortamı ve orijinal kodların beklediği dosya yolları için [`docs/CALISTIRMA.md`](docs/CALISTIRMA.md) belgesine bakın. Sadece çıktı dosyalarını gözden geçirmek için ham veriye ihtiyaç yoktur.

```bash
python tools/verify_repository.py
```

Bu doğrulama komutu **dosya bütünlüğü ve kaynak kodu sözdizimini** kontrol eder; analizleri çalıştırmaz veya yeniden üretilebilirliği ispatlamaz.

## Veri erişimi ve lisans

**Meteoroloji Genel Müdürlüğünden (MGM) temin edilen ham veriler ve kaynak Excel çalışma kitapları bu depoda yer almaz.** İçerik sahipliği ve paylaşım koşulları açıklığa kavuşturulmadan ham veriler GitHub'a veya Zenodo'ya yüklenmemelidir. Ayrıntılar: [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md).

**Kod lisansı:** Araştırmacının paylaşma hakkına sahip olduğu bu depodaki kaynak kodları, depo kökündeki [`LICENSE`](LICENSE) dosyasında belirtilen **MIT Lisansı** altında sunulmaktadır. Bu lisans, Meteoroloji Genel Müdürlüğünden temin edilen ham verileri, üçüncü taraf veri kaynaklarını veya bu depodaki analiz sonuçlarının ayrıca izin gerektirebilecek veri içeriklerini otomatik olarak kapsamaz. Veri paylaşımı için [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md) belgesine bakınız.

## Atıf ve DOI

Geçici atıf meta verisi [`CITATION.cff`](CITATION.cff) dosyasındadır. GitHub sürümü Zenodo'da arşivlenip gerçek DOI oluştuktan sonra README, CITATION.cff ve tezin Ek 3 bölümü **gerçek, doğrulanmış DOI ile** güncellenmelidir. DOI henüz yoktur.

## Provenans

Bu paket, araştırmacının mevcut Python betikleri ve kayıtlı deney sonuçlarından hazırlanmış düzenli bir **arşiv kopyasıdır**. Kaynak ZIP adları için [`docs/KAYNAK_KOKENI.tsv`](docs/KAYNAK_KOKENI.tsv), SHA-256 değerleri için `checksums.sha256` incelenebilir. `tezfinal.py` kopyasından yalnızca kişisel Colab belge bağlantısı çıkarılmış; bilimsel mantığı değiştirilmemiştir. Notebook çıktıları ve kullanıcı kimlik meta verileri temizlenmiştir.
