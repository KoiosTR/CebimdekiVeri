# 💰 CebimdekiVeri: Kişisel Bütçe ve Tahmin Asistanı

**CebimdekiVeri**, kullanıcıların gelir ve giderlerini takip etmesini sağlayan, geçmiş verileri analiz ederek gelecek ayki finansal durumlarını istatistiksel algoritmalarla tahmin eden Python tabanlı bir terminal uygulamasıdır.

Bu proje, **Sistem Analizi ve Tasarımı** dersi kapsamında; Nesne Yönelimli Programlama (OOP) prensipleri ve Yazılım Tasarım Desenleri (Design Patterns) kullanılarak geliştirilmiştir.

---

## 🚀 Özellikler

* **📊 Kişiselleştirilmiş Veri Simülasyonu:** Kullanıcının gerçek harcama alışkanlıklarına göre geçmiş 1 yıllık veriyi otomatik oluşturur.
* **🔮 Gelecek Tahmini:** Geçmiş harcama trendlerini (Hareketli Ortalama Yöntemi) analizerek gelecek ayın tahmini giderini hesaplar.
* **🔔 Akıllı Bildirim Sistemi (Observer Pattern):** Bakiye kritik seviyeye düştüğünde veya eksiye indiğinde kullanıcıyı anlık uyarır.
* **📈 Görsel Analiz:** Gelir-Gider dengesini ve harcama dağılımını grafiklerle (Pie & Line Chart) görselleştirir.
* **📄 Raporlama:** İsteğe bağlı formatlarda (PDF/Excel simülasyonu) finansal rapor üretir.

---

## 🛠️ Kullanılan Teknolojiler ve Mimariler

Proje geliştirilirken aşağıdaki **Tasarım Desenleri (Design Patterns)** aktif olarak kullanılmıştır:

1.  **Singleton Pattern (`ButceYonetici`):** Sistem genelinde veri tutarlılığını sağlamak için tek bir yönetici sınıfı oluşturulmuştur.
2.  **Observer Pattern (`Kullanici`):** Bütçe durumu değiştiğinde kullanıcı nesneleri otomatik olarak bilgilendirilir (Event-Driven yaklaşım).
3.  **Factory Pattern (`RaporFactory`):** Kullanıcının isteğine göre (PDF veya Excel) dinamik rapor nesneleri üretilir.
4.  **Template/Strategy:** Gelir ve Gider sınıfları, soyut `Islem` sınıfından türetilerek (Inheritance) genişletilebilir bir yapı kurulmuştur.

**Kütüphaneler:**
* `Python 3.x`
* `Pandas` (Veri Analizi)
* `Matplotlib` & `Seaborn` (Veri Görselleştirme)

---

## ⚙️ Kurulum ve Çalıştırma

Projeyi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

### 1. Gerekli Kütüphaneleri Yükleyin
Terminale şu komutu yazarak bağımlılıkları yükleyin:
```bash
pip install pandas matplotlib seaborn
```

---

## 📂 Dosya Rehberi (Tüm Proje)
**Kök:**
- `README.md`: Bu doküman.
- `requirements.txt`: Python bağımlılıkları (pandas, matplotlib, seaborn).
- `package.json`, `package-lock.json`: Frontend bağımlılıkları (yalnızca `firebase` tanımlı; Node ≥20 gerekir).
- `.firebaserc`, `firebase.json`, `firestore.rules`, `firestore.indexes.json`: Firebase/Firestore proje ve kural dosyaları. **Not:** `firestore.rules` tarih bazlı herkese açık; üretimde kimlik doğrulama ile sıkılaştırın.
- `serviceAccountKey.json`: Firebase servis hesabı anahtarı. **Kesinlikle gizli tutun, repodan çıkarın.**
- `.venv/`, `node_modules/`: Yerel sanal ortam ve JS bağımlılıkları (sürüm kontrolüne dahil edilmemeli).

**Backend (Python, terminal + yardımcılar):**
- `main.py`: Terminal arayüzü; gelir/gider ekleme, bakiye gösterme, grafik ve rapor akışını yönetir.
- `sistem_modelleri.py`: Temel domain sınıfları (`Islem`, `Gelir`, `Gider`), gözlemci (`Kullanici`), `ButceYonetici` (Singleton) ve rapor fabrikası (`RaporFactory`).
- `grafik_analiz.py`: `butce_verisi.csv`'den veriyi okuyup gelir-gider trendleri ve kategori dağılımı grafiklerini çizer; son 3 ay ortalamasına dayalı tahmin üretir.
- `veri_uretici.py`: Kullanıcı girdilerine göre son 1 yılı simüle eden `butce_verisi.csv` dosyasını oluşturur.
- `backend/ai_service.py`: Analiz özetinden esprili finans tavsiyesi üretir; Gemini → OpenAI → yerel heuristik sırasıyla dener.
- `backend/firebase_config.py`: Firebase Admin/Firestore istemcisini ortam değişkeni veya `serviceAccountKey.json` ile başlatan yardımcı.

**Docs:**
- `docs/README_UML.md`: UML sınıf listesi ve PlantUML diyagramı.

**Frontend:**
- `frontend/`: Vite/Tailwind iskeleti; şimdilik yalnız `firebase` bağımlılığı tanımlı (uygulama kodu eklenmemiş). Yapı dosyaları: `vite.config.js`, `tailwind.config.js`, `postcss.config.js`, `index.html`, `src/` klasörü.
