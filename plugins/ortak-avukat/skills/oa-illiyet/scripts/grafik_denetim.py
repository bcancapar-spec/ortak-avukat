#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-illiyet — grafik_denetim.py
Nedensellik/ilişki grafının DETERMİNİSTİK boşluk denetimi.

Felsefe (Ortak Avukat anayasası): bu script illiyetin HUKUKİ niteliğine karar
VERMEZ ("uygun illiyet vardır" demez). Yalnızca gözün kaçıracağı YAPISAL
boşlukları kesin yakalar. Hukuki yorum ve nihai karar avukata aittir.

Girdi:  graf.json  (şema aşağıda / references/illiyet-doktrini.md sonunda)
Çıktı:  insan-okunur deterministik denetim raporu (stdout) + --json makine-okur

Kullanım:
    python grafik_denetim.py graf.json --json denetim.json
    python grafik_denetim.py graf.json --json denetim.json --taraf sanik
    python grafik_denetim.py graf.json --json denetim.json --kok <dava kökü>
    python grafik_denetim.py --goc eski.json --dal medeni|miras|ceza --cikti yeni.json

v0.5.16/A-2 (G10, G9, G12, avukat kararları #7 #8 #9 #11):
    - kesme_flag DAL-AYRIMLI (medeni: | miras: | ceza:); eski çıplak değer
      [ŞEMA UYARISI] + "--goc ile dal etiketle" (exit değişmez — geriye uyum).
    - --taraf / --kok (pipeline defteri `ceza_dali`): savunma kanadı (sanık/
      müdafii/davalı/borçlu) için §6/§7/§8 tavsiye yönü TERS ("kur" → "çürüt").
    - tip: karar | mahkeme; kenar tur: kanun_yolu (+ sonuc ZORUNLU) yalnız
      karar/mahkeme düğümleri arasında; illiyet zinciri/çevrim/yük hesabına
      GİRMEZ; §9 KANUN YOLU ZİNCİRİ (JSON kanun_yolu_zinciri).
    Bu scriptteki doktrin notları (ör. ceza:magdur_kusuru) hukuki HÜKÜM değil,
    doktrin HATIRLATMASIDIR — model kurar, script denetler; künye kütükten.

ÇIKIŞ KODU SÖZLEŞMESİ (v0.5.16/A — K2+G6, avukat kararı #1: SERT KAPI):
    0  temiz (şema hatası yok, çevrim yok)
    1  kullanım hatası (argüman yok)
    2  DENETİM ÇÖKTÜ (dosya yok / bozuk JSON / beklenmeyen istisna) —
       stdout'a "DENETİM ÇÖKTÜ: <sınıf>: <mesaj>", --json'a denetim_coktu:true
    3  çevrim VEYA şema hatası var (JSON blok_sinifi: "sema" | "cevrim")
Eski sözleşme (bulguda da exit 0) bilinçli terk edildi: opsiyonel kapı =
ateşlemeyen kapı; exit 0 dönen denetim pipeline'da hiçbir şeyi durdurmuyordu.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import difflib
import json
import os
import sys
import traceback
from collections import defaultdict

# G6: DFS'ler özyinelemesiz yazıldı (aşağıda); bu sınır yalnız savunma
# derinliğidir — 5.000 düğümlük zincirde hiçbir DFS Python yığınına dayanmaz.
try:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))
except Exception:
    pass

ILISKI_KATEGORI = "iliski"
ILLIYET_KATEGORI = "illiyet"
ARAC_ADI = "grafik_denetim"

# ── v0.5.9 T23/P1 SAHTE-YEŞİL kapanışı: SÖZLÜK DENETİMİ (ADVISORY) ──────────
# Bilinmeyen alan adı + kanonik-dışı enum değeri bugüne dek SESSİZCE tolere
# ediliyordu → yanlış alanlı graf "Şema bütün ✓" + 8 yeşil katman + boş
# analiz üretiyordu. Bu sözlük yalnız UYARIR; hiçbir şeyi bloklamaz, exit
# kodunu değiştirmez.
DUGUM_ALANLARI = {"id", "tip", "usul_rolu", "ad"}
KENAR_ALANLARI = {"kaynak", "hedef", "kategori", "tur", "illiyet_tipi", "guc",
                  "kesme_flag", "dayanak_delil", "dogrulama", "norm", "sonuc"}

# ── G10 (Hamle 7, avukat kararı #7): kesme_flag DAL-AYRIMLI — şema KIRILDI ──
# Eski tek liste (mucbir_sebep/magdur_kusuru/ucuncu_kisi_kusuru) medeni hukuk
# doktriniydi; ceza dosyasında "mağdur kusuru" illiyeti KESMEZ (TCK m.22/4-5:
# ceza failin kusuruna göre belirlenir — Mevzuat MCP teyit 2026-09-07), miras
# dosyasında kesme kavramı "paylaştırma kastı / ivaz" ekseninde işler. Aynı
# etiket üç dalda üç ayrı hukuki sonuç doğurduğundan dal öneki ZORUNLU oldu.
# Eski çıplak değer kanonik-dışı [ŞEMA UYARISI] + --goc önerisi alır; exit
# kodu DEĞİŞMEZ (geriye uyum — saha grafları kırılmaz).
KESME_DALLARI = {
    "medeni": ("mucbir_sebep", "magdur_kusuru", "ucuncu_kisi_kusuru"),
    "miras":  ("paylastirma_kasti", "ivaz"),
    "ceza":   ("izin_verilen_risk", "kendi_tehlikesine_girme",
               "hukuka_uygunluk", "magdur_kusuru"),
}
ESKI_KESME_FLAGLAR = {"mucbir_sebep", "magdur_kusuru", "ucuncu_kisi_kusuru"}
# §6 sabit DOKTRİN HATIRLATMALARI — hukuki HÜKÜM değildir (model kurar, script
# denetler); künye KÜTÜKTEN gelir, script hafızadan künye yazmaz.
KESME_NOTLARI = {
    "ceza:magdur_kusuru": (
        "illiyeti KESMEZ — kusur derecesine/ceza miktarına etki eder "
        "(Yargıtay 12. CD yerleşik hattı; künye KÜTÜKTEN, hafızadan yazılmaz; "
        "norm çerçevesi TCK m.22/4-5 — Mevzuat MCP teyit 2026-09-07)"),
    "miras:paylastirma_kasti": (
        "muris muvazaasında bozma gerekçesi — ispat ölçütü (muvazaa çerçevesi "
        "TBK m.19 — Mevzuat MCP teyit 2026-09-06; künye KÜTÜKTEN)"),
}

KANONIK = {  # şema: references/illiyet-doktrini.md §6 (enum tablosu — DOKTRİN↔KOD KİLİDİ:
             # buradaki HER string değer illiyet-doktrini.md'de literal geçer; aile_dogrula denetler)
    "tip": {"gercek_kisi", "tuzel_kisi", "kamu", "nesne", "delil", "olay", "hak",
            "karar", "mahkeme"},                       # G12: karar/mahkeme (kanun yolu katı)
    "kategori": {ILISKI_KATEGORI, ILLIYET_KATEGORI},
    "illiyet_tipi": {"dogal", "uygun", "objektif_isnadiyet"},
    "guc": {"dispozitif", "guclu", "zayif", "tartismali"},
    "kesme_flag": {f"{dal}:{v}" for dal, vs in KESME_DALLARI.items() for v in vs},
    # "delil": bu ağacın saha/fikstür gerçeğinde yerleşik "teyitli" eşanlamı —
    # uyarıya boğmamak için kabul kümesindedir (gürültü disiplini).
    "dogrulama": {"teyitli", "iddia", "karine", "delil"},
    # G12 (Hamle 8, avukat kararı #9): kanun_yolu kenarının ZORUNLU sonucu.
    # HMK m.353 (kaldırma / esastan ret), m.370 (onama); CMK m.280 (esastan ret /
    # bozma / kaldırma), m.302 (esastan ret / bozma) — Mevzuat MCP teyit 2026-09-07.
    "sonuc": {"onadi", "bozdu", "kaldirdi", "geri_cevirdi", "esastan_ret", "kesin"},
}

# G8: mahkeme/karar düğümleri yapıları gereği HER tarafı bağlar — köprü
# (perde) hesabından muaf. A-2 (G12) bu tipleri KANONIK'e ekledi; muafiyet
# tipe göredir.
KOPRU_MUAF_TIPLER = {"karar", "mahkeme"}
# G12: kanun_yolu kenarı yalnız karar|mahkeme düğümleri arasında; illiyet
# zinciri / çevrim / yük hesabına GİRMEZ (yargı kademesi neden-sonuç değildir).
KANUN_YOLU_TUR = "kanun_yolu"
KANUN_YOLU_TIPLER = KOPRU_MUAF_TIPLER
KANUN_YOLU_DERINLIK = 12      # kat sırası DFS derinlik freni (çevrimli kanun yolu çökmesin)

# G9 (Hamle 7, avukat kararı #8): taraf → tavsiye YÖNÜ. Savunma/borçlu/davalı
# kanadı karşı tarafın illiyetini ÇÜRÜTÜR; iddia kanadı KURAR.
SAVUNMA_TARAFLARI = ("sanik", "mudafii", "davali", "borclu")
IDDIA_TARAFLARI = ("katilan", "musteki", "davaci", "alacakli")
TARAFLAR = SAVUNMA_TARAFLARI + IDDIA_TARAFLARI
# pipeline defteri `ceza_dali` (pipeline_kayit.py --baslat --ceza mudafii|musteki)
CEZA_DALI_TARAF = {"mudafii": "sanik", "musteki": "musteki", "musteki-vekili": "musteki"}
DEFTER_DURUM_YOLU = os.path.join("_oa", "defter", "pipeline-durum.json")
DELIL_TIPI = "delil"
DELIL_AD_ESIK = 0.6          # G7: serbest metin dayanak ↔ delil adı benzerlik eşiği
JOHNSON_DUGUM_TAVANI = 200   # G1: bu düğüm sayısına kadar TAM basit çevrim sayımı
CEVRIM_TAVANI = 200          # G1: sayılan çevrim tavanı (yoğun grafta patlama freni)
YAZIM_TAVANI = 40            # stdout satır tavanı (JSON tam listeyi taşır — sessiz kırpma yok)


def _oneri(deger, bilinenler):
    aday = difflib.get_close_matches(str(deger), sorted(bilinenler), n=1, cutoff=0.5)
    return f" — kastedilen '{aday[0]}' olabilir" if aday else ""


def sozluk_uyarilari(dugumler, kenarlar):
    """Bilinmeyen alan adları + kanonik-dışı enum değerleri (ADVISORY)."""
    uyarilar = []

    def _denetle(kayit, etiket, bilinen_alanlar):
        for alan in kayit:
            if alan not in bilinen_alanlar:
                uyarilar.append(f"{etiket}: bilinmeyen alan: '{alan}'"
                                f"{_oneri(alan, bilinen_alanlar)}")
        for alan, kume in KANONIK.items():
            deger = kayit.get(alan)
            if isinstance(deger, str) and deger not in kume:
                if alan == "kesme_flag" and deger in ESKI_KESME_FLAGLAR:
                    # G10: eski çıplak değer — dal öneki eksik; göç önerisi
                    adaylar = " | ".join(f"{d}:{deger}" for d, vs in KESME_DALLARI.items()
                                         if deger in vs)
                    uyarilar.append(
                        f"{etiket}: kanonik-dışı kesme_flag: '{deger}' — eski (dal öneksiz) "
                        f"değer; `--goc <eski.json> --dal medeni|miras|ceza --cikti "
                        f"<yeni.json>` ile dal etiketle (aday: {adaylar})")
                    continue
                if alan == "kesme_flag":
                    # yazım hatası → çıplak ada yakın-eşleşme + dal önekli adaylar
                    ciplak = {v for vs in KESME_DALLARI.values() for v in vs}
                    govde = deger.split(":", 1)[-1]
                    yakin = difflib.get_close_matches(govde, sorted(ciplak), n=1, cutoff=0.5)
                    if yakin:
                        adaylar = " | ".join(f"{d}:{yakin[0]}" for d, vs in KESME_DALLARI.items()
                                             if yakin[0] in vs)
                        uyarilar.append(
                            f"{etiket}: kanonik-dışı kesme_flag: '{deger}' — kastedilen "
                            f"'{yakin[0]}' olabilir; dal önekiyle yaz (kanonik: {adaylar})")
                        continue
                uyarilar.append(f"{etiket}: kanonik-dışı {alan}: '{deger}'"
                                f"{_oneri(deger, kume)}"
                                f" (kanonik: {' | '.join(sorted(kume))})")

    for kid, d in dugumler.items():
        _denetle(d, f"Düğüm '{kid}'", DUGUM_ALANLARI)
    for i, k in enumerate(kenarlar):
        _denetle(k, f"Kenar #{i}", KENAR_ALANLARI)
    return uyarilar


def norm_uyarilari(kenarlar):
    """G3 (Hamle 6): `norm` eksik kenar → [ŞEMA UYARISI] (ADVISORY, hata
    DEĞİL — saha grafları kırılmasın). Doktrin her kenarın normunu ister;
    norm yalnız Mevzuat MCP teyitli yazılır (anayasa m.4/m.5)."""
    return [f"Kenar #{i}: 'norm' eksik (advisory — kenarı hukuken anlamlı kılan "
            "maddeyi Mevzuat MCP teyidiyle bağla)"
            for i, k in enumerate(kenarlar) if not k.get("norm")]


def _kanun_yolu_mu(k):
    return k.get("tur") == KANUN_YOLU_TUR


def _illiyet_kenar_mi(k):
    """G12: illiyet hesaplarına giren kenar = kategori illiyet VE kanun_yolu
    DEĞİL (kanun yolu kenarı kategori ne yazılırsa yazılsın zincire girmez)."""
    return k.get("kategori") == ILLIYET_KATEGORI and not _kanun_yolu_mu(k)


def kanun_yolu_uyarilari(dugumler, kenarlar):
    """G12 (ADVISORY): kanun_yolu kenarı yalnız karar|mahkeme düğümleri arasında
    anlamlıdır; başka uçta [ŞEMA UYARISI]. Kategori 'illiyet' yazılmışsa
    uyarılır (kanun yolu neden-sonuç değildir; hesaba zaten girmez)."""
    uyarilar = []
    for i, k in enumerate(kenarlar):
        if not _kanun_yolu_mu(k):
            continue
        for uc in ("kaynak", "hedef"):
            tip = dugumler.get(k.get(uc), {}).get("tip")
            if tip not in KANUN_YOLU_TIPLER:
                uyarilar.append(
                    f"Kenar #{i}: kanun_yolu kenarının {uc} ucu '{k.get(uc)}' "
                    f"(tip: {tip}) karar | mahkeme değil — kanun_yolu yalnız karar/"
                    "mahkeme düğümleri arasında geçerli")
        if k.get("kategori") == ILLIYET_KATEGORI:
            uyarilar.append(
                f"Kenar #{i}: kanun_yolu kenarı kategori 'illiyet' taşıyor — yargı "
                "kademesi neden-sonuç değildir; illiyet zinciri/çevrim/yük hesabına "
                f"alınmadı (kategori: {ILISKI_KATEGORI} olmalı)")
    return uyarilar


def bosluk_aciklamalari(dugumler, kenarlar):
    """Analiz katmanını boş bırakacak yapısal boşluk SESSİZ geçilmez."""
    notlar = []
    if not dugumler and not kenarlar:
        notlar.append("graf boş (0 düğüm / 0 kenar) — tüm analiz katmanları "
                      "boş çalışacak; graf.json içeriğini denetleyin")
    elif not kenarlar:
        notlar.append(f"0 kenar bulundu ({len(dugumler)} düğüm var) — kenar "
                      "analizleri boş çalışacak; kenar kayıtlarını denetleyin")
    elif not any(k.get("kategori") == ILLIYET_KATEGORI for k in kenarlar):
        notlar.append(f"0 'illiyet' kategorili kenar bulundu ({len(kenarlar)} "
                      "kenar var) — çevrim/yük/zincir katmanları boş çalışacak; "
                      "kategori değerlerini denetleyin (kanonik: "
                      f"{ILISKI_KATEGORI} | {ILLIYET_KATEGORI})")
    return notlar


def yukle(yol):
    """Grafı yükle → (dugumler, kenarlar, on_hatalar).

    v0.5.16/A SÖZLEŞME DEĞİŞİKLİĞİ (K2+G5): eski `{d["id"]: d ...}` sözlük
    üretimi `id` eksik düğümde KeyError traceback'i veriyor, MÜKERRER id'yi
    sessizce yutuyordu (son kayıt öncekini eziyordu). Şimdi: id eksik →
    şema hatası; mükerrer id → şema hatası, İLK kayıt korunur (kayıt
    düşürülmez, hata basılır, exit 3 sınıfına girer). Sözlük/liste olmayan
    kayıtlar fail-closed hata satırıyla dışlanır."""
    with open(yol, "r", encoding="utf-8") as f:
        g = json.load(f)
    hatalar = []
    if not isinstance(g, dict):
        return {}, [], ["graf.json kök nesnesi sözlük değil (fail-closed)"]
    ham_dugumler = g.get("dugumler", [])
    ham_kenarlar = g.get("kenarlar", [])
    if not isinstance(ham_dugumler, list):
        hatalar.append("'dugumler' liste değil (fail-closed — düğümler yok sayıldı)")
        ham_dugumler = []
    if not isinstance(ham_kenarlar, list):
        hatalar.append("'kenarlar' liste değil (fail-closed — kenarlar yok sayıldı)")
        ham_kenarlar = []

    dugumler = {}
    sayac = defaultdict(int)
    for i, d in enumerate(ham_dugumler):
        if not isinstance(d, dict):
            hatalar.append(f"Düğüm #{i}: kayıt sözlük değil (dışlandı)")
            continue
        if "id" not in d or d.get("id") in (None, ""):
            hatalar.append(f"Düğüm #{i}: 'id' eksik")
            continue
        kid = str(d["id"])
        sayac[kid] += 1
        if kid in dugumler:
            continue  # G5: ilk kayıt korunur; hata aşağıda toplanır
        dugumler[kid] = d
    for kid, n in sayac.items():
        if n > 1:
            hatalar.append(f"Düğüm '{kid}': mükerrer id '{kid}' ({n} kez) — ilk kayıt "
                           "korundu, sonrakiler yok sayıldı")

    kenarlar = []
    for i, k in enumerate(ham_kenarlar):
        if not isinstance(k, dict):
            hatalar.append(f"Kenar #{i}: kayıt sözlük değil (dışlandı)")
            continue
        kenarlar.append(k)
    return dugumler, kenarlar, hatalar


def dogrula_sema(dugumler, kenarlar):
    """Şema bütünlüğü — eksik zorunlu alan = hata (UYAP/Anthropic output_schema mantığı).
    G3 (v0.5.16/A): illiyet kenarında `dogrulama` ZORUNLU — doğrulanmamış
    illiyet 'null' kabul edilir (SKILL.md anayasal süzgeç); beyansız kenar
    sessizce teyitli sayılamaz."""
    hatalar = []
    for kid, d in dugumler.items():
        if "tip" not in d:
            hatalar.append(f"Düğüm '{kid}': 'tip' eksik")
        if d.get("tip") == "gercek_kisi" and not d.get("usul_rolu"):
            hatalar.append(f"Düğüm '{kid}' (gerçek kişi): 'usul_rolu' eksik (zorunlu)")
    for i, k in enumerate(kenarlar):
        for alan in ("kaynak", "hedef", "kategori", "tur"):
            if alan not in k:
                hatalar.append(f"Kenar #{i}: '{alan}' eksik")
        if k.get("kaynak") not in dugumler:
            hatalar.append(f"Kenar #{i}: kaynak '{k.get('kaynak')}' tanımsız düğüm")
        if k.get("hedef") not in dugumler:
            hatalar.append(f"Kenar #{i}: hedef '{k.get('hedef')}' tanımsız düğüm")
        if _kanun_yolu_mu(k):                              # G12: sonuc ZORUNLU
            # kanun_yolu illiyet DEĞİLDİR: kategori 'illiyet' yazılmışsa
            # illiyet_tipi/dogrulama istenmez (advisory uyarı ayrıca basılır).
            if not k.get("sonuc"):
                hatalar.append(f"Kenar #{i} (kanun_yolu): 'sonuc' eksik (zorunlu)")
        elif k.get("kategori") == ILLIYET_KATEGORI:
            if "illiyet_tipi" not in k:
                hatalar.append(f"Kenar #{i} (illiyet): 'illiyet_tipi' eksik")
            if not k.get("dogrulama"):
                hatalar.append(f"Kenar #{i} (illiyet): 'dogrulama' eksik (zorunlu)")
    return hatalar


def yetim_dugumler(dugumler, kenarlar):
    """Hiçbir kenara bağlı olmayan düğüm — dosyada neden var?
    G7 (v0.5.16/A, avukat kararı #6): `tip: delil` düğümleri bu sınıfa
    GİRMEZ — delil, kenar ucu değil `dayanak_delil` referansıyla bağlanır;
    onlar `baglanmamis_deliller` ayrı sınıfında denetlenir. Delil dışı
    yetim mantığı değişmedi."""
    bagli = set()
    for k in kenarlar:
        bagli.add(k.get("kaynak"))
        bagli.add(k.get("hedef"))
    return [kid for kid, d in dugumler.items()
            if kid not in bagli and d.get("tip") != DELIL_TIPI]


def _tr_kucuk(metin):
    """Türkçe küçük harf katlama: İ→i, I→ı (str.lower() 'I'→'i' yapar)."""
    return str(metin).replace("İ", "i").replace("I", "ı").lower()


def _delil_eslesir(referans, ad, esik=DELIL_AD_ESIK):
    """Serbest metin dayanak referansı ↔ delil düğümü adı (difflib ratio ≥ esik,
    tr küçük harf katlamalı). Hukuki yorum değil, yazım benzerliği."""
    a, b = _tr_kucuk(referans).strip(), _tr_kucuk(ad).strip()
    if not a or not b:
        return False
    if a == b:
        return True
    sm = difflib.SequenceMatcher(None, a, b)
    if sm.real_quick_ratio() < esik or sm.quick_ratio() < esik:
        return False
    return sm.ratio() >= esik


def _dayanak_listesi(k):
    d = k.get("dayanak_delil")
    if d is None or d == "":
        return []
    if isinstance(d, (list, tuple)):
        return [str(x) for x in d if x not in (None, "")]
    return [str(d)]


def baglanmamis_deliller(dugumler, kenarlar):
    """G7 (Hamle 5): hiçbir kenarın `dayanak_delil`inde anılmayan `tip: delil`
    düğümü = BAĞLANMAMIŞ DELİL (oa-vakia yetim delil semantiği — hangi
    iddiayı/kenarı ispatlıyor?). Referans düğüm id'si olabilir; serbest
    metinse düğüm `ad`ı ile ≥0.6 benzerlik bağlı sayar."""
    deliller = [(kid, d) for kid, d in dugumler.items() if d.get("tip") == DELIL_TIPI]
    if not deliller:
        return []
    referanslar = set()
    for k in kenarlar:
        referanslar.update(_dayanak_listesi(k))
    serbest = [r for r in referanslar if r not in dugumler]
    anilan = set()
    for kid, d in deliller:
        if kid in referanslar:
            anilan.add(kid)
            continue
        ad = d.get("ad")
        if ad and any(_delil_eslesir(r, ad) for r in serbest):
            anilan.add(kid)
    return [kid for kid, _ in deliller if kid not in anilan]


def desteksiz_kenarlar(kenarlar):
    """§3 ispat boşluğu (oa-vakia'ya). G3 (v0.5.16/A): dogrulama YOK veya
    (dogrulama=iddia ve dayanak_delil boş) → yakalar. Eskiden yalnız ikinci
    hal yakalanıyordu; beyansız kenar sessizce 'teyitli' görünüyordu."""
    out = []
    for i, k in enumerate(kenarlar):
        if not k.get("dogrulama"):
            out.append((i, k))
        elif k.get("dogrulama") == "iddia" and not _dayanak_listesi(k):
            out.append((i, k))
    return out


def desteksiz_neden(k):
    if not k.get("dogrulama"):
        return "dogrulama beyan edilmemiş"
    return "iddia + delilsiz"


def guc_beyansiz_kenarlar(kenarlar):
    """G4 (Hamle 6, avukat kararı #5): `guc` beyan edilmemiş illiyet kenarı
    AYRI SINIF — 'beyan-yok' ağırlığı GUC_VARSAYILAN (0.4 ≤ tartışmalı)."""
    return [(i, k) for i, k in enumerate(kenarlar)
            if _illiyet_kenar_mi(k) and not k.get("guc")]


def kesme_adaylari(kenarlar):
    """kesme_flag dolu illiyet kenarları → oa-antitez beslemesi."""
    out = []
    for i, k in enumerate(kenarlar):
        if _illiyet_kenar_mi(k) and k.get("kesme_flag"):
            out.append((i, k))
    return out


def kesme_dali(flag):
    """'ceza:magdur_kusuru' → 'ceza'; dal öneksiz (eski) değer → None."""
    if isinstance(flag, str) and ":" in flag:
        dal = flag.split(":", 1)[0]
        return dal if dal in KESME_DALLARI else None
    return None


def kesme_notu(flag):
    """§6 sabit doktrin hatırlatması (varsa). HÜKÜM değil; künye kütükten."""
    return KESME_NOTLARI.get(flag)


def goc(eski_yol, dal, cikti_yol):
    """G10 göç: `kesme_flag`leri dal önekiyle yeniden etiketler. Kaynağa
    DOKUNMAZ; yalnız dal öneksiz VE hedef dalda kanonik olan değer göçer
    (ör. --dal ceza ile 'ivaz' göçmez → 'atlanan' listesinde, elle düzelt —
    sahte kanoniklik üretilmez). Zaten dal önekli değer aynen kalır. Kategori
    ayrımı yok (iliski kenarındaki flag de göçer — veri kaybı yok).
    Döner: {"degisen": n, "atlanan": [(index, deger)], "kenar": toplam}."""
    if dal not in KESME_DALLARI:
        raise ValueError(f"dal '{dal}' tanımsız (medeni | miras | ceza)")
    with open(eski_yol, "r", encoding="utf-8") as f:
        g = json.load(f)
    if not isinstance(g, dict) or not isinstance(g.get("kenarlar", []), list):
        raise ValueError("graf.json kök nesnesi sözlük değil / 'kenarlar' liste değil")
    degisen, atlanan = 0, []
    for i, k in enumerate(g.get("kenarlar", [])):
        if not isinstance(k, dict):
            continue
        flag = k.get("kesme_flag")
        if not isinstance(flag, str) or not flag:
            continue
        if flag in KANONIK["kesme_flag"]:
            continue                                   # zaten dal önekli
        if ":" not in flag and flag in KESME_DALLARI[dal]:
            k["kesme_flag"] = f"{dal}:{flag}"
            degisen += 1
        else:
            atlanan.append((i, flag))
    with open(cikti_yol, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=2)
    return {"degisen": degisen, "atlanan": atlanan,
            "kenar": len(g.get("kenarlar", []))}


def taraf_yonu(taraf):
    """G9: taraf → 'kur' (iddia kanadı) | 'curut' (savunma kanadı) | None."""
    if taraf in SAVUNMA_TARAFLARI:
        return "curut"
    if taraf in IDDIA_TARAFLARI:
        return "kur"
    return None


def defterden_taraf(kok):
    """G9: `<kok>/_oa/defter/pipeline-durum.json` → (taraf|None, not).
    Defterin `ceza_dali` alanı (pipeline_kayit.py: mudafii → sanık tarafı,
    musteki[-vekili] → müşteki tarafı). Dosya yok / bozuk / alan boş →
    (None, görünür not) — fail-closed, ASLA çökertmez (hukuk dosyasında
    ceza_dali null olması NORMALDİR)."""
    yol = os.path.join(kok or ".", DEFTER_DURUM_YOLU)
    if not os.path.isfile(yol):
        return None, f"defter yok ({yol})"
    try:
        with open(yol, "r", encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:                            # noqa: BLE001 — fail-closed
        return None, f"defter okunamadı ({type(e).__name__}) — {yol}"
    if not isinstance(d, dict):
        return None, f"defter okunamadı (kök nesne sözlük değil) — {yol}"
    dal = d.get("ceza_dali")
    if not dal:
        return None, f"defterde ceza_dali boş (hukuk dosyası?) — {yol}"
    taraf = CEZA_DALI_TARAF.get(str(dal))
    if not taraf:
        return None, f"defterde ceza_dali '{dal}' tanınmadı — {yol}"
    return taraf, f"defterden: ceza_dali={dal} → taraf {taraf} ({yol})"


def kanun_yolu_zinciri(dugumler, kenarlar):
    """G12 §9: kanun_yolu kenarlarını KAT SIRASIYLA (kaynak → hedef: alt
    derece kararı → üst derece kararı) izler; köklerden (gelen kanun_yolu
    kenarı olmayan) başlayan her maksimal yol bir zincirdir. Özyinelemesiz,
    derinlik frenli; çevrimli kanun yolu (K1→K2→K1) çökertmez, yol kapanır.
    Döner: [{"yol": [id...], "sonuclar": [sonuc...]}] (JSON kanun_yolu_zinciri)."""
    ky = [k for k in kenarlar if _kanun_yolu_mu(k)]
    if not ky:
        return []
    giden = defaultdict(list)
    gelen = set()
    sira = []
    for k in ky:
        a, b = k.get("kaynak"), k.get("hedef")
        giden[a].append(k)
        gelen.add(b)
        for n in (a, b):
            if n not in sira:
                sira.append(n)
    kokler = [n for n in sira if n not in gelen] or sira[:1]   # çevrimde ilk düğüm kök
    zincirler = []
    for kok in kokler:
        yigin = [(kok, [kok], [], {kok})]
        while yigin and len(zincirler) < YAZIM_TAVANI * 5:
            dugum, yol, sonuclar, gorulen = yigin.pop()
            devam = False
            if len(yol) <= KANUN_YOLU_DERINLIK:
                for k in reversed(giden.get(dugum, [])):
                    h = k.get("hedef")
                    if h in gorulen:
                        continue
                    devam = True
                    yigin.append((h, yol + [h], sonuclar + [k.get("sonuc")], gorulen | {h}))
            if not devam and len(yol) > 1:
                zincirler.append({"yol": yol, "sonuclar": sonuclar})
    return zincirler


def _komsuluk(kenarlar, kategori=None, yonsuz=False):
    """Komşuluk listesi kur. kategori verilirse sadece o tip kenarlar."""
    adj = defaultdict(set)
    for k in kenarlar:
        if kategori and k.get("kategori") != kategori:
            continue
        a, b = k.get("kaynak"), k.get("hedef")
        adj[a].add(b)
        if yonsuz:
            adj[b].add(a)
    return adj


def _kesme_noktalari(adj, siralama, tuzel_mi):
    """Özyinelemesiz Tarjan articulation point — her kesme noktası için
    KALDIRILINCA oluşan bileşenlerin (boyut, tüzel_kişi_sayısı) listesi.
    O(V+E); eski O(V·(V+E)) 'her düğümü çıkar-say' yaklaşımı 5.000 düğümde
    pratikte çökme demekti (G6)."""
    disc, low, boyut, tuzel = {}, {}, {}, {}
    sonuc = {}
    zaman = 0
    for kok in siralama:
        if kok in disc:
            continue
        disc[kok] = low[kok] = zaman
        zaman += 1
        boyut[kok] = 1
        tuzel[kok] = int(bool(tuzel_mi(kok)))
        ziyaret = [kok]
        ayrik = defaultdict(list)
        cocuk = defaultdict(int)
        yigin = [(kok, None, iter(adj.get(kok, ())))]
        while yigin:
            u, ebeveyn, it = yigin[-1]
            ilerledi = False
            for v in it:
                if v == ebeveyn:
                    continue
                if v not in disc:
                    disc[v] = low[v] = zaman
                    zaman += 1
                    boyut[v] = 1
                    tuzel[v] = int(bool(tuzel_mi(v)))
                    ziyaret.append(v)
                    cocuk[u] += 1
                    yigin.append((v, u, iter(adj.get(v, ()))))
                    ilerledi = True
                    break
                low[u] = min(low[u], disc[v])
            if ilerledi:
                continue
            yigin.pop()
            if ebeveyn is not None:
                low[ebeveyn] = min(low[ebeveyn], low[u])
                boyut[ebeveyn] += boyut[u]
                tuzel[ebeveyn] += tuzel[u]
                if low[u] >= disc[ebeveyn]:
                    ayrik[ebeveyn].append((boyut[u], tuzel[u]))
        bilesen_boyut, bilesen_tuzel = boyut[kok], tuzel[kok]
        for u in ziyaret:
            if u == kok:
                if cocuk[kok] >= 2:
                    sonuc[u] = list(ayrik[kok])
                continue
            if not ayrik[u]:
                continue
            ayri = list(ayrik[u])
            kalan_boyut = bilesen_boyut - 1 - sum(b for b, _ in ayri)
            kalan_tuzel = bilesen_tuzel - int(bool(tuzel_mi(u))) - sum(t for _, t in ayri)
            sonuc[u] = ayri + [(kalan_boyut, kalan_tuzel)]
    return sonuc


def kopru_dugumler(dugumler, kenarlar):
    """
    Köprü düğüm — TÜM ilişki+illiyet kenarları yönsüz; articulation point
    AMA (G8, Hamle 5) yalnız kaldırılınca kalan bileşenlerden EN AZ İKİSİ
    ≥2 düğümlüyse (yaprak komşusu ve doğrusal zincir iç düğümü elenir —
    A-B-C'de B 'perde' değildir). Etiket TİP-DUYARLI:
      "perde"   → köprü gercek_kisi VE ayırdığı en az iki bileşenin her
                  birinde tuzel_kisi var (iki şirketi bağlayan tek müdür:
                  muvazaa / tüzel kişilik perdesi sinyali — TBK m.19,
                  Mevzuat MCP teyit 2026-09-06)
      "yapisal" → aksi hâlde nötr yapısal köprü (perde etiketi DEĞİL)
    `tip: karar|mahkeme` düğümleri hesaptan muaf. Döner: [(id, etiket)].
    """
    if len(dugumler) < 3:
        return []
    adj = _komsuluk(kenarlar, yonsuz=True)
    siralama = list(dugumler.keys())
    gorulen = set(siralama)
    for u in list(adj.keys()):
        if u not in gorulen:
            siralama.append(u)
            gorulen.add(u)

    def tuzel_mi(kid):
        return dugumler.get(kid, {}).get("tip") == "tuzel_kisi"

    kesme = _kesme_noktalari(adj, siralama, tuzel_mi)
    koprular = []
    for kid in dugumler:
        if kid not in kesme:
            continue
        d = dugumler[kid]
        if d.get("tip") in KOPRU_MUAF_TIPLER:
            continue
        bilesenler = kesme[kid]
        if sum(1 for b, _ in bilesenler if b >= 2) < 2:
            continue
        tuzel_kanat = sum(1 for _, t in bilesenler if t >= 1)
        etiket = "perde" if (d.get("tip") == "gercek_kisi" and tuzel_kanat >= 2) \
            else "yapisal"
        koprular.append((kid, etiket))
    return koprular


# ── G1: ÇEVRİM — eksiksiz ve MİNİMAL ────────────────────────────────────────

def _sccs(dugumler_sira, adj):
    """Özyinelemesiz Tarjan SCC. adj: düğüm → sıralı komşu listesi."""
    index, low, ustunde, yigin, sonuc = {}, {}, set(), [], []
    sayac = 0
    for kok in dugumler_sira:
        if kok in index:
            continue
        index[kok] = low[kok] = sayac
        sayac += 1
        yigin.append(kok)
        ustunde.add(kok)
        is_yigini = [(kok, iter(adj.get(kok, ())))]
        while is_yigini:
            u, it = is_yigini[-1]
            ilerledi = False
            for v in it:
                if v not in index:
                    index[v] = low[v] = sayac
                    sayac += 1
                    yigin.append(v)
                    ustunde.add(v)
                    is_yigini.append((v, iter(adj.get(v, ()))))
                    ilerledi = True
                    break
                if v in ustunde:
                    low[u] = min(low[u], index[v])
            if ilerledi:
                continue
            is_yigini.pop()
            if is_yigini:
                p = is_yigini[-1][0]
                low[p] = min(low[p], low[u])
            if low[u] == index[u]:
                bilesen = []
                while True:
                    w = yigin.pop()
                    ustunde.discard(w)
                    bilesen.append(w)
                    if w == u:
                        break
                sonuc.append(bilesen)
    return sonuc


def _unblock(dugum, blocked, B):
    yigin = {dugum}
    while yigin:
        n = yigin.pop()
        if n in blocked:
            blocked.discard(n)
            yigin.update(B[n])
            B[n].clear()


def _johnson_cevrimler(sira, adj, tavan):
    """Johnson (1975) basit çevrim sayımı — özyinelemesiz (networkx
    simple_cycles deseninin stdlib devşirmesi). Döner: (çevrimler, kırpıldı)."""
    G = {u: [v for v in adj.get(u, []) if v != u] for u in sira}
    cevrimler = [[u, u] for u in sira if u in adj.get(u, [])]  # öz-döngüler

    def altgraf(kume):
        return {u: [v for v in G[u] if v in kume] for u in kume}

    sira_no = {n: i for i, n in enumerate(sira)}
    sccs = [c for c in _sccs(sira, G) if len(c) > 1]
    while sccs:
        scc = sorted(sccs.pop(), key=sira_no.get)
        sccG = altgraf(set(scc))
        bas = scc[0]
        yol, blocked, closed, B = [bas], {bas}, set(), defaultdict(set)
        yigin = [(bas, list(reversed(sccG[bas])))]
        while yigin:
            u, komsular = yigin[-1]
            if komsular:
                v = komsular.pop()
                if v == bas:
                    cevrimler.append(yol + [bas])
                    if len(cevrimler) >= tavan:
                        return cevrimler, True
                    closed.update(yol)
                elif v not in blocked:
                    yol.append(v)
                    yigin.append((v, list(reversed(sccG[v]))))
                    closed.discard(v)
                    blocked.add(v)
                    continue
            if not komsular:
                if u in closed:
                    _unblock(u, blocked, B)
                else:
                    for w in sccG[u]:
                        B[w].add(u)
                yigin.pop()
                yol.pop()
        kalan = [n for n in scc if n != bas]
        H = altgraf(set(kalan))
        sccs.extend(c for c in _sccs(kalan, H) if len(c) > 1)
    return cevrimler, False


def _geri_kenar_cevrimler(sira, adj, tavan):
    """>200 düğüm: özyinelemesiz renkli DFS, geri-kenardan MİNİMAL çevrim
    (yolun v'den itibaren dilimi — çevrim-dışı düğüm içermez). Örneklemdir:
    her basit çevrimi saymaz; JSON/rapor bunu açıkça söyler."""
    BEYAZ, GRI, SIYAH = 0, 1, 2
    renk = defaultdict(int)
    cevrimler = []
    for kok in sira:
        if renk[kok] != BEYAZ:
            continue
        yol, konum = [kok], {kok: 0}
        renk[kok] = GRI
        yigin = [(kok, iter(adj.get(kok, ())))]
        while yigin:
            u, it = yigin[-1]
            ilerledi = False
            for v in it:
                if renk[v] == GRI:
                    cevrimler.append(yol[konum[v]:] + [v])
                    if len(cevrimler) >= tavan:
                        return cevrimler, True
                elif renk[v] == BEYAZ:
                    renk[v] = GRI
                    konum[v] = len(yol)
                    yol.append(v)
                    yigin.append((v, iter(adj.get(v, ()))))
                    ilerledi = True
                    break
            if ilerledi:
                continue
            yigin.pop()
            renk[u] = SIYAH
            yol.pop()
            konum.pop(u, None)
    return cevrimler, False


def _kanonik_cevrim(c, sira_no):
    """Çevrimi en erken görülen düğümden başlayacak şekilde döndür (mükerrer
    rotasyonları tekilleştirmek için)."""
    govde = c[:-1]
    if not govde:
        return tuple(c)
    k = min(range(len(govde)), key=lambda i: sira_no.get(govde[i], 1 << 30))
    dondu = govde[k:] + govde[:k]
    return tuple(dondu + [dondu[0]])


def cevrimleri_bul(kenarlar):
    """G1: illiyet kenarlarında yönlü çevrimler — eksiksiz ve MİNİMAL.
    ≤200 düğümde Johnson ile TAM basit çevrim sayımı; üstünde geri-kenar
    örneklemi. Raporlanan çevrim çevrim-dışı düğüm içermez (A→B→C→B →
    ["B","C","B"], eski DFS [A,B,C,B] basıyordu); aynı çevrim iki kez
    raporlanmaz. Döner: (çevrimler, kırpıldı, yöntem)."""
    sira, adj = [], {}
    for k in kenarlar:
        if not _illiyet_kenar_mi(k):
            continue
        a, b = k.get("kaynak"), k.get("hedef")
        for n in (a, b):
            if n not in adj:
                adj[n] = []
                sira.append(n)
        if b not in adj[a]:
            adj[a].append(b)
    if not sira:
        return [], False, "yok"
    if len(sira) <= JOHNSON_DUGUM_TAVANI:
        ham, kirpildi = _johnson_cevrimler(sira, adj, CEVRIM_TAVANI)
        yontem = "johnson"
    else:
        ham, kirpildi = _geri_kenar_cevrimler(sira, adj, CEVRIM_TAVANI)
        yontem = "geri-kenar-orneklem"
    sira_no = {n: i for i, n in enumerate(sira)}
    tekil, gorulen = [], set()
    for c in ham:
        kc = _kanonik_cevrim(c, sira_no)
        if kc in gorulen:
            continue
        gorulen.add(kc)
        tekil.append(list(kc))
    tekil.sort(key=lambda c: (len(c), [sira_no.get(x, 1 << 30) for x in c]))
    return tekil, kirpildi, yontem


def cevrim_var_mi(kenarlar):
    """Geriye uyumlu sarmal: yalnız çevrim listesi."""
    return cevrimleri_bul(kenarlar)[0]


def _illiyet_kokler(kenarlar):
    """İlliyet alt-grafında gelen kenarı olmayan kaynak düğümler (zincir kökleri)."""
    giden, gelen_var = [], set()
    for k in kenarlar:
        if not _illiyet_kenar_mi(k):
            continue
        giden.append(k.get("kaynak"))
        gelen_var.add(k.get("hedef"))
    kokler, gorulen = [], set()
    for d in giden:
        if d not in gelen_var and d not in gorulen:
            kokler.append(d)
            gorulen.add(d)
    return kokler


def yuk_tasiyan_kenarlar(dugumler, kenarlar):
    """
    Çıkarıldığında illiyet zincirinin uçtan uca bağlantısını koparan kenar.
    = ispatlanmazsa dava düşen kritik bağ (oa-strateji hedefi).
    İlliyet alt-grafında köprü-kenar (bridge) — özyinelemesiz Tarjan, O(V+E)
    (G6; eski 'her kenarı çıkar-say' O(E·(V+E)) idi).
    KARAKTERİZASYON KORUNDU (tests/test_grafik_denetim.py): bileşen sayımı
    kalan kenarlardan türeyen düğümler üzerinde yapıldığından zincirin UÇ
    kenarı (sarkaç düğüm) bridge sayılmaz → yalnız her iki ucu ≥2 dereceli
    bridge'ler raporlanır; 2 kenarlı zincirde hiçbir kenar çıkmaz.
    """
    illiyet_kenar = [(k.get("kaynak"), k.get("hedef"), i)
                     for i, k in enumerate(kenarlar)
                     if _illiyet_kenar_mi(k)]
    if not illiyet_kenar:
        return []
    adjl = defaultdict(list)
    derece = defaultdict(int)
    sira = []
    for a, b, i in illiyet_kenar:
        for n in (a, b):
            if n not in derece:
                sira.append(n)
                derece[n] = 0
        adjl[a].append((b, i))
        adjl[b].append((a, i))
        derece[a] += 1
        derece[b] += 1

    disc, low = {}, {}
    koprular = set()
    zaman = 0
    for kok in sira:
        if kok in disc:
            continue
        disc[kok] = low[kok] = zaman
        zaman += 1
        yigin = [(kok, -1, iter(adjl[kok]))]
        while yigin:
            u, gelen_kenar, it = yigin[-1]
            ilerledi = False
            for v, ei in it:
                if ei == gelen_kenar:
                    continue
                if v not in disc:
                    disc[v] = low[v] = zaman
                    zaman += 1
                    yigin.append((v, ei, iter(adjl[v])))
                    ilerledi = True
                    break
                low[u] = min(low[u], disc[v])
            if ilerledi:
                continue
            yigin.pop()
            if yigin:
                p = yigin[-1][0]
                low[p] = min(low[p], low[u])
                if low[u] > disc[p]:
                    koprular.add(gelen_kenar)

    out = []
    for a, b, i in illiyet_kenar:
        if i in koprular and derece[a] >= 2 and derece[b] >= 2:
            out.append((i, kenarlar[i]))
    return out


def _ad(dugumler, kid):
    d = dugumler.get(kid, {})
    return d.get("ad", kid)


def _kenar_ref(dugumler, i, k):
    return {
        "index": i,
        "kaynak": k.get("kaynak"),
        "hedef": k.get("hedef"),
        "kategori": k.get("kategori"),
        "tur": k.get("tur"),
        "dayanak_delil": k.get("dayanak_delil") or [],
        "dogrulama": k.get("dogrulama"),
    }


GUC_AGIRLIK = {"dispozitif": 1.0, "guclu": 0.9, "zayif": 0.6, "tartismali": 0.4}
# G4 (v0.5.16/A, avukat kararı #5): beyan-yok ≤ tartışmalı. Eski 0.8 değeri
# 'guc' beyan ETMEYEN kenarı 'zayif' beyan edenden (0.6) daha güçlü sayıyordu
# → dürüstlük ödülü tersine dönmüştü (beyan etmemek kazandırıyordu).
GUC_VARSAYILAN = 0.4


def zincir_analizi(dugumler, kenarlar, en_cok=10, derinlik=12):
    """v0.5.8 P3 — İLLİYET ZİNCİRİ GÜVEN ANALİZİ (semantica confidence_decay +
    weakest_link deseninin devşirmesi; anayasa m.0 devşirme protokolü, Can
    kararı 2026-08-12). Her maksimal illiyet yolunda kenar ağırlıklarının
    ÇARPIMI = zincir güveni ("zincir uzadıkça iddia gücü düşer"); en düşük
    ağırlıklı sıçrama = EN ZAYIF HALKA (karşı tarafın saldıracağı yer —
    oa-antitez beslemesi). Ağırlık `guc` alanından türetilir; hukuki niteleme
    değildir, YAPISAL kırılganlık sinyalidir. ADVISORY — hiçbir şeyi bloklamaz.
    G6: DFS özyinelemesiz + açık derinlik sınırı (derinlik)."""
    ill = [k for k in kenarlar if _illiyet_kenar_mi(k)]
    giden = {}
    for k in ill:
        giden.setdefault(k.get("kaynak"), []).append(k)
    kokler = _illiyet_kokler(kenarlar)
    zincirler = []
    tavan = en_cok * 5

    for kok in kokler:
        yigin = [(kok, [], {kok})]
        while yigin and len(zincirler) < tavan:
            dugum, yol, gorulen = yigin.pop()
            devam = False
            if len(yol) < derinlik:
                for k in reversed(giden.get(dugum, [])):
                    h = k.get("hedef")
                    if h in gorulen:
                        continue
                    devam = True
                    yigin.append((h, yol + [k], gorulen | {h}))
            if not devam and yol:
                zincirler.append(yol)

    sonuc = []
    for yol in zincirler:
        guven, zayif, zayif_w = 1.0, None, None
        for k in yol:
            w = GUC_AGIRLIK.get(k.get("guc"), GUC_VARSAYILAN)
            guven *= w
            if zayif_w is None or w < zayif_w:
                zayif, zayif_w = k, w
        sonuc.append({
            "yol": [yol[0].get("kaynak")] + [k.get("hedef") for k in yol],
            "halka": len(yol),
            "guven": round(guven, 3),
            "en_zayif": {"kaynak": zayif.get("kaynak"),
                         "hedef": zayif.get("hedef"),
                         "tur": zayif.get("tur"),
                         "guc": zayif.get("guc") or "beyan-yok",
                         "agirlik": zayif_w} if zayif else None,
        })
    sonuc.sort(key=lambda z: (z["guven"], -z["halka"]))  # en kırılgan önce
    return sonuc[:en_cok]


def _kesme_ref(dugumler, i, k):
    """G10: kesme adayı referansı = _kenar_ref + kesme_flag / dal / not.
    (tests/test_grafik_denetim.py'deki 'kesme_adaylari anahtar seti = kenar
    ref anahtar seti' karakterizasyonu BİLİNÇLİ değiştirildi — dal ve doktrin
    notu bekçiye/oa-antitez'e makine-okur gitmeli.)"""
    ref = _kenar_ref(dugumler, i, k)
    flag = k.get("kesme_flag")
    ref["kesme_flag"] = flag
    ref["dal"] = kesme_dali(flag)
    ref["not"] = kesme_notu(flag)
    return ref


def json_sonuc(dugumler, kenarlar, hatalar, yetim, dk, kopru, cevrimler, kesme, yuk,
               baglanmamis=(), guc_beyansiz=(), cikis_kodu=0, blok_sinifi=(),
               taraf=None, yon=None, kanun_yolu=()):
    """Denetim sonucunu makine-okur sözlük olarak topla (çapraz-denetçi / B
    grubu bekçisi bunu okur). JSON SÖZLEŞMESİ (alan adları BİREBİR):
    arac="grafik_denetim" sabit; cevrimler, sema_hatalari, denetim_coktu,
    cikis_kodu, blok_sinifi, baglanmamis_deliller, guc_beyansiz_kenarlar,
    kopru_dugumler[].etiket; A-2: taraf, yon ("kur"|"curut"|null),
    kanun_yolu_zinciri, kesme_adaylari[].{kesme_flag,dal,not}; eski alanlar korunur."""
    return {
        "taraf": taraf,
        "yon": yon,
        "kanun_yolu_zinciri": [dict(z) for z in kanun_yolu],
        "arac": ARAC_ADI,
        "ozet": {"dugum": len(dugumler), "kenar": len(kenarlar)},
        "denetim_coktu": False,
        "cikis_kodu": int(cikis_kodu),
        "blok_sinifi": list(blok_sinifi),
        "sema_hatalari": hatalar,
        "yetim_dugumler": [{"id": kid, "ad": _ad(dugumler, kid)} for kid in yetim],
        "baglanmamis_deliller": [{"id": kid, "ad": _ad(dugumler, kid)}
                                 for kid in baglanmamis],
        "desteksiz_kenarlar": [_kenar_ref(dugumler, i, k) for i, k in dk],
        "guc_beyansiz_kenarlar": [_kenar_ref(dugumler, i, k) for i, k in guc_beyansiz],
        "kopru_dugumler": [{"id": kid, "ad": _ad(dugumler, kid), "etiket": etiket}
                           for kid, etiket in kopru],
        "cevrimler": [list(c) for c in cevrimler],
        "kesme_adaylari": [_kesme_ref(dugumler, i, k) for i, k in kesme],
        "yuk_tasiyan_kenarlar": [_kenar_ref(dugumler, i, k) for i, k in yuk],
        "dugumler": [
            {"id": kid, "tip": d.get("tip"), "ad": d.get("ad", kid),
             "usul_rolu": d.get("usul_rolu")}
            for kid, d in dugumler.items()
        ],
        "kenarlar": [_kenar_ref(dugumler, i, k) for i, k in enumerate(kenarlar)],
    }


def _tavanli(liste):
    """stdout için tavanlı dilim + açık 'daha' sayısı (sessiz kırpma yok)."""
    if len(liste) <= YAZIM_TAVANI:
        return liste, 0
    return liste[:YAZIM_TAVANI], len(liste) - YAZIM_TAVANI


def _taraf_coz(taraf=None, kok=None):
    """G9: (taraf, yon, kaynak notu). CLI --taraf defteri EZER; --kok verilirse
    defterden okunur; ikisi de yoksa/çözülemezse taraf None + görünür not."""
    if taraf:
        return taraf, taraf_yonu(taraf), f"--taraf {taraf}"
    if kok:
        t, notu = defterden_taraf(kok)
        if t:
            return t, taraf_yonu(t), notu
        return None, None, f"taraf bilinmiyor — --taraf ver ({notu})"
    return None, None, "taraf bilinmiyor — --taraf ver (veya --kok ile defterden)"


def _rapor_govde(yol, json_yol=None, zincir=True, taraf=None, kok=None):
    """Denetimin gövdesi — çıkış kodunu DÖNER (0 temiz / 3 şema-veya-çevrim)."""
    dugumler, kenarlar, on_hatalar = yukle(yol)
    taraf, yon, taraf_notu = _taraf_coz(taraf, kok)
    curut = yon == "curut"
    cizgi = "=" * 60
    print(cizgi)
    print("OA-ILLIYET — DETERMİNİSTİK GRAF DENETİM RAPORU")
    print(cizgi)
    print(f"Düğüm: {len(dugumler)}  |  Kenar: {len(kenarlar)}")
    if yon:
        print(f"Taraf: {taraf} → tavsiye yönü: "
              f"{'ÇÜRÜT (karşı tarafın illiyetini çürüt / kesme savunmasını kur)' if curut else 'KUR (kendi illiyetini sağlamlaştır)'}"
              f"  [{taraf_notu}]")
    else:
        print(f"Taraf: {taraf_notu} — §6/§7/§8 tavsiyeleri 'kur' yönünde (varsayılan) yazıldı")
    print()

    # v0.5.9 T23/P1 — sözlük + açıklanabilir-boşluk uyarıları (ADVISORY):
    # rapor başında görünür; exit kodunu ve alttaki bölümleri DEĞİŞTİRMEZ.
    uyarilar = sozluk_uyarilari(dugumler, kenarlar) \
        + kanun_yolu_uyarilari(dugumler, kenarlar) \
        + bosluk_aciklamalari(dugumler, kenarlar)
    if uyarilar:
        for u in uyarilar:
            print(f"[ŞEMA UYARISI] {u}")
        print()

    hatalar = on_hatalar + dogrula_sema(dugumler, kenarlar)
    print("### 1. ŞEMA DENETİMİ")
    if hatalar:
        for h in hatalar:
            print(f"  ✗ {h}")
        print("\n  ⚠ Şema hataları var — diğer denetimler eksik çalışabilir. "
              "[KAPI: exit 3]")
    else:
        print("  ✓ Şema bütün.")
    normsuz = norm_uyarilari(kenarlar)          # G3: advisory, hata değil
    dilim, fazla = _tavanli(normsuz)
    for u in dilim:
        print(f"  [ŞEMA UYARISI] {u}")
    if fazla:
        print(f"  [ŞEMA UYARISI] … +{fazla} kenar daha 'norm' eksik (advisory)")
    print()

    print("### 2. YETİM DÜĞÜM (hiçbir bağı yok)")
    yetim = yetim_dugumler(dugumler, kenarlar)
    if yetim:
        for kid in yetim:
            print(f"  ⚠ {_ad(dugumler, kid)} ({kid}) — dosyada neden var? bağ kur veya çıkar")
    else:
        print("  ✓ Yetim düğüm yok.")
    print()

    print("### 2b. BAĞLANMAMIŞ DELİL (oa-vakia yetim delil semantiği — "
          "hangi iddiayı/kenarı ispatlıyor?)")
    baglanmamis = baglanmamis_deliller(dugumler, kenarlar)
    if baglanmamis:
        for kid in baglanmamis:
            print(f"  ⚠ {_ad(dugumler, kid)} ({kid}) — hiçbir kenarın dayanak_delil'inde "
                  "anılmıyor → hangi iddiayı ispatlıyor? kenara bağla veya oa-vakia'ya "
                  "yetim delil olarak taşı (ispat yükü: HMK m.190, Mevzuat MCP teyit "
                  "2026-09-06)")
    else:
        print("  ✓ Her delil bir kenara bağlı.")
    print()

    print("### 3. DESTEKSİZ KENAR (iddia + delilsiz → ispat boşluğu)")
    dk = desteksiz_kenarlar(kenarlar)
    if dk:
        for i, k in dk:
            print(f"  ⚠ {_ad(dugumler, k.get('kaynak'))} —[{k.get('tur')}]→ "
                  f"{_ad(dugumler, k.get('hedef'))}  ({desteksiz_neden(k)})"
                  f"  → oa-vakia ile delil tespiti")
    else:
        print("  ✓ Her kenar delil-teyitli veya karine.")
    guc_beyansiz = guc_beyansiz_kenarlar(kenarlar)
    for i, k in guc_beyansiz:                    # G4: ayrı sınıf
        print(f"  ◇ {_ad(dugumler, k.get('kaynak'))} —[{k.get('tur')}]→ "
              f"{_ad(dugumler, k.get('hedef'))}  GÜÇ BEYAN EDİLMEMİŞ "
              f"(beyan-yok ≤ tartışmalı) ağırlık {GUC_VARSAYILAN} → guc beyan et")
    print()

    print("### 4. KÖPRÜ DÜĞÜM (tek bağlantı noktası — tip-duyarlı etiket)")
    kopru = kopru_dugumler(dugumler, kenarlar)
    if kopru:
        dilim, fazla = _tavanli(kopru)
        for kid, etiket in dilim:
            if etiket == "perde":
                print(f"  ⚑ {_ad(dugumler, kid)} ({kid}) iki kümeyi bağlıyor → "
                      f"perde/muvazaa sinyali (gerçek kişi, her yanda tüzel kişi) "
                      f"→ muvazaa / perdeyi kaldırma incele; karşı taraf buraya vurabilir")
            else:
                print(f"  ⚑ {_ad(dugumler, kid)} ({kid}) iki kümeyi bağlıyor → "
                      f"yapısal köprü (perde etiketi değil) — kopması zinciri böler; "
                      f"bağı sağlamlaştır")
        if fazla:
            print(f"  … +{fazla} köprü daha (tam liste --json 'kopru_dugumler')")
    else:
        print("  ✓ Tek-nokta köprü yok.")
    print()

    print("### 5. ÇEVRİM (dairesel illiyet = mantık hatası)")
    cevrimler, kirpildi, yontem = cevrimleri_bul(kenarlar)
    if cevrimler:
        dilim, fazla = _tavanli(cevrimler)
        for c in dilim:
            print(f"  ✗ {' → '.join(_ad(dugumler, x) for x in c)}")
        if fazla:
            print(f"  … +{fazla} çevrim daha (tam liste --json 'cevrimler')")
        if kirpildi:
            print(f"  ⚠ çevrim sayımı TAVANA ulaştı ({CEVRIM_TAVANI}) — tam sayım yapılmadı")
        if yontem == "geri-kenar-orneklem":
            print(f"  ⚠ >{JOHNSON_DUGUM_TAVANI} düğüm: geri-kenar ÖRNEKLEMİ — "
                  "her basit çevrim sayılmadı")
        print("  [KAPI: exit 3]")
    else:
        print("  ✓ İlliyet zinciri dairesel değil.")
    print()

    print("### 6. KESME ADAYLARI (→ oa-antitez)")
    kesme = kesme_adaylari(kenarlar)
    if kesme:
        for i, k in kesme:
            if curut:
                tavsiye = ("→ karşı tarafın bu bağına karşı kesme savunmasını KUR "
                           "(oa-antitez: karşı tarafın çürütmesini öngör)")
            else:
                tavsiye = "→ oa-antitez ile çürüt veya kabul et"
            print(f"  ⚑ {_ad(dugumler, k.get('kaynak'))} —[{k.get('tur')}]→ "
                  f"{_ad(dugumler, k.get('hedef'))}  KESME: {k['kesme_flag']} {tavsiye}")
            notu = kesme_notu(k.get("kesme_flag"))
            if notu:                                 # G10: sabit doktrin hatırlatması
                print(f"      ℹ doktrin hatırlatması (hüküm değil): {notu}")
    else:
        print("  — Kesme adayı işaretlenmemiş. (medeni: mücbir sebep / mağdur / üçüncü "
              "kişi kusuru · miras: paylaştırma kastı / ivaz · ceza: izin verilen risk / "
              "kendi tehlikesine girme / hukuka uygunluk / mağdur kusuru ihtimalini elle "
              "gözden geçir.)")
    print()

    print("### 7. YÜK TAŞIYAN KENAR (→ oa-strateji; ispatlanmazsa zincir kopar)")
    if cevrimler:                                # G2: sahte-yeşil kapanışı
        print("  ⚠ çevrim var — yük taşıyan kenar çevrimde anlamsız (önce §5 çevrimi çöz)")
    yuk = yuk_tasiyan_kenarlar(dugumler, kenarlar)
    if yuk:
        dilim, fazla = _tavanli(yuk)
        yuk_tavsiye = ("→ stratejik hedef: karşı tarafın bu bağını ÇÜRÜT "
                       "(ispatlanmazsa zinciri kopar)" if curut
                       else "→ stratejik öncelik: bu bağı sağlamlaştır")
        for i, k in dilim:
            print(f"  ★ {_ad(dugumler, k.get('kaynak'))} —[{k.get('tur')}]→ "
                  f"{_ad(dugumler, k.get('hedef'))}  {yuk_tavsiye}")
        if fazla:
            print(f"  … +{fazla} kenar daha (tam liste --json 'yuk_tasiyan_kenarlar')")
    else:
        print("  — Belirgin tek yük taşıyan kenar yok (zincir paralel/dağıtık).")
    print()

    zincirler = None
    zincir_uyarisi = None
    if zincir:
        print("### 8. ZİNCİR GÜVEN ANALİZİ (v0.5.8 P3 — → oa-antitez/oa-strateji)")
        illiyet_var = any(k.get("kategori") == ILLIYET_KATEGORI for k in kenarlar)
        kokler = _illiyet_kokler(kenarlar)
        zincirler = zincir_analizi(dugumler, kenarlar)
        if illiyet_var and not kokler:           # G2: köksüz graf
            zincir_uyarisi = ("çevrim nedeniyle kök yok — zincir güven analizi "
                              "GÜVENİLMEZ (önce §5 çevrimi çöz)")
            print(f"  ✗ {zincir_uyarisi}")
        elif cevrimler:
            zincir_uyarisi = ("çevrim var — çevrime giren zincirler eksik/GÜVENİLMEZ "
                              "olabilir (önce §5 çevrimi çöz)")
            print(f"  ⚠ {zincir_uyarisi}")
        if zincirler:
            for z in zincirler:
                adlar = " → ".join(_ad(dugumler, x) for x in z["yol"])
                print(f"  ◆ [{z['guven']}] {adlar}  ({z['halka']} halka)")
                ez = z["en_zayif"]
                if ez:
                    ez_tavsiye = ("→ karşı tarafın EN ZAYIF halkası; saldırı buraya "
                                  "(ÇÜRÜT)" if curut
                                  else "→ karşı taraf buraya saldırır; önce burayı sağlamlaştır")
                    print(f"      en zayıf halka: {_ad(dugumler, ez['kaynak'])} "
                          f"—[{ez['tur']}]→ {_ad(dugumler, ez['hedef'])} "
                          f"(güç: {ez['guc']}, ağırlık {ez['agirlik']}) {ez_tavsiye}")
        elif zincir_uyarisi is None:
            print("  — İlliyet zinciri bulunamadı (illiyet kategorili kenar yok).")
        print()

    print("### 9. KANUN YOLU ZİNCİRİ (G12 — kat sırası + sonuçlar; illiyet hesabına girmez)")
    kanun_yolu = kanun_yolu_zinciri(dugumler, kenarlar)
    if kanun_yolu:
        dilim, fazla = _tavanli(kanun_yolu)
        for z in dilim:
            adlar = " → ".join(_ad(dugumler, x) for x in z["yol"])
            sonuclar = " · ".join(str(s) for s in z["sonuclar"])
            print(f"  ⚖ {adlar}  [sonuçlar: {sonuclar}]")
        if fazla:
            print(f"  … +{fazla} zincir daha (tam liste --json 'kanun_yolu_zinciri')")
    else:
        print("  — kanun_yolu kenarı yok.")
    print()

    blok_sinifi = []
    if hatalar:
        blok_sinifi.append("sema")
    if cevrimler:
        blok_sinifi.append("cevrim")
    cikis_kodu = 3 if blok_sinifi else 0

    print(cizgi)
    print("NOT: Bu rapor YAPISAL boşlukları gösterir. İlliyetin hukuki niteliği "
          "(uygun illiyet / objektif isnadiyet / kesilme) ve nihai karar avukata aittir.")
    if cikis_kodu:
        print(f"KAPI: exit {cikis_kodu} — blok sınıfı: {', '.join(blok_sinifi)} "
              "(temizlenmeden pipeline ilerlemez)")
    print(cizgi)

    if json_yol:
        sonuc = json_sonuc(dugumler, kenarlar, hatalar, yetim, dk, kopru,
                           cevrimler, kesme, yuk, baglanmamis=baglanmamis,
                           guc_beyansiz=guc_beyansiz, cikis_kodu=cikis_kodu,
                           blok_sinifi=blok_sinifi, taraf=taraf, yon=yon,
                           kanun_yolu=kanun_yolu)
        sonuc["girdi"] = yol
        sonuc["zincir_uyarisi"] = zincir_uyarisi
        if zincirler is not None:
            sonuc["zincirler"] = zincirler
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")
    return cikis_kodu


def rapor(yol, json_yol=None, zincir=True, taraf=None, kok=None):
    """v0.5.8.4 SÖZLEŞME DEĞİŞİKLİĞİ (bilinçli): `zincir` varsayılanı True —
    372 sahasında --zincir bayrağı 0 kez verildi (opsiyonel kapı = ateşlemeyen
    kapı). Kapatmak isteyen `--zincirsiz` verir; `--zincir` NO-OP.

    v0.5.16/A K2+G6 (SERT KAPI): gövde try/except ile sarılıdır — çökme
    hâlinde stdout 'DENETİM ÇÖKTÜ: <sınıf>: <mesaj>', --json'a
    {denetim_coktu:true, cikis_kodu:2}, dönüş 2. Traceback stderr'e gider
    (teşhis), stdout'taki satır bekçi içindir. Çıkış kodunu DÖNER; sys.exit
    __main__'dedir (fonksiyon çağıran testler/araçlar çökmesin)."""
    try:
        return _rapor_govde(yol, json_yol=json_yol, zincir=zincir, taraf=taraf, kok=kok)
    except Exception as e:                       # noqa: BLE001 — fail-closed kapı
        traceback.print_exc(file=sys.stderr)
        hata = f"{type(e).__name__}: {e}"
        print(f"DENETİM ÇÖKTÜ: {hata}")
        print("KAPI: exit 2 — denetim tamamlanamadı; girdi/ortam onarılmadan "
              "pipeline ilerlemez")
        if json_yol:
            try:
                with open(json_yol, "w", encoding="utf-8") as f:
                    json.dump({"arac": ARAC_ADI, "denetim_coktu": True, "hata": hata,
                               "girdi": str(yol), "cikis_kodu": 2},
                              f, ensure_ascii=False, indent=2, sort_keys=True)
                print(f"[JSON] Çökme kaydı yazıldı: {json_yol}")
            except Exception as e2:              # noqa: BLE001
                print(f"[JSON] Çökme kaydı YAZILAMADI ({type(e2).__name__}: {e2})")
        return 2


def goc_komutu(eski_yol, dal, cikti_yol):
    """CLI --goc: özet basar, çıkış kodunu DÖNER (0 tamam / 2 GÖÇ ÇÖKTÜ).
    Kaynağa dokunmaz; çökmede çıktı dosyası yazılmaz."""
    try:
        ozet = goc(eski_yol, dal, cikti_yol)
    except Exception as e:                       # noqa: BLE001 — fail-closed
        print(f"GÖÇ ÇÖKTÜ: {type(e).__name__}: {e}")
        print("KAPI: exit 2 — göç tamamlanamadı; kaynak dosyaya dokunulmadı")
        return 2
    print(f"GÖÇ (kesme_flag → '{dal}:' dal öneki): {eski_yol} → {cikti_yol}")
    print(f"  değişen kenar: {ozet['degisen']}  (toplam kenar: {ozet['kenar']}; "
          "kaynağa dokunulmadı)")
    for i, deger in ozet["atlanan"]:
        print(f"  ⚠ Kenar #{i}: kesme_flag '{deger}' '{dal}' dalında kanonik değil — "
              f"göçmedi, elle düzelt (kanonik: "
              f"{' | '.join(f'{dal}:{v}' for v in KESME_DALLARI[dal])})")
    return 0


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="OA-illiyet deterministik graf denetimi")
    p.add_argument("graf", nargs="?", help="graf.json yolu")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="denetim sonucunu makine-okur JSON olarak bu yola yaz "
                        "(pipeline'da ZORUNLU — bekçi bunu okur)")
    p.add_argument("--taraf", choices=list(TARAFLAR),
                   help="G9: temsil edilen taraf — savunma kanadı (sanik/mudafii/davali/"
                        "borclu) için §6/§7/§8 tavsiye yönü ÇÜRÜT; defteri ezer")
    p.add_argument("--kok", metavar="DAVA_KÖKÜ",
                   help="G9: <kök>/_oa/defter/pipeline-durum.json 'ceza_dali' alanından "
                        "taraf çözümü (mudafii → sanık, musteki → müşteki)")
    p.add_argument("--goc", metavar="ESKI_JSON",
                   help="G10: eski (dal öneksiz) kesme_flag'leri --dal önekiyle "
                        "yeniden etiketle, --cikti'ya yaz (kaynağa dokunmaz)")
    p.add_argument("--dal", choices=sorted(KESME_DALLARI), help="--goc için dal")
    p.add_argument("--cikti", metavar="YENI_JSON", help="--goc çıktı yolu")
    p.add_argument("--zincir", action="store_true",
                   help="(geriye uyum — NO-OP) illiyet zinciri güven analizi "
                        "v0.5.8.4'ten beri VARSAYILANDIR (372 sahası: bayrak 0 kez "
                        "verildi, analiz hiç üretilmedi); kapatmak için --zincirsiz")
    p.add_argument("--zincirsiz", action="store_true",
                   help="v0.5.8.4: zincir güven analizini (bölüm 8 + json "
                        "'zincirler' alanı) bilinçli olarak KAPATIR")
    a = p.parse_args()
    if a.goc:
        if not (a.dal and a.cikti):
            print("Kullanım: python grafik_denetim.py --goc eski.json --dal medeni|miras|ceza "
                  "--cikti yeni.json")
            sys.exit(1)
        sys.exit(goc_komutu(a.goc, a.dal, a.cikti))
    if not a.graf:
        print("Kullanım: python grafik_denetim.py graf.json --json out.json "
              "[--taraf sanik|...|alacakli | --kok <dava kökü>] [--zincirsiz]")
        print("          python grafik_denetim.py --goc eski.json --dal medeni|miras|ceza "
              "--cikti yeni.json")
        print("Çıkış: 0 temiz · 1 kullanım · 2 DENETİM ÇÖKTÜ · 3 çevrim/şema hatası")
        sys.exit(1)
    # --zincir kabul edilir ama okunmaz (no-op) — tek etkili bayrak --zincirsiz.
    sys.exit(rapor(a.graf, json_yol=a.json_yol, zincir=not a.zincirsiz,
                   taraf=a.taraf, kok=a.kok))
