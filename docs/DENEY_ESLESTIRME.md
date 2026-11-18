# Tez bölümleri ↔ arşiv kaynakları — v3(2) referansı

Bu eşleştirme *Zafer Gökçe Tez - Düzeltilmiş Sürüm (v3)(2).docx* dosyasındaki başlıklara ve kod arşivindeki dosyalara dayanır. Özgün kaynak betikler ile sonradan yeniden oluşturulmuş olanlar ayrılmıştır.

| Tezdeki bölüm / tablo | Kaynak betik | Kayıtlı çıktı | Durum |
|---|---|---|---|
| §3.2–3.5, Tablo 3–6: Seed 42 referans ayrımı | `scripts/tezfinal.py` | Kodun çıktıları; bu arşivde ayrı referans çıktı paketi yok | Kaynak var; eksiksiz bağımsız yeniden üretim raporlanmadı |
| §3.6, Tablo 7: TAM/MALATYA 10×5 CV | `scripts/analiz_v2.py` | `results/02_tekrarli_cv/cv_ana_model_sonuclari.csv`, `cv_katlar.csv` | Kaynak ve kaydedilmiş sonuçlar mevcut |
| §3.6, Tablo 8: sabit ve nested 5×3 CV | `scripts/nested_cv_reconstruction.py` | `results/04_nested_cv_sonuclar/nested_cv_ozet.csv`, `nested_outer_katlar.csv` | **Yeniden oluşturma**; seçili katlar doğrulandı, tamamı henüz değil |
| §3.7, Tablo 9: 2003–2024 kronolojik | `scripts/analiz_v2.py` | `results/03_kronolojik/kronolojik_sonuclar.csv`, `kronolojik_tahminler.csv` | Kaynak ve kaydedilmiş sonuçlar mevcut |
| §3.8.1–3.8.3, Tablo 10: değişken grupları | `scripts/analiz_v2.py`, referans karşılaştırma `tezfinal.py` | `results/02_tekrarli_cv/cv_degiskengruplari_sonuclari.csv` | Kaynak ve kaydedilmiş sonuçlar mevcut |
| §3.8.4, Tablo 11: L1 değişken duyarlılığı | `scripts/analiz_v2.py`, referans karşılaştırma `tezfinal.py` | `results/02_tekrarli_cv/cv_l1_sonuclari.csv` | Kaynak ve kaydedilmiş sonuçlar mevcut |
| §3.8.5, Tablo 12: 8/11 değişken ilkbahar duyarlılığı | `scripts/ilkbahar_min_reconstruction.py` | `results/05_ilkbahar_sonuclar/` | **Yeniden oluşturma**; 8/8 CSV kayıtları doğrulandı |

**Kritik farklar:** Beş-seed (%80/%20) deneyleri 10 tekrarlı 5-katlı CV değildir. Nested CV'nin 5 dış + 3 iç kat düzeni, Tablo 7'deki 10 tekrarlı 5-katlı CV ile aynı deney değildir. Tekil kat ortalaması, havuzlanmış OOF ölçütü ve kronolojik test skorları farklı özetleme koşullarını temsil eder.

**Açık veri notu:** `results/03_kronolojik/kronolojik_tahminler.csv`, `results/04_nested_cv_sonuclar/nested_outer_katlar.csv` ve ilkbahar tahmin sonuçları yıl/gerçek değer veya gözlem düzeyinde tahminler içerir. Kaynak meteorolojik ham veriler dahil edilmemiş olsa da açık yayımlama öncesinde bu çıktılar ayrıca gözden geçirilmelidir.
