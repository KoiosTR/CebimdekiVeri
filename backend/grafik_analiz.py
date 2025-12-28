import pandas as pd
from typing import Dict, Any

from backend.firebase_config import get_db


def _fetch_transactions_df() -> pd.DataFrame:
    try:
        db = get_db()
        docs = db.collection("transactions").stream()

        rows = []
        for d in docs:
            data = d.to_dict() or {}
            # Normalize fields and provide defaults if missing
            tarih = data.get("Tarih")  # Firestore Timestamp or datetime
            islem_tipi = data.get("Islem_Tipi")
            aciklama = data.get("Aciklama")
            kaynak = data.get("Kaynak")
            tutar = data.get("Tutar")

            # Kategori belirleme: Eğer gider ve Kategori boşsa Aciklama'yı kategori olarak kullan
            kategori_raw = data.get("Kategori") or data.get("kategori")
            if (not kategori_raw) and islem_tipi == "Gider" and aciklama:
                kategori_raw = aciklama
            kategori = (kategori_raw or "Bilinmiyor")

            rows.append({
                "Tarih": pd.to_datetime(tarih) if tarih is not None else pd.NaT,
                "Kategori": kategori,
                "Tutar": float(tutar) if tutar is not None else 0.0,
                "Islem_Tipi": islem_tipi,
                "Aciklama": aciklama,
                "Kaynak": kaynak,
            })

        if not rows:
            return pd.DataFrame(columns=["Tarih", "Kategori", "Tutar", "Islem_Tipi", "Aciklama", "Kaynak"])  # empty

        df = pd.DataFrame(rows)
        df = df.dropna(subset=["Tarih"]).copy()
        df["Tarih"] = pd.to_datetime(df["Tarih"])  # ensure dtype
        return df
    except Exception as e:
        error_msg = str(e).lower()
        if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
            raise RuntimeError(
                f"Firestore'dan veri çekilemedi: Network hatası. İnternet bağlantınızı kontrol edin. Detay: {e}"
            ) from e
        raise



def get_analysis_summary() -> Dict[str, Any]:
    """
    Firestore'dan veriyi çekip DataFrame'e dönüştürür, mevcut analiz ve tahmin mantığını uygular
    ve sonuçları JSON uyumlu bir sözlük olarak döndürür.
    """
    df = _fetch_transactions_df()
    if df.empty:
        return {
            "message": "Veri bulunamadı",
            "toplam_gelir": 0,
            "toplam_gider": 0,
            "gunluk_ozet": [],
            "aylik_ozet": [],
            "tahmin": {"gelir": 0, "gider": 0},
            "kategori_dagilimi": {},
        }

    # Günlük özet: Her gün için gelir ve gider toplamları
    sadece_giderler = df[df['Islem_Tipi'] == 'Gider'].copy()
    # Kategori normalizasyonu: boş/None -> Bilinmiyor, trim ve Title Case
    if not sadece_giderler.empty:
        sadece_giderler['Kategori'] = (
            sadece_giderler['Kategori']
            .fillna('Bilinmiyor')
            .astype(str)
            .str.strip()
            .replace({'': 'Bilinmiyor'})
            .str.title()
        )
    
    # Tarih sütununu normalize et (sadece tarih, saat bilgisi yok)
    df['Tarih_Gun'] = pd.to_datetime(df['Tarih']).dt.normalize()
    
    # Günlük özet: Her gün için gelir ve gider toplamları
    gunluk_ozet = df.groupby([df['Tarih_Gun'], 'Islem_Tipi'])['Tutar'].sum().unstack(fill_value=0)
    
    if 'Gelir' not in gunluk_ozet.columns:
        gunluk_ozet['Gelir'] = 0
    if 'Gider' not in gunluk_ozet.columns:
        gunluk_ozet['Gider'] = 0
    
    # Aylık özet (tahmin için hala gerekli)
    aylik_ozet = df.groupby([pd.Grouper(key='Tarih', freq='ME'), 'Islem_Tipi'])['Tutar'].sum().unstack().fillna(0)

    if 'Gelir' not in aylik_ozet.columns:
        aylik_ozet['Gelir'] = 0
    if 'Gider' not in aylik_ozet.columns:
        aylik_ozet['Gider'] = 0

    son_3_ay_gelir_ort = float(aylik_ozet['Gelir'].tail(3).mean()) if not aylik_ozet.empty else 0.0
    son_3_ay_gider_ort = float(aylik_ozet['Gider'].tail(3).mean()) if not aylik_ozet.empty else 0.0

    toplam_gelir = float(df[df['Islem_Tipi'] == 'Gelir']['Tutar'].sum())
    toplam_gider = float(df[df['Islem_Tipi'] == 'Gider']['Tutar'].sum())

    kategori_toplam = (
        sadece_giderler.groupby("Kategori")["Tutar"].sum()
        if not sadece_giderler.empty else pd.Series(dtype=float)
    )
    kategori_dagilimi = {str(k): float(v) for k, v in kategori_toplam.to_dict().items()}

    # Günlük özetin JSON'a uygun hali (TÜM günler, sınırlama yok)
    gunluk_list = []
    if not gunluk_ozet.empty:
        # Tüm günleri göster (sıralı)
        for idx, row in gunluk_ozet.iterrows():
            # idx bir Timestamp olabilir, normalize et
            if isinstance(idx, pd.Timestamp):
                tarih_str = idx.strftime('%Y-%m-%d')
            else:
                tarih_str = pd.to_datetime(idx).strftime('%Y-%m-%d')
            gunluk_list.append({
                "gun": tarih_str,
                "gelir": float(row.get('Gelir', 0.0)),
                "gider": float(row.get('Gider', 0.0)),
            })
        # Tarihe göre sırala
        gunluk_list.sort(key=lambda x: x['gun'])
    
    # Aylık özetin JSON'a uygun hali (tahmin için) - Ayın ilk günü olarak göster
    aylik_list = []
    if not aylik_ozet.empty:
        for idx, row in aylik_ozet.iterrows():
            # Ayın ilk günü olarak göster (daha anlamlı)
            ay_baslangic = idx.replace(day=1)
            aylik_list.append({
                "ay": ay_baslangic.strftime('%Y-%m-%d'),
                "gelir": float(row.get('Gelir', 0.0)),
                "gider": float(row.get('Gider', 0.0)),
            })

    return {
        "toplam_gelir": toplam_gelir,
        "toplam_gider": toplam_gider,
        "tahmin": {
            "gelir": son_3_ay_gelir_ort,
            "gider": son_3_ay_gider_ort,
        },
        "gunluk_ozet": gunluk_list,  # Günlük veri (chart için)
        "aylik_ozet": aylik_list,  # Aylık veri (tahmin için)
        "kategori_dagilimi": kategori_dagilimi,
    }
