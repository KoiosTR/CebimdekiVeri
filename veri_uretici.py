import pandas as pd
import random
from datetime import datetime, timedelta


def veri_olustur():
    print("=" * 50)
    print("   KİŞİSELLEŞTİRİLMİŞ VERİ SETİ OLUŞTURUCU")
    print("   (Sunumda analizin doğru çalışması için bu gereklidir)")
    print("=" * 50)

    try:
        # Kullanıcıdan GERÇEK ortalamalarını alıyoruz
        print("\nLütfen aylık ortalama giderlerini gir (Tahmini):")
        kira = float(input("🏠 Kira/Yurt Giderin (TL): "))
        market = float(input("🛒 Ortalama Market (TL): "))
        ulasim = float(input("🚌 Ortalama Ulaşım (TL): "))
        fatura = float(input("💡 Ortalama Faturalar (TL): "))
        eglence = float(input("🎉 Eğlence/Sosyal (TL): "))
        maas = float(input("💰 Aylık Ortalama Gelirin (Burs/Maaş) (TL): "))
    except ValueError:
        print("Lütfen sadece sayı girin!")
        return

    # Veri setini oluşturma döngüsü
    baslangic_tarihi = datetime.now() - timedelta(days=365)
    veri_seti = []

    print("\n⏳ Geçmiş 1 yıl, senin verilerine göre simüle ediliyor...")

    for i in range(365):
        gun = baslangic_tarihi + timedelta(days=i)

        # 1. GELİR EKLEME (Her ayın 15'inde)
        if gun.day == 15:
            veri_seti.append({
                "Tarih": gun.strftime("%Y-%m-%d"),
                "Kategori": "Maaş/Burs",
                "Tutar": maas,
                "Islem_Tipi": "Gelir"
            })

        # 2. SABİT GİDER (Kira - Her ayın 1'inde)
        if gun.day == 1:
            veri_seti.append({
                "Tarih": gun.strftime("%Y-%m-%d"),
                "Kategori": "Kira",
                "Tutar": kira,
                "Islem_Tipi": "Gider"
            })

        # 3. DEĞİŞKEN GİDERLER (Rastgele günlere dağıt ama senin ortalamana sadık kal)

        # Market: Ayda ortalama 8 kez gidildiği varsayımıyla
        if random.random() < (8 / 30):
            # Senin girdiğin ortalamayı günlere bölüp biraz sapma (randomness) ekliyoruz
            tutar = (market / 8) * random.uniform(0.8, 1.2)
            veri_seti.append(
                {"Tarih": gun.strftime("%Y-%m-%d"), "Kategori": "Market", "Tutar": int(tutar), "Islem_Tipi": "Gider"})

        # Ulaşım: Ayda 20 kez
        if random.random() < (20 / 30):
            tutar = (ulasim / 20) * random.uniform(0.9, 1.1)
            veri_seti.append(
                {"Tarih": gun.strftime("%Y-%m-%d"), "Kategori": "Ulaşım", "Tutar": int(tutar), "Islem_Tipi": "Gider"})

        # Eğlence: Haftada 1-2 kez
        if random.random() < (6 / 30):
            tutar = (eglence / 6) * random.uniform(0.7, 1.5)
            veri_seti.append(
                {"Tarih": gun.strftime("%Y-%m-%d"), "Kategori": "Eğlence", "Tutar": int(tutar), "Islem_Tipi": "Gider"})

    # Veriyi Kaydet
    df = pd.DataFrame(veri_seti)
    df.to_csv("butce_verisi.csv", index=False)
    print("\n✅ Harika! 'butce_verisi.csv' senin gerçeklerine göre oluşturuldu.")
    print("✅ Şimdi main.py'yi çalıştırıp 'Analiz' dersen mantıklı sonuçlar göreceksin.")


if __name__ == "__main__":
    veri_olustur()