from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from backend.firebase_config import get_db


# --- ARAYÜZLER ---
class Gozlemci(ABC):
    @abstractmethod
    def update(self, bildirim: "Bildirim"):
        pass


# --- TEMEL SINIF (GÜNCELLENDİ: Artık tarih parametresi alıyor) ---
class Islem(ABC):
    def __init__(self, tutar, aciklama, tarih_str=None, user_email: Optional[str] = None, id: Optional[str] = None):
        self.id = id  # Firestore belge ID'si veya None
        self.tutar = tutar
        self.aciklama = aciklama
        self.user_email = user_email
        # Eğer tarih girildiyse onu kullan, girilmediyse şu anı al
        if tarih_str:
            try:
                self.tarih = datetime.strptime(tarih_str, "%Y-%m-%d")
            except ValueError:
                print("⚠️ Tarih formatı hatalı! Bugünün tarihi kullanılıyor.")
                self.tarih = datetime.now()
        else:
            self.tarih = datetime.now()

    def getDetay(self) -> str:
        """İşlem detaylarını okunabilir string formatında döndürür."""
        tip = "Gelir" if isinstance(self, Gelir) else "Gider"
        detay = f"{tip} - {self.aciklama}\n"
        detay += f"Tutar: {self.tutar} TL\n"
        detay += f"Tarih: {self.tarih.strftime('%Y-%m-%d')}\n"
        if self.user_email:
            detay += f"Kullanıcı: {self.user_email}\n"
        if isinstance(self, Gelir):
            detay += f"Kaynak: {self.kaynak}\n"
            detay += f"Düzenli Gelir: {'Evet' if self.duzenliMi else 'Hayır'}\n"
            detay += f"Tahmini Vergi: {self.vergiHesapla()} TL\n"
        elif isinstance(self, Gider):
            detay += f"Kategori: {self.kategori}\n"
            detay += f"Zorunlu Gider: {'Evet' if self.zorunluMu else 'Hayır'}\n"
            detay += f"Taksitli: {'Evet' if self.taksitVarMi() else 'Hayır'}\n"
        if self.id:
            detay += f"ID: {self.id}"
        return detay.strip()

    def toJSON(self) -> str:
        """İşlemi JSON string formatında döndürür."""
        import json
        data: Dict[str, Any] = {
            "id": self.id,
            "tutar": self.tutar,
            "aciklama": self.aciklama,
            "tarih": self.tarih.isoformat(),
            "user_email": self.user_email,
            "islem_tipi": "Gelir" if isinstance(self, Gelir) else "Gider",
        }
        if isinstance(self, Gelir):
            data["kaynak"] = self.kaynak
            data["duzenliMi"] = self.duzenliMi
            data["tahmini_vergi"] = self.vergiHesapla()
        elif isinstance(self, Gider):
            data["kategori"] = self.kategori
            data["zorunluMu"] = self.zorunluMu
            data["taksitVarMi"] = self.taksitVarMi()
        return json.dumps(data, ensure_ascii=False, indent=2)

    def __str__(self):
        return f"[{self.tarih.strftime('%Y-%m-%d')}] {self.aciklama}: {self.tutar} TL"


# --- MİRAS ALAN SINIFLAR (GÜNCELLENDİ) ---
class Gelir(Islem):
    def __init__(self, tutar, aciklama, kaynak, tarih_str=None, user_email: Optional[str] = None, duzenliMi: bool = False, id: Optional[str] = None):
        super().__init__(tutar, aciklama, tarih_str, user_email, id)
        self.kaynak = kaynak
        self.duzenliMi = duzenliMi

    def vergiHesapla(self) -> float:
        """
        Gelir vergisi hesaplar. Türkiye'de 2024 için:
        - İlk 110.000 TL için %15
        - 110.000 - 230.000 TL arası %20
        - 230.000 TL üzeri %27
        Düzenli gelirlerde %5 ek indirim uygulanır.
        """
        vergi_orani = 0.15
        if self.tutar > 230000:
            vergi_orani = 0.27
        elif self.tutar > 110000:
            vergi_orani = 0.20
        
        vergi = self.tutar * vergi_orani
        
        # Düzenli gelirlerde %5 indirim
        if self.duzenliMi:
            vergi *= 0.95
        
        return round(vergi, 2)


class Gider(Islem):
    def __init__(self, tutar, aciklama, kategori, tarih_str=None, user_email: Optional[str] = None, zorunluMu: bool = False, id: Optional[str] = None):
        super().__init__(tutar, aciklama, tarih_str, user_email, id)
        self.kategori = kategori
        self.zorunluMu = zorunluMu

    def taksitVarMi(self) -> bool:
        """
        Giderin taksitli olup olmadığını kontrol eder.
        Basit bir heuristik: Tutar 1000 TL üzerindeyse ve kategori "FATURA", "KREDI", "TAKSIT" içeriyorsa taksitli kabul edilir.
        """
        if self.tutar >= 1000:
            kategori_upper = (self.kategori or "").upper()
            taksit_kategorileri = ["FATURA", "KREDI", "TAKSIT", "KREDİ", "ÖDEME"]
            return any(k in kategori_upper for k in taksit_kategorileri)
        return False


# --- KULLANICI ---
class Bildirim:
    def __init__(self, user_id: Optional[str], mesaj: str, tarih: Optional[datetime] = None, okundu_mu: bool = False):
        self.user_id = user_id
        self.mesaj = mesaj
        self.tarih = tarih or datetime.now()
        self.okundu_mu = okundu_mu


class Kullanici(Gozlemci):
    def __init__(self, ad, soyad):
        self.ad = ad
        self.soyad = soyad

    def update(self, bildirim: Bildirim):
        print(f"\n🔔 BİLDİRİM ({self.ad} {self.soyad}): {bildirim.mesaj}")


# --- YÖNETİCİ ---
class ButceYonetici:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ButceYonetici, cls).__new__(cls)
            cls._instance.islemler = []
            cls._instance.gozlemciler = []
            cls._instance.bakiye = 0.0
            cls._instance.aylikLimit = 0.0  # Aylık limit (TL)
            cls._instance.veritabaniYolu = "transactions"  # Firestore koleksiyon adı
        return cls._instance

    def gozlemci_ekle(self, gozlemci: Gozlemci):
        self.gozlemciler.append(gozlemci)

    def islem_ekle(self, islem: Islem):
        self.islemler.append(islem)

        limit_info: Optional[Dict[str, Any]] = None

        if isinstance(islem, Gelir):
            self.bakiye += islem.tutar
            print(f"➕ Gelir Eklendi: {islem.aciklama} ({islem.tarih.strftime('%Y-%m-%d')})")
            # Gelir sonrası da bilgilendirme yapılabilir (negatif/kritik bakiye toparlandı mı vs.)
            limit_info = self.limit_kontrol()
            self.csv_ye_yaz(islem, "Gelir", "Gelir")

        elif isinstance(islem, Gider):
            self.bakiye -= islem.tutar
            print(f"➖ Gider Eklendi: {islem.aciklama} ({islem.tarih.strftime('%Y-%m-%d')})")
            # Aylik gider toplamını (bu gider dahil) hesaplayıp limit kontrolü yap
            toplam = (self._aylik_gider_toplami(islem.tarih) or 0.0) + float(islem.tutar)
            limit_info = self.limit_kontrol(aylik_gider_toplam=toplam)
            self.csv_ye_yaz(islem, getattr(islem, "kategori_id", None), "Gider")

        return limit_info

    def csv_ye_yaz(self, islem: Islem, kategori_degeri: Any, islem_tipi: str):
        """
        Firestore'a yazan kalıcılık katmanı. Metot adı korunmuştur.
        Koleksiyon: transactions
        Belge alanları: User_Email, Tarih, Kategori (ops.), Tutar, Islem_Tipi, Aciklama, Kaynak (ops.)
        Dönen belge ID'si Islem nesnesine eklenir.
        """
        try:
            db = get_db()
            data: Dict[str, Any] = {
                "User_Email": getattr(islem, "user_email", None),
                "Tarih": islem.tarih,  # firebase-admin, datetime -> Timestamp'e dönüştürür
                "Kategori": kategori_degeri if islem_tipi == "Gider" else None,
                "Tutar": float(islem.tutar),
                "Islem_Tipi": islem_tipi,
                "Aciklama": getattr(islem, "aciklama", None),
            }
            if isinstance(islem, Gelir):
                data["Kaynak"] = getattr(islem, "kaynak", None)
                data["DuzenliMi"] = getattr(islem, "duzenliMi", False)
            elif isinstance(islem, Gider):
                data["ZorunluMu"] = getattr(islem, "zorunluMu", False)
            # Firestore add() metodu (timestamp, DocumentReference) tuple döndürür
            _, doc_ref = db.collection("transactions").add(data)
            # Firestore'dan dönen belge ID'sini Islem nesnesine ekle
            islem.id = doc_ref.id
        except Exception as exc:
            error_msg = str(exc)
            if "network" in error_msg.lower() or "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                print(f"⚠️ Network Hatası: Firestore'a bağlanılamadı. İşlem kaydedilemedi: {error_msg}")
                print("💡 İnternet bağlantınızı kontrol edin veya Firebase servisinin çalıştığından emin olun.")
            else:
                print(f"❌ Firestore Hatası: {error_msg}")
            # Hata durumunda işlemi geri al (bakiye güncellemesini geri al)
            if isinstance(islem, Gelir):
                self.bakiye -= islem.tutar
            elif isinstance(islem, Gider):
                self.bakiye += islem.tutar
            raise  # Hata yukarıya fırlatılır

    def limit_kontrol(self, aylik_gider_toplam: Optional[float] = None) -> Dict[str, Any]:
        """
        Aylık limit durumunu değerlendirir ve eşik bazlı bilgi döndürür.
        Dönüş: { asildi: bool, yuzde: float, esik: Optional[int], mesaj: str }
        Not: Aylık limit gider toplamına göre değerlendirilir (bakiye değil).
        """
        # Önce bakiye ile ilgili kritik durumlar için yayın (limitten bağımsız)
        if self.bakiye < 0:
            self._bildirim_yayinla(f"ACİL! Bakiye negatife düştü! ({self.bakiye} TL)")
        elif self.bakiye < 1000:
            self._bildirim_yayinla(f"Dikkat: Bakiye kritik seviyede. ({self.bakiye} TL)")

        if self.aylikLimit <= 0:
            return {"asildi": False, "yuzde": 0.0, "esik": None, "mesaj": "Limit ayarlı değil"}

        # Aylık gider toplamı verilmediyse Firestore'dan/hatıradan hesapla
        if aylik_gider_toplam is None:
            aylik_gider_toplam = self._aylik_gider_toplami(datetime.now())

        try:
            yuzde = float(aylik_gider_toplam) / float(self.aylikLimit) if self.aylikLimit else 0.0
        except Exception:
            yuzde = 0.0

        esik = None
        mesaj = None
        if yuzde >= 1.0:
            esik = 100
            mesaj = f"Aylık limit AŞILDI! (Gider: {aylik_gider_toplam} TL / Limit: {self.aylikLimit} TL)"
        elif yuzde >= 0.8:
            esik = 80
            mesaj = f"Kritik eşik %80'e ulaşıldı. (Gider: {aylik_gider_toplam} TL / Limit: {self.aylikLimit} TL)"
        elif yuzde >= 0.5:
            esik = 50
            mesaj = f"Aylık limitin %50'si aşıldı. (Gider: {aylik_gider_toplam} TL / Limit: {self.aylikLimit} TL)"

        if mesaj:
            self._bildirim_yayinla(mesaj)

        return {"asildi": yuzde >= 1.0, "yuzde": round(yuzde, 4), "esik": esik, "mesaj": mesaj or ""}

    def _aylik_gider_toplami(self, referans_tarih: datetime) -> float:
        """
        Verilen tarihin ait olduğu ay için toplam Gider tutarını hesaplar.
        Firestore'dan tüm işlemleri çekip Python tarafında filtreler (basit ve yeterli).
        """
        try:
            db = get_db()
            docs = db.collection(self.veritabaniYolu).order_by("Tarih").stream()
            yil = referans_tarih.year
            ay = referans_tarih.month
            toplam = 0.0
            for d in docs:
                data = d.to_dict() or {}
                if data.get("Islem_Tipi") != "Gider":
                    continue
                t = data.get("Tarih")
                try:
                    t_py = t if isinstance(t, datetime) else None
                    if t_py is None:
                        # Bazı durumlarda Timestamp/datetime farklı olabilir; dönüştürmeyi dene
                        from pandas import to_datetime
                        t_py = to_datetime(t).to_pydatetime()
                except Exception:
                    continue
                if t_py.year == yil and t_py.month == ay:
                    try:
                        toplam += float(data.get("Tutar", 0))
                    except Exception:
                        pass
            return toplam
        except Exception as exc:
            print(f"❌ Aylık gider toplami hesaplanamadı: {exc}")
            return 0.0

    def islem_sil(self, id: str) -> bool:
        """
        Belirtilen ID'ye sahip işlemi siler.
        Firestore'dan siler ve bakiyeyi günceller.
        """
        try:
            db = get_db()
            # Firestore'dan sil
            doc_ref = db.collection(self.veritabaniYolu).document(id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            data = doc.to_dict()
            tutar = float(data.get("Tutar", 0))
            islem_tipi = data.get("Islem_Tipi", "")
            
            # Firestore'dan sil
            doc_ref.delete()
            
            # Bakiyeyi güncelle
            if islem_tipi == "Gelir":
                self.bakiye -= tutar
            elif islem_tipi == "Gider":
                self.bakiye += tutar
            
            # Bellekteki işlemler listesinden de sil
            self.islemler = [i for i in self.islemler if getattr(i, "id", None) != id]
            
            print(f"🗑️ İşlem silindi: {id}")
            return True
        except Exception as exc:
            error_msg = str(exc)
            print(f"❌ İşlem silme hatası: {error_msg}")
            return False

    def gecmisi_yukle(self) -> None:
        """
        Firestore'dan geçmiş işlemleri yükler ve bellekteki listeye ekler.
        Bakiyeyi de günceller.
        """
        try:
            db = get_db()
            docs = db.collection(self.veritabaniYolu).order_by("Tarih").stream()
            
            self.islemler = []
            self.bakiye = 0.0
            
            for doc in docs:
                data = doc.to_dict()
                transaction_id = doc.id
                
                # TransactionFactory ile Islem nesnesi oluştur
                data["id"] = transaction_id
                islem = TransactionFactory.create(data)
                
                # Bakiyeyi güncelle
                if isinstance(islem, Gelir):
                    self.bakiye += islem.tutar
                elif isinstance(islem, Gider):
                    self.bakiye -= islem.tutar
                
                self.islemler.append(islem)
            
            print(f"📥 Geçmiş veriler yüklendi: {len(self.islemler)} işlem, Bakiye: {self.bakiye} TL")
        except Exception as exc:
            error_msg = str(exc)
            print(f"❌ Geçmiş yükleme hatası: {error_msg}")

    def veriyi_kaydet(self) -> None:
        """
        Tüm işlemleri Firestore'a kaydeder.
        csv_ye_yaz metodunu kullanır (her işlem için).
        """
        try:
            kaydedilen = 0
            for islem in self.islemler:
                # Eğer ID yoksa yeni kayıt, varsa güncelleme gerekir
                if not hasattr(islem, "id") or not islem.id:
                    if isinstance(islem, Gelir):
                        self.csv_ye_yaz(islem, "Gelir", "Gelir")
                    elif isinstance(islem, Gider):
                        self.csv_ye_yaz(islem, getattr(islem, "kategori", None), "Gider")
                    kaydedilen += 1
            print(f"💾 Veriler kaydedildi: {kaydedilen} işlem")
        except Exception as exc:
            error_msg = str(exc)
            print(f"❌ Veri kaydetme hatası: {error_msg}")

    def gozlemcileri_duyur(self, mesaj: str) -> None:
        """
        Tüm gözlemcilere bildirim gönderir.
        Public metod - _bildirim_yayinla'yı çağırır.
        """
        self._bildirim_yayinla(mesaj)

    def _bildirim_yayinla(self, mesaj):
        bildirim = Bildirim(user_id=None, mesaj=mesaj)
        for g in self.gozlemciler:
            g.update(bildirim)

    def bakiye_goster(self):
        print(f"\n💰 Güncel Bakiye: {self.bakiye} TL")
        if self.aylikLimit > 0:
            print(f"📊 Aylık Limit: {self.aylikLimit} TL")
            kalan = self.aylikLimit - self.bakiye
            if kalan > 0:
                print(f"✅ Kalan Limit: {kalan} TL")
            else:
                print(f"⚠️ Limit Aşıldı: {abs(kalan)} TL")


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


class TransactionFactory:
    @staticmethod
    def create(data: Dict[str, Any]):
        """
        Beklenen giriş örnekleri:
        Gelir: {"islem_tipi": "Gelir", "tutar": 1000, "aciklama": "Maaş", "kaynak": "Şirket", "tarih": "YYYY-MM-DD", "id": "..."}
        Gider: {"islem_tipi": "Gider", "tutar": 300, "aciklama": "Market", "kategori": "Market", "tarih": "YYYY-MM-DD", "id": "..."}
        """
        tip = (data.get("islem_tipi") or data.get("Islem_Tipi") or "").strip()
        tutar = data.get("tutar") if data.get("tutar") is not None else data.get("Tutar")
        aciklama = data.get("aciklama") if data.get("aciklama") is not None else data.get("Aciklama")
        tarih = data.get("tarih") if data.get("tarih") is not None else data.get("Tarih")
        transaction_id = data.get("id") or data.get("Id")

        user_email = data.get("user_email") or data.get("User_Email")

        if tip.lower() == "gelir" or tip == "Gelir":
            kaynak = data.get("kaynak") if data.get("kaynak") is not None else data.get("Kaynak")
            duzenliMi = data.get("duzenliMi") if data.get("duzenliMi") is not None else data.get("DuzenliMi", False)
            if isinstance(duzenliMi, str):
                duzenliMi = duzenliMi.lower() in ("true", "evet", "yes", "1")
            return Gelir(tutar=float(tutar), aciklama=aciklama, kaynak=kaynak, tarih_str=tarih, user_email=user_email, duzenliMi=bool(duzenliMi), id=transaction_id)
        elif tip.lower() == "gider" or tip == "Gider":
            kategori = (
                data.get("kategori")
                if data.get("kategori") is not None else data.get("Kategori")
            )
            zorunluMu = data.get("zorunluMu") if data.get("zorunluMu") is not None else data.get("ZorunluMu", False)
            if isinstance(zorunluMu, str):
                zorunluMu = zorunluMu.lower() in ("true", "evet", "yes", "1")
            return Gider(tutar=float(tutar), aciklama=aciklama, kategori=kategori, tarih_str=tarih, user_email=user_email, zorunluMu=bool(zorunluMu), id=transaction_id)
        else:
            raise ValueError("Geçersiz islem_tipi. 'Gelir' veya 'Gider' olmalı.")
