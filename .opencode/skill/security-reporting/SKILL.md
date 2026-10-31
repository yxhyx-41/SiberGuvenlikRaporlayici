---
name: security-reporting
description: Güvenlik analiz bulgularını yapılandırılmış ve anlaşılır bir güvenlik raporuna dönüştürmede kullan. Rapor, risk seviyesi, sınıflandırma, öneri ve risk yazımı gerektiren güvenlik analizi/raporlama görevlerinde tetikle. "güvenlik raporu", "security report", "risk seviyesi", "bulgu raporu", "finding" gibi anahtar kelimelerde kullan.
---

# Security Reporting

Güvenlik analizlerinden elde edilen ham bulguları, okunabilir ve aksiyona dönüştürülebilir yapılandırılmış bir güvenlik raporuna dönüştürmek için izlenen prosedürdür.

Bu skill, `.opencode/rules/project.md` dosyasındaki tüm proje kurallarıyla birlikte uygulanır. Bu skill hiçbir kuralı geçersiz kılmaz; özellikle:
- Güvenlik araçları yalnızca kullanıcının kendi sistemi üzerinde veya izin verilen ortamlarda kullanılır.
- Hassas bilgiler (parola, API anahtarı, token vb.) asla rapora ham olarak yazılmaz; gerektiğinde maskelenir.
- Yalnızca analiz kapsamındaki bulgular raporlanır; kapsam dışına çıkılmaz.

## 1. Güvenlik Bulgularının Sınıflandırılması

Her bulgu önce bir **kategori** altında sınıflandırılır. Bulgu kategorileri şunlardır:

- **Kimlik ve Erişim** — kimlik doğrulama, yetkilendirme, oturum yönetimi, ayrıcalık sorunları
- **Ağ Güvenliği** — açık port, servis maruziyeti, zayıf protokol, yapılandırma hataları
- **Uygulama Güvenliği** — girdi doğrulama, enjeksiyon (SQL/XSS/komut), güvensiz deserialization
- **Veri Koruma** — şifreleme eksikliği, hassas veri sızıntısı, yedekleme/şifreleme yokluğu
- **Sistem ve Konfigürasyon** — güncel olmayan yazılım, eksik yama, zayıf varsayılan ayarlar
- **Olay ve Loglama** — loglama eksikliği, izleme yokluğu, denetim izi yokluğu
- **Fiziksel ve Çevresel** — fiziksel erişim, çevresel kontroller eksikliği
- **Diğer** — yukarıdakilere uymayan bulgular (her zaman açık bir notla)

## 2. Risk Seviyesinin Belirlenmesi

Her bulguya aşağıdaki beş kademeli risk seviyesinden biri atanır. Seviye; **olasılık (tehdidin gerçekleşme ihtimali)** ve **etki (gerçekleşirse vereceği zarar)** çarpımıyla belirlenir.

- **Kritik (Critical)** — Uzaktan, kimlik doğrulamasız istismar edilebilir; sistem veya veri bütünlüğü tamamen tehlikeye girer. Acil müdahale gerekir.
- **Yüksek (High)** — Önemli bir fonksiyonu/veriyi tehlikeye atan, ancak mutlaka yetkilendirme veya belirli koşullar gerektiren açık.
- **Orta (Medium)** — Etki sınırlı veya olasılık düşük; sistemin güvenlik duruşunu zayıflatır ama doğrudan ciddi hasar vermez.
- **Düşük (Low)** — Sınırlı etki, düşük olasılık; öncelikli olmayan iyileştirme.
- **Bilgi (Informational)** — Bir açık değil; gözlem, iyileştirme önerisi veya en iyi uygulama notu.

Risk seviyesi atanırken şu kriterler sıralı değerlendirilir:
1. İstismar edilebilirlik (uzaktan/yeti izinsiz mi?)
2. Gerekli yetkilendirme/önkoşullar
3. Etkilenen varlıkların gizlilik/bütünlük/erişilebilirlik değeri
4. Olasılık ve etki her bulguda kısaca gerekçelendirilir.

## 3. Bulguların Raporlanması

- Her bulgu için aşağıdaki **Bölüm 4**'teki alanların tümü doldurulur.
- Bulgular önce **risk seviyesine göre** (Kritik → Bilgi), sonra kategoriye göre sıralanır.
- Dil, hedef kitleye göre tutarlı olur; jargon yalın bir açıklamayla desteklenir.
- Ham teknik ayrıntı (log, çıktı) yalnızca gerektiğinde ve maskelenmiş halde verilir.
- Teknik olmayan paydaşlar için her bulgunun sonucu bir cümlede özetlenir.

## 4. Her Bulgu İçin Bulunan Bilgiler

Her bir bulgu için şu alanlar doldurulur:

- **ID** — Bulguyu benzersiz tanımlayan numara (örn. `F-001`)
- **Başlık** — Kısa ve açıklayıcı bulgu adı
- **Kategori** — Bölüm 1'deki kategorilerden biri
- **Risk Seviyesi** — Bölüm 2'deki seviyelerden biri
- **Konum / Etkilenen Varlık** — Bulgunun tespit edildiği konum, servis, dosya veya sistem
- **Açıklama** — Bulgunun ne olduğu ve nasıl tespit edildiği (teknik + sade açıklama)
- **Kanıt** — Doğrulanabilir, mümkünse maskelenmiş kanıt (çıktı, log, gözlem)
- **Olasılık** — Tehdidin gerçekleşme ihtimali (Düşük/Orta/Yüksek)
- **Etki** — Gerçekleşirse vereceği zarar (Düşük/Orta/Yüksek)
- **Risk Gerekçesi** — Olasılık ve etkinin neden böyle değerlendirildiği
- **Önerilen Çözüm** — somut, adım adım, uygulanabilir düzeltme (Bölüm 5)
- **Durum** — `Açık` / `İlerlemede` / `Kapalı` / `Azaltıldı`

## 5. Çözüm / Öneri Yazımı

Öneriler **spesifik**, **önceliklendirilmiş** ve **uygulanabilir** olmalıdır:

- Riske göre önceliklendirilir (Kritik/Yüksek riskli olanlar ilk sırada).
- Somut adımlar halinde yazılır; "güvenliği artır" gibi muğlak ifadeler yerine eyleme dönüştürülebilir adımlar verilir.
- Mümkünse birden fazla seçenek sunulur (örn. hızlı önlem / kalıcı çözüm).
- Her öneriye, çözüldüğünde **risk seviyesinin neye düşeceği** notu eklenir (örn. "Yüksek → Düşük").
- Hassas bilgi içeren hiçbir öneri gerçek parola/token örneği içermez.
- Temizlenemeyen bir açık varsa **azaltma (mitigation)** stratejisi açıklanır.

## 6. Raporun Genel Yapısı

Bir güvenlik raporu aşağıdaki bölümleri sırayla içerir. Zorunlu çekirdek bölümler: (1), (2), (3), (4), (7), (8).

1. **Yönetici Özeti (Executive Summary)** — hedef, kapsam, dönem, genel seviye ve en kritik bulguların 5 maddelik özeti
2. **Kapsam ve Yöntem (Scope & Methodology)** — analiz edilen sistemler, kullanılan yöntemler/araçlar, sınırlamalar
3. **Genel Risk Özeti (Risk Overview)** — seviyelere göre bulgu dağılımı (tablo veya sayaç)
4. **Bulgular (Findings)** — Bölüm 4 formatında tüm bulgular, risk sırasına göre
5. **Risk Puanlama / Matrisi** — (opsiyonel) sayısal puanlama kullanılıyorsa açıklama
6. **Ekler** — (opsiyonel) ham log, araç çıktıları, referanslar
7. **Önerilen Öncelikli Eylemler (Prioritized Actions)** — ilk yapılması gerekenler kısa liste
8. **Sonuç (Conclusion)** — genel değerlendirme ve sonraki adımlar

## 7. Örnek Rapor Formatı

```markdown
# Siber Güvenlik Raporu — <Hedef/Sistem Adı>

**Tarih:** YYYY-AA-GG
**Kapsam:** <analiz edilen sistemler>
**Yöntem:** <kullanılan araçlar/yöntemler>

## 1. Yönetici Özeti
<3-5 madde; en kritik bulgular ve genel risk durumu>

## 2. Kapsam ve Yöntem
<analiz edilen varlıklar, yöntemler, sınırlamalar>

## 3. Genel Risk Özeti

| Risk Seviyesi | Adet |
|---------------|------|
| Kritik        | 1    |
| Yüksek        | 2    |
| Orta          | 1    |
| Düşük         | 3    |
| Bilgi         | 2    |
| **Toplam**    | **9**|

## 4. Bulgular

### F-001 — <Başlık>
- **Kategori:** <kategori>
- **Risk Seviyesi:** Kritik
- **Konum:** <konum>
- **Açıklama:** <ne olduğu ve nasıl tespit edildiği>
- **Kanıt:** <maskelenmiş kanıt>
- **Olasılık:** Yüksek | **Etki:** Yüksek
- **Risk Gerekçesi:** <neden bu seviye>
- **Çözüm:** 
  1. <adım 1>
  2. <adım 2>
  - *Risk seviyesi çözüldüğünde: Kritik → Düşük*
- **Durum:** Açık

## 5. Önerilen Öncelikli Eylemler
1. <eylem 1>
2. <eylem 2>

## 6. Sonuç
<genel değerlendirme ve sonraki adımlar>
```

## Kullanımdaki Notlar

- Bu skill, ham analiz verisini rapora **dönüştürmek** içindir; analizi yapan araç prosedürü bu skill'i kapsamaz.
- Rapor her zaman doğrulanabilir (kanıt) ve açıklanabilir (gerekçe) olmalıdır.
- `.opencode/rules/project.md` kuralları çelişki durumunda önceliklidir.
