# 🎓 Voice-Guided Academic Solver (VGAS)

VGAS, üniversite düzeyindeki karmaşık problemleri görsel girdiden işitsel rehberliğe dönüştüren, bulut tabanlı bir akademik asistandır. Sistem, bir donanım kontrolcüsü (Raspberry Pi) ve güçlü bir bulut arka planının (Nitro + Gemini) senkronize çalışmasıyla, öğrencilere problemleri adım adım kağıda dökme imkanı tanır.

---

## 🏗️ Sistem Mimarisi

Proje, düşük gecikmeli veri işleme ve yüksek performans için iki ana katmana ayrılmıştır:

### 🌐 1. Bulut Sunucu (Cloud/Web) - `/web`

Merkezi işlem birimi olarak çalışır. Herhangi bir VPS veya Cloud platformunda barındırılabilir.

-   **API Endpoint (`/api/analyze`):** Raspberry Pi'dan gelen görüntüleri karşılar.
-   **Zeka:** Gemini 1.5 Pro Vision API kullanarak problemi analiz eder ve çözüm mantığını kurar.
-   **Ses Sentezleme:** ElevenLabs API aracılığıyla çözüm adımlarını doğal bir insan sesine dönüştürür.
-   **Teknoloji:** Nitro (UnJS), TypeScript, ElevenLabs SDK, Google Generative AI.

### 🤖 2. Uç Cihaz (Controller) - `/controller`

Öğrencinin masasında bulunan fiziksel donanımı yönetir.

-   **Görüntü Yakalama:** Pi Camera üzerinden yüksek çözünürlüklü problem çekimi.
-   **İletişim:** Yakalanan veriyi Bulut API'ye asenkron olarak iletir.
-   **Oynatma:** Sunucudan dönen sesli komutları hoparlör üzerinden öğrenciye aktarır.
-   **Teknoloji:** Python/Node.js, Raspberry Pi OS.

---

---

## ✨ Ana Özellikler

-   **Dikte Modu:** Matematiksel ifadeleri ($ax^2 + bx + c$) sadece sonuç olarak değil, yazım hızına uygun talimatlarla söyler.
-   **Akıllı Eleme (MCQ):** Çoktan seçmeli sorularda yanlış şıkların neden elendiğini mantıksal olarak açıklar.
-   **LaTeX'ten Doğal Dile:** Karmaşık formülleri işitsel olarak betimler (Örn: "İntegral sembolü içine x kare yazın").
-   **Hibrit Yapı:** Ağır işlemleri bulutta yaparak Raspberry Pi üzerinde minimum kaynak tüketimi sağlar.

---

## 🛠️ Kurulum

### Bulut Sunucu Kurulumu (`/web`)

```bash
cd web
pnpm install
# .env dosyasını oluşturun:
# GEMINI_API_KEY=...
# ELEVENLABS_API_KEY=...
pnpm dev
```

### Raspberry Pi Kurulumu (`/controller`)

Raspberry Pi üzerinde terminali açın ve cihazı hazırlamak için kurulum scriptini çalıştırın:

```bash
curl -sSL https://raw.githubusercontent.com/yigit0356/vgas/refs/heads/main/controller_setup.sh | bash
```

Script; kamera sürücülerini, gerekli kütüphaneleri ve ses çıkış ayarlarını otomatik yapılandırır.

---

🚀 Çalışma Akışı

1. **Capture**: Öğrenci butona basar, Raspberry Pi fotoğrafı çeker.
2. **Upload**: Fotoğraf, buluttaki /api/analyze endpoint'ine POST edilir.
3. **Process**: Bulut sunucu Gemini ile soruyu çözer, ElevenLabs ile seslendirir.
4. **Execute**: Raspberry Pi, gelen ses dosyasını oynatarak öğrenciyi yönlendirir.

---

⚖️ Kullanım Amacı ve Etik Notu

Bu araç, özellikle **işitsel öğrenme modelini** benimseyen öğrenciler ve **görme güçlüğü/disleksi** gibi engelleri olan bireyler için bir "kişisel öğretmen" konseptiyle geliştirilmiştir. Akademik dürüstlük çerçevesinde, öğrenme sürecini desteklemek amacıyla kullanılması tavsiye edilir.
