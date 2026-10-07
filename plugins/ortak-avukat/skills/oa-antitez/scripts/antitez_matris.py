#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
antitez_matris.py — DETERMİNİSTİK antitez/çürütme motoru.

Amaç (Can): Antitez DURUM FARKINDALIĞI içindir. Karşı tarafın bizi kapatacak
savunma/iddialarını işin ilk etabında görür, sonra her birini ÇÖKERTİRİZ.
Çıktı: çürütülmüş ve güçlenmiş konumumuz + dürüstçe işaretlenmiş artık riskler.

Dürüst sınır (anayasa gereği): Bu script hukuki içeriği ÜRETMEZ. İki deterministik
iş yapar:
  1. İSKELET: sabit, eksiksiz "saldırı cepheleri" listesini ve doldurulacak matris
     şablonunu üretir (protokol her seferinde aynı sırada çalışır).
  2. DENETİM: doldurulmuş matrisi eksiksizlik + bütünlük açısından denetler —
     hiçbir cephe atlanmadı mı, her antitezin çürütmesi YA DA işaretli artık riski
     var mı, her çürütme dayanağı teyitli mi. Eksikleri/kör noktaları raporlar.
Hukuki muhakemeyi sen yaparsın; künyeyi oa-ictihat (Yargı/Mevzuat MCP) doğrular.

Kullanım:
  python antitez_matris.py --iskelet                 # cepheler + boş şablon
  python antitez_matris.py --dogrula matris.json      # doldurulmuş matrisi denetle

M3 (Paket D, v0.5.5) — DUYULMUŞ alanı: her cephe kaydı artık bir `duyulmus`
(bool) taşır — karşı taraf bu antitezi FİİLEN ileri sürdü mü (cevap dilekçesi/
karar gerekçesi/dosyadaki bir belgede)? `False` (varsayılan) = hipotetik/dahili
antitez (dilekçeye GİRMEZ, cephanelikte kalır); `True` = duyulmuş antitez
(dilekçede çürütmesiyle karşılanabilir — bkz. oa-dilekce "Çıplak künye yasağı"
ile aynı dış/iç ayrımı). `oa-dilekce/scripts/dilekce_denetim.py`'nin [G] ANTİTEZ-
CEVAP-ÇAPASI advisory kapısı `duyulmus_curutmeler()`'i çağırıp duyulmuş+çürütülmüş
her cephenin dilekçede bir karşılığı (çapa) var mı diye BAKAR (bloklamaz).

v0.5.16 (P1-5 / A-20) — 9. cephe `bilirkisi_teknik` (bkz. STANDART_CEPHELER
yorumu). Eski sekiz cepheli matrisler `--dogrula`da "AÇIK CEPHE: bilirkisi_teknik"
alır — istenen etkidir (kör nokta görünür; sessiz uyum YOK). `duyulmus_curutmeler()`
sözleşmesi ve [G] kapısının okuduğu `_oa/cikti/*antitez*.json` adı DEĞİŞMEDİ.

v0.5.18 (B-8 — antitez K1 sözleşmesine girdi; Fable tutarlılık raporu
2026-10-07): (1) `arac: "antitez_matris"` damgası YALNIZ `--dogrula … --json`
denetim çıktısındadır (K1 damga sözleşmesi = motor çıktısı damgası; vakia/graf/
kıyas ile aynı anlam). `--iskelet` şablonu ve girdi matrisi damga TAŞIMAZ (ana
oturum kararı Ö-1, düzeltme turu 1): aynı damga iki nesnede olsa damgaya bakan
her tüketici girdiyi denetim sanıp DURUM.md'ye sahte "sağlıksız" satırı
yazabilirdi. Girdi matrisi [G] kapısı/bekçi tarafından dosya adıyla
(`*antitez*.json`) ve `cepheler` LİSTESİYLE tanınır. (2) `--dogrula …
--json <yol>` makine-okur denetim JSON'u yazar (S2: arac · girdi · kaynaklar ·
acik_cepheler · curutulmemis · teyitsiz_dayanak · dayanaksiz_guclu ·
artik_riskler · gecersiz · uyarilar · saglikli; sort_keys; atomik yazım) —
DURUM.md hattı açık cepheyi/çürütülmemiş antitezi buradan okur. (3) Cephe
kaydında opsiyonel `hedef: {"halka": "vakia|illiyet|kiyas", "id": str}` —
cephenin zincirin HANGİ halkasına saldırdığı kimlikle bağlanır; biçimsiz
hedef UYARIDIR (şema hatası değil, `saglikli`ye girmez).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import argparse
import hashlib
import json
import os
import sys
import time

# v0.5.18 (B-8): DENETİM ÇIKTISI damgası — pipeline_kayit
# `_denetim_jsonlari(kok, "antitez_matris")` bu literali arar; aile_dogrula
# `_damga_yazar_mi` üretici scriptte `"arac": "<arac>"` ya da `ARAC_ADI = …`
# literalini denetler (K1/H5 damga sözleşmesi). Ö-1 (ana oturum kararı,
# düzeltme turu 1): `--iskelet` şablonu / girdi matrisi bu damgayı TAŞIMAZ —
# aynı damga iki nesnede olsa damgaya bakan her tüketici girdiyi denetim
# sanıp DURUM.md'ye sahte "sağlıksız" satırı yazabilirdi (vakia/graf/kıyas
# ile aynı anlam: damga = motor çıktısı).
ARAC_ADI = "antitez_matris"

# v0.5.18 (B-8): cephe kaydının saldırdığı zincir halkası — opsiyonel `hedef`
# alanının kapalı `halka` kümesi. Kimlik (`id`) o halkanın kendi kimliğidir
# (vakia `olaylar[].id` / `iddialar[].id`, graf düğüm/kenar kimliği, kıyas
# unsur kimliği); eşleme tüketicinin (capraz_denetim) işidir, bu script yalnız
# BİÇİMİ denetler.
HEDEF_HALKALARI = ("vakia", "illiyet", "kiyas")


# ── v0.5.18 (B-1(a)/S1 · B-4/S3) — KAYNAK BEYANI ve ATOMİK JSON YAZIMI ───────
# NEDEN VAR: denetim JSON'u hangi girdiden üretildiğini BEYAN ETMELİ ki künye/
# matris değişince eski denetim "bayat halka" olarak görünür kılınabilsin
# (Fable tutarlılık raporu 2026-10-07, B-1 "zincirleme tepki yok"); yazım
# yarıda kesilirse hedefte yarım JSON kalmasın (B-4). Sözleşme ve gerekçenin
# tamamı oa-vakia/scripts/vakia_matris.py'de aynı başlık altında; dört motor
# aynı iki yardımcıyı (ad + imza) bilinçli olarak taşır — paket yok, ortak
# modül yok (tests/README.md §1). `yol` `_oa`ya göre POSIX göreli, `sha8` =
# sha256[:8] (tazelik_denetim.sha8 ile aynı); `_oa` dışı girdi → [] + not.
OA_DISI_NOTU = "_oa dışı girdi — tazelik denetimi dışı"
KUNYE_GORELI = ("metin", "00-kunye.json")


def _oa_dizini_bul(yol):
    """Dosyayı içeren EN YAKIN `_oa` dizini (mutlak); yoksa None."""
    dizin = os.path.dirname(os.path.abspath(yol))
    while True:
        if os.path.basename(dizin) == "_oa":
            return dizin
        ust = os.path.dirname(dizin)
        if ust == dizin:
            return None
        dizin = ust


def kaynak_beyani(girdi_yolu):
    """S1 → (kaynaklar, kaynaklar_notu). ASLA fırlatmaz: okunamayan kaynak
    beyandan düşer ama NOTA yazılır (sessiz atlama yasağı)."""
    try:
        oa = _oa_dizini_bul(girdi_yolu)
    except Exception:                          # noqa: BLE001 — beyan motoru düşürmez
        oa = None
    if oa is None:
        return [], OA_DISI_NOTU
    kayitlar, notlar = [], []

    def _ekle(rol, dosya):
        try:
            with open(dosya, "rb") as f:
                bayt = f.read()
            goreli = os.path.relpath(os.path.abspath(dosya), oa).replace(os.sep, "/")
        except Exception as e:                 # noqa: BLE001
            notlar.append(f"{rol} kaynak beyanına alınamadı ({type(e).__name__})")
            return
        kayitlar.append({"rol": rol, "yol": goreli,
                         "sha8": hashlib.sha256(bayt).hexdigest()[:8]})

    _ekle("girdi", girdi_yolu)
    kunye = os.path.join(oa, *KUNYE_GORELI)
    if os.path.isfile(kunye):
        _ekle("kunye", kunye)
    kayitlar.sort(key=lambda k: (k["rol"], k["yol"]))
    return kayitlar, (" · ".join(notlar) if notlar else None)


def _atomik_json_yaz(yol, nesne):
    """S3: aynı dizinde geçici dosyaya yaz, `os.replace` ile hedefe taşı.
    Biçim dört motorda aynı (ensure_ascii=False, indent=2, sort_keys=True).
    K-4 (Windows): hedef başka süreçte açıkken (okuyucu, Defender taraması)
    `os.replace` PermissionError verir — 3 kısa yeniden deneme (3 × 80 ms =
    240 ms < 300 ms), sonra istisna AYNEN fırlar (fail-closed: eski dosya
    durur, geçici silinir)."""
    gecici = f"{yol}.{os.getpid()}.oa-tmp"
    try:
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(nesne, f, ensure_ascii=False, indent=2, sort_keys=True)
        for deneme in range(4):
            try:
                os.replace(gecici, yol)
                break
            except PermissionError:
                if deneme == 3:
                    raise
                time.sleep(0.08)
    except BaseException:
        try:
            os.unlink(gecici)
        except OSError:
            pass
        raise


def _hedef_uyarisi(ad, hedef):
    """Opsiyonel `hedef` BİÇİM denetimi → uyarı metni ya da None. Biçimli:
    {"halka": vakia|illiyet|kiyas, "id": boş olmayan dize}. Bilinmeyen biçim
    UYARIDIR, şema hatası değil (`saglikli`ye girmez — bağ bilgisi eksik
    diye matris "eksik" sayılmaz; ama sessizce de yutulmaz)."""
    if isinstance(hedef, dict) and hedef.get("halka") in HEDEF_HALKALARI \
            and isinstance(hedef.get("id"), str) and hedef["id"].strip():
        return None
    return (f"{ad}: 'hedef' biçimsiz — {{\"halka\": \"vakia|illiyet|kiyas\", \"id\": str}} "
            f"bekleniyor (verilen: {json.dumps(hedef, ensure_ascii=False)[:80]})")


# --- Sabit saldırı cepheleri (deterministik omurga — eksiksiz değerlendirilir) ---
STANDART_CEPHELER = {
    "usul":            "Usul/şekil: görev, yetki, derdestlik, kesin hüküm, husumet, dava şartı, süre/hak düşürücü",
    "maddi_vakia":     "Maddi vakıa: olgu doğru/ispatlanabilir mi, iç çelişki var mı",
    "ispat_delil":     "İspat ve delil: ispat yükü kimde, delil caiz mi (HMK m.189/2), yeterli mi",
    "hukuki_niteleme": "Hukuki niteleme: olguya uygulanan norm doğru mu, alternatif norm/sonuç",
    "ictihat":         "İçtihat: dayanılan karar esastan mı, güncel mi, aleyhe içtihat/daire kayması var mı",
    "zamanasimi":      "Zamanaşımı / hak düşürücü süre",
    "defi_karsi_talep":"Def'i / karşı talep / takas (ödeme, ifa, zamanaşımı def'i)",
    "muvekkil_zaaf":   "Müvekkilin kendi belgelerindeki zaaf (oa-kontrol C protokolü ile)",
    # v0.5.16 (P1-5 / A-20): 9. cephe. Saha dersi — çoğu dosyada fiilî karar
    # mercii bilirkişi raporudur; sekiz cephe raporu hiçbir yerde ZORUNLU
    # taramıyordu (kör nokta). Eski sekiz cepheli matrisler bu cepheyi
    # "AÇIK CEPHE" olarak alır — BİLİNÇLİ: sessiz uyum yok, kör nokta görünür.
    # Norm çıpaları Mevzuat MCP'den okundu (teyit 2026-09-06, HMK 6100):
    #   m.279/2 rapor zorunlu içeriği (görevlendirme konusu, maddi vakıa,
    #           gerekçe/sonuç, görüş ayrılığı sebebi, tarih, imzalar) + /3 kurul
    #   m.279/4 hukuki nitelendirme/değerlendirme YASAĞI (Değişik 6754/54)
    #   m.281   tebliğden İKİ HAFTA içinde itiraz; ek süre (7251/24); ek rapor/
    #           yeni bilirkişi
    #   m.293   uzman görüşü (taraf mütalaası; duruşmaya gelmeyen uzmanın
    #           raporu değerlendirilmez)
    "bilirkisi_teknik": ("Bilirkişi/teknik: raporun kırılma noktaları, itiraz stratejisi "
                         "(HMK m.281), uzman görüşü (HMK m.293), hukuki nitelendirme yasağı "
                         "(HMK m.279/4), tek imza/heyet, keşif dayanağı"),
}

GUC_DEGERLERI = {"yuksek", "orta", "dusuk", "yok"}
DAYANAK_DURUMLARI = {"teyitli", "teyitsiz", "yok"}


def iskelet():
    """v0.5.14 (B-26): STDOUT yalnız GEÇERLİ JSON taşır; cephe listesi ve
    açıklamalar STDERR'e gider. `--iskelet > _oa/cikti/NN-antitez.json`
    bugüne kadar ayrıştırılamaz bir dosya üretiyordu — oysa
    `dilekce_denetim.py`'nin [G] ANTİTEZ-CEVAP-ÇAPASI kapısı tam da
    `_oa/cikti/*antitez*.json` dosyalarını okur."""
    def _not(*a):
        print(*a, file=sys.stderr)

    _not("=" * 70)
    _not("  ANTİTEZ CEPHELERİ — durum farkındalığı için EKSİKSİZ değerlendirilir")
    _not("=" * 70)
    for k, v in STANDART_CEPHELER.items():
        _not(f"  [{k}]\n      {v}")
    _not("\n--- Doldurulacak matris şablonu (JSON — STDOUT) ---")
    _not("  Opsiyonel cephe alanı `hedef`: {\"halka\": \"vakia|illiyet|kiyas\", \"id\": \"…\"} —")
    _not("  cephenin saldırdığı zincir halkasının kimliği (vakia olay/iddia id'si, graf düğümü,")
    _not("  kıyas unsuru); bağ yoksa yazmayın. Biçimsiz hedef --dogrula'da UYARI alır.")
    # Ö-1: şablon `arac` damgası TAŞIMAZ — damga yalnız `--dogrula --json` çıktısında.
    sablon = {
        "tez": "Müvekkilin ana tezi — bir cümle",
        "cepheler": [
            {
                "cephe": k,
                "antitez": "Karşı tarafın bu cepheden saldırısı (saldırı yoksa kısaca 'değerlendirildi: saldırı zayıf/yok')",
                "guc": "yuksek|orta|dusuk|yok",
                "curutme": "Bizim çürütmemiz (antitezi nasıl çökertiyoruz)",
                "curutme_dayanak": "Çürütmenin içtihat/mevzuat künyesi veya boş",
                "dayanak_durum": "teyitli|teyitsiz|yok",
                "artik_risk": "Çürütülemeyen kalıntı risk (varsa) — dürüstçe yaz",
                "duyulmus": False,
            }
            for k in STANDART_CEPHELER
        ],
    }
    print(json.dumps(sablon, ensure_ascii=False, indent=2))
    _not("\nDoldurduktan sonra: python antitez_matris.py --dogrula matris.json "
         "--json _oa/cikti/06-antitez-denetim.json")
    _not("  --json ZORUNLU (pipeline): DURUM.md hattı ve teslim makbuzu açık cepheyi / "
         "çürütülmemiş antitezi bu dosyadan okur (opsiyonel kapı = ateşlemeyen kapı).")


def dogrula(path, json_yol=None):
    """Doldurulmuş matrisi denetler; `json_yol` verilirse S2 denetim JSON'unu
    (v0.5.18/B-8) atomik yazar. Exit kodu sözleşmesi DEĞİŞMEZ (bulguda da 0 —
    antitez boşluğu stratejik tercih olabilir; görünürlük DURUM.md hattıyla)."""
    try:
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
    except Exception as e:
        print(f"❌ JSON okunamadı: {e}")
        sys.exit(1)

    # v0.5.14 (B-23): kök tipi denetimi — girdiyi MODEL üretir; kök sözlük
    # değilse (null / [] / "dize") eski kod ham AttributeError traceback'i
    # veriyor, asıl mesaj kayboluyordu.
    if not isinstance(m, dict):
        print(f"❌ JSON kökü sözlük değil ({type(m).__name__}) — antitez_matris "
              '{"tez": "...", "cepheler": [...]} biçiminde bir nesne bekler '
              "(şablon: --iskelet).")
        sys.exit(1)

    tez = m.get("tez", "(tez belirtilmemiş)")
    ham_cepheler = m.get("cepheler") or []
    if not isinstance(ham_cepheler, list):
        ham_cepheler = []
    cepheler = [c for c in ham_cepheler if isinstance(c, dict)]
    bicimsiz_cephe = len(ham_cepheler) - len(cepheler)
    verilen = {c.get("cephe") for c in cepheler}

    eksik_cepheler = [k for k in STANDART_CEPHELER if k not in verilen]
    curutulmemis = []      # saldırı var ama ne çürütme ne artık risk
    teyitsiz_dayanak = []  # çürütme bir künyeye dayanıyor ama teyitsiz
    dayanaksiz_guclu = []  # güçlü antiteze dayanaksız çürütme
    artik_riskler = []     # dürüst kalıntı riskler
    gecersiz = []          # şema hatası
    uyarilar = []          # v0.5.18 (B-8): advisory kanal — biçimsiz `hedef`; saglikli'ye GİRMEZ
    if bicimsiz_cephe:
        # sessiz atlama yasağı: düşürülen kayıt GÖRÜNÜR olsun (B-23)
        gecersiz.append(f"cepheler: {bicimsiz_cephe} kayıt sözlük değil — "
                        "denetime alınmadı")

    saldiri_sayisi = 0
    cozulen = 0

    for c in cepheler:
        ad = c.get("cephe", "(adsız)")
        guc = (c.get("guc") or "").lower()
        curutme = (c.get("curutme") or "").strip()
        dayanak = (c.get("curutme_dayanak") or "").strip()
        durum = (c.get("dayanak_durum") or "").lower()
        risk = (c.get("artik_risk") or "").strip()

        if guc and guc not in GUC_DEGERLERI:
            gecersiz.append(f"{ad}: geçersiz 'guc' = {guc}")
        if durum and durum not in DAYANAK_DURUMLARI:
            gecersiz.append(f"{ad}: geçersiz 'dayanak_durum' = {durum}")
        if c.get("hedef") is not None:                     # v0.5.18 (B-8): opsiyonel halka bağı
            hedef_uyarisi = _hedef_uyarisi(ad, c["hedef"])
            if hedef_uyarisi:
                uyarilar.append(hedef_uyarisi)

        if guc in {"yuksek", "orta", "dusuk"}:
            saldiri_sayisi += 1
            if not curutme and not risk:
                curutulmemis.append(ad)
            elif curutme or risk:
                cozulen += 1
            if curutme and dayanak and durum == "teyitsiz":
                teyitsiz_dayanak.append(f"{ad}: '{dayanak}'")
            if guc == "yuksek" and curutme and not dayanak:
                dayanaksiz_guclu.append(ad)
            if risk:
                artik_riskler.append(f"{ad}: {risk}")

    # --- Rapor ---
    print("=" * 70)
    print("  ANTİTEZ DENETİMİ — KARAR-MALZEMESİ, NİHAİ TEYİT KULLANICININDIR")
    print("=" * 70)
    print(f"Tez: {tez}\n")

    kapsam = (len(STANDART_CEPHELER) - len(eksik_cepheler)) / len(STANDART_CEPHELER)
    print(f"Cephe kapsamı     : {len(STANDART_CEPHELER)-len(eksik_cepheler)}/{len(STANDART_CEPHELER)} (%{kapsam*100:.0f})")
    if saldiri_sayisi:
        print(f"Çürütme kapsamı   : {cozulen}/{saldiri_sayisi} saldırı çürütüldü/işaretlendi")
    print()

    def blok(baslik, items, isaret="!"):
        if items:
            print(f"--- {baslik} ---")
            for it in items:
                print(f"  {isaret} {it}")
            print()

    blok("AÇIK CEPHELER (değerlendirilmemiş — KÖR NOKTA)", eksik_cepheler, "✗")
    blok("ÇÜRÜTÜLMEMİŞ ANTİTEZLER (ne çürütme ne risk işareti)", curutulmemis, "✗")
    blok("TEYİTSİZ DAYANAK (atıf denetimi — oa-kontrol A)", teyitsiz_dayanak, "!")
    blok("GÜÇLÜ ANTİTEZE DAYANAKSIZ ÇÜRÜTME (zayıf)", dayanaksiz_guclu, "!")
    blok("ŞEMA HATASI", gecersiz, "!")
    blok("HEDEF UYARISI (cephe → zincir halkası bağı biçimsiz — advisory, saglikli'ye girmez)",
         uyarilar, "?")
    blok("ARTIK RİSKLER (çürütülemeyen — dürüst rapor; müvekkile sun)", artik_riskler, "→")

    saglikli = not (eksik_cepheler or curutulmemis or teyitsiz_dayanak or gecersiz)
    if saglikli:
        print(">>> Matris bütünlüğü TAMAM: tüm cepheler değerlendirildi, her saldırı")
        print("    çürütüldü ya da artık risk olarak işaretlendi, dayanaklar teyitli. <<<")
    else:
        print(">>> Matris bütünlüğü EKSİK: yukarıdaki kör noktalar/eksikler kapatılmadan")
        print("    dosya 'durum farkındalığı tam' sayılmaz. <<<")
    print("=" * 70)

    if json_yol:
        # v0.5.18 (B-8 / S2): makine-okur denetim — DURUM.md hattı ve teslim
        # makbuzu açık cepheyi / çürütülmemiş antitezi buradan okur. Listeler
        # yukarıdaki rapor bloklarının AYNISIDIR (ikisi ayrışamaz). `girdi`
        # komut satırının yankısı (B-11), `kaynaklar` S1, yazım atomik (S3).
        kaynaklar, kaynaklar_notu = kaynak_beyani(path)
        sonuc = {
            "arac": ARAC_ADI, "girdi": path,
            "kaynaklar": kaynaklar, "kaynaklar_notu": kaynaklar_notu,
            "acik_cepheler": eksik_cepheler,
            "curutulmemis": curutulmemis,
            "teyitsiz_dayanak": teyitsiz_dayanak,
            "dayanaksiz_guclu": dayanaksiz_guclu,
            "artik_riskler": artik_riskler,
            "gecersiz": gecersiz,
            "uyarilar": uyarilar,
            "saglikli": saglikli,
        }
        _atomik_json_yaz(json_yol, sonuc)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")


def duyulmus_curutmeler(m):
    """M3 (Paket D, v0.5.5) — matristeki cephelerden `duyulmus: true` VE dolu
    `curutme` taşıyanları döndürür: `[{"cephe": ..., "curutme": ...}, ...]`.
    Bunlar dilekçede karşılanMASI beklenen (dış çıktıya girebilecek) tek
    antitez sınıfıdır; `dilekce_denetim.py`'nin [G] advisory kapısı bunu
    çağırır. Şema hatalı/`m` beklenmedik biçimliyse boş liste döner (fail-
    safe — bu bir ADVISORY girdisidir, hiçbir zaman çökmez)."""
    try:
        cepheler = m.get("cepheler", []) if isinstance(m, dict) else []
    except Exception:
        return []
    sonuc = []
    for c in cepheler:
        if not isinstance(c, dict):
            continue
        if c.get("duyulmus") and (c.get("curutme") or "").strip():
            sonuc.append({"cephe": c.get("cephe"), "curutme": c["curutme"].strip()})
    return sonuc


def main():
    p = argparse.ArgumentParser(description="Deterministik antitez/çürütme motoru")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--iskelet", action="store_true", help="Cephe listesi + boş şablon üret")
    g.add_argument("--dogrula", metavar="JSON", help="Doldurulmuş matrisi denetle")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="--dogrula ile: denetim sonucunu makine-okur JSON olarak bu yola yaz "
                        "(v0.5.18/B-8 — DURUM.md hattı `arac == antitez_matris` damgasını okur; "
                        "--iskelet ile verilirse yok sayılır)")
    a = p.parse_args()
    if a.iskelet:
        iskelet()
    else:
        dogrula(a.dogrula, json_yol=a.json_yol)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # head/less gibi araçlara borulanınca sessizce çık
        sys.stderr.close()
