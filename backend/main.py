from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any, Dict

# Import Firestore client singleton
from backend.firebase_config import get_db
from backend.sistem_modelleri import ButceYonetici, TransactionFactory
from backend.grafik_analiz import get_analysis_summary
from backend.ai_service import run_ai_on_current_data, generate_finance_chat_reply

app = FastAPI(title="CebimdekiVeri API", version="0.1.0")

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TransactionIn(BaseModel):
    islem_tipi: str
    tutar: float
    aciklama: Optional[str] = None
    kategori: Optional[str] = None
    kaynak: Optional[str] = None
    tarih: Optional[str] = None  # YYYY-MM-DD
    user_email: Optional[str] = None
    duzenliMi: Optional[bool] = False  # Gelir için: düzenli gelir mi?
    zorunluMu: Optional[bool] = False  # Gider için: zorunlu gider mi?


class ImagePayload(BaseModel):
    data: Optional[str] = None  # base64 (no header)
    mime_type: Optional[str] = None  # e.g., image/png


class ChartRow(BaseModel):
    tarih: Optional[str] = None
    gelir: Optional[float] = None
    gider: Optional[float] = None


class ChatIn(BaseModel):
    message: Optional[str] = None
    chart_data: Optional[List[ChartRow]] = None
    summary: Optional[Dict[str, Any]] = None  # istemci özet gönderebilir
    image: Optional[ImagePayload] = None


@app.get("/health")
def health_check():
    """Simple health check that verifies Firebase Firestore connectivity."""
    try:
        db = get_db()
        # Attempt a lightweight operation to ensure connectivity
        # Listing collections (may be empty) is sufficient for a ping-like check
        _ = list(db.collections())
        return JSONResponse({"status": "ok", "firebase": True})
    except Exception as e:
        error_msg = str(e).lower()
        error_type = "network" if ("network" in error_msg or "connection" in error_msg or "timeout" in error_msg) else "other"
        return JSONResponse({
            "status": "error",
            "firebase": False,
            "error_type": error_type,
            "detail": str(e),
            "message": "Network hatası: İnternet bağlantınızı kontrol edin." if error_type == "network" else "Firebase bağlantı hatası."
        }, status_code=500)


@app.post("/transactions")
def create_transaction(payload: TransactionIn):
    try:
        trx = TransactionFactory.create(payload.dict())
        yonetici = ButceYonetici()
        limit_info = yonetici.islem_ekle(trx)
        return JSONResponse({"status": "ok", "limit": limit_info})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=400)


@app.get("/transactions")
def list_transactions():
    try:
        db = get_db()
        docs = db.collection("transactions").order_by("Tarih").stream()
        items: List[Dict[str, Any]] = []
        for d in docs:
            data = d.to_dict() or {}
            t = data.get("Tarih")
            # Convert Firestore Timestamp/datetime to iso string
            try:
                data["Tarih"] = t.isoformat()
            except Exception:
                try:
                    # pandas Timestamp or other types
                    from pandas import to_datetime
                    data["Tarih"] = to_datetime(t).isoformat()
                except Exception:
                    data["Tarih"] = None
            items.append({"id": d.id, **data})
        return JSONResponse({"items": items})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.get("/dashboard-data")
def dashboard_data():
    try:
        summary = get_analysis_summary()
        return JSONResponse(summary)
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.get("/ask-ai")
def ask_ai():
    try:
        advice = run_ai_on_current_data()
        return JSONResponse({"message": advice})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.post("/ask-ai")
def ask_ai_chat(payload: ChatIn):
    try:
        summary = payload.summary or get_analysis_summary()
        chart_data = None
        if payload.chart_data:
            chart_data = [row.dict() for row in payload.chart_data]
        reply = generate_finance_chat_reply(summary, payload.message, chart_data, payload.image.dict() if payload.image else None)
        return JSONResponse({"message": reply})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):
    """Belirtilen ID'ye sahip işlemi siler."""
    try:
        yonetici = ButceYonetici()
        success = yonetici.islem_sil(transaction_id)
        if success:
            return JSONResponse({"status": "ok", "message": "İşlem silindi"})
        else:
            return JSONResponse({"status": "error", "detail": "İşlem bulunamadı"}, status_code=404)
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


class BudgetLimitIn(BaseModel):
    aylikLimit: float


@app.get("/budget-manager/status")
def budget_status():
    """Bütçe yöneticisinin durumunu döndürür (bakiye, limit, işlem sayısı)."""
    try:
        yonetici = ButceYonetici()
        # Firestore'dan en güncel durumu çekerek tutarlılık sağla
        try:
            yonetici.gecmisi_yukle()
        except Exception:
            # Sessizce geç; en azından mevcut bellek durumunu döndür
            pass
        return JSONResponse({
            "bakiye": yonetici.bakiye,
            "aylikLimit": yonetici.aylikLimit,
            "islemSayisi": len(yonetici.islemler),
            "gozlemciSayisi": len(yonetici.gozlemciler),
            "veritabaniYolu": yonetici.veritabaniYolu,
        })
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.put("/budget-manager/limit")
def set_budget_limit(payload: BudgetLimitIn):
    """Aylık limiti günceller."""
    try:
        yonetici = ButceYonetici()
        yonetici.aylikLimit = payload.aylikLimit
        return JSONResponse({"status": "ok", "aylikLimit": yonetici.aylikLimit})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.post("/budget-manager/load-history")
def load_history():
    """Firestore'dan geçmiş işlemleri yükler."""
    try:
        yonetici = ButceYonetici()
        yonetici.gecmisi_yukle()
        return JSONResponse({
            "status": "ok",
            "islemSayisi": len(yonetici.islemler),
            "bakiye": yonetici.bakiye,
        })
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.post("/budget-manager/save")
def save_data():
    """Tüm işlemleri Firestore'a kaydeder."""
    try:
        yonetici = ButceYonetici()
        yonetici.veriyi_kaydet()
        return JSONResponse({"status": "ok", "message": "Veriler kaydedildi"})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.post("/budget-manager/notify")
def notify_observers(payload: Dict[str, str]):
    """Gözlemcilere bildirim gönderir."""
    try:
        yonetici = ButceYonetici()
        mesaj = payload.get("mesaj", "")
        yonetici.gozlemcileri_duyur(mesaj)
        return JSONResponse({"status": "ok", "message": "Bildirim gönderildi"})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


# For local debug via: python backend/main.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
