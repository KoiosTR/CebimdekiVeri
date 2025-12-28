import os
import base64
from typing import Any, Dict, Optional, List

from backend.grafik_analiz import get_analysis_summary

# Optional: use python-dotenv if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def _format_summary_text(summary: Dict) -> str:
    toplam_gelir = summary.get("toplam_gelir", 0)
    toplam_gider = summary.get("toplam_gider", 0)
    bakiye = toplam_gelir - toplam_gider
    tahmin = summary.get("tahmin", {}) or {}
    t_gelir = tahmin.get("gelir", 0)
    t_gider = tahmin.get("gider", 0)
    return (
        f"Özet: Toplam Gelir={int(toplam_gelir)} TL, Toplam Gider={int(toplam_gider)} TL, "
        f"Bakiye={int(bakiye)} TL, Gelecek Ay Tahmini Gelir={int(t_gelir)} TL, "
        f"Gelecek Ay Tahmini Gider={int(t_gider)} TL."
    )


def generate_finance_advice(summary: Dict) -> str:
    """
    Given numeric analysis summary, produce a short, friendly, slightly humorous advice text.
    If OPENAI_API_KEY is missing, returns a local heuristic message.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    prompt_style = (
        "Sen esprili ve içten bir finans koçusun. Net ama tatmin edici uzunlukta konuş, "
        "yalnızca 1-2 cümleyle sınırlama; gerektiğinde 3-6 cümlede somut öneriler ver. "
        "Övgü + aksiyon önerisi dengesi kur, anlaşılır ve motive edici ol. "
        "Yanıtı markdown formatında ver: kısa bir başlık (#), ardından maddeler. Önemli rakamları **kalın** yaz."
    )
    summary_text = _format_summary_text(summary)

    # 1) Gemini 2.5 Flash (tercih edilen)
    if gemini_key:
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"{prompt_style}\n\n{summary_text}"
            resp = model.generate_content(prompt)
            # SDK'ya göre farklı alan isimleri olabilir; güvenli erişim
            if hasattr(resp, "text") and resp.text:
                return resp.text.strip()
            if hasattr(resp, "candidates") and resp.candidates:
                parts = getattr(resp.candidates[0], "content", None)
                if parts and hasattr(parts, "parts") and parts.parts:
                    return str(parts.parts[0].text).strip()
            # Fallback, eğer boş dönerse
            return "Analize göre harcamalarını dengede tutuyorsun. Küçük iyileştirmelerle daha da iyi olur!"
        except Exception as e:
            error_msg = str(e).lower()
            if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                # Network hatası - sessizce OpenAI'ye geç
                pass
            else:
                # Diğer hatalar için de sessizce geç
                pass

    # Fallback heuristic without calling any external API
    bakiye = summary.get("toplam_gelir", 0) - summary.get("toplam_gider", 0)
    t_gider = (summary.get("tahmin", {}) or {}).get("gider", 0)
    if bakiye < 0:
        return (
            "## Finans Tavsiyesi\n"
            f"- **Bakiye:** {int(bakiye)} TL (negatif)\n"
            f"- **Tahmini Gider (ay):** {int(t_gider)} TL\n"
            "- **Öneri:** Eğlence ve dışarıda yemek kaleminde küçük kesintiler dene; sabit giderleri yeniden pazarlık et."
        )
    return (
        "## Finans Tavsiyesi\n"
        f"- **Bakiye:** {int(bakiye)} TL (pozitif)\n"
        f"- **Tahmini Gider (ay):** {int(t_gider)} TL\n"
        "- **Öneri:** Düzenli giderleri gözden geçir, indirim/pazarlık fırsatlarını değerlendir; birikim oranını artır."
    )


def run_ai_on_current_data() -> str:
    summary = get_analysis_summary()
    return generate_finance_advice(summary)


def _format_chart_data_rows(chart_data: List[Dict[str, Any]]) -> str:
    rows = []
    for row in chart_data[:50]:  # limit to keep prompt small
        tarih = row.get("tarih") or row.get("gun") or row.get("ay")
        gelir = row.get("gelir", 0)
        gider = row.get("gider", 0)
        rows.append(f"- {tarih}: gelir={gelir}, gider={gider}")
    return "\n".join(rows)


def generate_finance_chat_reply(
    summary: Dict,
    user_message: Optional[str] = None,
    chart_data: Optional[List[Dict[str, Any]]] = None,
    image: Optional[Dict[str, str]] = None,
) -> str:
    """
    Chat tarzı istekler için kullanıcı mesajını, grafik verisini ve (varsa) görseli dikkate alarak yanıt üretir.
    Öncelik: GEMINI_API_KEY (vision destekli) -> heuristik.
    """
    import os
    gemini_key = os.getenv("GEMINI_API_KEY")

    system_prompt = (
        "Sen esprili ve içten bir finans koçusun. Net, anlaşılır ve motive edici konuş. "
        "Kullanıcının verileri ve mesajı doğrultusunda doyurucu, uygulanabilir öneriler ver; "
        "yalnızca 1-2 cümleyle sınırlama, 3-6 cümleye kadar somut tavsiyeler sunabilirsin. "
        "Yanıtı markdown formatında ver: kısa bir başlık (#), ardından maddeler; önemli rakamları **kalın** yaz. "
        "Eğer bir görsel (grafik) sağlanırsa, öncelikle görseldeki trendleri ve kritik noktaları yorumla."
    )
    context_text = _format_summary_text(summary)
    chart_text = ""
    if chart_data:
        chart_text = "\nGrafik Verisi (tarih, gelir, gider):\n" + _format_chart_data_rows(chart_data)
    image_text = "\nGörsel: Grafik/çizim eklendi, önce görseli analiz et." if image else ""
    user_text = (user_message or "")

    # Gemini
    if gemini_key:
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"{system_prompt}\n\nVeri Özeti: {context_text}{chart_text}{image_text}\n\nKullanıcı: {user_text}"
            if image and image.get("data") and image.get("mime_type"):
                image_bytes = base64.b64decode(image["data"])
                resp = model.generate_content(
                    [
                        prompt,
                        {
                            "mime_type": image["mime_type"],
                            "data": image_bytes,
                        },
                    ]
                )
            else:
                resp = model.generate_content(prompt)
            if hasattr(resp, "text") and resp.text:
                return resp.text.strip()
        except Exception as e:
            error_msg = str(e).lower()
            # Network veya diğer hatalarda heuristik fallback'e düş
            pass

    # Heuristic fallback
    bakiye = summary.get("toplam_gelir", 0) - summary.get("toplam_gider", 0)
    if bakiye < 0:
        return (
            "## Finans Tavsiyesi\n"
            "- Bakiye negatif.\n"
            "- Bu ay eğlence ve dışarıda yemek kaleminde küçük kesintiler dene.\n"
            "- Sabit giderlerde indirim veya erteleme seçeneklerini ara."
        )
    return (
        "## Finans Tavsiyesi\n"
        "- Bakiye pozitif.\n"
        "- Rutini koru, aylık sabit giderlerde pazarlık/indirim fırsatlarını değerlendir.\n"
        "- Fazlayı otomatik tasarruf/yatırım hesabına yönlendir."
    )
