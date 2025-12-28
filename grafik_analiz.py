import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def grafik_ciz():
    if not os.path.exists("butce_verisi.csv"):
        print("❌ Veri dosyası bulunamadı!")
        return

    df = pd.read_csv("butce_verisi.csv")
    df['Tarih'] = pd.to_datetime(df['Tarih'])

    sadece_giderler = df[df['Islem_Tipi'] == 'Gider']
    aylik_ozet = df.groupby([pd.Grouper(key='Tarih', freq='ME'), 'Islem_Tipi'])['Tutar'].sum().unstack().fillna(0)

    if 'Gelir' not in aylik_ozet.columns: aylik_ozet['Gelir'] = 0
    if 'Gider' not in aylik_ozet.columns: aylik_ozet['Gider'] = 0

    # --- TAHMİN ALGORİTMASI (GÜNCELLENDİ: TÜM VERİYİ KULLAN) ---
    # Artık son ayı silmiyoruz çünkü sen tarihleri elle yönetiyorsun.
    # Son 3 ayın (veya ne kadar varsa) ortalamasını alıyoruz.

    son_3_ay_gelir_ort = aylik_ozet['Gelir'].tail(3).mean()
    son_3_ay_gider_ort = aylik_ozet['Gider'].tail(3).mean()

    son_tarih = aylik_ozet.index[-1]
    gelecek_tarih = son_tarih + pd.DateOffset(months=1)

    # --- GRAFİK ---
    plt.figure(figsize=(16, 8))

    # SOL GRAFİK
    plt.subplot(1, 2, 1)
    kategori_toplam = sadece_giderler.groupby("Kategori")["Tutar"].sum()
    explode = [0.05] * len(kategori_toplam)
    colors = sns.color_palette("pastel")[0:len(kategori_toplam)]

    plt.pie(kategori_toplam, labels=kategori_toplam.index, autopct='%1.1f%%',
            startangle=140, explode=explode, shadow=True, colors=colors)
    plt.title("Genel Harcama Dağılımı", fontsize=13)

    # SAĞ GRAFİK
    plt.subplot(1, 2, 2)

    plt.plot(aylik_ozet.index, aylik_ozet['Gelir'], marker='o', color='green', linewidth=2, label='Gerçekleşen Gelir')
    plt.plot(aylik_ozet.index, aylik_ozet['Gider'], marker='o', color='red', linewidth=2, label='Gerçekleşen Gider')

    plt.plot([son_tarih, gelecek_tarih], [aylik_ozet['Gelir'].iloc[-1], son_3_ay_gelir_ort],
             color='green', linestyle='--', marker='>', markersize=8, alpha=0.7, label='AI Tahmini')

    plt.plot([son_tarih, gelecek_tarih], [aylik_ozet['Gider'].iloc[-1], son_3_ay_gider_ort],
             color='red', linestyle='--', marker='>', markersize=8, alpha=0.7, label='AI Tahmini')

    plt.annotate(f"Gelecek Tahmini:\n{int(son_3_ay_gider_ort)} TL",
                 (gelecek_tarih, son_3_ay_gider_ort),
                 textcoords="offset points", xytext=(10, 0), ha='left', color='red', fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=1))

    plt.fill_between(aylik_ozet.index, aylik_ozet['Gelir'], aylik_ozet['Gider'],
                     where=(aylik_ozet['Gelir'] >= aylik_ozet['Gider']),
                     interpolate=True, color='green', alpha=0.05)

    plt.fill_between(aylik_ozet.index, aylik_ozet['Gelir'], aylik_ozet['Gider'],
                     where=(aylik_ozet['Gelir'] < aylik_ozet['Gider']),
                     interpolate=True, color='red', alpha=0.05)

    plt.title("Bütçe Dengesi ve Gelecek Tahmini", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("sunum_grafikleri.png")
    print(f"\n✅ Analiz Bitti. Son veri ayı dahil edildi.")


if __name__ == "__main__":
    grafik_ciz()