#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa_hafiza.py — ÇALIŞMA KÖKÜ / YEREL HAFIZA motoru (`_oa/`)

Ailenin tüm kalıcı izleri (defter, devir paketleri, künye teyit kütüğü, çalışma
evrakları, oturum devri, süre flag'leri) çalışılan klasörün `_oa/` kökünde YEREL
ve FİZİKSEL yaşar. Ortamdan bağımsızdır: Cowork, Codex veya Claude Code — iz aynı.
Kaynak evrak SALT-OKUNURDUR; her üretim _oa altına gider.

Kullanım (çalışılan klasörün kökünden — ya da mutlak --kok ile):
  python oa_hafiza.py init [--dosya "Dosya adı"] [--kok KLASÖR]
  python oa_hafiza.py oturum-ac [--ortam cowork|codex|claude-code]
  python oa_hafiza.py devir --adim 3 --parca oa-ictihat \
      --yapilan "..." --beklenen "..." --kanit "..."
  python oa_hafiza.py teyit --arac ictihat_ara --sorgu "..." --sonuc "..." [--dokum HAM_DOKUM]
  python oa_hafiza.py sure-flag --tarih 2026-08-14 --aciklama "istinaf son günü" --kural hmk_istinaf
  python oa_hafiza.py ajan-brif --parca oa-antitez --gorev "..." [--skill-yol YOL]
  python oa_hafiza.py oturum --not "ara not"
  python oa_hafiza.py oturum-kapat --not "yapılan / kalan / bekleyen avukat kararı"
  python oa_hafiza.py durum

--kok: her alt-komutta geçerlidir (tam_tur.py/oa_metrik.py simetrisi). Verilirse
_oa kökü <KLASÖR>/_oa; verilmezse mevcut davranış (CWD/_oa). Claude Code alt-ajan
thread'lerinde cwd sıfırlandığından mutlak --kok, hayalet _oa oluşmasını önler.
--dokum (teyit): teyit satırını ham MCP döküm dosyasına bağlar (kütük+döküm okuma altyapısı).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, datetime, json, os, re, sys

KOK = "_oa"
DIZINLER = ["defter", "devir", "cikti", "teyit", "oturum", "arsiv-yerel"]
KILIT = os.path.join(KOK, ".oturum-kilidi")


def _kok_ayarla(kok_arg):
    """--kok verilirse _oa kökünü <kok_arg>/_oa'ya taşı (tam_tur.py/oa_metrik.py
    simetrisi). Verilmezse mevcut davranış: CWD/_oa. Claude Code alt-ajan
    thread'lerinde cwd sıfırlandığından mutlak --kok, yanlış yerde hayalet _oa
    oluşmasını önler. yol()/KILIT bu global KOK'u okur."""
    global KOK, KILIT
    if kok_arg:
        KOK = os.path.join(kok_arg, "_oa")
    KILIT = os.path.join(KOK, ".oturum-kilidi")


def ts():
    return datetime.datetime.now().isoformat(timespec="seconds")


def gun():
    return datetime.date.today().isoformat()


def yol(*p):
    return os.path.join(KOK, *p)


def kontrol():
    if not os.path.isdir(KOK):
        sys.exit("HATA: _oa kökü yok — önce `oa_hafiza.py init` çalıştır.")


def cmd_init(args):
    for d in DIZINLER:
        os.makedirs(yol(d), exist_ok=True)
    if not os.path.exists(yol("README.md")):
        with open(yol("README.md"), "w", encoding="utf-8") as f:
            f.write(f"""# _oa — Ortak Avukat yerel hafıza kökü
Oluşturma: {ts()}

Bu klasör, Ortak Avukat ailesinin bu dosyadaki TÜM kalıcı izlerini tutar.
Kaynak evrak salt-okunurdur; ailenin her üretimi buraya yazılır. Ortamdan
bağımsızdır (Cowork/Codex/Claude Code — iz aynı).

- defter/       pipeline-durum.json — işletim defteri, kanıtlı statüler
- devir/        parçalar arası DEVİR PAKETLERİ (ne yapıldı → ne bekleniyor → kanıt)
- cikti/        ÇALIŞMA EVRAKLARI: her adımın adlandırılmış izi
                (NN-parca-icerik.md/json — ör. 04-vakia.json, 08-dilekce-taslak-v1.md)
- teyit/        künye teyit kütüğü — her MCP teyidi araç+sorgu+sonuç ile satır satır
- oturum/       oturum devir notları — yeni oturum buradan devralır
- arsiv-yerel/  dosya kapanınca ders kaydı (genel arşive anonimleştirilerek taşınır)
- sureler.json  süre flag'leri (son günler; hatırlatıcıya da bağlanır)
- .oturum-kilidi  TEK OTURUM kuralının kilidi (oturum-ac/oturum-kapat)

GİZLİLİK: Bu kök müvekkil verisi içerir → içeriği dış araca (bulut MCP, web,
e-posta) gönderilmeden önce oa-gizlilik Layer 0 taraması zorunludur.
""")
    if not os.path.exists(yol("dosya.md")):
        ad = args.dosya or "[doldur]"
        with open(yol("dosya.md"), "w", encoding="utf-8") as f:
            f.write(f"""# Dosya Kimliği — {ad}
Oluşturma: {ts()}

- Müvekkil sıfatı / karşı taraf: [doldur — oa-interview]
- Talep (somut, ölçülebilir): [doldur]
- Aşama + merci + esas no: [doldur]
- ⏰ SÜRE FLAG'LERİ (en kritik): bkz. `_oa/sureler.json` — özet: [doldur]
- Uyuşmazlığın tek cümlelik özeti: [doldur]
- Dokunduğu hukuk dalları: [doldur — oa-alan]
- Açık uçlar: [doldur]

> Her oturum başında bu dosya + `oturum/` son kaydı + `defter/` okunarak devralınır.
""")
    if not os.path.exists(yol("teyit", "kunye-teyit.md")):
        with open(yol("teyit", "kunye-teyit.md"), "w", encoding="utf-8") as f:
            f.write("""# Künye Teyit Kütüğü
Kural: Bir künye/madde bu kütükte YOKSA, çıktıya "teyitli" olarak GİREMEZ
(pipeline künye tutarlılık kuralının fiziksel karşılığı). Her satır fiilen
yapılmış bir MCP çağrısına dayanır: yapılmamış çağrı buraya yazılamaz.
Döküm sütunu, satırı ham MCP çıktı dosyasına bağlar (`teyit --dokum <dosya>`);
böylece künye ileride yalnız kütük + döküm okunarak doğrulanabilir.

| Zaman | Araç | Sorgu | Sonuç (künye/madde + lehe/aleyhe) | Döküm |
|---|---|---|---|---|
""")
    if not os.path.exists(yol("sureler.json")):
        with open(yol("sureler.json"), "w", encoding="utf-8") as f:
            json.dump({"flagler": []}, f, ensure_ascii=False, indent=2)
    print(f"_oa kökü hazır: {os.path.abspath(KOK)}")
    print("Sıradaki adım: `oa_hafiza.py oturum-ac` ile oturum kilidini al (tek-oturum kuralı).")


def cmd_oturum_ac(args):
    kontrol()
    if os.path.exists(KILIT):
        eski = open(KILIT, encoding="utf-8").read().strip()
        print(f"DUR: oturum kilidi dolu → {eski}")
        print("Aynı klasörde aynı anda TEK oturum çalışır (defter/kütük çakışması).")
        print("Önceki oturum kapanmadıysa önce onu `oturum-kapat` ile kapat; oturum "
              "gerçekten kapandıysa ve kilit BAYATsa `.oturum-kilidi` dosyasını elle sil, tekrar aç.")
        sys.exit(1)
    with open(KILIT, "w", encoding="utf-8") as f:
        f.write(f"açılış: {ts()} | ortam: {args.ortam or 'belirtilmedi'}")
    print(f"Oturum açıldı ({ts()}, ortam: {args.ortam or '—'}).")
    print("DEVRALMA SIRASI: 1) _oa/dosya.md  2) son oturum notu  3) defter "
          "(pipeline_kayit.py --goster)  4) `python <oa-sure>/scripts/sure_nobetci.py --kok .` "
          "(süre nöbetçisi — GEÇMİŞ/BUGÜN/YAKLAŞAN son gün varsa exit 3 ile DİKKAT çeker)")
    odir = yol("oturum")
    if os.path.isdir(odir):
        notlar = sorted(os.listdir(odir))
        if notlar:
            print(f"Son oturum notu: {os.path.join(KOK, 'oturum', notlar[-1])}")


def _oturum_notu(metin):
    dosya = yol("oturum", f"{gun()}.md")
    yeni = not os.path.exists(dosya)
    with open(dosya, "a", encoding="utf-8") as f:
        if yeni:
            f.write(f"# Oturum Devri — {gun()}\n\n")
        f.write(f"## {ts()}\n{metin}\n\n")
    return dosya


def cmd_oturum(args):
    kontrol()
    print("Oturum kaydı: " + _oturum_notu(args.not_ or "[not girilmedi]"))


def cmd_oturum_kapat(args):
    kontrol()
    if not args.not_ or len(args.not_.strip()) < 15:
        sys.exit("RET: kapanış ritüelsiz olmaz. --not içinde üç soruyu cevapla: "
                 "(1) defter --denetle'den geçti mi / hangi adımda kalındı? "
                 "(2) süre flag'leri + hatırlatıcı güncel mi? (3) bekleyen avukat kararı ne?")
    dosya = _oturum_notu("KAPANIŞ RİTÜELİ:\n" + args.not_.strip())
    if os.path.exists(KILIT):
        os.remove(KILIT)
        print(f"Oturum kapatıldı, kilit kaldırıldı. Devir notu: {dosya}")
    else:
        print(f"Not yazıldı ({dosya}); kilit zaten yoktu (oturum-ac kullanılmamış olabilir).")


def cmd_devir(args):
    kontrol()
    for alan, ad in ((args.yapilan, "--yapilan"), (args.beklenen, "--beklenen"),
                     (args.kanit, "--kanit")):
        if not alan or len(alan.strip()) < 10:
            sys.exit(f"RET: devir paketi {ad} olmadan/boş yazılamaz — devir sözle olmaz.")
    damga = ts().replace(":", "-")
    dosya = yol("devir", f"{args.adim:02d}-{args.parca}-{damga}.md")
    with open(dosya, "w", encoding="utf-8") as f:
        f.write(f"""# DEVİR PAKETİ — adım {args.adim} / {args.parca}
Zaman: {ts()}

## Ne yapıldı
{args.yapilan}

## Ne bekleniyor (devralan parçanın işi)
{args.beklenen}

## Kanıt (fiilî çağrı / script çıktısı / MCP kaydı)
{args.kanit}
""")
    print(f"Devir paketi yazıldı: {dosya}")
    print("Hatırlatma: statüyü ayrıca deftere işle (pipeline_kayit.py --isle ...).")


def cmd_teyit(args):
    kontrol()
    if not (args.arac and args.sorgu and args.sonuc):
        sys.exit("RET: teyit kaydı üçlü ister: --arac + --sorgu + --sonuc. "
                 "Yapılmamış çağrı kütüğe yazılamaz.")
    # --dokum: teyit satırını ham MCP döküm dosyasına bağlar (kunye_teyit'in
    # ileride yalnız kütük+döküm okuyabilmesi için altyapı). Boru (|) hücresini
    # bozmamak için değeri sadeleştir.
    dokum_hucre = ""
    if args.dokum:
        d = args.dokum.strip().replace("|", "/").replace("\n", " ")
        dokum_hucre = f"[döküm]({d})"
        if not os.path.exists(args.dokum):
            print(f"UYARI: döküm dosyası bulunamadı: {args.dokum} — link kaydedildi, dosya yok.")
    with open(yol("teyit", "kunye-teyit.md"), "a", encoding="utf-8") as f:
        f.write(f"| {ts()} | {args.arac} | {args.sorgu} | {args.sonuc} | {dokum_hucre} |\n")
    print("Teyit kütüğüne işlendi." + (f" (döküm: {args.dokum})" if args.dokum else ""))


def cmd_sure_flag(args):
    kontrol()
    if not (args.tarih and args.aciklama):
        sys.exit("RET: süre flag'i --tarih ve --aciklama ister (--kural önerilir).")
    syol = yol("sureler.json")
    try:
        d = json.load(open(syol, encoding="utf-8"))
    except Exception:
        d = {"flagler": []}
    if not isinstance(d.get("flagler"), list):
        d["flagler"] = []
    # KANONİK ŞEMA (sure_nobetci.py ile PAYLAŞILAN kayıt biçimi — mimari tutarlılık):
    # "son_gun" kanonik alan adıdır; "tarih" GERİYE UYUMLULUK için AYNEN korunur
    # (mevcut çağıranlar/CLI bayrağı --tarih değişmedi). sure_nobetci.py her iki
    # alanı da okuyabilir (son_gun öncelikli, yoksa tarih'e düşer).
    kayit = {"son_gun": args.tarih, "tarih": args.tarih, "aciklama": args.aciklama,
             "kural": args.kural, "kayit": ts()}
    if args.tur:
        kayit["tur"] = args.tur
    d["flagler"].append(kayit)
    d["flagler"].sort(key=lambda x: x.get("son_gun") or x.get("tarih") or "")
    with open(syol, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"Süre flag'i işlendi: {args.tarih} — {args.aciklama}"
          + (f" ({args.kural})" if args.kural else ""))
    print(f"Yazıldı: {syol} (sure_nobetci.py --kok . bu deftere göre GEÇMİŞ/YAKLAŞAN son günü tarar).")
    print("UYARI: disk pasiftir, dürtmez — takvim/hatırlatıcı aracı varsa ŞİMDİ kur; "
          "yoksa kullanıcıya 'hatırlatıcıyı elle kur' de ve bunu açıkça raporla. "
          "_oa/dosya.md süre özetini de güncelle.")


# --- ANAYASA ÖZETİ (standalone alt-ajana taşınan çekirdek) -------------------
# Kaynak: ortak-avukat/references/anayasa.md — 10 madde, madde başına 1-2 satır.
# Gömülü özet, dosya bulunamazsa devreye giren KÜRATÖRLÜ düşüş kaynağıdır;
# dosya varsa başlıklar + sürüm anayasa.md'den DİNAMİK çekilir (özet metni sabit kalır).
_ANAYASA_GOMULU = [
    ("Çaba ve kalite standardı + token",
     "Model/efor kullanıcının tercihidir; token tasarrufu YALNIZ mekanik/temsil "
     "katmanında ve veri-kayıpsız — muhakeme, doğrulama, araştırma, içtihat/mevzuat "
     "taraması ve unsur denetiminde tasarruf ASLA yapılmaz, çaba karmaşıklıkla YÜKSELİR."),
    ("Usul esasa üstündür",
     "Usul (görev/yetki, dava şartı, süre, harç, temsil) esastan ÖNCE ve en az eşit "
     "ciddiyette denetlenir; süre telafisi olmayan tek hatadır; karşı tarafın usul "
     "zaafı (kaçırılmış süre) en kesin kazanımdır, gizlenmez, derhâl ileri sürülür."),
    ("Örnekleme ilkesi — konu sınırlaması yasağı",
     "Kapsam istisnasız TÜM Türk hukukudur; metinlerdeki her liste/tablo/çıpa yalnız "
     "ÖRNEKLEMDİR, kapsamı DARALTMAZ; listede olmayan konu aynı metotla kıyasen işlenir "
     "+ norm/içtihat resmî kaynaktan teyit edilir."),
    ("Doğaçlama meşruiyeti — yöntem serbest, olgu teyitli",
     "Format/lafız korunarak halüsinasyonsuz HER düşünce metodu (muhakeme, argüman "
     "dizilimi, strateji, üslup) serbestçe doğaçlanır; sınır tek ve keskin: YÖNTEMde "
     "serbest, OLGUda asla — künye/madde/tarih/parasal-teknik veri daima MCP-teyitli."),
    ("Doğrulama mimarisi — tavizsiz",
     "İçtihat resmî kaynaktan (Yargı Pro/Mevzuat MCP) doğrulanmadıkça YOKTUR, hafızadan "
     "atıf 'iddia'dır; üç katman norm→içtihat→doktrin ayrılır; iki modelin hemfikirliği "
     "doğrulama DEĞİLDİR; şüpheli her bilgi açıkça etiketlenir (teyit edilmedi/tek kaynak)."),
    ("Müvekkil-aleyhi dış çıktı yasağı",
     "*** TEK KATI SINIR *** Dış çıktı (dilekçe/sözleşme/başvuru) daima müvekkil lehine "
     "kurgulanır — zaaf/gereksiz ikrar/koz ÜRETİLMEZ; iç analizde ise zaaf/aleyhe delil/risk "
     "DÜRÜSTÇE, eksiksiz raporlanır. Zaaf dış belgeye yazılmaz, iç analizde saklanmaz; "
     "sunulmamış antiteze preemptive ifşa YASAK (karşı tarafı silahlandırır)."),
    ("Anonimleştirme / soyutlama kuralı",
     "Skill metinlerinde (ve _oa dışına taşınan içerikte) Av. Bayram Can Çapar dışında "
     "hiçbir kişi/müvekkil/karşı taraf/dava/dosya İSMEN anılamaz; tecrübe yalnız soyut "
     "örüntü olarak işlenir (Av.K. m.36 meslek sırrı + KVKK + önyargısızlık)."),
    ("Fiziksel aktivasyon — simülasyon yasağı",
     "Bir parça yalnız ÜÇ kanıttan biriyle 'çalıştı' sayılır: fiilî skill çağrısı+SKILL.md "
     "yüklendi / gerçek script koştu+çıktısı görünür / fiilî MCP çağrısına dayalı 'teyitli' "
     "etiketi. Description'dan taklit = simülasyon = ÇALIŞMAMIŞ. Çağrı olmazsa SKILL.md Read "
     "ile yüklenir; o da olmazsa 'fiziken yüklenemedi — elden yürütüldü' açıkça yazılır."),
    ("Başbakan denetimi",
     "oa-pipeline anayasayı her aşamada icra/denetim eden BAŞBAKANDIR: parça atlayarak / "
     "muhakeme kısarak token kısmak YASAK, her adımda öz-denetim, MCP aktifliği ön-koşulu, "
     "teyitsiz künye/madde DOĞRUDAN dışlanır. Karar materyali üretir; nihai karar avukatındır."),
    ("Layer 0 — gizlilik / meslek sırrı",
     "Her dış-araç çağrısı (bulut MCP/Gemini/e-posta/Drive/takvim) ÖNCE oa-gizlilik "
     "süzgecinden geçer: müvekkil verisi, TC, dosya/esas no, sağlık/ceza, hesap/kart, UYAP "
     "login / e-imza / PIN taranır (Av.K. m.36, TCK m.239, KVKK m.6; fail-closed). UYAP "
     "login ve e-imza/PIN münhasıran avukata aittir. _oa müvekkil verisi içerir → dış çıkış Layer 0'a tabi."),
]


def _anayasa_yolu():
    """anayasa.md'yi bu script'e göre (cwd'den bağımsız) konumlandır; yoksa None."""
    burada = os.path.dirname(os.path.abspath(__file__))
    adaylar = [
        os.path.join(burada, "..", "..", "ortak-avukat", "references", "anayasa.md"),
        os.path.join(burada, "..", "..", "..", "ortak-avukat", "references", "anayasa.md"),
    ]
    for a in adaylar:
        a = os.path.normpath(a)
        if os.path.isfile(a):
            return a
    return None


def _anayasa_dinamik(yolu):
    """anayasa.md'den sürüm + 10 madde başlığını DİNAMİK çek. Eksik/başarısızsa None."""
    try:
        with open(yolu, encoding="utf-8") as f:
            metin = f.read()
    except Exception:
        return None
    surum = None
    m = re.search(r"Sürüm:\s*\*\*([^*]+)\*\*", metin)
    if m:
        surum = m.group(1).strip()
    basliklar = {}
    for m in re.finditer(r"(?m)^##\s+(\d{1,2})\.\s+(.+?)\s*$", metin):
        ham = m.group(2).strip()
        # "(anayasal ...)" / "(usulün ...)" parantezini at → kısa, taşınabilir başlık
        kis = re.split(r"\s*\((?:anayasal|usul)", ham)[0].strip()
        basliklar[int(m.group(1))] = kis or ham
    if len(basliklar) < 10:
        return None
    return surum, basliklar


def _anayasa_ozet():
    """(kaynak_etiketi, [satır,...]) döndürür. Dosya varsa başlık+sürüm dinamik,
    özet metni her hâlde küratörlü; dosya yoksa tümü gömülü özete düşer."""
    yolu = _anayasa_yolu()
    dinamik = _anayasa_dinamik(yolu) if yolu else None
    if dinamik:
        surum, basliklar = dinamik
        kaynak = "anayasa.md (dinamik" + (f", {surum}" if surum else "") + f") — {yolu}"
    else:
        basliklar = {}
        kaynak = "GÖMÜLÜ ÖZET (anayasa.md bulunamadı — dinamik kaynak yok)"
    satirlar = []
    for i, (gomulu_baslik, ozet) in enumerate(_ANAYASA_GOMULU, start=1):
        baslik = basliklar.get(i, gomulu_baslik)
        satirlar.append(f"   {i:>2}. {baslik} — {ozet}")
    return kaynak, satirlar


def cmd_ajan_brif(args):
    kontrol()
    skill_yol = args.skill_yol or f"<kurulu-skill-konumu>/{args.parca}/SKILL.md"
    son_devir = "—"
    ddir = yol("devir")
    if os.path.isdir(ddir):
        d = sorted(os.listdir(ddir))
        if d:
            son_devir = os.path.join(KOK, "devir", d[-1])
    anayasa_kaynak, anayasa_satirlari = _anayasa_ozet()
    anayasa_blok = "\n".join(anayasa_satirlari)
    print(f"""=== ALT-AJAN BRİFİ (Agent aracına aynen ver) ===
Sen Ortak Avukat ailesinin `{args.parca}` parçasını yürüten alt-ajansın.

1) ÖNCE şu dosyayı Read ile TAM oku ve disiplinini aynen uygula: {skill_yol}
2) Bağlamı devral: `_oa/dosya.md` + son devir paketi ({son_devir}) + `_oa/defter/pipeline-durum.json`.
3) Görev: {args.gorev}
4) KURALLAR (anayasal — operasyonel):
   - Fiilen yapılmadan hiçbir MCP çağrısı "yapıldı", koşmadan hiçbir script "koştu" sayılmaz.
   - Her künye/madde teyidini `python <oa-pipeline>/scripts/oa_hafiza.py teyit --arac ... --sorgu ... --sonuc ...` ile kütüğe işle; kütükte olmayan künye çıktına giremez.
   - Kalıcı her üretimini `_oa/cikti/` altına ÇALIŞMA EVRAKI adıyla yaz (NN-parca-icerik); müvekkil evrakını DEĞİŞTİRME (salt-okunur).
   - Dışarı (bulut/web) veri gönderilecekse önce oa-gizlilik taraması (Layer 0).
   - Çıktın karar materyalidir, karar değildir; belirsizliği etiketle, uydurma.
5) ANAYASA ÖZETİ — standalone koşan alt-ajana taşınan çekirdek (kaynak: {anayasa_kaynak}):
{anayasa_blok}
6) Dönüşünü DEVİR PAKETİ formatında ver (ne yapıldı → ne bekleniyor → kanıt) ve
   `oa_hafiza.py devir` ile dosyala; ana hat defteri buna göre güncellenecek.

>>> BAĞLAYICILIK: Bu parça standalone koşuyorsan (çekirdek + anayasa bağlamda olmayabilir)
    yukarıdaki ANAYASA BAĞLAYICIDIR; herhangi bir çelişkide `ortak-avukat/references/anayasa.md` ESASTIR.
=== BRİF SONU ===""")


def cmd_durum(args):
    kontrol()
    print(f"# _oa durumu — {os.path.abspath(KOK)}")
    print("Oturum kilidi: " + (open(KILIT, encoding="utf-8").read().strip()
                               if os.path.exists(KILIT) else "yok (oturum kapalı)"))
    for d in DIZINLER:
        p = yol(d)
        icerik = sorted(os.listdir(p)) if os.path.isdir(p) else []
        print(f"\n[{d}] ({len(icerik)} kayıt)")
        for ad in icerik[-8:]:
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(p, ad)))
            print(f"  - {ad}  ({mt:%Y-%m-%d %H:%M})")
    try:
        fl = json.load(open(yol("sureler.json"), encoding="utf-8")).get("flagler", [])
        if fl:
            print("\n[süre flag'leri]")
            for x in fl[:6]:
                _sg = x.get("son_gun") or x.get("tarih") or "?"
                print(f"  ⏰ {_sg} — {x.get('aciklama','')}" + (f" ({x['kural']})" if x.get("kural") else ""))
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description="Ortak Avukat yerel hafıza kökü (_oa)")
    # --kok her alt-komutta geçerli olsun diye ortak (parents) parser.
    ortak = argparse.ArgumentParser(add_help=False)
    ortak.add_argument("--kok", help="çalışma kökü (tam_tur.py/oa_metrik.py simetrisi); "
                                     "verilirse <KOK>/_oa, verilmezse CWD/_oa")
    sub = ap.add_subparsers(dest="komut")

    s = sub.add_parser("init", parents=[ortak]); s.add_argument("--dosya")
    s = sub.add_parser("oturum-ac", parents=[ortak]); s.add_argument("--ortam")
    s = sub.add_parser("devir", parents=[ortak])
    s.add_argument("--adim", type=int, required=True)
    s.add_argument("--parca", required=True)
    s.add_argument("--yapilan"); s.add_argument("--beklenen"); s.add_argument("--kanit")
    s = sub.add_parser("teyit", parents=[ortak])
    s.add_argument("--arac"); s.add_argument("--sorgu"); s.add_argument("--sonuc")
    s.add_argument("--dokum", help="satırı ham MCP döküm dosyasına bağlar (link)")
    s = sub.add_parser("sure-flag", parents=[ortak])
    s.add_argument("--tarih"); s.add_argument("--aciklama"); s.add_argument("--kural")
    s.add_argument("--tur", choices=["usul", "maddi"],
                    help="süre türü (sure_nobetci.py etiketinde gösterilir); opsiyonel")
    s = sub.add_parser("ajan-brif", parents=[ortak])
    s.add_argument("--parca", required=True); s.add_argument("--gorev", required=True)
    s.add_argument("--skill-yol")
    s = sub.add_parser("oturum", parents=[ortak]); s.add_argument("--not", dest="not_")
    s = sub.add_parser("oturum-kapat", parents=[ortak]); s.add_argument("--not", dest="not_")
    sub.add_parser("durum", parents=[ortak])

    args = ap.parse_args()
    _kok_ayarla(getattr(args, "kok", None))
    {"init": cmd_init, "oturum-ac": cmd_oturum_ac, "devir": cmd_devir,
     "teyit": cmd_teyit, "sure-flag": cmd_sure_flag, "ajan-brif": cmd_ajan_brif,
     "oturum": cmd_oturum, "oturum-kapat": cmd_oturum_kapat,
     "durum": cmd_durum}.get(args.komut, lambda a: ap.print_help())(args)


if __name__ == "__main__":
    main()
