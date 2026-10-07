#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
vakia_matris.py — DETERMİNİSTİK vakıa/delil yönetim motoru.

Amaç: Dosyanın OLGU/DELİL yarısını disipline etmek. (1) Kronoloji kurar, (2) her
iddiayı dayandığı delile eşler, (3) ispat boşluklarını ve yetim delilleri yakalar.

Dürüst sınır (anayasa): Script hukuki değerlendirme yapmaz. Deterministik olarak
SIRALAR (kronoloji), EŞLER (iddia↔delil) ve BOŞLUK/YETİM tespiti yapar. İspatın
yeterli olup olmadığına, delilin caiz olup olmadığına muhakeme + oa-kontrol/oa-antitez
(ispat_delil cephesi) karar verir. Script yalnız modelin YAZDIĞI etiketi (iddia
türü, tanık caizliği) mekanik olarak uygular; etiket yoksa fail-closed varsayar
ve varsayımı GÖRÜNÜR yazar (v0.5.16 / A-13).

Kullanım:
  python vakia_matris.py --iskelet
  python vakia_matris.py --dogrula vakia.json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, hashlib, importlib.util, json, os, sys, time
from datetime import date

# ── v0.5.14 (B-10 / T5A) — İSPAT KÜMESİ ÜÇE BÖLÜNDÜ ────────────────────────
# Eski hesap NEGATİF listeye dayanıyordu (`ispat_durumu != "ispatsiz"`): kapalı
# kümede HİÇ olmayan bir etiket (ör. "video") dolu bir `belge` ile birleşince
# iddiayı "belgeli" sayıyor ve `ispat_bosluklari` boş çıkıyordu (fail-open).
# Artık POZİTİF BEYAZ LİSTE geçerlidir:
#   ISPAT_TAM   → tek başına iddiayı BELGELİ destekleyebilen ispat araçları
#   ISPAT_KISMI → beyan: kayda geçer, ama tek başına belgeli destek SAYILMAZ
#   ISPAT       → adı ve rolü DEĞİŞMEDİ (iskelet basımı + geçersiz-etiket denetimi
#                 tek küme üzerinden çalışmaya devam eder)
#
# ── v0.5.16 (A-13 / P0-1) — İSPAT ONTOLOJİSİ DÜZELTMESİ ───────────────────
# Saha dersi («yeşil matris, dinlenmeyen delil»): v0.5.14 kümesi `tanik` ve
# `karine`yi tek başına "belgeli destek" sayıyordu. Üç kategori hatası:
#   * TANIK şartlı delildir: senetle ispat zorunluluğu (HMK m.200) ve senede
#     karşı tanık yasağı (m.201) altında hiç dinlenemeyebilir; dinlenmesi delil
#     başlangıcına (m.202) veya m.203 istisnalarına bağlıdır. Caizliği
#     belirsiz tanık iddiayı belgeli YAPAMAZ → olay kaydındaki `caizlik`
#     etiketine göre TAM (caiz) / KISMİ (sinirli, bilinmiyor) / SAYILMAZ
#     (caiz_degil). Etiket yoksa `bilinmiyor` (fail-closed).
#   * KARİNE ispat etmez, ispat yükünü kaydırır (HMK m.190/2: karineye dayanan
#     taraf yalnız karinenin TEMELİNİ oluşturan vakıayı ispatla yükümlüdür) →
#     ayrı sınıf ISPAT_YUK_KAYDIRIR; belgeli SAYILMAZ, satır `yuk_kaydiran`
#     damgası alır.
#   * HUKUKİ iddia (nitelendirme) delille ispatlanmaz; bilirkişi hukuki konuda
#     delil değildir (HMK m.266: hâkimlik mesleğinin gerektirdiği hukuki
#     bilgiyle çözülecek konularda bilirkişiye başvurulamaz) → `iddialar[].tur`
#     = hukuki olan iddia boşluk ÜRETMEZ; `bilirkisi` desteği orada sayılmaz.
#   (Madde metinleri Mevzuat MCP'den 2026-09-06'da okunmuştur.)
# ISPAT'ın ÜYE KÜMESİ değişmedi (aynı 8 etiket) — yalnız bölümleme değişti.
ISPAT_TAM = {"belgeli", "ikrar", "yemin", "bilirkisi"}   # bilirkisi: yalnız vakıa iddiasında
ISPAT_KISMI = {"beyan", "tanik"}                          # tanik: caiz değilse/belirsizse kısmi
ISPAT_YUK_KAYDIRIR = {"karine"}
ISPAT = ISPAT_TAM | ISPAT_KISMI | ISPAT_YUK_KAYDIRIR | {"ispatsiz"}

IDDIA_TUR = {"vakia", "hukuki"}                     # iddialar[].tur — yoksa vakia
TANIK_CAIZLIK = {"caiz", "sinirli", "caiz_degil", "bilinmiyor"}  # olaylar[].caizlik — yoksa bilinmiyor
_TANIK_CAIZ, _TANIK_BELIRSIZ = {"caiz"}, {"sinirli", "bilinmiyor"}

# Matris satırı açıklama metinleri (tek yer — SKILL.md ile aynı ifade)
NOT_HUKUKI = ("tur: hukuki — bilirkişi delil değildir (HMK m.266 sınırı: hâkimlik "
              "mesleğinin gerektirdiği hukuki bilgiyle çözülecek konularda bilirkişiye "
              "başvurulamaz — Mevzuat MCP teyit 2026-09-06)")
NOT_TANIK_BELIRSIZ = ("tanık caizliği belirsiz — senetle ispat kuralı/delil başlangıcı "
                      "denetlenmeli (HMK m.200-203 — Mevzuat MCP teyit 2026-09-06)")
NOT_KARINE = ("karine ispat etmez, ispat yükünü kaydırır (HMK m.190/2 — Mevzuat MCP "
              "teyit 2026-09-06)")


# ── v0.5.18 (B-1(a)/S1 · B-4/S3) — KAYNAK BEYANI ve ATOMİK JSON YAZIMI ───────
# NEDEN VAR (S1 — zincirleme tepki): denetim JSON'u hangi girdiden üretildiğini
# BEYAN ETMİYORDU. Ingest yeniden koşup `00-kunye.json` değişince eski girdiye
# göre üretilmiş matris yerinde duruyor, DURUM.md ve teslim yeşil kalıyordu
# (Fable tutarlılık raporu 2026-10-07, B-1). Tüketici `oa-kontrol/
# tazelik_denetim` bu beyanı okuyup sha8 farkından "bayat halka"yı GÖRÜNÜR
# kılar. Sözleşme: `kaynaklar: [{rol, yol, sha8}]` (rol, yol) sıralı; `yol`
# dosyayı içeren `_oa` dizinine göre POSIX göreli (dava klasörü taşınsa da,
# cwd değişse de aynı bayt — determinizm kilidi); `sha8` = sha256[:8]
# (tazelik_denetim.sha8 ile aynı formül). Roller: `girdi` (denetlenen model
# girdisi) ve `kunye` (`<_oa>/metin/00-kunye.json` VARSA). `_oa` ağacı
# dışındaki girdi (avukatın masaüstündeki taslak) → boş liste + not:
# "denetim dışı", "temiz" DEĞİL. Not alanı her zaman yazılır (not yoksa null)
# ki üst-düzey anahtar kümesi girdinin yerine göre değişmesin. Mevcut `girdi`
# alanı GERİYE UYUM için AYNEN kalır (B-11 kararı: köke göreli kimlik
# `kaynaklar[].yol` ile sağlanır, `girdi` komut satırının yankısıdır).
# NEDEN VAR (S3 — atomik yazım): `open(yol, "w")` + json.dump yarıda kesilirse
# hedefte YARIM JSON kalıyor; K2 graf kapısı okunamayan dosyayı sessizce
# atlıyordu (B-4 fail-open — deneyle doğrulandı). Aynı dizinde geçici dosya +
# `os.replace` (aynı birimde atomik yeniden adlandırma): hedef ya eski tam
# içerik ya yeni tam içerik; kesintide eski dosya korunur, artık silinir.
# Dört motor (vakia_matris · grafik_denetim · kiyas_denetim · antitez_matris)
# aynı iki yardımcıyı taşır — paket yok, ortak modül yok (tests/README.md §1);
# ad ve imza bilinçli olarak aynıdır (tests/test_v0518_uretici_atomik.py).
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


# ── v0.5.8.4 ÖZNE TETİĞİ (372 karnesi: ozne_eslestirici'yi HİÇBİR akış
# çağırmıyordu — kullanıcı kararı: tetik oa-vakia'ya bağlanır). vakia_matris
# matris kurarken taraf/özne yazım varyantlarını toplar ve kardeş motorun
# kural setiyle damgalar. v0.5.18 (kullanıcı kararı 2026-10-05 — "yanlış
# birleştirme fazladan sorudan daha kötü"): BAGLA yalnız yapısal eşdeğerlikte
# (katlanmış parçalar / birleşik biçim / OCR jokeri); ayrıca `taraflar`
# kaydındaki opsiyonel `tur` iki tarafta farklıysa BAGLA asla.
# ADVISORY — karar vermez, `saglikli` hesabına GİRMEZ; varyant yoksa sessiz.

def _ozne_eslestirici_modulu():
    """ozne_eslestirici.py'yi (aynı dizin) İN-PROCESS import eder — algoritma
    TEKRARLANMAZ (tek-yazar kuralı: eşleştirme kuralları yalnız
    ozne_eslestirici.py'de yaşar; bu dosya onları yalnız kullanır). Import
    çökerse None döner; çağıran taraf bunu GÖRÜNÜR uyarıya çevirir (sessiz
    atlama yasağı)."""
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "ozne_eslestirici.py")
    if not os.path.isfile(yol):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_vakia_ozne_eslestirici", yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _ozne_adlarini_topla(m):
    """Matris girdisindeki taraf/özne YAZIMLARINI deterministik sırayla toplar:
    üst-düzey `taraflar` listesi (dize veya {"ad": ..., "tur": ...}) + her
    olayın opsiyonel `ozne` alanı. Birebir aynı dize TEK sayılır (aynı yazım
    varyant değildir). v0.5.18: `taraflar` kaydındaki opsiyonel `tur`
    (gercek_kisi | tuzel_kisi | kamu) eşleştiriciye taşınır — eskiden yalnız ad
    toplanıyordu ve kişi ile şirketi ayıracak bilgi kayboluyordu. Döner:
    [{"ad": ...} | {"ad": ..., "tur": ...}]."""
    adlar, gorulen = [], {}

    def _ekle(ad, tur=None):
        ad = str(ad or "").strip()
        tur = str(tur).strip() if tur is not None and str(tur).strip() else None
        if not ad:
            return
        if ad in gorulen:
            # Aynı yazım iki farklı türle gelmişse ikinci tür sessizce düşmesin:
            # ilk kayıt korunur, çelişki ozne_eslestirme_kur'da GÖRÜNÜR uyarı olur.
            onceki = adlar[gorulen[ad]]
            if tur and onceki.get("tur") and onceki["tur"] != tur:
                onceki.setdefault("_tur_celiskisi", []).append(tur)
            return
        gorulen[ad] = len(adlar)
        kayit = {"ad": ad}
        if tur:
            kayit["tur"] = tur
        adlar.append(kayit)

    for t in m.get("taraflar", []) or []:
        if isinstance(t, dict):
            _ekle(t.get("ad"), t.get("tur"))
        else:
            _ekle(t)
    for o in m.get("olaylar", []) or []:
        _ekle(o.get("ozne") if isinstance(o, dict) else None)
    return adlar


def ozne_eslestirme_kur(m):
    """Birden çok taraf/özne yazımı varsa ozne_eslestirici kural setiyle
    `ozne_eslestirme` bölümünü kurar:
      [{"varyantlar": [...], "skor": f, "karar": "BAGLA"|"AVUKATA-SOR",
        "kural": "...", "gerekce": "..."}]
    Varyant yoksa boş liste (sessiz). Döner: (bulgular, uyari) — `uyari`
    kardeş modül import edilemez/çökerse, çok uzun ad yalnız yazım
    eşdeğerliğiyle karşılaştırılabildiyse, iş bütçesi aşıldıysa, `tur`
    tanınmadıysa ya da aynı ad iki ayrı türle yazıldıysa dolar (görünür
    fail-open — tanınmayan tür sessizce yok sayılmaz)."""
    adlar = _ozne_adlarini_topla(m)
    if len(adlar) < 2:
        return [], None
    oe = _ozne_eslestirici_modulu()
    if oe is None:
        return [], ("ozne_eslestirici.py import edilemedi — özne yazım-varyantı "
                    "taraması YAPILAMADI (advisory; varyant birleştirme kararı "
                    "avukatta kalır)")
    notlar = []
    celiskiler = [(k["ad"], k["tur"], k.pop("_tur_celiskisi")) for k in adlar if "_tur_celiskisi" in k]
    try:
        eslesmeler = oe.eslestir(adlar, uyarilar=notlar)
        uzunlar = oe.asiri_uzun_adlar(adlar)
        taninmayan = [(k["ad"], k["tur"]) for k in adlar
                      if k.get("tur") and oe.tur_normalize(k["tur"])[0] is None]
    except Exception as e:  # advisory motor çökerse matris DÜŞMEZ, ama sessiz de kalmaz
        return [], (f"özne yazım-varyantı taraması YAPILAMADI ({type(e).__name__}: "
                    f"{str(e)[:160]}) — varyant birleştirme kararı avukatta kalır")
    bulgular = [{"varyantlar": [e["a"]["ad"], e["b"]["ad"]],
                 "skor": e["skor"], "karar": e["karar"],
                 "kural": e.get("kural", ""), "gerekce": e.get("gerekce", "")}
                for e in eslesmeler]
    if uzunlar:
        notlar.append("çok uzun özne adı yalnız yazım eşdeğerliğiyle karşılaştırıldı (varyant "
                      "taraması sınırlı): " + "; ".join(f"«{a}»" for a in uzunlar))
    for ad, tur in taninmayan:
        notlar.append(f"«{ad}» için tur «{tur}» tanınmadı ve YOK SAYILDI — gercek_kisi | tuzel_kisi | "
                      "kamu yazın (usul rolü — davacı/davalı — tür değildir)")
    for ad, tur, digerleri in celiskiler:
        notlar.append(f"«{ad}» iki ayrı türle yazılmış ({tur} / {', '.join(digerleri)}) — ilk tür "
                      "kullanıldı; avukatça teyit edin")
    return bulgular, (" · ".join(notlar) if notlar else None)

def iskelet():
    """v0.5.14 (B-26): STDOUT yalnız GEÇERLİ JSON taşır; banner ve açıklamalar
    STDERR'e gider. SKILL.md'nin kendi öğrettiği kullanım
    `--iskelet > _oa/cikti/04-vakia.json` idi ve bugüne kadar sessizce
    AYRIŞTIRILAMAZ bir dosya üretiyordu (hata bir sonraki adımda çıkıyordu)."""
    def _not(*a):
        print(*a, file=sys.stderr)

    _not("="*68); _not("  VAKIA/DELİL MATRİSİ — kronoloji + iddia↔delil eşleme"); _not("="*68)
    _not("ispat_durumu değerleri:", ", ".join(sorted(ISPAT)))
    _not("  · ISPAT_TAM          :", ", ".join(sorted(ISPAT_TAM)),
         "→ dolu `belge` ile VAKIA iddiasını BELGELİ destekler",
         "(bilirkisi yalnız vakıa iddiasında — HMK m.266 sınırı)")
    _not("  · ISPAT_KISMI        :", ", ".join(sorted(ISPAT_KISMI)),
         "→ kayda geçer, tek başına belgeli destek SAYILMAZ",
         "(tanik: olayda caizlik=caiz ise TAM sayılır — HMK m.200-203)")
    _not("  · ISPAT_YUK_KAYDIRIR :", ", ".join(sorted(ISPAT_YUK_KAYDIRIR)),
         "→ ispat etmez, ispat yükünü kaydırır (HMK m.190/2); belgeli SAYILMAZ")
    _not("iddialar[].tur değerleri:", ", ".join(sorted(IDDIA_TUR)),
         "— yoksa 'vakia'; 'hukuki' iddiada delil aranmaz (boşluk üretmez)")
    _not("olaylar[].caizlik değerleri (yalnız tanik):", ", ".join(sorted(TANIK_CAIZLIK)),
         "— yoksa 'bilinmiyor' (fail-closed → yalnız kısmi destek)")
    sablon = {
        "taraflar": [{"ad": "Taraf adı",
                      "tur": "gercek_kisi|tuzel_kisi|kamu (opsiyonel; taraflar düz ad listesi de "
                             "olabilir — yazım varyantları taranır; tür farklıysa BAGLA asla, v0.5.18)"}],
        "iddialar": [{"id":"I1","metin":"İspatlanacak maddi iddia — bir cümle",
                      "tur":"|".join(sorted(IDDIA_TUR))
                             + " (vakia: delille ispatlanır; hukuki: nitelendirme, delil aranmaz)"}],
        "olaylar": [{
            "id":"O1 (opsiyonel — olay kimliği, benzersiz; oa-kiyas vakıası `vakia_id` ile buna bağlanır — v0.5.18/S5)",
            "tarih":"YYYY-MM-DD","olgu":"Ne oldu (kısa)",
            "ozne":"Olayın öznesi/faili (opsiyonel — özne varyant taramasına girer)",
            "belge":"Dayanak belge/delil (sözleşme, ihtarname, tutanak, tanık...) veya boş",
            "destekler":["I1"],
            "ispat_durumu":"|".join(sorted(ISPAT)),
            "caizlik":"|".join(sorted(TANIK_CAIZLIK))
                      + " (yalnız ispat_durumu=tanik için; yoksa bilinmiyor)"
        }]
    }
    _not("\n--- Doldurulacak şablon (JSON — STDOUT) ---")
    print(json.dumps(sablon, ensure_ascii=False, indent=2))
    _not("\nDoldurduktan sonra: python vakia_matris.py --dogrula vakia.json")

def _parse_tarih(s):
    try: return date.fromisoformat(s)
    except Exception: return None

def dogrula(path, json_yol=None):
    try:
        with open(path, encoding="utf-8") as f: m = json.load(f)
    except Exception as e:
        print(f"❌ JSON okunamadı: {e}"); sys.exit(1)
    # v0.5.14 (B-23): kök tipi denetimi. Girdiyi model üretir; kök sözlük
    # değilse (null / [] / "dize") eski kod ham AttributeError traceback'i
    # veriyordu ve asıl mesaj kayboluyordu ("araç bozuldu" izlenimi).
    if not isinstance(m, dict):
        print(f"❌ JSON kökü sözlük değil ({type(m).__name__}) — vakia_matris "
              '{"iddialar": [...], "olaylar": [...]} biçiminde bir nesne bekler '
              "(şablon: --iskelet).")
        sys.exit(1)
    _ham_iddia = m.get("iddialar") or []
    _ham_olay = m.get("olaylar") or []
    iddialar = {i.get("id"): i.get("metin","") for i in _ham_iddia if isinstance(i, dict)}
    olaylar = [o for o in _ham_olay if isinstance(o, dict)]
    # sessiz atlama yasağı: sözlük olmayan kayıtlar düşürüldüyse GÖRÜNÜR olsun
    bicimsiz = [("iddialar", sum(1 for i in _ham_iddia if not isinstance(i, dict))),
                ("olaylar", sum(1 for o in _ham_olay if not isinstance(o, dict)))]
    bicimsiz = [f"{ad}: {n} kayıt sözlük değil — denetime alınmadı"
                for ad, n in bicimsiz if n > 0]

    # v0.5.16 (A-13): iddia TÜRÜ ve tanık CAİZLİĞİ etiketleri. Alan yoksa
    # fail-closed varsayılan (vakia / bilinmiyor) + GÖRÜNÜR [BİLGİ] satırı;
    # kapalı küme dışı değer → yine fail-closed varsayılan, ama geçersiz
    # enum GEÇERSİZ ispat_durumu ile aynı ciddiyettedir → tur için BİÇİMSİZ
    # KAYIT bloğu (saglikli'yi bozar), caizlik için görünür uyarı.
    iddia_tur, bilgi = {}, []
    _tursuz = []
    for i in _ham_iddia:
        if not isinstance(i, dict):
            continue
        iid = i.get("id")
        if "tur" not in i or i.get("tur") in (None, ""):
            iddia_tur[iid] = "vakia"; _tursuz.append(str(iid))
        elif i.get("tur") in IDDIA_TUR:
            iddia_tur[iid] = i.get("tur")
        else:
            iddia_tur[iid] = "vakia"
            bicimsiz.append(f"iddialar: '{iid}' tur='{i.get('tur')}' kapalı kümede "
                            f"({', '.join(sorted(IDDIA_TUR))}) değil — 'vakia' sayıldı (fail-closed)")
    if _tursuz:
        bilgi.append(f"tur alanı olmayan iddia: {', '.join(_tursuz)} → 'vakia' varsayıldı "
                     "(hukuki nitelendirme iddiası ise tur: hukuki yazın — v0.5.16/A-13)")

    def _caizlik(o):
        """Yalnız `tanik` olayı için anlamlı; yoksa/geçersizse 'bilinmiyor'."""
        c = o.get("caizlik")
        return c if c in TANIK_CAIZLIK else "bilinmiyor"

    _caizsiz, _caiz_gecersiz = [], []
    for o in olaylar:
        if (o.get("ispat_durumu") or "") != "tanik":
            continue
        c = o.get("caizlik")
        if c in (None, ""):
            _caizsiz.append(o.get("olgu", ""))
        elif c not in TANIK_CAIZLIK:
            _caiz_gecersiz.append(f"{o.get('olgu','')}: '{c}'")
    if _caizsiz:
        bilgi.append("caizlik alanı olmayan tanık olayı: " + "; ".join(_caizsiz)
                     + " → 'bilinmiyor' varsayıldı (fail-closed: yalnız kısmi destek; "
                     "HMK m.200-203 denetimi sonrası caiz/sinirli/caiz_degil yazın)")
    for g in _caiz_gecersiz:
        bilgi.append(f"caizlik etiketi kapalı kümede değil — {g} → 'bilinmiyor' sayıldı "
                     f"(geçerli: {', '.join(sorted(TANIK_CAIZLIK))})")

    # v0.5.18 (S5 / B-3): opsiyonel olay kimliği `olaylar[].id` ŞEMA HATASI
    # DEĞİLDİR — capraz_denetim kıyas vakıasını `vakia_id` ile buna bağlar
    # (ad benzerliği yerine kimlik eşitliği). Mükerrer kimlik eşlemeyi
    # belirsiz kılar ama olguyu geçersiz kılmaz → yalnız [BİLGİ], saglikli'ye
    # girmez; karar avukatın. Sayaç girdi sırasını korur (determinizm).
    _kimlik_sayac = {}
    for o in olaylar:
        kid = o.get("id")
        if kid not in (None, ""):
            _kimlik_sayac[str(kid)] = _kimlik_sayac.get(str(kid), 0) + 1
    _mukerrer = [f"{k} ({n} kez)" for k, n in _kimlik_sayac.items() if n > 1]
    if _mukerrer:
        bilgi.append("olaylar: 'id' mükerrer: " + ", ".join(_mukerrer)
                     + " — çapraz denetim kimlik eşlemesi belirsiz kalır; kimlikleri "
                     "tekilleştirin (v0.5.18/S5)")

    tarihli, tarihsiz = [], []
    for o in olaylar:
        d = _parse_tarih(o.get("tarih","") or "")
        (tarihli if d else tarihsiz).append((d,o))
    tarihli.sort(key=lambda x: x[0])

    print("="*68); print("  VAKIA/DELİL DENETİMİ — KARAR-MALZEMESİ"); print("="*68)

    # 1) Kronoloji
    kronoloji = []
    print("\n--- KRONOLOJİ ---")
    for d,o in tarihli:
        bel = o.get("belge","") or "—"
        print(f"  {d.isoformat()} | {o.get('olgu','')}  [delil: {bel}; {o.get('ispat_durumu','?')}]")
        kronoloji.append({"tarih": d.isoformat(), "olgu": o.get("olgu",""),
                          "belge": o.get("belge","") or "", "ispat_durumu": o.get("ispat_durumu","")})
    if tarihsiz:
        print("  (tarihsiz — sıralanamadı:)")
        for _,o in tarihsiz: print(f"   ? {o.get('olgu','')}")

    # 2) İddia↔delil matrisi + ispat boşlukları
    if bilgi:
        print("\n--- BİLGİ (varsayılanlar — görünür, saglikli'ye girmez) ---")
        for b in bilgi:
            print(f"  [BİLGİ] {b}")
    print("\n--- İDDİA ↔ DELİL MATRİSİ ---")
    bos_iddia = []
    matris = []
    n_hukuki = 0
    # v0.5.14 (B-10 / T5A): POZİTİF BEYAZ LİSTE. `belgeli` yalnız ISPAT_TAM
    # etiketli VE dolu `belge` taşıyan destekten doğar; `beyan` (ISPAT_KISMI)
    # ayrı sayılır ve tek başına iddiayı belgeli YAPMAZ.
    # v0.5.16 (A-13): üç ek kural — (a) `hukuki` iddiada delil aranmaz, boşluk
    # üretmez, `bilirkisi` orada sayılmaz; (b) `tanik` yalnız caizlik=caiz ise
    # TAM, sinirli/bilinmiyor ise KISMİ, caiz_degil ise SAYILMAZ; (c) `karine`
    # belgeli sayılmaz, satırı `yuk_kaydiran` damgalar.
    _d = lambda o: (o.get("ispat_durumu") or "")
    _bel = lambda o: bool(o.get("belge") or "")
    for iid, metin in iddialar.items():
        tur = iddia_tur.get(iid, "vakia")
        destek = [o for o in olaylar if iid in (o.get("destekler") or [])]
        taniklar = [o for o in destek if _d(o) == "tanik"]
        tanik_caiz = [o for o in taniklar if _caizlik(o) in _TANIK_CAIZ and _bel(o)]
        tanik_belirsiz = [o for o in taniklar if _caizlik(o) in _TANIK_BELIRSIZ]
        tanik_caiz_degil = [o for o in taniklar if _caizlik(o) == "caiz_degil"]
        tam_kume = ISPAT_TAM - ({"bilirkisi"} if tur == "hukuki" else set())
        belgeli = [o for o in destek if _d(o) in tam_kume and _bel(o)] + tanik_caiz
        kismi = ([o for o in destek if _d(o) == "beyan" and _bel(o)] + tanik_belirsiz)
        karineler = [o for o in destek if _d(o) in ISPAT_YUK_KAYDIRIR]
        bilirkisi_hukuki = [o for o in destek if _d(o) == "bilirkisi"] if tur == "hukuki" else []
        print(f"  [{iid}] {metin}" + ("  (tur: hukuki)" if tur == "hukuki" else ""))
        if destek:
            for o in destek:
                print(f"       ← {o.get('tarih','?')} {o.get('olgu','')} ({o.get('ispat_durumu','?')})")
        if tur == "hukuki":
            n_hukuki += 1
            print(f"       ○ {NOT_HUKUKI}")
            if bilirkisi_hukuki:
                print("       ! bilirkişi desteği hukuki iddiada SAYILMAZ: "
                      + "; ".join(o.get("olgu", "") for o in bilirkisi_hukuki))
        elif not belgeli:
            bos_iddia.append(iid)
            print("       ⚠ İSPAT BOŞLUĞU: bu iddiayı destekleyen belgeli/somut delil yok")
            if kismi:
                # etiket dinamik: yalnız beyan → "(beyan)" (v0.5.14 satırı aynen
                # korunur), yalnız tanık → "(tanık)", ikisi → "(beyan/tanık)"
                _k = sorted({"beyan" if _d(o) == "beyan" else "tanık" for o in kismi})
                print(f"       ↳ yalnız KISMİ destek ({'/'.join(_k)}) — tek başına belgeli sayılmaz")
        if tanik_belirsiz:
            print(f"       ↳ {NOT_TANIK_BELIRSIZ}")
        if tanik_caiz_degil:
            print("       ↳ tanık caiz değil — destek SAYILMADI: "
                  + "; ".join(o.get("olgu", "") for o in tanik_caiz_degil))
        if karineler:
            print(f"       ↳ yuk_kaydiran: true — {NOT_KARINE}")
        matris.append({
            "iddia_id": iid, "metin": metin, "tur": tur,
            "destekler": [o.get("olgu","") for o in destek],
            "belgeli": bool(belgeli),
            "kismi_destek": bool(kismi),
            "yuk_kaydiran": bool(karineler),
            "tanik_caizlik_belirsiz": bool(tanik_belirsiz),
        })
    # yük kaydıran karine OLAYI sayısı (en az bir iddiayı destekleyen)
    n_karine = sum(1 for o in olaylar
                   if _d(o) in ISPAT_YUK_KAYDIRIR
                   and any(r in iddialar for r in (o.get("destekler") or [])))

    # 3) Yetim / eşlenmemiş deliller + geçersiz referans
    yetim, gecersiz_ref, gecersiz_durum = [], [], []
    for o in olaylar:
        dest = o.get("destekler") or []
        if not dest:
            yetim.append(o.get("olgu",""))
        for r in dest:
            if r not in iddialar: gecersiz_ref.append(f"{o.get('olgu','')} → bilinmeyen iddia '{r}'")
        if (o.get("ispat_durumu") or "") not in ISPAT:
            gecersiz_durum.append(f"{o.get('olgu','')}: '{o.get('ispat_durumu')}'")

    def blok(b, items, mark="!"):
        if items:
            print(f"\n--- {b} ---")
            for it in items: print(f"  {mark} {it}")

    blok("İSPAT BOŞLUKLARI (delilsiz iddialar — ispat yükü riski)", bos_iddia, "✗")
    blok("YETİM DELİLLER (hiçbir iddiaya bağlanmamış olgu)", yetim, "!")
    blok("GEÇERSİZ İDDİA REFERANSI", gecersiz_ref, "!")
    blok("GEÇERSİZ ispat_durumu", gecersiz_durum, "!")
    blok("BİÇİMSİZ KAYIT (sözlük değil — v0.5.14/B-23)", bicimsiz, "!")

    # 4) Özne yazım-varyantı taraması (v0.5.8.4 ÖZNE TETİĞİ — advisory,
    # saglikli hesabına GİRMEZ; "öznenin tüm beyanları" sorgusu varyant
    # yüzünden kayıt kaçırmasın — kayıpsızlık invaryantı). Varyant yoksa
    # SESSİZ (blok basılmaz); kardeş modül çökerse görünür uyarı.
    ozne_bulgular, ozne_uyari = ozne_eslestirme_kur(m)
    if ozne_uyari:
        print(f"\n  ! {ozne_uyari}")
    if ozne_bulgular:
        print("\n--- ÖZNE EŞLEŞTİRME (yazım varyantları — advisory, karar avukatta) ---")
        for b in ozne_bulgular:
            isaret = "?" if b["karar"] == "AVUKATA-SOR" else "~"
            print(f"  {isaret} {b['karar']} [{b['skor']}] "
                  + " ↔ ".join(f"«{v}»" for v in b["varyantlar"])
                  + (f" — {b['gerekce']}" if b.get("gerekce") else ""))

    # Özet
    # v0.5.16 (A-13): bölümleme iddia = belgeli_destekli + ispat_boslugu +
    # hukuki_iddia — hukuki iddia "belgeli destekli" SAYILMAZ (delil aranmadı).
    n_id = len(iddialar); n_destekli = n_id - len(bos_iddia) - n_hukuki
    print("\n--- ÖZET ---")
    print(f"  İddia: {n_id} | belgeli destekli: {n_destekli} | ispat boşluğu: {len(bos_iddia)}"
          f" | hukuki iddia: {n_hukuki} | yük kaydıran karine: {n_karine}")
    print(f"  Olay: {len(olaylar)} | tarihsiz: {len(tarihsiz)} | yetim: {len(yetim)}")
    # v0.5.14 (B-12): BOŞ GİRDİ AYRI SONUÇ SINIFI. Eskiden `{}` girdisi hiçbir
    # tespit listesini doldurmadığı için ">>> ... TAMAM <<<" basıyordu:
    # "0 iddia = kusursuz dosya". Denetlenecek içerik yokluğu, denetimin
    # GEÇTİĞİ anlamına gelmez. (Exit kodu sözleşmesi DEĞİŞMEZ — dogrula()
    # içinde sys.exit yoktur; sağlık sinyali çıktıdan/JSON'dan okunur.)
    denetlenemez = not iddialar and not olaylar
    saglikli = (not denetlenemez) and not (
        bos_iddia or tarihsiz or gecersiz_ref or gecersiz_durum or bicimsiz)
    if denetlenemez:
        print(">>> Dosya olgu/delil bütünlüğü DENETLENEMEDİ — girdide ne iddia "
              "ne olay var; boş matris 'TAMAM' sayılmaz <<<")
    else:
        print(">>> Dosya olgu/delil bütünlüğü " + ("TAMAM <<<" if saglikli else "EKSİK — yukarıdakiler kapatılmalı <<<"))
    print("="*68)

    if json_yol:
        kaynaklar, kaynaklar_notu = kaynak_beyani(path)      # v0.5.18 S1
        sonuc = {
            "arac": "vakia_matris", "girdi": path,
            "kaynaklar": kaynaklar, "kaynaklar_notu": kaynaklar_notu,
            "kronoloji": kronoloji,
            "tarihsiz": [o.get("olgu","") for _,o in tarihsiz],
            "iddia_delil_matrisi": matris,
            "ispat_bosluklari": bos_iddia,
            "yetim_deliller": yetim,
            "gecersiz_referans": gecersiz_ref,
            "gecersiz_ispat_durumu": gecersiz_durum,
            "ozne_eslestirme": ozne_bulgular,
            "ozet": {"iddia": n_id, "belgeli_destekli": n_destekli,
                     "ispat_boslugu": len(bos_iddia), "olay": len(olaylar),
                     "tarihsiz": len(tarihsiz), "yetim": len(yetim),
                     "hukuki_iddia": n_hukuki, "yuk_kaydiran_karine": n_karine},
            "saglikli": saglikli,
        }
        _atomik_json_yaz(json_yol, sonuc)                      # v0.5.18 S3
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")

def main():
    p = argparse.ArgumentParser(description="Deterministik vakıa/delil motoru")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--iskelet", action="store_true")
    g.add_argument("--dogrula", metavar="JSON")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="--dogrula ile: denetim sonucunu makine-okur JSON olarak bu yola yaz (opsiyonel)")
    a = p.parse_args()
    iskelet() if a.iskelet else dogrula(a.dogrula, json_yol=a.json_yol)

if __name__=="__main__":
    try: main()
    except BrokenPipeError: sys.stderr.close()
