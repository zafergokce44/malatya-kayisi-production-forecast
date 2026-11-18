# Tez bölümleri ↔ arşiv dosyaları

| Tez konusu | İlgili kod | Kayıtlı çıktı | Yeniden çalıştırma durumu |
|---|---|---|---|
| §3.2–3.5: referans Seed 42 karşılaştırması | `scripts/tezfinal.py` | Kod tekrar çalıştırıldığında oluşturur; bu ZIP'e aynı aşamanın bağımsız çıktı arşivi dahil değildir | Kaynak mevcut, veriyle yeniden test edilmedi |
| §3.6: 10×5 tekrarlı CV | `scripts/analiz_v2.py` | `results/02_tekrarli_cv/cv_ana_model_sonuclari.csv`, `cv_katlar.csv` vb. | Kaynak ve kayıtlı çıktı mevcut |
| §3.7: 2003–2024 genişleyen pencere | `scripts/analiz_v2.py` | `results/03_kronolojik/kronolojik_sonuclar.csv`, `kronolojik_tahminler.csv` | Kaynak ve kayıtlı çıktı mevcut |
| §3.8: değişken grupları / L1 | `scripts/tezfinal.py`; `scripts/analiz_v2.py` | `results/02_tekrarli_cv/cv_degiskengruplari_sonuclari.csv`, `cv_l1_sonuclari.csv` | Kaynak ve kayıtlı çıktı mevcut |
| §3.6: iç içe CV (Tablo 8) | **Kaynak betiğin kesin sürümü doğrulanmadı** | `results/04_nested_cv_sonuclar/` | Yalnız sonuçlar arşivlendi |
| §3.8.5: ilkbahar minimum sıcaklığı (Tablo 12) | **Kaynak betiğin kesin sürümü doğrulanmadı** | `results/05_ilkbahar_sonuclar/` | Yalnız sonuçlar arşivlendi |

**Uyarı:** `analiz_v2.py` Aşama 2/3 sonuçları, `tezfinal.py` içindeki 5-seed sağlamlık testiyle aynı değerlendirme tasarımı değildir. Bu ölçütleri birbirinin yerine kullanmayın.
