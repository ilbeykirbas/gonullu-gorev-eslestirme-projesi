from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import math
from sentence_transformers import SentenceTransformer, util

# ESKİ HALİNİ SİL, SADECE BUNU KULLAN:
print("Türkçe Yapay Zeka Modeli Yükleniyor... (Bu biraz sürebilir)")
# "paraphrase-multilingual-MiniLM-L12-v2" modeli Türkçe için en iyisidir.
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

app = Flask(__name__)
CORS(app)

print("✅ Model ve Algoritma Hazır.")

def init_db():
    conn = sqlite3.connect('rsm_afet.db')
    c = conn.cursor()
    
    # Temiz kurulum
    c.execute("DROP TABLE IF EXISTS gorevler")
    c.execute("DROP TABLE IF EXISTS gonulluler")
    c.execute("DROP TABLE IF EXISTS bolgeler")
    
    # 1. BÖLGELER
    c.execute('''CREATE TABLE bolgeler (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ad TEXT,
                 merkez_x INTEGER,
                 merkez_y INTEGER,
                 yaricap INTEGER)''')

    # 2. GÖREVLER (YENİ SÜTUN: aciklama)
    c.execute('''CREATE TABLE gorevler (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 baslik TEXT,        -- Örn: Tıbbi Destek (Tabloda görünen)
                 aciklama TEXT,      -- Örn: Serum takabilen, dikiş atabilen... (AI için)
                 zorluk_seviyesi INTEGER,
                 x_coord INTEGER,
                 y_coord INTEGER,
                 durum TEXT DEFAULT 'Bekliyor')''')
    
    # 3. GÖNÜLLÜLER
    c.execute('''CREATE TABLE gonulluler (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ad_soyad TEXT,
                 yetenekler TEXT,
                 x_coord INTEGER,
                 y_coord INTEGER,
                 durum TEXT DEFAULT 'Hazır',
                 gorev_id INTEGER,
                 ai_skoru REAL)''')
    
    # --- VERİ GİRİŞİ (DETAYLI AÇIKLAMALAR İLE) ---
    
    # Bölgeler
    c.executemany("INSERT INTO bolgeler (ad, merkez_x, merkez_y, yaricap) VALUES (?, ?, ?, ?)", [
        ("Merkez Kampüs", 50, 50, 30),
        ("Kuzey Sahası", 20, 80, 25)
    ])
    
    # Görevler: Artık hem BAŞLIK hem de DETAYLI AÇIKLAMA var
    gorevler = [
        (
            "Arama Kurtarma (Enkaz)", 
            "Yıkılan binalarda göçük altında kalan vatandaşlara ulaşmak için beton kırıcı, hilti, demir kesme makası ve sismik dinleme cihazlarını kullanabilen teknik personel. İnşaat mühendisi, madenci, itfaiyeci veya AFAD eğitimi almış, fiziksel gücü yüksek, kapalı alan fobisi olmayan saha personeli aranıyor.", 
            5, 10, 10
        ),
        (
            "Acil Tıp ve Sağlık", 
            "Sahra hastanesinde ve acil müdahale çadırlarında görev alacak doktor, hemşire, paramedik, ATT ve cerrahlar. Açık yaraya dikiş atma (sütür), damar yolu açma, entübasyon, triyaj yapma, CPR (kalp masajı) ve ilaç yönetimi konularında uzman, diplomalı, ameliyat yapabilecek sağlık profesyoneli aranıyor.", 
            5, 12, 15
        ),
        (
            "Lojistik ve Depo Yönetimi", 
            "Tırlarla gelen yardım malzemelerinin indirilmesi, kolilerin taşınması, sınıflandırılması ve depolanması. Zincir market veya depo tecrübesi olan, stok sayımı yapabilen, ağır yük kaldırabilen, forklift kullanabilen veya insan zinciri ile elden ele koli taşıyacak beden gücü yüksek gönüllüler.", 
            2, 80, 80
        ),
        (
            "Tercümanlık ve Çeviri", 
            "Yurt dışından gelen uluslararası arama kurtarma ekipleriyle (USAR) yerel halk ve yetkililer arasında iletişimi sağlayacak tercümanlar. İngilizce, Arapça, Rusça, İspanyolca veya Fransızca dillerini akıcı konuşabilen, sözlü çeviri yapabilen, dilbilim veya mütercim tercümanlık geçmişi olan kişiler.", 
            3, 85, 75
        ),
        (
            "Sıcak Yemek ve Mutfak", 
            "Mobil mutfak tırlarında veya aşevlerinde binlerce kişiye yemek pişirecek ve dağıtacak personel. Aşçı, aşçı yardımcısı, gıda mühendisi veya toplu yemek dağıtımı (katering) tecrübesi olan, hijyen kurallarına dikkat eden, patates/soğan doğrama ve kazan karıştırma işlerini yapacak gönüllüler.", 
            1, 50, 50
        ),
        (
            "Psikososyal Destek",
            "Afetzede çocuklara ve yetişkinlere travma sonrası stres bozukluğu konusunda destek olacak psikolog, psikiyatrist, rehberlik ve psikolojik danışmanlık (PDR) mezunları. Oyun terapisi yapabilen ve insan psikolojisinden anlayan uzmanlar.",
            4, 40, 60
        )
    ]
    c.executemany("INSERT INTO gorevler (baslik, aciklama, zorluk_seviyesi, x_coord, y_coord) VALUES (?, ?, ?, ?, ?)", gorevler)

    conn.commit()
    conn.close()
    print("✅ Veritabanı: Görev Başlıkları ve Detaylı Açıklamalar ayrıştırıldı.")


@app.route('/api/kayit', methods=['POST'])
def kayit_ol():
    data = request.json
    ad = data.get('ad')
    yetenekler = data.get('yetenekler')
    user_x = int(data.get('x', 0))
    user_y = int(data.get('y', 0))

    print(f"\n--- YENİ ANALİZ: {ad} ---")

    conn = sqlite3.connect('rsm_afet.db')
    c = conn.cursor()
    # Zorluk seviyesini çektiğinden emin ol
    c.execute("SELECT id, baslik, aciklama, zorluk_seviyesi, x_coord, y_coord FROM gorevler WHERE durum = 'Bekliyor'")
    tum_gorevler = c.fetchall()

    en_iyi_gorev_id = None
    en_yuksek_skor = -1.0
    en_iyi_gorev_baslik = ""
    en_iyi_gorev_x = None
    en_iyi_gorev_y = None
    
    volunteer_embedding = model.encode(yetenekler)

    for gorev in tum_gorevler:
        g_id, g_baslik, g_aciklama, g_zorluk, g_x, g_y = gorev
        
        # Sadece açıklama üzerinden karşılaştırma yapmak bazen daha temiz sonuç verir
        ai_input_text = g_aciklama 
        task_embedding = model.encode(ai_input_text)
        
        nlp_score = util.cos_sim(volunteer_embedding, task_embedding).item()
        
        # --- DEBUG LOG (Konsolda görmek için) ---
        print(f"   > '{g_baslik}' için NLP Skoru: {nlp_score:.4f}")

        # --- DÜZELTME: BARAJ YÜKSELTİLDİ (0.25 -> 0.30) ---
        if nlp_score < 0.30:
            continue

        distance = math.sqrt((g_x - user_x)**2 + (g_y - user_y)**2)
        dist_score = max(0, 1 - (distance / 100))
        
        # Dinamik Ağırlıklar
        if g_zorluk >= 4:
            w_nlp = 0.90
            w_dist = 0.10
        elif g_zorluk <= 2:
            w_nlp = 0.50
            w_dist = 0.50
        else:
            w_nlp = 0.75
            w_dist = 0.25

        final_score = (nlp_score * w_nlp) + (dist_score * w_dist)
        
        print(f"   ✅ [ADAY] Final Skor: {final_score:.3f}")

        if final_score > en_yuksek_skor:
            en_yuksek_skor = final_score
            en_iyi_gorev_id = g_id
            en_iyi_gorev_baslik = g_baslik
            en_iyi_gorev_x = g_x
            en_iyi_gorev_y = g_y
    
    FINAL_BARAJ = 0.50 

    if en_yuksek_skor < FINAL_BARAJ:
        print(f"En yüksek skor ({en_yuksek_skor:.2f}) barajın ({FINAL_BARAJ}) altında kaldı. Atama yapılmadı.")
        en_iyi_gorev_id = None # Atamayı iptal et

    # --- KAYIT İŞLEMLERİ ---
    durum = "Hazır"
    if en_iyi_gorev_id:
        durum = "Görevde"
        c.execute("INSERT INTO gonulluler (ad_soyad, yetenekler, x_coord, y_coord, durum, gorev_id, ai_skoru) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (ad, yetenekler, user_x, user_y, durum, en_iyi_gorev_id, en_yuksek_skor))
    else:
        # Eşleşme yoksa
        c.execute("INSERT INTO gonulluler (ad_soyad, yetenekler, x_coord, y_coord, durum, ai_skoru) VALUES (?, ?, ?, ?, ?, 0)",
                  (ad, yetenekler, user_x, user_y, durum))

    conn.commit()
    conn.close()

    return jsonify({
        "mesaj": "İşlem tamam",
        "atanan_gorev_id": en_iyi_gorev_id,
        "gorev_tanimi": en_iyi_gorev_baslik,
        "gorev_x": en_iyi_gorev_x, 
        "gorev_y": en_iyi_gorev_y,
        "ai_match_score": round(en_yuksek_skor, 3) if en_yuksek_skor > 0 else 0
    })

@app.route('/api/reset', methods=['POST'])
def reset_db():
    init_db() # Veritabanını silip yeniden kurar
    print("\n--- SİSTEM JÜRİ İÇİN SIFIRLANDI ---\n")
    return jsonify({"mesaj": "Veritabanı temizlendi."})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)