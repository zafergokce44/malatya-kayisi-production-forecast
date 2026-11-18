# Arşiv denetim özeti — 18 Kasım 2026

**Dayanak belge:** `Zafer Gökçe Tez - Düzeltilmiş Sürüm (v3)(2).docx`. Belgedeki Ekler üç parçalıdır: Ek 1 Değişkenler; Ek 2 Model Parametreleri; Ek 3 Python Kodları. Eski ek performans tabloları (16–18) kaldırılmıştır.

## Denetimin kapsamı

- Aynı aşamalara ait özgün betikler `scripts/tezfinal.py` ve `scripts/analiz_v2.py` olarak arşivlendi; tam sayısal yeniden üretim bu denetimde yapılmadı.
- İç içe CV için kaydedilmiş yöntem notu ve dış kat sonuçlarından **sonradan yeni betik oluşturuldu**. Seçili kat eşleşmeleri hesaplandı; bütün 30 dış katın yeniden üretimi **henüz tamamlanmadı**.
- İlkbahar minimum sıcaklık analizi için **sonradan yeni betik oluşturuldu**. Önceki doğrulama kayıtlarında 8/8 CSV dosyası, 1×10⁻⁵ mutlak toleransla eşleşmiştir (maksimum yaklaşık 3,12×10⁻⁶).
- **Tablo 12** için TAM ve MALATYA 8/11 değişkenli performans sonuçları tezdeki değerlerle uyumludur. Ek deney sonucu gerektiren bir tablo güncellemesi tespit edilmedi.
- `results/` içindeki çeşitli dosyalar ham meteoroloji değişkenleri içermese de yıl ve gerçek üretim/hazır tahminler içerir; kamuya açık paylaşımın hukuki uygunluğu bu kod denetimince belirlenmemiştir.
- GitHub deposunun varlığı, kullanıcının **Private** depo ekran görüntülerinde ve yükleme commit kayıtlarında gözlendi. Repo içeriğinin *uzaktan otomatik dosya okuması* bu denetimde doğrulanmadı; eşleştirme, kullanıcı tarafından Github'a yüklenen aynı adlardaki yerel paketleri temel alır.

## Yeniden üretim durumunun raporlanması

| Durum | Kapsam |
|---|---|
| Tarihsel kod + kayıtlı sonuç | Referans model, tekrarlı CV ve kronolojik deneyler |
| Yeniden oluşturma + kısmi sayısal doğrulama | Nested CV |
| Yeniden oluşturma + arşiv çıktılarıyla tam sayısal eşleşme | İlkbahar 8/11 değişken analizi |
| Dışarıda tutulan içerik | MGM kaynağı içeren ham Excel / kaynak meteoroloji tabloları |

## Yayına hazırlık için kalan işler

1. Yetkilendirme/veri paylaşım sınırları netleştirildikten sonra, açıklığı kısıtlı satır bazlı sonuç dosyalarını çıkarmak veya uygun raporlama düzeyine indirmek.
2. Tam nested CV kontrolünü yapmak veya teknik notlarda mevcut kısmi doğrulamayı açıkça korumak.
3. Depoda `python tools/verify_repository.py` çalıştırmak ve kodun değişmediğini teyit etmek.
4. Yayımlanan GitHub Release sürümünü Zenodo'da arşivleyip doğrulanmış DOI'yi tezin Ek 3 kısmına yerleştirmek.

**Bu dosya, olmayan bir DOI'yi veya tamamlanmamış doğrulamayı tamamlanmış gibi göstermemek için hazırlanmıştır.**
