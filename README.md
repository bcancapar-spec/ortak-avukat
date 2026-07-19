# Ortak Avukat · Türk Hukuku Co-Counsel Sistemi

> Kıdemli bir **Ortak Avukat (Co-Counsel)** kimliğiyle çalışan, İlk İlkeler ve **illiyet bağı** odaklı derin muhakeme yürüten Türk hukuku metodoloji sistemi. Bir Claude Code / Cowork **plugin marketplace** deposu.

**Sürüm:** 0.5.0 (metodoloji v3.20) · **Yazar:** Av. Bayram Can Çapar · **20 skill** (çekirdek + 19 `oa-*` parça)

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır.** Bu eserin fikri mülkiyeti ile tüm mali ve manevi hakları münhasıran Av. Bayram Can Çapar'a aittir.Ticari amaçla klonlanıp kullanılmadığı müddetçe ücretsizdir.  (5846 sayılı FSEK). Depo kamuya açıktır; izinsiz kopyalama/dağıtma/türev yasaktır.Yalnızca Yargı Pro MCP  geliştiren ekibin münhasıran kullanımı ve geliştirmesi serbesttir ve tam yetkiyle ticari iş kapsamı olmaksızın geliştirmeye yetkilidir.  Bkz. [LICENSE](LICENSE) ve [NOTICE](NOTICE).

---

## Ne işe yarar

Dilekçe / temyiz / istinaf / cevap dilekçesi yazımı, dava-dosya-uyuşmazlık analizi, hukuki mütalaa, içtihat & mevzuat araştırması, AYM bireysel başvuru, sözleşme inceleme ve tahriri — Türk hukukunun **herhangi bir dalında**. Sistem kişilere değil **yönteme** bağlıdır; her olgusal unsuru (künye, madde, tarih, içtihat) resmî kaynaktan **doğrular**, halüsinasyonu yapısal olarak dışlar.

## Kurulum (2 adım)

### 1) Yargı Pro MCP bağlantısını kurun — zorunlu

Ailenin içtihat/mevzuat/kurum-kararı doğrulaması **Yargı Pro** MCP sunucusuna dayanır. Claude Code'da **connectors** bölümünden ekleyin:

```
https://yargi.betaspacestudio.com/mcp
```

veya komut satırından:

```bash
claude mcp add --transport http "yargipro" https://yargi.betaspacestudio.com/mcp
```

Kimlik doğrulama (OAuth) akışını tamamlayın. Bu bağlantı olmadan yetenekler künye doğrulaması yapamaz ve "elden-teyitli" moda düşer.

### 2) Eklentiyi kurun

```
/plugin marketplace add <github-kullanıcı>/ortak-avukat
/plugin install ortak-avukat@ortak-avukat
```

> `<github-kullanıcı>` yerine depoyu yüklediğiniz GitHub hesabını yazın. Alternatif olarak `releases` altındaki `.plugin` dosyasını sohbete bırakıp onaylayarak da kurabilirsiniz.

## Depo yapısı

```
ortak-avukat/
├── .claude-plugin/
│   └── marketplace.json          # marketplace kataloğu
├── plugins/
│   └── ortak-avukat/             # eklentinin kendisi
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/               # 20 skill (çekirdek + 19 oa-*)
│       │   ├── ortak-avukat/
│       │   ├── oa-pipeline/
│       │   └── …
│       └── README.md             # eklenti dokümanı + parça kataloğu
├── README.md                     # bu dosya
├── LICENSE
└── .gitignore
```

Parçaların tam kataloğu, mimari ve anayasal ilkeler için: **[plugins/ortak-avukat/README.md](plugins/ortak-avukat/README.md)**.

## Öne çıkanlar

- **Lego mimarisi** — 20 bağımsız parça; `oa-pipeline` uçtan uca orkestrasyon (MANİFEST → … → KAPANIŞ).
- **Kesişen katmanlar** — `oa-usul` (usulün esasa takaddümü), `oa-illiyet` (nedensellik grafı), `oa-gizlilik` (meslek sırrı / Privacy Layer 0).
- **Deterministik denetim** — 14 Python scripti model muhakemesini denetler (süre/zamanaşımı, illiyet grafı, antitez, usul, kıyas, sözleşme kloz, manifest, arşiv).
- **Ceza dalı** — `oa-mudafii` (savunma) ve `oa-musteki-vekili` (iddia) aynı unsur-inşasının iki yüzü.
- **Doğrulanmış kaynak** — içtihat/mevzuat daima Yargı Pro + Mevzuat MCP'den; doktrin Literatür/YÖK Tez'den.

## Gizlilik

Bu depo **hiçbir müvekkil verisi veya MCP kimlik bilgisi içermez**. Çalışma evrakı (`_oa/`) `.gitignore` ile dışlanmıştır ve asla depoya girmez. Dış araca veri çıkışı, `oa-gizlilik` Layer 0 süzgecine tabidir.

## Fikri Mülkiyet ve Lisans

Bu depodaki tüm içerik — "Ortak Avukat" metodolojisi, skill metinleri, scriptler ve dokümantasyon dâhil — özgün bir eserdir ve **5846 sayılı Fikir ve Sanat Eserleri Kanunu (FSEK)** kapsamında korunur. Eserin sahibi ve tüm **mali ve manevi hakların** münhasır hak sahibi **Av. Bayram Can Çapar**'dır (b.cancapar@gmail.com).

Depo kamuya açık (public) olarak yayımlanmıştır;   Kopyalama, çoğaltma, dağıtma, değiştirme, çeviri, türev çalışma oluşturma ve ticari kullanım **önceden yazılı izne tabidir**. Telif/atıf bildirimleri ve hak sahibinin adı kaldırılamaz. Yalnızca Yargı Pro MCP oluşturan ekibin fikri değişimine ve gerektiğinde ticari amaçla kullanımına izin verilmiştir. 

Tam koşullar: [LICENSE](LICENSE) · Özet bildirim: [NOTICE](NOTICE).
