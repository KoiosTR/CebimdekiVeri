import sys
import time
from sistem_modelleri import ButceYonetici, Kullanici, Gelir, Gider, RaporFactory
import grafik_analiz


def menuyu_goster():
    print("\n" + "=" * 45)
    print("   CEBİMDEKİ VERİ - KONTROL PANELİ   ")
    print("=" * 45)
    print("1. ➕ Gelir Ekle (Tarih Seçmeli)")
    print("2. ➖ Gider Ekle (Tarih Seçmeli)")
    print("3. 💰 Güncel Bakiye ve Durum")
    print("4. 📈 Geçmiş Analizi ve Gelecek Tahmini")
    print("5. 📄 Rapor Oluştur")
    print("6. ❌ Çıkış")
    print("=" * 45)


def tarih_sor():
    tarih = input("Tarih (YYYY-AA-GG) [Boş bırakırsan BUGÜN]: ")
    if tarih.strip() == "":
        return None  # None dönerse sistem bugünü alır
    return tarih


def uygulamayi_baslat():
    yonetici = ButceYonetici()

    print("\n👋 Merhaba! Sisteme hoş geldin.")
    # Hızlı test için buraları enter geçebilirsin
    ad = input("Adınız: ") or "Misafir"
    soyad = input("Soyadınız: ") or "Kullanıcı"

    kullanici = Kullanici(ad, soyad)
    yonetici.gozlemci_ekle(kullanici)

    print(f"\nSistem hazır! Geçmişe veya geleceğe veri girebilirsin.")

    while True:
        menuyu_goster()
        secim = input("👉 Seçiminiz (1-6): ")

        if secim == '1':
            try:
                tutar = float(input("Gelir Tutarı (TL): "))
                aciklama = input("Açıklama: ")
                kaynak = input("Kaynak: ")
                tarih_str = tarih_sor()  # Tarihi soruyoruz

                # Tarihi parametre olarak gönderiyoruz
                yeni_gelir = Gelir(tutar, aciklama, kaynak, tarih_str)
                yonetici.islem_ekle(yeni_gelir)
            except ValueError:
                print("❌ Hata: Tutar sayı olmalı!")

        elif secim == '2':
            try:
                tutar = float(input("Gider Tutarı (TL): "))
                aciklama = input("Açıklama: ")
                kategori = input("Kategori: ")
                tarih_str = tarih_sor()  # Tarihi soruyoruz

                yeni_gider = Gider(tutar, aciklama, kategori, tarih_str)
                yonetici.islem_ekle(yeni_gider)
            except ValueError:
                print("❌ Hata: Tutar sayı olmalı!")

        elif secim == '3':
            yonetici.bakiye_goster()

        elif secim == '4':
            print("\n🔄 Veriler işleniyor...")
            grafik_analiz.grafik_ciz()
            print("\n✅ Analiz tamamlandı! Grafikleri kontrol et.")

        elif secim == '5':
            tip = input("Format (pdf / excel): ").lower()
            fabrika = RaporFactory()
            rapor = fabrika.rapor_uret(tip)
            if rapor:
                print(f"\n✅ {rapor.olustur()}")
            else:
                print("\n❌ Geçersiz format.")

        elif secim == '6':
            print("Güle güle! 👋")
            break

        else:
            print("Geçersiz seçenek.")


if __name__ == "__main__":
    uygulamayi_baslat()