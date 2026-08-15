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
  # GETİR sınıfı (tam metin) — --damga ZORUNLU, tek-komut içtihat muhakeme ritüeli:
  python oa_hafiza.py teyit --arac ictihat_getir --sorgu "..." --sonuc "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678" \
      --damga LEHE|ALEYHE|ALEYHE-AYIRT|NOTR --bag "...(≥40 karakter)..." \
      --ilgili-kisim "...(döküm içinde VERBATİM geçen alıntı)..." --dokum-icerik @ham.md \
      [--ayirt "...(yalnız ALEYHE-AYIRT'ta ≥20 karakter)..."] [--damga-degistir "...(≥40 karakter gerekçe)..."]
  python oa_hafiza.py sure-flag --tarih 2026-08-14 --aciklama "istinaf son günü" --kural hmk_istinaf
  python oa_hafiza.py ajan-brif --parca oa-antitez --gorev "..." [--skill-yol YOL]
  python oa_hafiza.py oturum --not "ara not"
  python oa_hafiza.py oturum-kapat --not "yapılan / kalan / bekleyen avukat kararı"
  python oa_hafiza.py durum

--kok: her alt-komutta geçerlidir (tam_tur.py/oa_metrik.py simetrisi). Verilirse
_oa kökü <KLASÖR>/_oa; verilmezse mevcut davranış (CWD/_oa). Claude Code alt-ajan
thread'lerinde cwd sıfırlandığından mutlak --kok, hayalet _oa oluşmasını önler.
--dokum (teyit): teyit satırını ham MCP döküm dosyasına bağlar (kütük+döküm okuma altyapısı).

`ajan-brif` kural #4 mekanik denetimi: `oturum-kapat` (KAPANIŞ ritüeli), _oa/cikti'da
hiç çalışma evrakı YOKSA görünür bir UYARI basar (bloklamaz) — alt-ajanların "her üretim
_oa/cikti'ya" kuralını hiç uygulamadan bir oturumun sessizce kapanmasını önler.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, datetime, glob, importlib.util, json, os, re, sys

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


def _cikti_bos_mu():
    """Ajan-brif kural #4 mekanik kontrolü ('her üretim _oa/cikti'ya çalışma
    evrakı') — KAPANIŞ ritüelinde UYARI için: _oa/cikti'da hiç dosya YOKSA True.
    Yalnız GÖRÜNÜR kılar, kapanışı BLOKLAMAZ (defter/tam_tur'un kendi sert
    kapıları zaten var; bu, alt-ajan çıktısı hiç bırakmadan kapanan bir oturumu
    sessizce geçirmemek için ek bir mekanik uyarı katmanıdır)."""
    cdir = yol("cikti")
    if not os.path.isdir(cdir):
        return True
    return not any(os.path.isfile(os.path.join(cdir, ad)) for ad in os.listdir(cdir))


def _devir_bos_mu():
    """GÖREV C(3) — PAS PROTOKOLÜ ucuzlatmasının GÖRÜNÜRLÜK ayağı: `_oa/devir`
    içinde hiç DEVİR PAKETİ (`oa_hafiza.py devir ...`) YOKSA True. `_cikti_bos_mu`
    ile SİMETRİK — yeni bir zorunluluk EKLEMEZ, yalnız parçalar arası hiç
    fiziksel devir bırakılmadan (yalnız defter statüsüyle) ilerleyen bir turu
    KAPANIŞ ritüelinde GÖRÜNÜR kılar (bloklamaz)."""
    ddir = yol("devir")
    if not os.path.isdir(ddir):
        return True
    return not any(os.path.isfile(os.path.join(ddir, ad)) for ad in os.listdir(ddir))


_PIPELINE_KAYIT_MOD = None


def _pipeline_kayit_modulu():
    """pipeline_kayit.py'yi (aynı dizin — oa-pipeline/scripts/) İN-PROCESS
    import eder (subprocess YOK — P0-4/P0-5/P0-7'deki 'kapı başka kapıyı
    subprocess ile çağırmaz' ilkesiyle simetrik). Bulunamaz/çökerse None
    döner; çağıran taraf bunu GÖRÜNÜR bir dar-RET'e çevirir (P1-12 fail-open
    kapatma yönü — 'script bulunamadı' burada da KAPI KAPALI sayılır)."""
    global _PIPELINE_KAYIT_MOD
    if _PIPELINE_KAYIT_MOD is not None:
        return _PIPELINE_KAYIT_MOD
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_kayit.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "_oa_hafiza_pipeline_kayit_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _PIPELINE_KAYIT_MOD = mod
    return _PIPELINE_KAYIT_MOD


def _kapanis_denetim_calistir(kok_arg):
    """P1-8 — KAPANIŞ Gate: `pipeline_kayit.py --denetle` (Gate-G + makbuz +
    önkoşul kapıları dahil) VE `oa_metrik.py` özetini İN-PROCESS çalıştırır.

    DÜZELTME (sinav 'advisory kapı = olmayan kapı' × 'kapanış normal akışı
    kilitlememeli' çelişkisinin çözümü — bağlayıcı plan metni): --denetle'nin
    BULDUĞU sorunlar/uyarılar (G2/G3 engeli, önkoşul eksiği, Gate G vb.)
    KAPANIŞI BLOKLAMAZ — çıktı KESMESİZ (tam metin) devir notuna ve stdout'a
    yazılır, görünürlük hedefi böyle karşılanır ('sessiz bitiş' imkânsızlaşır,
    ama iş-ortası kapanış RET olup DEVAM-KOMUTU'nun kendisi kaybolmaz). Yalnız
    denetimin KENDİSİ fiilen KOŞULAMAZSA (modül yok/import çöktü/beklenmedik
    istisna) dar bir RET üretilir (bkz. cmd_oturum_kapat — --serhle supabı).

    Döner: (metin: str|None, calisti: bool). Bu kök hiç pipeline defteri
    kullanmıyorsa (_oa/defter yok) (None, True) — eski davranış (yalnız --not
    + cikti-boş uyarısı) AYNEN korunur, yeni bir zorunluluk EKLENMEZ."""
    kok = os.path.abspath(kok_arg or ".")
    defter = os.path.join(kok, "_oa", "defter")
    if not os.path.isdir(defter):
        return None, True
    pk = _pipeline_kayit_modulu()
    if pk is None:
        return ("[HATA] pipeline_kayit.py bulunamadı/yüklenemedi — KAPANIŞ Gate "
                 "(--denetle) koşulamadı."), False
    try:
        _temiz, cikti = pk.denetle_calistir(kok)
        try:
            ozet = pk._oa_metrik_ozet_al(kok)
        except Exception as e:
            ozet = f"(oa_metrik özeti alınamadı: {e})"
        parcalar = [p for p in (cikti, ozet) if p]
        return "\n\n".join(parcalar), True
    except Exception as e:
        return f"[HATA] KAPANIŞ Gate denetimi (--denetle) çöktü: {e}", False


def cmd_oturum_kapat(args):
    kontrol()
    if not args.not_ or len(args.not_.strip()) < 15:
        sys.exit("RET: kapanış ritüelsiz olmaz. --not içinde üç soruyu cevapla: "
                 "(1) defter --denetle'den geçti mi / hangi adımda kalındı? "
                 "(2) süre flag'leri + hatırlatıcı güncel mi? (3) bekleyen avukat kararı ne?")
    if _cikti_bos_mu():
        print("UYARI: _oa/cikti boş — ajan-brif kural #4 ('her üretim _oa/cikti'ya "
              "çalışma evrakı adıyla yazılır') karşılanmamış görünüyor; KAPANIŞ'a kadar "
              "hiçbir alt-ajan çalışma evrakı bırakmamış olabilir (mekanik uyarı — engel değil).")
    if _devir_bos_mu():
        print("UYARI: _oa/devir boş — GÖREV C(3): parçalar arası hiç DEVİR PAKETİ "
              "(`oa_hafiza.py devir ...`) bırakılmamış olabilir; statüler deftere işlenmiş "
              "olsa bile ara bağlam yalnız sözle/beyanla kalmış olabilir "
              "(mekanik uyarı — engel değil).")

    denetim_metni, denetim_calisti = _kapanis_denetim_calistir(getattr(args, "kok", None))
    serhle = getattr(args, "serhle", None)
    serhle_gecerli = bool(serhle and len(serhle.strip()) >= 30)
    ret_gerekli = (not denetim_calisti) and (not serhle_gecerli)

    devir_metni = "KAPANIŞ RİTÜELİ:\n" + args.not_.strip()
    if serhle:
        devir_metni += f"\n\nŞERH (--serhle): {serhle.strip()}"
    gate_blok = None
    if denetim_metni:
        gate_blok = (
            "─" * 60 +
            "\nKAPANIŞ GATE — pipeline_kayit --denetle + oa_metrik (KESMESİZ, tam metin)\n" +
            "─" * 60 + "\n" + denetim_metni
        )
        devir_metni += "\n\n" + gate_blok

    # P1-8 DÜZELTME (BLOKER, sinav bulgusu): devir notu HER DALDA — dar RET dahil
    # — exit kararından ÖNCE diske yazılır. Eski sıra (önce sys.exit, sonra
    # _oturum_notu) dar RET'te kapanış artefaktını (yapılan/kalan/bekleyen +
    # '[HATA] ... koşulamadı' metni) TAMAMEN kaybediyordu; kayıpsızlık
    # invaryantı bunu yasaklar — kapanış notu hiçbir dalda kaybolmaz.
    dosya = _oturum_notu(devir_metni)

    if ret_gerekli:
        sys.exit(
            "RET: KAPANIŞ Gate (pipeline_kayit.py --denetle) FİİLEN koşulamadı ve "
            "--serhle (≥30 karakter gerekçe) verilmedi.\n"
            + (denetim_metni or "")
            + f"\nDevir notu YİNE DE diske yazıldı ({dosya}) — kilit KALDI (kaldırılmadı). "
              "--serhle ile şerhli-izli kapanabilirsin (şerh devir notuna KESMESİZ yazılır); "
              "kilit YALNIZ başarılı/şerhli kapanışta kaldırılır. Kilit gerçekten BAYATsa "
              "(oturum fiilen kapandıysa) `.oturum-kilidi` elle silinip tekrar açılabilir — "
              "bu son çaredir, sonraki oturuma DEVAM-KOMUTU notuyla iz bırakmayı unutma."
        )

    if os.path.exists(KILIT):
        os.remove(KILIT)
        print(f"Oturum kapatıldı, kilit kaldırıldı. Devir notu: {dosya}")
    else:
        print(f"Not yazıldı ({dosya}); kilit zaten yoktu (oturum-ac kullanılmamış olabilir).")
    if gate_blok:
        print("\n" + gate_blok)


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


# P0-2 (v0.5.5) — tek-komut içtihat muhakeme ritüeli: iki araç sınıfı.
# ARAMA tam metin döndürmez → --damga vurulamaz (metinsiz damga imkânsızlaştırılır).
# GETİR tam metin döndürür → --damga (+--bag+--dokum) ZORUNLU (damgasız içtihat
# kütüğe, kütüksüz künye çıktıya GİREMEZ). Diğer araçlar (mevzuat_*, vb.)
# serbest kalır — geriye uyum (v0.5.1 davranışı birebir).
# v0.5.7.4 — BAĞLANTI KATMANI: birincil Yargı Pro adları + Pro düşerse
# devreye giren açık kaynak `yargi-mcp-yedek` adları (bkz. oa-ictihat SKILL
# "BAĞLANTI KATMANI"). Yedek kipteki teyitler de aynı kütük disipliniyle
# işlenir; sözlük iki sunucuyu da tanır.
ARAMA_ARACLARI = {"ictihat_ara", "semantik_ictihat_ara", "aym_ictihat_ara", "aihm_ictihat_ara",
                  "search_bedesten_unified", "search_bedesten_semantic", "search_anayasa_unified"}
GETIR_ARACLARI = {"ictihat_getir", "kurum_karari_getir",
                  "get_bedesten_document_markdown", "get_anayasa_document_unified"}

# DÜZELTME (v0.5.5 şerh turu — Ş1/Ş3/Ş4 KÖK ÇÖZÜM): `--arac` ESKİDEN
# doğrulanmayan serbest metindi ve DÖRT yerde (kütük satırı, muhakeme dosyası
# bölüm başlığı, döküm dosya adı, is_arama/is_getir sınıf karşılaştırması)
# HAM kullanılıyordu — bu tek boşluk taşması ve büyük harf ile sınıf
# atlatmaya (t8), kütük satırı/bölüm enjeksiyonuna (t1/t3) ve dizin dışına
# yazmaya (t4) izin veriyordu. Bilinen araştırma araçları (ARAMA ∪ GETİR ∪
# mevzuat/kurum) casefold+strip ile KANONİK ada normalize edilir — sınıf
# atlatma (t8) burada kapanır. `oa-ictihat/SKILL.md`'nin AÇIKÇA belirttiği
# gibi araç adları kurulumdan kuruluma değişebilir (Türkçe/İngilizce eşdeğer
# adlar) — bu yüzden sözlük DIŞI bir ad TAMAMEN reddedilmez (o zaman farklı
# adlandırılmış kurulumlarda tüm ritüel kilitlenirdi); bunun yerine GÜVENLİ
# TOKEN deseniyle sınırlanır (bkz. `_arac_normalize_ve_dogrula`) — bu desen
# `\n`/`|`/`/`/boşluk/`*`/`:` gibi HİÇBİR yapısal/enjeksiyon karakteri
# TAŞIYAMAZ, dolayısıyla t1/t2/t3/t4'ün payload'ları (çok satırlı sahte kütük
# satırı, hayalet **KUNYE:** bölümü, `../` path traversal) sözlük dışı kalsalar
# bile YAPISAL OLARAK İMKÂNSIZLAŞIR; sözlük-dışı bir ad ARAMA/GETİR sınıfına
# GİRMEZ (mevcut "diğer araçlar serbest kalır" davranışı korunur).
MEVZUAT_KURUM_ARACLARI = {
    "mevzuat_ara", "mevzuat_getir", "mevzuat_icinde_ara", "kurum_karari_ara",
    "resmi_gazete_fihrist", "resmi_gazete_getir", "reklam_bulten_icinde_ara",
    "sigorta_dergi_icinde_ara", "spk_icinde_ara", "agentic_legal_deep_research",
    "legal_research_guide",
}
BILINEN_ARACLAR = ARAMA_ARACLARI | GETIR_ARACLARI | MEVZUAT_KURUM_ARACLARI
_BILINEN_ARACLAR_CASEFOLD = {a.casefold(): a for a in BILINEN_ARACLAR}
_GUVENLI_ARAC_TOKEN_RE = re.compile(r"[A-Za-z0-9_.-]{1,64}")
DAMGA_ENUM = {"LEHE", "ALEYHE", "ALEYHE-AYIRT", "NOTR"}


def _arac_normalize_ve_dogrula(arac_ham):
    """--arac değerini doğrular/normalize eder. Döner: (kanonik_arac, hata)
    — başarıda hata None, başarısızlıkta kanonik_arac None (fail-closed).

    (1) strip() sonrası boşsa RET.
    (2) BİLİNEN_ARACLAR'da (ARAMA/GETİR/mevzuat-kurum) casefold ile eşleşen
        bir ad varsa sözlükteki KANONİK biçime normalize edilir — sondaki
        boşluk/büyük-küçük harf ile sınıf atlatma (t8) burada kapanır.
    (3) Sözlük dışı bir ad TAMAMEN reddedilmez (kurulum-bağımlı farklı adlı
        araçlar için) ama GÜVENLİ TOKEN deseniyle ([A-Za-z0-9_.-]{1,64})
        SINIRLANIR — enjeksiyon karakteri taşıyan HİÇBİR değer bu adımdan
        geçemez (fail-closed); ARAMA/GETİR sınıfına da girmez — bu durumda
        (v0.5.5 şerh turu 2 — YENİ-2) çağırana GÖRÜNÜR bir UYARI basılır ki
        ARAMA/GETİR sınıf kurallarının (--damga zorunluluğu/yasağı) o çağrı
        için UYGULANMADIĞI sessizce gözden kaçmasın (depo'nun kendi 'sessiz
        atlama yasağı' ilkesiyle simetrik, krş. kunye_ortak.py bozuk kütük
        satırı UYARI'sı, ictihat_muhakeme_denetim.py [BİLGİ] satırı)."""
    arac = (arac_ham or "").strip()
    if not arac:
        return None, "RET: --arac boş olamaz."
    kanonik = _BILINEN_ARACLAR_CASEFOLD.get(arac.casefold())
    if kanonik is not None:
        return kanonik, None
    if not _GUVENLI_ARAC_TOKEN_RE.fullmatch(arac):
        return None, (
            "RET: bilinmeyen araç adı ('" + arac[:80] + "') güvenli biçimde değil — "
            "--arac serbest metin DEĞİLDİR; bilinen araçlar dışında bir ad yalnız "
            "harf/rakam/_/./- içerebilir (azami 64 karakter), satır sonu/boru/boşluk/"
            "eğik-çizgi/yıldız TAŞIYAMAZ (fail-closed enjeksiyon kapısı). Bilinen "
            "araçlar: " + ", ".join(sorted(BILINEN_ARACLAR)))
    print(f"UYARI: \"{arac}\" bilinen araç sözlüğünde yok — ARAMA/GETİR sınıf "
          "kuralları (--damga zorunluluğu/yasağı) bu çağrıda UYGULANMADI; ad "
          "doğruysa BILINEN_ARACLAR'a ekleyin.", file=sys.stderr)
    return arac, None

# Layer-0 ucuz sorgu taraması (P0-2 DÜZELTME e, v0.5.5): --sorgu ANONİM olmalı
# (müvekkil-tanımlayıcı veri dış MCP'ye gönderilemez) — anayasa §10 dört deseni
# AÇIKÇA sayar: TCKN/ad-soyad/dosya-esas no/IBAN. Tarama artık ARAÇ SINIFINDAN
# BAĞIMSIZDIR (eskiden yalnız ARAMA/GETİR — 6 araç adı — taranıyordu; mevzuat_*
# dahil HER --sorgu dış MCP'ye giden metindir, aynı taramadan geçer). Bilinen
# sınır: bağlam-bağımsız SAF esas/karar no ("E. 2023/1234") taranmaz — meşru
# içtihat aramasıyla ayırt edilemez (bkz. anayasa örnekleme ilkesi); yalnız
# BİRLEŞİK/kimliklendirici kalıplar (ad-soyad; yerel/ilk-derece mahkeme adı +
# esas no EŞ-GEÇMESİ — bir DOSYAYI, bir İÇTİHADI değil, işaret eder) yakalanır.
# Yanlış-pozitif riski --sorgu-onaylı ile bilinçli geçişle karşılanır.
_TCKN_RE = re.compile(r"(?<!\d)\d{11}(?!\d)")
_IBAN_RE = re.compile(r"\bTR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}\b")
_YN_RE = re.compile(r"\d{4}\s*/\s*\d{1,6}")

# v0.5.5 son sınav düzeltmesi (Layer 0 kaçış sınıfları): aşağıdaki kimlik
# belirteçleri hiçbir MEŞRU içtihat/mevzuat aramasında gerekmez; --sorgu dış
# MCP'ye gittiği için burada fail-closed yakalanır (bilinçli geçiş: --sorgu-onayli).
# Telefon: 05XX / +90 5XX / (0212) biçimleri — ara boşluk/tire/parantez toleranslı.
_TELEFON_RE = re.compile(
    r"(?<!\d)(?:\+?90[\s.\-]?)?(?:\(0?\d{3}\)|0?\d{3})[\s.\-]?\d{3}[\s.\-]?\d{2}[\s.\-]?\d{2}(?!\d)")
_EPOSTA_RE = re.compile(r"\b[\w.+\-]+@[\w\-]+\.[A-Za-z]{2,}\b")
# Türk plakası: 2 hane il + 1-3 harf + 2-5 rakam (ör. 34 ABC 123, 07AB1234)
_PLAKA_RE = re.compile(r"(?<![\w])(0[1-9]|[1-7]\d|8[01])\s?[A-ZÇĞİÖŞÜ]{1,3}\s?\d{2,5}(?![\w])")

# İlk derece/yerel mahkeme adı (Yargıtay/Danıştay/BAM gibi genel emsal-arama
# mercilerinden BİLİNÇLİ AYRI TUTULUR — "Yargıtay 4. HD" gibi genel daire
# referansları meşru içtihat aramasıdır; "<Şehir> N. İş Mahkemesi" gibi
# şehir+ilk-derece-mahkeme adı, esas no ile eş-geçtiğinde somut bir DOSYAYI
# işaret eder — anonimlik ihlali).
# DÜZELTME (v0.5.5 şerh turu — Ş5a çürütücü bulgusu): eski desen SABİT bir
# mahkeme-türü listesiyle (İş/Asliye Hukuk/.../Vergi) sınırlıydı — bu liste
# 'Asliye Ticaret', 'Tüketici', 'İcra Hukuk/Ceza', 'Fikri ve Sınai Haklar
# Hukuk', 'Çocuk', 'Kadastro' gibi GERÇEKÇİ mahkeme türlerini ve ASCII
# harf-çevrimli yazımları ('IS Mahkemesi') hiç yakalamıyordu (8/11
# yanlış-negatif). Artık GENEL bir "N. <en çok 6 sözcük> Mahkemesi" deseni
# kullanılır (`\w` zaten Türkçe harfleri VE düz ASCII'yi kapsar — ayrı bir
# harf-çevrim adımı gerekmez); yalnız BAM/BİM (Bölge Adliye/İdare Mahkemesi
# — genel emsal-arama mercii, somut dosya kimliği DEĞİL) `_ILK_DERECE_
# MAHKEME_ISTISNA_RE` ile AÇIKÇA muaf tutulur (fail-closed yön: bilinmeyen
# mahkeme adı yakalanır, yalnız bilinen emsal mercileri muaf).
_ILK_DERECE_MAHKEME_RE = re.compile(
    r"\b\d{1,2}\s*\.\s*(?:\w+\s+){0,6}Mahkemesi\b",
    re.I,
)
_ILK_DERECE_MAHKEME_ISTISNA_RE = re.compile(r"Bölge\s+(?:Adliye|İdare)\s+Mahkemesi", re.I)


def _ilk_derece_mahkeme_var_mi(sorgu):
    """İlk derece/yerel mahkeme deseni eşleşiyor mu (BAM/BİM istisnası hariç
    tutularak)? `_ILK_DERECE_MAHKEME_RE.search` yerine bu kullanılır."""
    for m in _ILK_DERECE_MAHKEME_RE.finditer(sorgu):
        if not _ILK_DERECE_MAHKEME_ISTISNA_RE.search(m.group(0)):
            return True
    return False

# Ad-soyad kalıbı: iki ardışık "Büyük harf + küçük harf(ler)" YA DA "TÜM BÜYÜK
# HARF" biçimli sözcük. DÜZELTME (v0.5.5 düzeltme turu — ÖNEMLİ çürütücü
# bulgusu): eski desen yalnız "Büyük+küçük" (TitleCase) sözcük çiftini
# yakalıyordu — UYAP evrakının standart biçimi olan TAM BÜYÜK HARFLİ soyadı
# ("AHMET YILMAZ", "Ahmet YILMAZ", "MEHMET DEMİR") YAKALAMIYORDU (yanlış-
# negatif — gerçek PII biçiminde en büyük körlük tam da buradaydı). Her iki
# sözcük ayrı ayrı TitleCase VEYA TAM BÜYÜK (2+ harf) olabilir.
_AD_SOYAD_KELIME_RE = r"(?:[A-ZÇĞİÖŞÜ][a-zçğıöşü]+|[A-ZÇĞİÖŞÜ]{2,})"
_AD_SOYAD_RE = re.compile(r"\b" + _AD_SOYAD_KELIME_RE + r"\s+" + _AD_SOYAD_KELIME_RE + r"\b")
# Kurumsal/hukuki çok-sözcüklü adların ÇOĞU (Yargıtay Hukuk Genel Kurulu,
# Asliye Hukuk Mahkemesi, Bölge Adliye Mahkemesi, ...) bu KELİME KÜMESİNDEN
# en az birini içerir — ikisi de kümede DEĞİLSE muhtemel bir kişi adı sayılır
# (fail-closed; yanlış-pozitifte --sorgu-onaylı kaçış yolu vardır).
_KURUMSAL_KELIMELER = {
    "yargıtay", "danıştay", "anayasa", "mahkemesi", "mahkeme", "hukuk", "ceza",
    "ticaret", "ağır", "asliye", "sulh", "icra", "aile", "idare", "vergi",
    "bölge", "adliye", "genel", "kurulu", "kurul", "kanunu", "kanun", "dairesi",
    "daire", "karar", "esas", "sayıştay", "uyuşmazlık", "türk", "türkiye",
    "cumhuriyeti", "bakanlığı", "bakanlık", "kurumu", "kurum", "başkanlığı",
    "başkanlık", "müdürlüğü", "müdürlük", "sözleşmesi", "yasası", "tebliği",
    "yönetmeliği", "tüzüğü", "dava", "davası", "kararı", "içtihat", "içtihadı",
    "sayılı", "tarihli", "medeni", "borçlar", "iş", "idari", "bölge",
    # DÜZELTME (v0.5.5 düzeltme turu): ölçülen 7 yanlış-pozitifte (Avrupa
    # İnsan Hakları Mahkemesi / Sosyal Güvenlik Kurumu / Kamu İhale Kurumu /
    # Yüksek Seçim Kurulu / Bilirkişi Raporu / Maddi Manevi Tazminat / Fikri
    # Sınai Haklar) EKSİK olan gündelik hukuk/kurum sözcükleri.
    "avrupa", "insan", "hak", "hakları", "haklar", "sosyal", "güvenlik",
    "kamu", "ihale", "yüksek", "seçim", "bilirkişi", "raporu", "rapor",
    "maddi", "manevi", "tazminat", "fikri", "sınai", "sınaî",
    # DÜZELTME (v0.5.5 düzeltme turu): ad-soyad deseni artık TAM BÜYÜK HARFLİ
    # sözcükleri de yakaladığından (yukarı bakınız), yaygın kanun kısaltmaları
    # (TBK/HMK/CMK/... — bkz. `kunye_teyit.KANUN_NO`) ve mahkeme/daire kısa
    # adları (HD/CD/AYM/BAM/...) da BÜYÜK HARFLİ "sözcük" sayılır; bunlar
    # kümeye eklenmezse önceden HİÇ eşleşmeyen abbreviation-çiftleri (ör.
    # "TBK HMK") yeni bir yanlış-pozitif sınıfı doğururdu.
    "tbk", "tmk", "ttk", "hmk", "humk", "cmk", "tck", "iyuk", "iik", "kvkk",
    "vuk", "gvk", "aatuhk", "ik", "ay", "isgk", "tkhk", "hsk", "sgk", "bk",
    "mk", "kdv", "aym", "bam", "bim", "hgk", "cgk", "ibk", "iddk", "vddk",
    "aihm", "hd", "cd", "id",
}

# DÜZELTME (v0.5.5 şerh turu — Ş5b çürütücü bulgusu): Title-Case YAZILMIŞ
# hukuki BAŞLIKLARDA ('Bilirkişi Raporuna İtiraz Dilekçesi', 'Mobbing
# İddiası Manevi Tazminat', 'Fazla Mesai Ücreti Takdiri İndirim', ...) her
# sözcük TitleCase olduğundan ad-soyad deseni yapısal olarak AYNI görünüyor
# (13 meşru sorgudan 7'si yanlış-pozitif). Kişi-bağlam sözcüğü VARSA (bir
# kişiden BAHSEDİLDİĞİNİN açık işareti) ya da sorgu tümüyle Title-Case bir
# BAŞLIK biçiminde DEĞİLSE (çevresinde küçük harfli sözcükler varsa — normal
# cümle akışı) ad-soyad sezgisi AYNEN tetiklenir; sorgu TÜMÜYLE Title-Case VE
# hiçbir kişi-bağlam sözcüğü YOKSA (salt başlık biçimi) bastırılır.
_KISI_BAGLAM_KELIMELERI = {
    "müvekkil", "müvekkilim", "müvekkili", "müvekkilimiz", "davacı", "davalı",
    "sanık", "mağdur", "vekili", "vekilim", "adına", "aleyhine", "hakkında",
    "katılan", "müşteki", "şüpheli", "tanık", "borçlu", "alacaklı",
}
_KELIME_RE = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]+")


def _sorgu_tamamen_title_case_mi(sorgu):
    """Sorgudaki HER alfabetik kelime TitleCase veya TAM BÜYÜK ise True —
    yani sorgu, tümü-Title-Case bir BAŞLIK gibi görünüyor ('Fazla Mesai
    Ücreti Takdiri İndirim' örneğinde olduğu gibi); en az bir düz-küçük-
    harfli kelime (2+ harf) varsa (normal cümle akışı — 'için', 'kıdem',
    'aleyhine' gibi) False döner."""
    for k in _KELIME_RE.findall(sorgu):
        if len(k) >= 2 and k.islower():
            return False
    return True


def _sorguda_kisi_baglami_var_mi(sorgu):
    return any(_tr_kucuk(k) in _KISI_BAGLAM_KELIMELERI for k in _KELIME_RE.findall(sorgu))


def _tr_kucuk(s):
    """Türkçe-duyarlı küçültme: Python'un `str.lower()`'ı 'İ'yi bileşik
    noktalı 'i̇' harfine çevirdiğinden basit ASCII eşlemeyle önce İ→i, I→ı
    çevrilir (kurumsal kelime kümesiyle KARŞILAŞTIRMA doğru çalışsın diye)."""
    return s.replace("İ", "i").replace("I", "ı").lower()


def _layer0_sorgu_tara(sorgu):
    if _TCKN_RE.search(sorgu):
        return "TCKN deseni (11 haneli sayı)"
    if _IBAN_RE.search(sorgu):
        return "IBAN deseni"
    if _EPOSTA_RE.search(sorgu):
        return "e-posta adresi deseni"
    if _TELEFON_RE.search(sorgu):
        return "telefon numarası deseni"
    if _PLAKA_RE.search(sorgu):
        return "araç plakası deseni"
    if _ilk_derece_mahkeme_var_mi(sorgu) and _YN_RE.search(sorgu):
        return ("ilk derece/yerel mahkeme adı + esas-karar no eş-geçen kalıbı "
                "(somut dosya kimliği olabilir)")
    # DÜZELTME (v0.5.5 şerh turu — Ş5b): tümü-Title-Case bir BAŞLIK
    # biçimindeki (çevresinde küçük harfli sözcük yok) VE hiçbir kişi-bağlam
    # sözcüğü (müvekkil/davacı/davalı/.../aleyhine/hakkında) TAŞIMAYAN
    # sorgularda ad-soyad sezgisi bastırılır — bu iki koşul BİRLİKTE 'salt
    # hukuki başlık' (Title-Case yazım hukuki başlıklarda YAPISAL olarak
    # ad-soyad kalıbına benzer) ile 'gerçek kişi anlatımı' ayrımını yapar.
    _baglam_var = _sorguda_kisi_baglami_var_mi(sorgu)
    _tamamen_baslik = _sorgu_tamamen_title_case_mi(sorgu)
    # DÜZELTME (yeni ihlal önleme): sorgu SALT eşleşen iki sözcükten
    # (ör. bariz "Ahmet Yılmaz") ibaretse başlık bastırması UYGULANMAZ — bir
    # hukuki BAŞLIK neredeyse her zaman 2'den FAZLA sözcük taşır ('Fazla
    # Mesai Ücreti Takdiri İndirim' gibi); yalnız 2 sözcüklü sorgular bariz
    # bir ad-soyad aramasıdır ve tamamen-Title-Case olsalar bile YAKALANMAYA
    # devam eder (aksi hâlde bastırma, bariz PII aramasını da susturabilirdi).
    _toplam_kelime = len(_KELIME_RE.findall(sorgu))
    # TÜM eşleşmeler taranır (yalnız ilki değil) — sorgunun başında kurumsal
    # bir çift (ör. "Yargıtay Hukuk") geçip DAHA SONRA gerçek bir ad-soyad
    # (ör. "Ahmet Yılmaz") gelmesi durumunda ilk-eşleşme-yeter yaklaşımı bunu
    # KAÇIRIRDI (yanlış-negatif) — fail-closed felsefesiyle uyumsuzdu.
    for m in _AD_SOYAD_RE.finditer(sorgu):
        kelimeler = m.group(0).split()
        if any(_tr_kucuk(k) in _KURUMSAL_KELIMELER for k in kelimeler):
            continue
        if _tamamen_baslik and not _baglam_var and _toplam_kelime > 2:
            continue
        return f"olası ad-soyad kalıbı ('{m.group(0)}')"
    return None


def _dokum_icerik_coz(deger):
    """--dokum-icerik değerini çözer: '@dosya' → dosyadan oku, '-' → stdin'den
    oku (PYTHONIOENCODING ne olursa olsun UTF-8'e zorla), aksi hâlde düz metin."""
    if deger.startswith("@"):
        with open(deger[1:], encoding="utf-8") as f:
            return f.read()
    if deger == "-":
        try:
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        return sys.stdin.read()
    return deger


def _ws_norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _hucre(s):
    """DÜZELTME (P0-2 (d) çürütücü, v0.5.5 düzeltme turu) — künye teyit
    kütüğüne (markdown tablosu) yazılan HER serbest-metin alanı (--sorgu,
    --sonuc/sonuc_yazilan, döküm-hücresi) bu TEK fonksiyondan geçer:
    (1) satır sonu/whitespace tek boşluğa toplanır — bir `--sorgu`/`--sonuc`
    değerine gömülen `\\n`, kütükte SAHTE bir ikinci tablo satırı AÇAMAZ
    (kütükten_son_damga satır-bazlı ayrıştırma yapar; enjekte edilen "satır"
    artık aynı hücrenin İÇİNDE kalır, yeni bir `|...|` satırı doğurmaz);
    (2) `|` karakteri kaldırılır (`/`e çevrilir) — split-tabanlı okuyucu bir
    kaçış sözdizimini TANIMAZ, kolon kaymasını önlemenin tek yolu karakteri
    hücreden tamamen çıkarmaktır (masum bir `--sorgu` içindeki tek bir `|`
    dürüst bir ALEYHE satırının hücrelerini kaydırıp `kutukten_son_damga`'yı
    görünmez kılıyordu — fail-open bug)."""
    return re.sub(r"\s+", " ", (s or "").replace("|", "/")).strip()


_DAMGA_ENJEKSIYON_RE = re.compile(r"DAMGA\s*=")


def _sonuc_damga_ize_karismasin(s):
    """DÜZELTME (v0.5.5 düzeltme turu — P0-2 (d) sızma yolu, İKİNCİ KATMAN):
    `_hucre`'nin `\\n`/`|` sadeleştirmesi kütükte SAHTE bir AYRI satır
    açılmasını önler, ama tek başına yeterli DEĞİLDİR — kullanıcı-kontrolündeki
    `--sonuc` metni (ör. damgasız bir ARAMA çağrısında), hiçbir --damga
    denetiminden geçmeden, İÇİNDE literal `DAMGA=LEHE` dizgesini
    TAŞIYABİLİYORDU; bu metin script'in KENDİ ürettiği (--damga doğrulamasından
    geçmiş) son ekle AYNI hücrede birleşince, `kutukten_son_damga`'nın saf
    metin taraması ikisini AYIRT EDEMEZ hâle geliyordu (görünürde tek satır,
    tek hücre — ama iki farklı 'DAMGA=' kaynağı). Bu fonksiyon script'in kendi
    ekleyeceği son ekten ÖNCE, kullanıcı-kontrolündeki HER tabana uygulanır:
    olası bir 'DAMGA=' dizgesi görsel eşdeğeri `DAMGA∶`ye çevrilir.

    DÜZELTME (v0.5.5 şerh turu 2 — YENİ-3, KÜÇÜK): eskiden yalnız --sonuc
    tabanına uygulanıyordu; `--damga-degistir` gerekçesi (kütük hücresine
    script'in kendi DAMGA= son ekinden SONRA eklenir) sanitize edilmediği
    için hücrede İKİNCİ bir ham 'DAMGA=' tokenı bırakabiliyordu — okuyucuların
    (`kunye_ortak.py`) İLK-eşleşme sırasına dayanan dokümante-edilmemiş bir
    varsayımla korunuyordu. Artık `--damga-degistir` gerekçesi de bu
    fonksiyondan geçirilir (bkz. çağrı noktası) — aşağıdaki garanti
    dokümante-edilmemiş bir sıralama tesadüfüne değil, gerçeğe dayanır:
    kütükte kalan TEK gerçek 'DAMGA=' izi HER ZAMAN script'in kendisinin
    (doğrulanmış --damga değerini) eklediği olur; `args.sonuc`/
    `args.damga_degistir`'in ASIL hâli (muhakeme dosyası/kunye_normalize/
    verbatim denetimi) bu dönüşümden ETKİLENMEZ — yalnız KÜTÜK hücresine
    yazılan taban için kullanılır."""
    return _DAMGA_ENJEKSIYON_RE.sub("DAMGA∶", s or "")


_MUHAKEME_YAPISAL_RE = re.compile(
    r"(?m)^(\*\*(?:KUNYE|KAYNAK-IZI|DAMGA|GEÇERSİZ-KILINDI):\*\*|#{1,6}\s)"
)


def _satir_sonu_normalize(metin):
    """DÜZELTME (v0.5.5 düzeltme turu — CR SATIR-SONU KAÇIŞ ATLATMASI,
    BLOKER, t3/t9): `_MUHAKEME_YAPISAL_RE` `(?m)^` kullanır — bu yalnız bir
    `\\n`'DEN SONRAKİ konumlarla eşleşir. Python metin modu, LONE bir `\\r`
    karakterini YAZARKEN olduğu gibi ham bırakır (kaçışlanmaz) ama dosya
    DAHA SONRA okunduğunda (universal-newlines — hem bu script hem
    `ictihat_muhakeme_denetim.py`) o `\\r`'yi `\\n`'e ÇEVİRİR: yani yazma
    anında kaçış katmanının GÖRMEDİĞİ bir konum, okuma anında TAM bir satır
    başına dönüşüyordu. `--bag`/`--ilgili-kisim`/`--ayirt`/`--sonuc`/
    `--damga-degistir` içine gömülen `\\r**KUNYE:** ...` bloğu bu asimetriyle
    kaçış katmanını HİÇ TETİKLEMEDEN dosyada TAM GEÇERLİ bir hayalet
    muhakeme bölümü doğurabiliyordu (canlı kanıt: sb2/sb5/sb6). Kaçış,
    dosyanın OKUNACAĞI biçim üzerinde çalışmalıdır — bu yüzden
    `_muhakeme_kacis`'in İLK adımı tüm satır sonu biçimlerini ('\\r\\n',
    lone '\\r') tekil '\\n'e indirger (görünür metin/kayıpsızlık invaryantı
    DEĞİŞMEZ — yalnız satır sonu gösterimi tekilleşir), SONRA satır-başı
    yapısal belirteçler kaçışlanır; artık kaçışın çalıştığı '^' konumları
    HER ZAMAN okuma-zamanındaki '^' konumlarıyla BİREBİR aynıdır."""
    return (metin or "").replace("\r\n", "\n").replace("\r", "\n")


def _muhakeme_kacis(metin):
    """DÜZELTME (v0.5.5 düzeltme turu — TAM BÖLÜM enjeksiyonu, BLOKER) —
    `03-ictihat-muhakeme.md`'ye yazılan serbest metinlerde (--ilgili-kisim,
    --bag, --ayirt, --sonuc, --damga-degistir gerekçesi) satır-başı yapısal
    belirteçleri (`**KUNYE:**`, `**KAYNAK-IZI:**`, `**DAMGA:**`,
    `**GEÇERSİZ-KILINDI:**`, markdown başlıkları) kaçışlar — bu alanlardan
    biri içine gömülen `\\n**KUNYE:** ...` bloğu, `kunye_ortak.bolum_araliklari`
    ayracını (satır-başı `**KUNYE:**`) tetikleyip YENİ ve TAM GEÇERLİ bir
    hayalet muhakeme kaydı DOĞURABİLİYORDU (VERBATİM kapısı engel değil —
    doğrulama attacker'ın kendi kontrolündeki `--dokum-icerik`e karşı
    yapılıyor). Zero-width space (`\\u200b`) eşleşen belirtecin HEMEN ÖNÜNE
    eklenir: görünür metin (kayıpsızlık invaryantı) DEĞİŞMEZ, ama satır artık
    `^\\*\\*KUNYE:\\*\\*` gibi satır-başı regex'leriyle EŞLEŞMEZ.

    DÜZELTME (v0.5.5 düzeltme turu — CR bypass, BLOKER): metin ÖNCE
    `_satir_sonu_normalize`'den geçirilir (bkz. o fonksiyonun docstring'i) —
    aksi hâlde lone `\\r` ile gömülü bir bölüm, kaçış regex'inin GÖRMEDİĞİ
    bir '^' konumundan dosyaya sızabiliyordu."""
    if not metin:
        return metin
    metin = _satir_sonu_normalize(metin)
    _zwsp = chr(0x200B)
    return _MUHAKEME_YAPISAL_RE.sub(lambda m: _zwsp + m.group(1), metin)


def _sayilar_gecer_mi(kunye_metin, icerik):
    """Künye metnindeki (--sonuc) YIL/SIRA sayılarının (esas/karar) döküm
    içeriğinde dize olarak (komşu rakamdan izole) geçtiğini denetler — künye
    ile döküm arasındaki en ucuz/deterministik tutarlılık kontrolü (P0-2
    DÜZELTME b). Döner: eksik sayı listesi (boşsa temiz)."""
    sayilar = [re.sub(r"\s*/\s*", "/", m.group(0)) for m in _YN_RE.finditer(kunye_metin or "")]
    return [no for no in sayilar
            if not re.search(r"(?<!\d)" + re.escape(no) + r"(?!\d)", icerik or "")]


# P0-2 kardeş-skill in-process import (kunye_ortak.py, oa-kontrol) — TEK
# tanım kunye_ortak.py'de yaşar; burada esas/karar ayrıştırma/kütük-damga
# mantığı TEKRARLANMAZ (tek-yazar kuralı, bkz. P0-4'teki aynı desen).
_KUNYE_ORTAK_MOD = None


def _kunye_ortak_modulu():
    """kunye_ortak.py'yi (…/oa-kontrol/scripts/) İN-PROCESS import eder.
    Kardeş skill kurulu değilse/import çökerse None döner — çağıran taraf
    bunu GÖRÜNÜR bir uyarıya çevirir (P0-4'teki fail-open deseniyle simetrik;
    sessiz atlama yasağı)."""
    global _KUNYE_ORTAK_MOD
    if _KUNYE_ORTAK_MOD is not None:
        return _KUNYE_ORTAK_MOD
    burada = os.path.dirname(os.path.abspath(__file__))
    adaylar = [
        os.path.join(burada, "..", "..", "oa-kontrol", "scripts", "kunye_ortak.py"),
        os.path.join(burada, "..", "..", "..", "oa-kontrol", "scripts", "kunye_ortak.py"),
    ]
    betik = next((os.path.normpath(a) for a in adaylar if os.path.isfile(a)), None)
    if betik is None:
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_hafiza_kunye_ortak_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _KUNYE_ORTAK_MOD = mod
    return _KUNYE_ORTAK_MOD


def _kaynak_izi_yolu(dokum_yolu, kok_arg):
    """P0-2 DÜZELTME (KAYNAK-IZI yolu, v0.5.5) — muhakeme kaydına gömülecek
    KAYNAK-IZI değerini HER ZAMAN köke-göreli + ileri-bölülü (posix) üretir.
    `--kok` mutlak verilse bile dosyaya MUTLAK makine yolu gömülmez (taşınabilirlik
    + anonimlik) ve `ictihat_muhakeme_denetim.py` farklı bir cwd'den koşulsa bile
    (`_yol_coz` aynı --kok'a göre çözer) yolu doğru bulur.

    DÜZELTME (v0.5.5 şerh turu 2 — YENİ-1, ÖNEMLİ): `--dokum` kullanıcı
    denetimindedir ve dosya adında satır sonu (`\\n`/`\\r`) taşıyabilen
    platformlarda (Linux/macOS/WSL) bu değer eskiden hiçbir kaçıştan
    geçirilmeden `03-ictihat-muhakeme.md`'ye HAM yazılıyordu — satır başında
    tam geçerli bir hayalet `**KUNYE:**`/`**DAMGA:**` bölümü doğurabiliyordu
    (komşu tüm serbest-metin alanları `_muhakeme_kacis`'ten geçerken bu tek
    alan geçmiyordu). Yol adında satır sonu MEŞRU bir kullanım DEĞİLDİR — bu
    yüzden burada girişte fail-closed RET edilir (çağıran taraf ayrıca
    savunma-derinliği için dönüş değerini de `_muhakeme_kacis`'ten geçirir)."""
    if not dokum_yolu:
        return dokum_yolu
    if "\n" in dokum_yolu or "\r" in dokum_yolu:
        sys.exit("RET: --dokum yolu satır sonu (\\n/\\r) içeremez — fail-closed "
                 "(KAYNAK-IZI enjeksiyon kapısı, muhakeme kaydına gömülecek yol).")
    taban = kok_arg if kok_arg else "."
    try:
        goreli = os.path.relpath(os.path.abspath(dokum_yolu), os.path.abspath(taban))
    except ValueError:
        # Windows'ta farklı sürücüler arası relpath ValueError atar — mutlak
        # yola düşmek yerine olduğu gibi (posix'e çevrilmiş) döndürülür.
        goreli = dokum_yolu
    return goreli.replace(os.sep, "/")


def _eski_bolumleri_gecersiz_kil(ko, cikti_dizin, esas, karar, daire, eski_damga, gerekce):
    """P0-2 DÜZELTME (d, v0.5.5) — `--damga-degistir` ile bilinçli DAMGA
    değişiminde, AYNI esas/karar (+ DAİRE) 'a ait ve DAMGA'sı `eski_damga`
    olan (henüz işaretlenmemiş) muhakeme bölüm(ler)ine `**GEÇERSİZ-KILINDI:**`
    satırı SURGICAL olarak eklenir — içerik SİLİNMEZ/değiştirilmez, yalnız bir
    satır eklenir (kayıpsızlık invaryantı). `kunye_ortak.bolum_araliklari` ile
    aynı ayraç kullanılır (tek-yazar kuralı). Döner: değiştirilen dosya sayısı.

    DÜZELTME (v0.5.5 düzeltme turu — DAİRE-KÖR): `daire` (bu çağrıdaki
    --sonuc'un dairesi) verilirse VE bulunan bölümün KÜNYE'sinden bir daire
    çıkarılabiliyorsa, İKİSİ DE tanınıyorken FARKLIYSA bölüm ATLANIR — esas/
    karar no'ları her dairede yılda sıfırdan başladığından, GERÇEKTEN FARKLI
    bir dairenin aynı numaralı kararı yanlışlıkla hükümsüz kılınmaz
    (`MuhakemeKaydi.eslesir`'in aynı ilkesiyle simetrik).

    DÜZELTME (v0.5.5 düzeltme turu — hayalet bölüm enjeksiyonu): `gerekce`
    serbest metindir (--damga-degistir); dosyaya yazılmadan önce
    `_muhakeme_kacis` ile satır-başı yapısal belirteçleri kaçışlanır — aksi
    hâlde gerekçe içine gömülü bir `\\n**KUNYE:** ...` bloğu hükümsüz kılma
    ekleme noktasından YENİ bir hayalet muhakeme bölümü doğurabilirdi."""
    if not os.path.isdir(cikti_dizin):
        return 0
    degisen = 0
    for dosya_yolu in sorted(glob.glob(os.path.join(cikti_dizin, "*ictihat-muhakeme*.md"))):
        try:
            with open(dosya_yolu, encoding="utf-8", errors="replace") as f:
                icerik = f.read()
        except OSError:
            continue
        eklenecekler = []
        for (a, b) in ko.bolum_araliklari(icerik):
            bolum = icerik[a:b]
            if "**GEÇERSİZ-KILINDI:**" in bolum:
                continue
            m_kunye = re.search(r"^\*\*KUNYE:\*\*\s*(.+)$", bolum, re.M)
            m_damga = re.search(r"^\*\*DAMGA:\*\*\s*(.+)$", bolum, re.M)
            if not (m_kunye and m_damga):
                continue
            kunye_metni = m_kunye.group(1).strip()
            b_esas, b_karar = ko.kunye_normalize(kunye_metni)
            if b_esas != esas or b_karar != karar:
                continue
            if daire is not None:
                b_daire = ko.daire_key(kunye_metni)
                if b_daire is not None and b_daire != daire:
                    continue
            if m_damga.group(1).strip().upper() != (eski_damga or "").upper():
                continue
            eklenecekler.append(a + m_damga.end())
        if not eklenecekler:
            continue
        for konum in sorted(eklenecekler, reverse=True):
            ekle = f"\n**GEÇERSİZ-KILINDI:** {ts()} {_muhakeme_kacis(gerekce.strip())}"
            icerik = icerik[:konum] + ekle + icerik[konum:]
        # DÜZELTME (v0.5.5 düzeltme turu — CR bypass, EK SAVUNMA): muhakeme
        # dosyasına yazılan `\n`'ler `newline="\n"` ile literal kalır (Windows
        # os.linesep çevirisi devre dışı) — `_muhakeme_kacis`/`_satir_sonu_
        # normalize` içeriği zaten tekilleştirdiğinden bu tek başına
        # yeterlidir, ama tek-yazar noktasında ikinci bir savunma katmanı
        # olarak dosyaya HİÇBİR '\r' yazılmaması garanti edilir.
        with open(dosya_yolu, "w", encoding="utf-8", newline="\n") as f:
            f.write(icerik)
        degisen += 1
    return degisen


def cmd_teyit(args):
    kontrol()
    if not (args.arac and args.sorgu and args.sonuc):
        sys.exit("RET: teyit kaydı üçlü ister: --arac + --sorgu + --sonuc. "
                 "Yapılmamış çağrı kütüğe yazılamaz.")

    # DÜZELTME (v0.5.5 şerh turu — Ş1/Ş3/Ş4 KÖK ÇÖZÜM, BLOKER): --arac
    # HERHANGİ bir dosya/kütük yazımından ÖNCE doğrulanır/normalize edilir —
    # kütük satırı (Ş1), muhakeme dosyası bölüm başlığı (Ş2), döküm dosya adı
    # (Ş3) ve is_arama/is_getir sınıf karşılaştırması (Ş4) artık HEPSİ bu
    # TEK normalize edilmiş değeri kullanır (tek-yazar kuralı).
    args.arac, _arac_hata = _arac_normalize_ve_dogrula(args.arac)
    if _arac_hata:
        sys.exit(_arac_hata)

    is_arama = args.arac in ARAMA_ARACLARI
    is_getir = args.arac in GETIR_ARACLARI

    # P0-2 DÜZELTME (e): Layer-0 taraması artık HER --sorgu için çalışır —
    # arac sınıfından (ARAMA/GETİR) BAĞIMSIZ; mevzuat_*/kurum_karari_ara dahil
    # HER araç dış MCP'ye giden bir sorgu taşır.
    if not args.sorgu_onayli:
        bulunan = _layer0_sorgu_tara(args.sorgu)
        if bulunan:
            sys.exit(f"RET (Layer 0): --sorgu içinde {bulunan} bulundu — sorgu "
                     "ANONİM olmalıdır (müvekkil-tanımlayıcı veri dış MCP'ye gönderilemez). "
                     "Bilinçli geçiş için --sorgu-onayli kullanın.")

    if is_arama and args.damga:
        sys.exit("RET: ARAMA araçları (ictihat_ara/semantik_ictihat_ara/aym_ictihat_ara/"
                 "aihm_ictihat_ara) TAM METİN döndürmez — --damga vurulamaz (m.4: olguda "
                 "asla serbest değil). Önce --arac ictihat_getir/kurum_karari_getir ile "
                 "tam metni çekip damgalayın.")

    if is_getir and not args.damga:
        sys.exit("RET: GETİR araçları (ictihat_getir/kurum_karari_getir) tam metin "
                 "döndürür — --damga LEHE|ALEYHE|ALEYHE-AYIRT|NOTR ZORUNLUDUR: damgasız "
                 "içtihat kütüğe, kütüksüz künye çıktıya GİREMEZ.")

    # --- --damga "ucuz" (IO'suz) alan denetimleri ÖNCE — bir RET'in dokum
    # dosyası gibi bir yan etki BIRAKMAMASI için dosya yazımından ÖNCE gelir.
    # KAYNAK-URL biçim denetimi (v0.5.5.3) — --damga'dan BAĞIMSIZ, çünkü URL
    # verildiği her çağrıda geçerli olmalıdır. Dilekçede künye yanına parantez
    # içinde YALNIZ buradan geçen bir bağlantı yazılabildiğinden, biçimi bozuk
    # bir değeri sessizce kabul etmek "teyitli link" görüntüsü üretirdi.
    if getattr(args, "kaynak_url", None):
        u = args.kaynak_url.strip()
        if not re.match(r"^https?://[^\s<>\"]+$", u):
            sys.exit("RET: --kaynak-url yalnız tek parça bir http(s) adresi olabilir "
                     f"(boşluk/satır sonu içeremez). Verilen: {args.kaynak_url!r}")
        args.kaynak_url = u

    # v0.5.8.4 [G5] AŞILMIŞLIK alanları — aşılmış-içtihat kapısının ÜRETİCİ ucu
    # (372 karnesi: `ictihat_muhakeme_denetim.py` [G5] kapısı kuruluydu ama
    # kütükte gecerlilik-bitis/asan-kaynak/asilma-tarihi alanlarını DOLDURAN
    # üretici adım YOKTU → 2 sahada %0 ateşleme; oysa risk gerçek — koşu elle
    # yakaladı: mülga HMK m.107, onamayla aşılan karar. Desen SİLİNMEZ,
    # BAĞLANIR). Üç alan da muhakeme kaydında yaşar; değer `_ws_norm` ile TEK
    # satıra indirgenir ki `ictihat_muhakeme_denetim.py`'nin satır-bazlı
    # `^**AŞAN-KAYNAK:** (.+)$` (ASAN_KAYNAK_LINE_RE vd.) regexleriyle
    # BİREBİR round-trip parse edilsin. Bir karar "aşıldı" işaretlenirken üç
    # alan TEK komutla yazılabilir (lehe-denetim iş akışı uygunluğu).
    # `getattr` — CLI dışında elle kurulmuş Namespace ile İN-PROCESS çağrı
    # (testler/kardeş scriptler) yeni alanın yokluğunda ÇÖKMEMELİDİR.
    _g5_asan = _ws_norm(getattr(args, "asan_kaynak", None))
    _g5_asilma = _ws_norm(getattr(args, "asilma_tarihi", None))
    _g5_bitis = _ws_norm(getattr(args, "gecerlilik_bitis", None))
    if (_g5_asan or _g5_asilma or _g5_bitis) and not args.damga:
        sys.exit("RET: --asan-kaynak/--asilma-tarihi/--gecerlilik-bitis yalnız "
                 "--damga ile birlikte yazılabilir — aşılmışlık alanları muhakeme "
                 "kaydında yaşar, kayıt yalnız --damga ile üretilir; damgasız "
                 "çağrıda alanların SESSİZCE düşmesi yasaktır (fail-closed, "
                 "sessiz atlama yasağı).")

    if args.damga:
        if args.damga not in DAMGA_ENUM:
            sys.exit(f"RET: --damga geçersiz enum ('{args.damga}') — LEHE|ALEYHE|"
                     "ALEYHE-AYIRT|NOTR olmalı.")
        if not args.bag or len(args.bag.strip()) < 40:
            sys.exit("RET: --damga verildiğinde --bag (DAVAYA-BAĞ) ZORUNLU ve ≥40 "
                     "karakter olmalı — tek satırlık yüzeysel bağ yeterli değildir.")
        if not args.ilgili_kisim or not args.ilgili_kisim.strip():
            sys.exit("RET: --damga verildiğinde --ilgili-kisim (VERBATİM alıntı) "
                     "ZORUNLUDUR — özet/ikame kabul edilmez (gizli özetleme yasak).")
        if args.damga == "ALEYHE-AYIRT" and (not args.ayirt or len(args.ayirt.strip()) < 20):
            sys.exit("RET: DAMGA=ALEYHE-AYIRT için --ayirt (AYIRT-ETME) ZORUNLU ve ≥20 "
                     "karakter olmalı — boş AYIRT-ETME ile ALEYHE-AYIRT geçersizdir.")
        if not (args.dokum or args.dokum_icerik):
            sys.exit("RET: --damga verildiğinde tam metin izi ZORUNLU — --dokum (mevcut "
                     "döküm dosyası) veya --dokum-icerik (yeni döküm) verin.")

    # P0-2 DÜZELTME (--dokum-icerik): dosya yazımı --damga'dan BAĞIMSIZDIR —
    # ARAMA sınıfının normal kullanımı (arama çıktısını iz olarak saklamak)
    # damgasızdır ama yine de kalıcı bir döküm izi hak eder; eskiden bu içerik
    # --damga verilmedikçe SESSİZCE atılıyordu (kayıpsızlık invaryantı ihlali).
    #
    # DÜZELTME (v0.5.5 düzeltme turu — YETİM DÖKÜM): dosyanın kendisi O_EXCL
    # ile HEMEN (çakışma-güvenli — mevcut TOCTOU testiyle bit-uyumlu) yazılır,
    # ama `.son-dokum` işaretçisi aşağıdaki `try/finally` içinde yalnız TÜM
    # denetimler (verbatim/künye-no/kütük-DAMGA çapraz kontrolü) geçtikten
    # SONRA güncellenir; RET olursa az önce yazılan dosya SİLİNİR — bir RET
    # artık `kunye_teyit.py`'nin teyit kaynağı SAYACAĞI bir YETİM döküm
    # bırakmaz (eskiden dosya kalıcıydı, yalnız `.son-dokum`/kütük/muhakeme
    # yazılmıyordu — kısmi/yarım yan etki).
    dokum_icerik = None
    dokum_bu_cagride_yazilan = None
    if args.dokum_icerik:
        ham = _dokum_icerik_coz(args.dokum_icerik)
        dokum_dizin = yol("teyit", "dokum")
        os.makedirs(dokum_dizin, exist_ok=True)
        mevcut = [a for a in os.listdir(dokum_dizin)
                  if os.path.isfile(os.path.join(dokum_dizin, a))]
        # DÜZELTME (v0.5.5 şerh turu — Ş3, savunma katmanı): `args.arac` artık
        # `_arac_normalize_ve_dogrula` ile zaten güvenli bir token'dır (ayırıcı
        # karakter TAŞIYAMAZ), ama dosya ADINA giren HER parça yine de ikinci
        # bir sanitize katmanından geçirilir (tek-yazar kuralı — bu yazım
        # noktası hiçbir zaman doğrudan `args.arac`'a güvenmez).
        _arac_dosya_guvenli = re.sub(r"[^A-Za-z0-9_.-]", "_", args.arac)[:40] or "arac"
        taban_ad = f"{len(mevcut) + 1:03d}-{_arac_dosya_guvenli}-{ts().replace(':', '-')}"
        dosya_adi = taban_ad + ".md"
        ek = 0
        # P0-2 DÜZELTME (dokum ad üretimi): sıra-sayacı dizinden bir dosya
        # silinirse/arşivlenirse GERİ SARABİLİR; aynı saniye+araçla ikinci bir
        # teyit ad ÇAKIŞMASI yaşarsa O_CREAT|O_EXCL bunu YAKALAR ve ek bir
        # sonek ekleyerek yeniden dener — mevcut dökümün SESSİZCE üzerine
        # yazılması (kayıpsızlık invaryantı ihlali) engellenir.
        dokum_dizin_gercek = os.path.realpath(dokum_dizin)
        while True:
            dokum_yolu_yazilan = yol("teyit", "dokum", dosya_adi)
            # DÜZELTME (v0.5.5 şerh turu — Ş3, sınır denetimi): dosya adı
            # yalnız sanitize edilmiş parçalardan kurulsa da, yazımdan HEMEN
            # önce hedefin fiilen `_oa/teyit/dokum` İÇİNDE kaldığı `realpath`
            # ile DOĞRULANIR — dışarıysa fail-closed RET (path traversal
            # ikinci katman, `ictihat_muhakeme_denetim._dizin_icinde_mi`
            # deseniyle simetrik).
            if os.path.realpath(os.path.dirname(dokum_yolu_yazilan)) != dokum_dizin_gercek:
                sys.exit("RET: döküm dosyası hedefi _oa/teyit/dokum dışında olamaz "
                         "(fail-closed — path traversal denetimi).")
            try:
                fd = os.open(dokum_yolu_yazilan, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                ek += 1
                dosya_adi = f"{taban_ad}-{ek}.md"
                continue
            except OSError as e:
                # DÜZELTME (v0.5.5 şerh turu — Ş3, t2 kanıtı): ham Python
                # traceback yerine anlaşılır bir RET (bu noktaya ulaşmak artık
                # --arac üzerinden pratik olarak imkânsızdır — --dosya-yolu
                # sınırları/izinleri gibi başka bir OSError kaynağına karşı
                # savunma).
                sys.exit(f"RET: döküm dosyası oluşturulamadı ({e}) — fail-closed.")
            break
        provenans = (
            "<!-- BU İÇERİK teyit komutuna VERİLEN metindir; MCP yanıtının doğrudan "
            "kaydı olduğu script tarafından DOĞRULANAMAZ (iz'dir, ispat değildir). -->\n\n"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(provenans + ham)
        dokum_icerik = ham
        args.dokum = dokum_yolu_yazilan
        dokum_bu_cagride_yazilan = dokum_yolu_yazilan

    basarili = False
    try:
        ko_mod = _kunye_ortak_modulu()
        esas_sonuc = karar_sonuc = None
        daire_sonuc = None
        son_damga_kutukte = None

        if args.damga:
            if dokum_icerik is None:
                if not os.path.exists(args.dokum):
                    sys.exit(f"RET: --damga verildi ama --dokum dosyası bulunamadı: {args.dokum} "
                             "— tam metin izi olmadan damga vurulamaz (fail-closed).")
                with open(args.dokum, encoding="utf-8", errors="replace") as f:
                    dokum_icerik = f.read()

            if _ws_norm(args.ilgili_kisim) not in _ws_norm(dokum_icerik):
                sys.exit("RET: --ilgili-kisim döküm içeriğinde VERBATİM (dize olarak) "
                         "bulunamadı — özet/parafraz kabul edilmez; alıntıyı döküm dosyasından "
                         "birebir kopyalayın.")

            eksik = _sayilar_gecer_mi(args.sonuc, dokum_icerik)
            if eksik:
                sys.exit("RET: --sonuc içindeki künye no'ları (" + ", ".join(eksik) + ") döküm "
                         "içeriğinde dize olarak geçmiyor — künye/döküm tutarsız (fail-closed).")

            # P0-2 DÜZELTME (kunye dogrulamasi): --sonuc'tan ayrıştırılabilir bir
            # künye (E./K. YYYY/NNNN) çıkmıyorsa üretilecek muhakeme kaydı HİÇBİR
            # dilekçe atfıyla eşleşemez — [F] kapısı onu 'çıplak künye' sayıp
            # BLOK eder ama neden BLOK olduğu görünmez; burada erkenden RET edilir.
            if ko_mod is None:
                # P1-12 DOKTRİNİ (v0.5.5 son sınav düzeltmesi): "çöken kapı =
                # ATLANAN kapı" sınıfı burada da kapatılır. Eskiden yalnız UYARI
                # basılıp akışa DEVAM ediliyordu; bu, kunye_ortak.py eksik/bozuk
                # (yarım kurulum, bozuk cache) olduğunda DAMGA çapraz kontrolünü
                # sessizce devre dışı bırakıyor, ALEYHE→LEHE denetimini kaldırıyordu.
                # Damga vurmak KÜNYE ayrıştırması ve kütük çapraz kontrolü OLMADAN
                # yapılamaz → FAIL-CLOSED.
                sys.exit(
                    "RET: kunye_ortak.py (oa-kontrol) import edilemedi — künye "
                    "ayrıştırma ön-denetimi ve DAMGA çapraz kontrolü YAPILAMAZ; "
                    "damga bu denetimler olmadan vurulamaz (kapı KAPALI, "
                    "FAIL-CLOSED, P1-12). Kurulumu onarın: oa-kontrol/scripts/"
                    "kunye_ortak.py erişilebilir olmalı.")
            else:
                esas_sonuc, karar_sonuc = ko_mod.kunye_normalize(args.sonuc)
                if esas_sonuc is None and karar_sonuc is None:
                    sys.exit("RET: --sonuc içinde ayrıştırılabilir bir künye (E. YYYY/NNNN, "
                             "K. YYYY/NNNN) yok — muhakeme kaydı hiçbir dilekçe atfıyla "
                             "eşleşemez (fail-closed).")

                # DÜZELTME (v0.5.5 düzeltme turu — DAİRE-KÖR): kütük çapraz
                # kontrolü `MuhakemeKaydi.eslesir` ile SİMETRİK biçimde
                # daireyi de dikkate alır — esas/karar no'ları her dairede
                # yılda sıfırdan başladığından, GERÇEKTEN FARKLI bir dairenin
                # aynı numaralı kararı 'aynı künye' sayılıp yanlış yere RET
                # üretmez (ve --damga-degistir ile YANLIŞ bölüm hükümsüz
                # kılınmaz — bkz. `_eski_bolumleri_gecersiz_kil`).
                daire_sonuc = ko_mod.daire_key(args.sonuc)

                # P0-2 DÜZELTME (d): aynı künye için kütükteki (append-only) SON
                # DAMGA'dan FARKLI bir --damga sessizce vurulamaz — salt-ALEYHE'nin
                # ikinci bir `teyit --damga LEHE` çağrısıyla (dosya elle
                # düzenlenmeden) örtülü biçimde temizlenmesi yolu kapanır.
                son_damga_kutukte = ko_mod.kutukten_son_damga(
                    yol("teyit", "kunye-teyit.md"), esas_sonuc, karar_sonuc, daire_sonuc)
                if son_damga_kutukte is not None and son_damga_kutukte != args.damga:
                    if not args.damga_degistir or len(args.damga_degistir.strip()) < 40:
                        sys.exit(
                            f"RET: bu künye için kütükteki SON DAMGA farklı "
                            f"('{son_damga_kutukte}' ≠ '{args.damga}') — damga sessizce "
                            "değiştirilemez (anayasa m.6 fail-closed). Bilinçli değişim "
                            "için --damga-degistir \"<gerekçe, ≥40 karakter>\" verin.")

        # --dokum: teyit satırını ham MCP döküm dosyasına bağlar. DÜZELTME
        # (v0.5.5 düzeltme turu — KAYNAK-IZI yolu): kütüğe de mutlak makine
        # yolu DEĞİL, muhakeme dosyasıyla AYNI köke-göreli/posix yol yazılır
        # (`_kaynak_izi_yolu`, tek-yazar kuralı — taşınabilirlik+anonimlik).
        dokum_hucre = ""
        if args.dokum:
            d = _hucre(_kaynak_izi_yolu(args.dokum, args.kok))
            dokum_hucre = f"[döküm]({d})"
            if not os.path.exists(args.dokum):
                print(f"UYARI: döküm dosyası bulunamadı: {args.dokum} — link kaydedildi, dosya yok.")

        # DÜZELTME (v0.5.5 düzeltme turu — P0-2 (d) sızma yolu, İKİNCİ KATMAN):
        # kullanıcı-kontrolündeki taban (args.sonuc) script'in KENDİ ekleyeceği
        # DAMGA= son ekinden ÖNCE _sonuc_damga_ize_karismasin'den geçirilir —
        # kütükte kalan TEK 'DAMGA=' izi HER ZAMAN doğrulanmış olur.
        sonuc_yazilan = _sonuc_damga_ize_karismasin(args.sonuc)
        if is_arama:
            sonuc_yazilan += " [ARAMA — tam metin çekilmedi]"
        if args.damga:
            sonuc_yazilan += f" DAMGA={args.damga}"
            if (args.damga_degistir and ko_mod is not None and son_damga_kutukte is not None
                    and son_damga_kutukte != args.damga):
                # DÜZELTME (v0.5.5 şerh turu 2 — YENİ-3, KÜÇÜK): gerekçe de
                # (args.sonuc tabanı gibi) `_sonuc_damga_ize_karismasin`'den
                # geçirilir — aksi hâlde kullanıcı-kontrolündeki gerekçe
                # metni hücreye İKİNCİ bir ham `DAMGA=` tokenı bırakabiliyordu
                # (docstring'in 'kütükte kalan TEK gerçek DAMGA= izi HER ZAMAN
                # script'in kendisinin eklediği olur' garantisini
                # dokümante-edilmemiş bir ilk-eşleşme sıralamasına
                # dayandırıyordu — bu satırla garanti fiilen doğru olur).
                gerekce_h = _sonuc_damga_ize_karismasin(args.damga_degistir.strip())
                sonuc_yazilan += (f" (DEĞİŞTİRİLDİ — önceki: {son_damga_kutukte}; "
                                   f"gerekçe: {gerekce_h})")

        # DÜZELTME (v0.5.5 düzeltme turu — P0-2 (d) BLOKER, salt-ALEYHE sızma
        # yolu): kütüğe yazılan HER serbest-metin alanı `_hucre`'den geçirilir
        # — gömülü bir `\n` artık sahte bir ikinci tablo satırı AÇAMAZ, gömülü
        # bir `|` artık hücreleri kaydırıp `kutukten_son_damga`'yı şaşırtamaz.
        # DÜZELTME (v0.5.5 şerh turu — Ş1, savunma katmanı): `args.arac`
        # `_arac_normalize_ve_dogrula`'dan zaten güvenli çıkar, ama kütük
        # hücresine yazılan HER alan (arac dahil) yine de `_hucre`'den geçer
        # — dokunulmazlar listesindeki 'her serbest-metin alanı _hucre'den
        # geçirilir' ilkesi hiçbir istisna BIRAKMAZ.
        arac_h = _hucre(args.arac)
        sorgu_h = _hucre(args.sorgu)
        sonuc_h = _hucre(sonuc_yazilan)
        with open(yol("teyit", "kunye-teyit.md"), "a", encoding="utf-8") as f:
            f.write(f"| {ts()} | {arac_h} | {sorgu_h} | {sonuc_h} | {dokum_hucre} |\n")
        print("Teyit kütüğüne işlendi." + (f" (döküm: {args.dokum})" if args.dokum else ""))

        if args.damga:
            if args.damga == "ALEYHE":
                print("UYARI: ALEYHE damgalı karar dış çıktıya GİREMEZ (anayasa m.6 — "
                      "müvekkil-aleyhi dış çıktı yasağı); yalnız iç analiz/oa-antitez "
                      "cephaneliğinde tutulur.")
            # v0.5.8.4 [G5] — LEHE + aşılmışlık ÇELİŞKİLİDİR (aşılmış karar
            # lehte dayanak olamaz). Üretici yine de yazar (kütük hijyeni ve
            # damga kararı avukatındır — bloklamaz) ama SESSİZ geçmez.
            if args.damga == "LEHE" and (_g5_asan or _g5_asilma or _g5_bitis):
                print("UYARI: DAMGA=LEHE ama AŞILMIŞLIK alanı dolu — AŞILMIŞ içtihat "
                      "lehte dayanak olamaz; dilekçede atfı varsa ictihat_muhakeme_"
                      "denetim [G5] kapısı TESLİM ENGELİ üretir (damga gözden "
                      "geçirilmeli: --damga-degistir).")
            if (ko_mod is not None and args.damga_degistir and son_damga_kutukte is not None
                    and son_damga_kutukte != args.damga):
                degisen = _eski_bolumleri_gecersiz_kil(
                    ko_mod, yol("cikti"), esas_sonuc, karar_sonuc, daire_sonuc,
                    son_damga_kutukte, args.damga_degistir)
                if degisen:
                    print(f"Eski muhakeme bölümü GEÇERSİZ-KILINDI olarak işaretlendi "
                          f"({degisen} dosya).")
            cikti_dizin = yol("cikti")
            os.makedirs(cikti_dizin, exist_ok=True)
            muhakeme_yolu = os.path.join(cikti_dizin, "03-ictihat-muhakeme.md")
            yeni = not os.path.exists(muhakeme_yolu)
            # DÜZELTME (v0.5.5 düzeltme turu — CR bypass, EK SAVUNMA): bkz.
            # yukarıdaki `_eski_bolumleri_gecersiz_kil` yorum satırı — aynı
            # gerekçeyle `newline="\n"`.
            with open(muhakeme_yolu, "a", encoding="utf-8", newline="\n") as f:
                if yeni:
                    f.write("# İçtihat Muhakeme Kaydı — teyit ritüeli (append-only, çok-bölümlü)\n\n")
                # DÜZELTME (v0.5.5 düzeltme turu — TAM BÖLÜM enjeksiyonu,
                # BLOKER): serbest-metin alanları `_muhakeme_kacis`'ten
                # GEÇMEDEN dosyaya yazılmaz (bkz. fonksiyon docstring'i) —
                # --ilgili-kisim/--bag/--ayirt/--sonuc üzerinden hayalet
                # `**KUNYE:**` bölümü enjeksiyonu kapanır.
                f.write(f"**KUNYE:** {_muhakeme_kacis(args.sonuc)}\n")
                # DÜZELTME (v0.5.5 şerh turu 2 — YENİ-1, savunma katmanı):
                # `_kaynak_izi_yolu` artık satır-sonu taşıyan bir --dokum
                # yolunu girişte fail-closed RET eder, ama bu satır da
                # komşularıyla (KUNYE/arac/ilgili-kisim/bag/ayirt) SİMETRİK
                # olsun diye yine `_muhakeme_kacis`'ten geçirilir — tek
                # istisna BIRAKILMAZ (tek-yazar kuralı).
                f.write(f"**KAYNAK-IZI:** {_muhakeme_kacis(_kaynak_izi_yolu(args.dokum, args.kok))}\n")
                # DÜZELTME (v0.5.5 şerh turu — Ş2, BLOKER): `args.arac` bu
                # satırda da (komşu alanlar gibi) `_muhakeme_kacis`'ten
                # geçirilir — TAM BÖLÜM enjeksiyonunun `--arac` üzerinden
                # atlattığı tek alan kapatılır.
                f.write(f"_(kütük satırı: {ts()} | {_muhakeme_kacis(args.arac)})_\n")
                # KAYNAK-URL (v0.5.5.3): dilekçede künye yanına parantez içinde
                # yazılacak RESMİ bağlantı. Yalnız TEYİT ANINDA kaydedilmiş bir
                # URL yazılabilir — yazım aşamasında model bağlantı ÜRETEMEZ.
                # Uydurma link, çıplak künyeden DAHA KÖTÜDÜR: çıplak künye
                # "teyit edilmedi" der, sahte link "teyit edildi" der. Satır
                # yalnız URL VARSA basılır (yokluk = dilekçeye yazılmayacak).
                # `getattr` — bu fonksiyon CLI dışında, elle kurulmuş Namespace
                # ile de İN-PROCESS çağrılır (testler ve kardeş scriptler);
                # yeni bir alanın yokluğu çağıranı ÇÖKERTMEMELİDİR.
                _kurl = getattr(args, "kaynak_url", None)
                if _kurl:
                    f.write(f"**KAYNAK-URL:** {_muhakeme_kacis(_kurl)}\n")
                f.write(f"**DAMGA:** {args.damga}\n")
                # v0.5.8.4 [G5] — aşılmışlık satırları: biçim
                # `ictihat_muhakeme_denetim.py`'nin ASAN_KAYNAK_LINE_RE /
                # ASILMA_TARIHI_LINE_RE / GECERLILIK_BITIS_LINE_RE regexleriyle
                # BİREBİR uyumludur (round-trip); komşu alanlar gibi
                # `_muhakeme_kacis`'ten geçer (tek istisna BIRAKILMAZ).
                if _g5_asan:
                    f.write(f"**AŞAN-KAYNAK:** {_muhakeme_kacis(_g5_asan)}\n")
                if _g5_asilma:
                    f.write(f"**AŞILMA-TARİHİ:** {_muhakeme_kacis(_g5_asilma)}\n")
                if _g5_bitis:
                    f.write(f"**GEÇERLİLİK-BİTİŞ:** {_muhakeme_kacis(_g5_bitis)}\n")
                f.write("\n")
                f.write("## İLGİLİ-KISIM\n" + _muhakeme_kacis(args.ilgili_kisim.strip()) + "\n\n")
                f.write("## DAVAYA-BAĞ\n" + _muhakeme_kacis(args.bag.strip()) + "\n\n")
                f.write("## AYIRT-ETME\n" +
                        _muhakeme_kacis(args.ayirt.strip() if args.ayirt else "") + "\n\n")
            print(f"Muhakeme kaydı işlendi: {muhakeme_yolu}")

        basarili = True
    finally:
        # DÜZELTME (v0.5.5 düzeltme turu — YETİM DÖKÜM): bu çağrıda YENİ
        # yazılan bir döküm dosyası varsa, `.son-dokum` YALNIZ tüm denetimler
        # geçip kütük/muhakeme yazımı TAMAMLANDIYSA güncellenir; herhangi bir
        # RET'te az önce yazılan dosya SİLİNİR (yetim iz kalmaz).
        if dokum_bu_cagride_yazilan:
            if basarili:
                with open(yol("teyit", ".son-dokum"), "w", encoding="utf-8") as f:
                    f.write(dokum_bu_cagride_yazilan)
            else:
                try:
                    os.remove(dokum_bu_cagride_yazilan)
                except OSError:
                    pass


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


# ── M1 (Paket D, v0.5.5) — PAS PROTOKOLÜ: TEZ + ÖNCEKİ PAS enjeksiyonu ──────
# `ajan-brif` çalışma köküne kardeş scriptleri (tam_tur.py — TEZ okumak için,
# pipeline_kayit.py — son işlenen `pas_yolu`yu okumak için) İN-PROCESS import
# eder (tam_tur.py'nin kendi `_pipeline_kayit_modulu` desenindeki gibi — ikinci
# bir subprocess sınıfı açılmaz). Her iki modül de bu scriptle AYNI klasörde
# (`oa-pipeline/scripts/`) yaşar; yol arayışı __file__ göreli, kırılgan değil.
_TAM_TUR_MOD_H = None
_PIPELINE_KAYIT_MOD_H = None


def _kardes_modul_yukle(dosya_adi, global_ad):
    mod = globals().get(global_ad)
    if mod is not None:
        return mod
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), dosya_adi)
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location(f"_oa_hafiza_inproc_{dosya_adi}", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    globals()[global_ad] = mod
    return mod


def _calisma_koku():
    """`KOK` (`<kok>/_oa` ya da salt `_oa`) → çalışma kökü (ebeveyn klasör).
    `--kok` verilmemişse (KOK == '_oa') kök CWD'dir ('.')."""
    ebeveyn = os.path.dirname(KOK)
    return ebeveyn if ebeveyn else "."


def _guncel_tez():
    """`tam_tur.py`nin durum.json'undan güncel DAVA TEZİni okur (M1). tam_tur
    hiç kullanılmamışsa/kayıt yoksa None — kapı sessizce atlanır."""
    mod = _kardes_modul_yukle("tam_tur.py", "_TAM_TUR_MOD_H")
    if mod is None:
        return None
    try:
        durum = mod._durum_oku(_calisma_koku())
    except Exception:
        return None
    return (durum or {}).get("tez") or None


_PAS_KAPSAM_DISI = "__OA_PAS_KAPSAM_DISI__"  # M1 YENİ-1 — sentinel (bkz. cmd_ajan_brif)


def _onceki_pas_govdesi():
    """P1-11 PAS PROTOKOLÜ (M1) — pipeline defterindeki EN SON `pas_yolu`yu
    bulur (`son_pas_yolu`) ve dosyanın TAM içeriğini (kayıpsız — özetlenmeden,
    `PAS_AZAMI_BAYT` tavanına kadar) döndürür: (yol, icerik) ya da defter/pas
    yoksa (None, None).

    YENİ-1 (Paket D DÜZELTME, ikinci savunma katmanı) — `pipeline_kayit.py
    --isle` girişte artık `_oa/cikti/` dışına çıkan bir `--pas-yolu`yu RET ile
    reddediyor, ama defter DAHA ÖNCEden (bu düzeltmeden önce) kirlenmiş
    olabilir. Bu yüzden burada da kapsam denetimi TEKRAR yapılır: kapsam
    dışıysa gövde HİÇ OKUNMAZ, (yol, _PAS_KAPSAM_DISI) döner — çağıran görünür
    bir uyarı basar, dosya İÇERİĞİ asla brife sızmaz."""
    mod = _kardes_modul_yukle("pipeline_kayit.py", "_PIPELINE_KAYIT_MOD_H")
    if mod is None:
        return None, None
    kok = _calisma_koku()
    olaylar_yol = os.path.join(kok, "_oa", "defter", "pipeline-olaylar.jsonl")
    if not os.path.isfile(olaylar_yol):
        return None, None
    try:
        d = mod.derle(olaylar_yol)
        pas_yolu = mod.son_pas_yolu(d)
    except Exception:
        return None, None
    if not pas_yolu:
        return None, None
    kapsam_disi_mi = getattr(mod, "_pas_yolu_kapsam_disi_mi", None)
    if kapsam_disi_mi is not None:
        try:
            if kapsam_disi_mi(kok, pas_yolu):
                return pas_yolu, _PAS_KAPSAM_DISI
        except Exception:
            return pas_yolu, _PAS_KAPSAM_DISI  # belirsizlikte FAIL-CLOSED: okuma
    tam_yol = pas_yolu if os.path.isabs(pas_yolu) else os.path.join(kok, pas_yolu)
    if not os.path.isfile(tam_yol):
        return pas_yolu, None
    azami = getattr(mod, "PAS_AZAMI_BAYT", 256 * 1024)
    try:
        with open(tam_yol, encoding="utf-8", errors="replace") as f:
            icerik = f.read(azami + 1)
    except OSError:
        return pas_yolu, None
    if len(icerik) > azami:
        icerik = icerik[:azami] + f"\n… (pas kırpıldı — azami {azami} bayt; tam metni: {pas_yolu})"
    return pas_yolu, icerik


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
    tez = _guncel_tez()
    pas_yolu, pas_govde = _onceki_pas_govdesi()
    on_blok = f"TEZ (dosyanın güncel hukuki tezi — P1-11 PAS PROTOKOLÜ): {tez or '(henüz belirlenmedi — tam_tur.py --tez ile kaydedilmeli)'}\n"
    if pas_yolu:
        if pas_govde == _PAS_KAPSAM_DISI:
            on_blok += (f"\n0) ÖNCEKİ PAS kayıtlı ({pas_yolu}) ama _oa/cikti/ DIŞINA işaret ediyor — "
                        "GÜVENLİK NEDENİYLE DEVRALINMADI (M1 kapsam denetimi, YENİ-1).\n")
        elif pas_govde is not None:
            on_blok += (f"\n0) ÖNCEKİ PAS (devral, 1. sırada — `{pas_yolu}`, TAM içerik, kayıpsız):\n"
                        f"----- ÖNCEKİ PAS BAŞLANGICI -----\n{pas_govde}\n----- ÖNCEKİ PAS SONU -----\n")
        else:
            on_blok += f"\n0) ÖNCEKİ PAS kayıtlı ({pas_yolu}) ama dosya diskte okunamadı — kontrol et.\n"
    print(f"""=== ALT-AJAN BRİFİ (Agent aracına aynen ver) ===
Sen Ortak Avukat ailesinin `{args.parca}` parçasını yürüten alt-ajansın.

{on_blok}
1) ÖNCE şu dosyayı Read ile TAM oku ve disiplinini aynen uygula: {skill_yol}
2) Bağlamı devral: `_oa/dosya.md` + son devir paketi ({son_devir}) + `_oa/defter/pipeline-durum.json`.
3) Görev: {args.gorev}
<!-- oa:brif:KURALLAR-BAS -->
4) KURALLAR (anayasal — operasyonel):
   - PAS PROTOKOLÜ: bu pasın çıktısı (`_oa/cikti/NN-{args.parca}-*.md`) İLK SATIRINDA `TEZ: <yukarıdaki güncel tez>` taşır; sonraki parça brifinde bu pas ÖNCEKİ PAS olarak devralınacaktır — `pipeline_kayit.py --isle ... --pas-yolu "_oa/cikti/NN-..."` ile deftere işlenmesi bu devrin KOŞULUDUR.
   - Fiilen yapılmadan hiçbir MCP çağrısı "yapıldı", koşmadan hiçbir script "koştu" sayılmaz.
   - Her künye/madde teyidini `python <oa-pipeline>/scripts/oa_hafiza.py teyit --arac ... --sorgu ... --sonuc ...` ile kütüğe işle; kütükte olmayan künye çıktına giremez.
   - Tek-komut içtihat örneği: `teyit --arac ictihat_getir --sorgu "..." --sonuc "..." --damga LEHE|ALEYHE|ALEYHE-AYIRT|NOTR --bag "..." --dokum-icerik @ham.txt` — damgasız içtihat kütüğe, kütüksüz künye çıktıya GİREMEZ.
   - TESLİM tanımı tekildir: `teslim_paketi.py` exit 0 + makbuz; makbuzsuz hiçbir çıktı TESLİM/FINAL adı alamaz.
   - `_oa/analiz/dosya-analiz.md` ham evrakın YERİNE GEÇMEZ; her vakıa/iddia dayanağı ham evraktan (metin/ + .harita.json) doğrulanır — özet üzerinden dilekçe yazılmaz.
   - Kalıcı her üretimini `_oa/cikti/` altına ÇALIŞMA EVRAKI adıyla yaz (NN-parca-icerik); müvekkil evrakını DEĞİŞTİRME (salt-okunur).
   - Dışarı (bulut/web) veri gönderilecekse önce oa-gizlilik taraması (Layer 0).
   - Çıktın karar materyalidir, karar değildir; belirsizliği etiketle, uydurma.
5) OKUMA DİSİPLİNİ (GATE B — `okuma_kapisi.py`, mekanik): Önce `_oa/analiz/dosya-analiz.md`
   + `_oa/metin/00-INDEX.md`; büyük işaretli (`buyuk: true`) evrakta önce `<evrak>.harita.json`dan
   ilgili bölüm, sonra gerekeni TAM oku — DERİNLİK ASLA KISILMAZ, amaç bilinçli seçimdir (m.4:
   dosya-analiz.md ham evrakın yerine geçmez). Tam yüklemeyi
   `okuma_kapisi.py --kok . --tam-yukle-kaydet "<kaynak>" --ajan {args.parca}` ile deftere logla;
   içtihat MCP turundan önce ucuz ön-bakış için `kunye_teyit.py --once-bak "<künye metni>"` kullan
   — kütükte zaten teyitliyse yeni tur gerekmez.
<!-- oa:brif:ANAYASA-BAS -->
6) ANAYASA ÖZETİ — standalone koşan alt-ajana taşınan çekirdek (kaynak: {anayasa_kaynak}):
{anayasa_blok}
7) Dönüşünü DEVİR PAKETİ formatında ver (ne yapıldı → ne bekleniyor → kanıt) ve
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
    s.add_argument("--dokum-icerik", dest="dokum_icerik", default=None,
                    help="ham döküm İÇERİĞİ — '@dosya' | '-' (stdin) | düz metin; script "
                         "kendi döküm dosyasını _oa/teyit/dokum/'a yazar (P0-2)")
    s.add_argument("--damga", default=None, choices=sorted(DAMGA_ENUM),
                    help="LEHE|ALEYHE|ALEYHE-AYIRT|NOTR — GETİR araçlarında ZORUNLU, "
                         "ARAMA araçlarında YASAK (tam metin gerektirir)")
    s.add_argument("--bag", default=None,
                    help="DAVAYA-BAĞ metni (--damga verildiğinde ZORUNLU, ≥40 karakter)")
    s.add_argument("--ayirt", default=None,
                    help="AYIRT-ETME metni (yalnız DAMGA=ALEYHE-AYIRT'ta ZORUNLU, ≥20 karakter)")
    s.add_argument("--ilgili-kisim", dest="ilgili_kisim", default=None,
                    help="İLGİLİ-KISIM — VERBATİM alıntı (--damga verildiğinde ZORUNLU; "
                         "döküm içeriğinde dize olarak geçtiği doğrulanır)")
    s.add_argument("--kaynak-url", dest="kaynak_url", default=None,
                    help="Kararın RESMİ KAYNAK BAĞLANTISI (http/https). Dilekçede künye "
                         "yanına parantez içinde bu bağlantı yazılır; kaydedilmemişse "
                         "YAZILMAZ (uydurma link, çıplak künyeden daha kötüdür)")
    s.add_argument("--asan-kaynak", dest="asan_kaynak", default=None,
                    help="v0.5.8.4 [G5] bu kararı AŞAN kaynağın künyesi (İBK / kanun "
                         "değişikliği / daire kayması) — muhakeme kaydına "
                         "**AŞAN-KAYNAK:** satırı yazılır; ictihat_muhakeme_denetim "
                         "[G5] kapısı okur (yalnız --damga ile birlikte)")
    s.add_argument("--asilma-tarihi", dest="asilma_tarihi", default=None,
                    help="v0.5.8.4 [G5] aşılma tarihi — muhakeme kaydına "
                         "**AŞILMA-TARİHİ:** satırı yazılır (yalnız --damga ile)")
    s.add_argument("--gecerlilik-bitis", dest="gecerlilik_bitis", default=None,
                    help="v0.5.8.4 [G5] içtihadın geçerlilik bitişi — muhakeme kaydına "
                         "**GEÇERLİLİK-BİTİŞ:** satırı yazılır (yalnız --damga ile); "
                         "bir karar 'aşıldı' işaretlenirken üç alan TEK komutla verilebilir")
    s.add_argument("--sorgu-onayli", dest="sorgu_onayli", action="store_true",
                    help="Layer-0 ucuz sorgu taramasını (TCKN/ad-soyad/mahkeme+esas/IBAN) "
                         "bilinçli biçimde geçer")
    s.add_argument("--damga-degistir", dest="damga_degistir", default=None,
                    help="Aynı künye için kütükteki SON DAMGA'dan FARKLI bir --damga "
                         "veriliyorsa ZORUNLU (≥40 karakter gerekçe) — P0-2 DÜZELTME (d): "
                         "damga sessizce değiştirilemez; eski muhakeme bölümüne "
                         "GEÇERSİZ-KILINDI satırı eklenir, gerekçe kütüğe de yazılır")
    s = sub.add_parser("sure-flag", parents=[ortak])
    s.add_argument("--tarih"); s.add_argument("--aciklama"); s.add_argument("--kural")
    s.add_argument("--tur", choices=["usul", "maddi"],
                    help="süre türü (sure_nobetci.py etiketinde gösterilir); opsiyonel")
    s = sub.add_parser("ajan-brif", parents=[ortak])
    s.add_argument("--parca", required=True); s.add_argument("--gorev", required=True)
    s.add_argument("--skill-yol")
    s = sub.add_parser("oturum", parents=[ortak]); s.add_argument("--not", dest="not_")
    s = sub.add_parser("oturum-kapat", parents=[ortak]); s.add_argument("--not", dest="not_")
    s.add_argument("--serhle", default=None,
                    help="(P1-8) KAPANIŞ Gate (pipeline_kayit --denetle) HİÇ koşulamadıysa "
                         "(script yok/import çöktü) dar RET'i ≥30 karakter GEREKÇEYLE geçer — "
                         "şerh devir notuna KESMESİZ yazılır. Denetim fiilen koştuysa (sorun/"
                         "uyarı bulsa dahi) --serhle GEREKMEZ; kapanış zaten devam eder.")
    sub.add_parser("durum", parents=[ortak])

    args = ap.parse_args()
    _kok_ayarla(getattr(args, "kok", None))
    {"init": cmd_init, "oturum-ac": cmd_oturum_ac, "devir": cmd_devir,
     "teyit": cmd_teyit, "sure-flag": cmd_sure_flag, "ajan-brif": cmd_ajan_brif,
     "oturum": cmd_oturum, "oturum-kapat": cmd_oturum_kapat,
     "durum": cmd_durum}.get(args.komut, lambda a: ap.print_help())(args)


if __name__ == "__main__":
    main()
