# GitHub → Zenodo: bilimsel arşiv kontrol listesi (v0.4.0)

Bu belge, **v3(2) tez metni** ve 18 Kasım 2026'da hazırlanan ön yayın kod paketine göre güncellenmiştir.

- [x] GitHub deposu oluşturuldu; `scripts`, `docs`, `results`, `notebooks`, `tools`, `data` klasörleri kullanıcı ekran görüntüsüyle teyit edildi (repo içeriğinin uzaktan otomatik okuması doğrulanmadı).
- [x] MIT lisansı araştırmacı tarafından `LICENSE` dosyasıyla eklendi.
- [x] Nested CV deneyine ait **yeniden oluşturulmuş** betik ve kısmi doğrulama kaydı hazırlandı.
- [x] İlkbahar 8/11 değişken deneyine ait **yeniden oluşturulmuş** betik ve 8/8 CSV eşleşme kaydı hazırlandı.
- [ ] Nested CV'nin her iki veri seti, üç model ve beş dış kattaki 30/30 sonuç satırının bağımsız sayısal karşılaştırmasını tamamla ya da mevcut kısmi kapsamı yayın belgelerinde aynen belirt.
- [ ] `scripts/tezfinal.py` ve `scripts/analiz_v2.py` için özgün sonuçlarla eksiksiz yeniden çalıştırma raporunu oluştur ya da bunların kayıtlı kod + çıktı arşivi olduğunu açık tut.
- [ ] `results/` altındaki **gerçek üretim ve satır bazlı tahmin** çıktılarının yeniden yayımlanabilirliğini kaynağa göre değerlendir; kısıtlı içerikleri kaldır.
- [ ] MGM kaynak Excel dosyalarının / ham meteorolojik verilerin açık arşive eklenmediğini, izin koşullarını ve hak sahipliğini teyit et.
- [ ] Repo üzerinde `python tools/verify_repository.py` komutunu çalıştır ve dosyalar değişirse `checksums.sha256` dosyasını yeniden üret.
- [ ] Kod metadatasını ve `CITATION.cff` yazarlık/sürümünü son kez kontrol et.
- [ ] Kamuya açık sürüm için depo görünürlüğünü, kaynak izinlerini ve kişisel/saklı bağlantıları denetle.
- [ ] Zenodo GitHub entegrasyonunu aç; GitHub Release ile ilk kalıcı arşiv sürümünü oluştur.
- [ ] Atanan **gerçek Zenodo DOI'sini** GitHub'daki `CITATION.cff`, README ve tezin **Ek 3** bölümünde göster.
- [ ] Ek 3'te eski Google Drive ve `README.txt`/kaynak Excel açıklamalarını yeni arşiv yapısına göre güncelle.

DOI kimliği ile bütün modellerin yeniden üretilebilir olması farklı konulardır. Zenodo'da yayımlanan **belirli sürümde hangi analizlerin ne düzeyde doğrulandığı** somut olarak belgelendirilmelidir.
