from abc import ABC, abstractmethod
from datetime import datetime
import csv
import os


# --- ARAYÜZLER ---
class Gozlemci(ABC):
    @abstractmethod
    def bildirim_al(self, mesaj: str):
        pass


# --- TEMEL SINIF (GÜNCELLENDİ: Artık tarih parametresi alıyor) ---
class Islem(ABC):
    def __init__(self, tutar, aciklama, tarih_str=None):
        self.tutar = tutar
        self.aciklama = aciklama
        # Eğer tarih girildiyse onu kullan, girilmediyse şu anı al
        if tarih_str:
            try:
                self.tarih = datetime.strptime(tarih_str, "%Y-%m-%d")
            except ValueError:
                print("⚠️ Tarih formatı hatalı! Bugünün tarihi kullanılıyor.")
                self.tarih = datetime.now()
        else:
            self.tarih = datetime.now()

    def __str__(self):
        return f"[{self.tarih.strftime('%Y-%m-%d')}] {self.aciklama}: {self.tutar} TL"


# --- MİRAS ALAN SINIFLAR (GÜNCELLENDİ) ---
class Gelir(Islem):
    def __init__(self, tutar, aciklama, kaynak, tarih_str=None):
        super().__init__(tutar, aciklama, tarih_str)
        self.kaynak = kaynak


class Gider(Islem):
    def __init__(self, tutar, aciklama, kategori, tarih_str=None):
        super().__init__(tutar, aciklama, tarih_str)
        self.kategori = kategori


# --- KULLANICI ---
class Kullanici(Gozlemci):
    def __init__(self, ad, soyad):
        self.ad = ad
        self.soyad = soyad

    def bildirim_al(self, mesaj):
        print(f"\n🔔 BİLDİRİM ({self.ad} {self.soyad}): {mesaj}")


# --- YÖNETİCİ ---
class ButceYonetici:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ButceYonetici, cls).__new__(cls)
            cls._instance.islemler = []
            cls._instance.gozlemciler = []
            cls._instance.bakiye = 0.0
        return cls._instance

    def gozlemci_ekle(self, gozlemci: Gozlemci):
        self.gozlemciler.append(gozlemci)

    def islem_ekle(self, islem: Islem):
        self.islemler.append(islem)

        if isinstance(islem, Gelir):
            self.bakiye += islem.tutar
            print(f"➕ Gelir Eklendi: {islem.aciklama} ({islem.tarih.strftime('%Y-%m-%d')})")
            self.csv_ye_yaz(islem, "Gelir", "Gelir")

        elif isinstance(islem, Gider):
            self.bakiye -= islem.tutar
            print(f"➖ Gider Eklendi: {islem.aciklama} ({islem.tarih.strftime('%Y-%m-%d')})")
            self.limit_kontrol()
            self.csv_ye_yaz(islem, islem.kategori, "Gider")

    def csv_ye_yaz(self, islem, kategori_adi, islem_tipi):
        dosya_adi = "butce_verisi.csv"
        veri = [
            islem.tarih.strftime("%Y-%m-%d"),
            kategori_adi,
            islem.tutar,
            islem_tipi
        ]
        try:
            with open(dosya_adi, mode='a', newline='', encoding='utf-8') as f:
                yazici = csv.writer(f)
                yazici.writerow(veri)
        except Exception as e:
            print(f"Hata: CSV'ye yazılamadı! {e}")

    def limit_kontrol(self):
        if self.bakiye < 0:
            self._bildirim_yayinla(f"ACİL! Bakiye negatife düştü! ({self.bakiye} TL)")
        elif self.bakiye < 1000:
            self._bildirim_yayinla(f"Dikkat: Bakiye kritik seviyede. ({self.bakiye} TL)")

    def _bildirim_yayinla(self, mesaj):
        for g in self.gozlemciler:
            g.bildirim_al(mesaj)

    def bakiye_goster(self):
        print(f"\n💰 Güncel Bakiye: {self.bakiye} TL")


# --- RAPORLAMA ---
class Rapor:
    def olustur(self): pass


class ExcelRapor(Rapor):
    def olustur(self): return "📊 Excel Raporu oluşturuldu."


class PDFRapor(Rapor):
    def olustur(self): return "📄 PDF Raporu oluşturuldu."


class RaporFactory:
    @staticmethod
    def rapor_uret(tip):
        if tip == "excel":
            return ExcelRapor()
        elif tip == "pdf":
            return PDFRapor()
        return None