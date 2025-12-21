# 🛡️ YAPAY KALKAN (Artificial Shield)
### AI Destekli Akıllı Afet Yönetim ve Karar Destek Sistemi

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-green)
![AI](https://img.shields.io/badge/AI-NLP%20%26%20Semantic%20Search-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**Yapay Kalkan**, afet durumlarında sınırlı insan kaynağını en verimli şekilde yönetmek için geliştirilmiş yeni nesil bir yapay zeka platformudur. Geleneksel sistemlerin aksine, sadece kelime eşleşmesine bakmaz; gönüllülerin yeteneklerini **Doğal Dil İşleme (NLP)** ile analiz eder ve anlamsal olarak en uygun göreve atar.

---

## 🚀 Projenin Amacı ve Çözüm

Afet anlarında binlerce gönüllü sisteme giriş yapar ("Doktorum", "İnşaatçıyım", "Elimden her iş gelir" vb.). Klasik veritabanı sorguları bu serbest metinleri doğru sınıflandıramaz.

**Yapay Kalkan şunları yapar:**
1.  **Anlar:** "Enkaz kaldırma" ile "Hilti kullanabilirim" arasındaki anlamsal bağı kurar.
2.  **Hesaplar:** Gönüllünün olay yerine olan uzaklığını GPS verisiyle ölçer.
3.  **Karar Verir:** Görevin hayati önemine (Zorluk Seviyesi) göre uzmanlığa mı yoksa hıza mı öncelik vereceğini dinamik olarak belirler.

---

## ⚙️ Temel Özellikler

* **🧠 Semantik Yapay Zeka (NLP):** `paraphrase-multilingual-MiniLM-L12-v2` modeli kullanılarak Türkçe metinler 384 boyutlu vektör uzayında analiz edilir.
* **⚖️ Dinamik Ağırlıklandırma (Dynamic Weighting):**
    * *Kritik Görevler (Örn: Ameliyat):* %90 Uzmanlık - %10 Konum
    * *Lojistik Görevler (Örn: Koli Taşıma):* %50 Uzmanlık - %50 Konum
* **📍 Konum Tabanlı Hibrit Skor:** Uzmanlık puanı ile mesafe puanı harmanlanarak tek bir başarı skoru üretilir.
* **🛡️ Güvenlik Barajı (Threshold):** Sistem, %50'nin altındaki riskli eşleşmeleri otomatik olarak eler.
* **📊 Gerçek Zamanlı Dashboard:** Atamaları ve AI skorlarını anlık gösteren web arayüzü.

---

## 🛠️ Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Gereksinimler
* Python 3.8 veya üzeri
* İnternet bağlantısı (İlk açılışta AI modelini indirmek için)

### 2. Kütüphanelerin Yüklenmesi
Terminali proje klasöründe açın ve gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

### 3. Uygulamanın Başlatılması
Backend sunucusunu başlatın:


```bash
python app.py
```

Not: İlk çalıştırmada yapay zeka modelinin (yaklaşık 400MB) indirilmesi internet hızınıza göre 1-2 dakika sürebilir. Konsolda ✅ Model ve Algoritma Hazır yazısını bekleyin.

### 4. Kullanım
Tarayıcınızda proje klasöründeki frontend.html dosyasına çift tıklayarak paneli açın.

Dashboard: Mevcut atamaları izleyin.

Gönüllü Kayıt: Yeni gönüllü verisi girerek AI'ın kararını test edin.

## 🧮 Algoritma Mantığı (Nasıl Çalışır?)
Sistem, her gönüllü-görev ikilisi için şu formülü uygular:

$$ Final Skor = (NLP Skor \times Ağırlık_{NLP}) + (Mesafe Skor \times Ağırlık_{Mesafe}) $$

Vektör Dönüşümü: Gönüllü yetenekleri ve görev tanımları vektörlere çevrilir.

Cosine Similarity: İki vektör arasındaki açı hesaplanarak anlamsal benzerlik (0-1 arası) bulunur.

Zorluk Kontrolü: Görevin zorluk_seviyesi parametresine bakılarak ağırlık katsayıları değiştirilir.

Atama: En yüksek skoru alan görev belirlenir. Eğer skor %50 üzerindeyse atama yapılır, değilse gönüllü havuzda bekletilir.

## 📂 Dosya Yapısı
app.py: Flask Backend, AI Modeli ve Veritabanı Yönetimi.

frontend.html: Kullanıcı Arayüzü (Bootstrap 5).

requirements.txt: Gerekli Python kütüphaneleri.

rsm_afet.db: SQLite veritabanı (Otomatik oluşur).

## 🤝 Katkıda Bulunanlar
Geliştirici: [Adınız Soyadınız]

Kurum/Organizasyon: RSM (Resilience Shield Management)

"Afet yönetiminde saniyeler hayat kurtarır, Yapay Kalkan doğru kaynağı saniyeler içinde doğru yere yönlendirir."
