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
                  "kesme_flag", "dayanak_delil", "dogrulama", "norm"}
KANONIK = {  # şema: references/illiyet-doktrini.md §6
    "tip": {"gercek_kisi", "tuzel_kisi", "kamu", "nesne", "delil", "olay", "hak"},
    "kategori": {ILISKI_KATEGORI, ILLIYET_KATEGORI},
    "illiyet_tipi": {"dogal", "uygun", "objektif_isnadiyet"},
    "guc": {"dispozitif", "guclu", "zayif", "tartismali"},
    "kesme_flag": {"mucbir_sebep", "magdur_kusuru", "ucuncu_kisi_kusuru"},
    # "delil": bu ağacın saha/fikstür gerçeğinde yerleşik "teyitli" eşanlamı —
    # uyarıya boğmamak için kabul kümesindedir (gürültü disiplini).
    "dogrulama": {"teyitli", "iddia", "karine", "delil"},
}

# G8: mahkeme/karar düğümleri yapıları gereği HER tarafı bağlar — köprü
# (perde) hesabından muaf. A-2 grubu bu tipleri şemaya ekler; kod tipe göre
# muaf tutar (KANONIK'te olmasa da).
KOPRU_MUAF_TIPLER = {"karar", "mahkeme"}
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
        if k.get("kategori") == ILLIYET_KATEGORI:
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
            if k.get("kategori") == ILLIYET_KATEGORI and not k.get("guc")]


def kesme_adaylari(kenarlar):
    """kesme_flag dolu illiyet kenarları → oa-antitez beslemesi."""
    out = []
    for i, k in enumerate(kenarlar):
        if k.get("kategori") == ILLIYET_KATEGORI and k.get("kesme_flag"):
            out.append((i, k))
    return out


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
        if k.get("kategori") != ILLIYET_KATEGORI:
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
        if k.get("kategori") != ILLIYET_KATEGORI:
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
                     if k.get("kategori") == ILLIYET_KATEGORI]
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
    ill = [k for k in kenarlar if k.get("kategori") == ILLIYET_KATEGORI]
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


def json_sonuc(dugumler, kenarlar, hatalar, yetim, dk, kopru, cevrimler, kesme, yuk,
               baglanmamis=(), guc_beyansiz=(), cikis_kodu=0, blok_sinifi=()):
    """Denetim sonucunu makine-okur sözlük olarak topla (çapraz-denetçi / B
    grubu bekçisi bunu okur). JSON SÖZLEŞMESİ (alan adları BİREBİR):
    arac="grafik_denetim" sabit; cevrimler, sema_hatalari, denetim_coktu,
    cikis_kodu, blok_sinifi, baglanmamis_deliller, guc_beyansiz_kenarlar,
    kopru_dugumler[].etiket; eski alanlar korunur."""
    return {
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
        "kesme_adaylari": [_kenar_ref(dugumler, i, k) for i, k in kesme],
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


def _rapor_govde(yol, json_yol=None, zincir=True):
    """Denetimin gövdesi — çıkış kodunu DÖNER (0 temiz / 3 şema-veya-çevrim)."""
    dugumler, kenarlar, on_hatalar = yukle(yol)
    cizgi = "=" * 60
    print(cizgi)
    print("OA-ILLIYET — DETERMİNİSTİK GRAF DENETİM RAPORU")
    print(cizgi)
    print(f"Düğüm: {len(dugumler)}  |  Kenar: {len(kenarlar)}")
    print()

    # v0.5.9 T23/P1 — sözlük + açıklanabilir-boşluk uyarıları (ADVISORY):
    # rapor başında görünür; exit kodunu ve alttaki bölümleri DEĞİŞTİRMEZ.
    uyarilar = sozluk_uyarilari(dugumler, kenarlar) \
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
            print(f"  ⚑ {_ad(dugumler, k.get('kaynak'))} —[{k.get('tur')}]→ "
                  f"{_ad(dugumler, k.get('hedef'))}  KESME: {k['kesme_flag']} "
                  f"→ oa-antitez ile çürüt veya kabul et")
    else:
        print("  — Kesme adayı işaretlenmemiş. (mücbir sebep / mağdur / üçüncü kişi "
              "kusuru ihtimalini elle gözden geçir.)")
    print()

    print("### 7. YÜK TAŞIYAN KENAR (→ oa-strateji; ispatlanmazsa zincir kopar)")
    if cevrimler:                                # G2: sahte-yeşil kapanışı
        print("  ⚠ çevrim var — yük taşıyan kenar çevrimde anlamsız (önce §5 çevrimi çöz)")
    yuk = yuk_tasiyan_kenarlar(dugumler, kenarlar)
    if yuk:
        dilim, fazla = _tavanli(yuk)
        for i, k in dilim:
            print(f"  ★ {_ad(dugumler, k.get('kaynak'))} —[{k.get('tur')}]→ "
                  f"{_ad(dugumler, k.get('hedef'))}  → stratejik öncelik: bu bağı sağlamlaştır")
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
                    print(f"      en zayıf halka: {_ad(dugumler, ez['kaynak'])} "
                          f"—[{ez['tur']}]→ {_ad(dugumler, ez['hedef'])} "
                          f"(güç: {ez['guc']}, ağırlık {ez['agirlik']}) "
                          f"→ karşı taraf buraya saldırır; önce burayı sağlamlaştır")
        elif zincir_uyarisi is None:
            print("  — İlliyet zinciri bulunamadı (illiyet kategorili kenar yok).")
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
                           blok_sinifi=blok_sinifi)
        sonuc["girdi"] = yol
        sonuc["zincir_uyarisi"] = zincir_uyarisi
        if zincirler is not None:
            sonuc["zincirler"] = zincirler
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")
    return cikis_kodu


def rapor(yol, json_yol=None, zincir=True):
    """v0.5.8.4 SÖZLEŞME DEĞİŞİKLİĞİ (bilinçli): `zincir` varsayılanı True —
    372 sahasında --zincir bayrağı 0 kez verildi (opsiyonel kapı = ateşlemeyen
    kapı). Kapatmak isteyen `--zincirsiz` verir; `--zincir` NO-OP.

    v0.5.16/A K2+G6 (SERT KAPI): gövde try/except ile sarılıdır — çökme
    hâlinde stdout 'DENETİM ÇÖKTÜ: <sınıf>: <mesaj>', --json'a
    {denetim_coktu:true, cikis_kodu:2}, dönüş 2. Traceback stderr'e gider
    (teşhis), stdout'taki satır bekçi içindir. Çıkış kodunu DÖNER; sys.exit
    __main__'dedir (fonksiyon çağıran testler/araçlar çökmesin)."""
    try:
        return _rapor_govde(yol, json_yol=json_yol, zincir=zincir)
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


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="OA-illiyet deterministik graf denetimi")
    p.add_argument("graf", nargs="?", help="graf.json yolu")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="denetim sonucunu makine-okur JSON olarak bu yola yaz "
                        "(pipeline'da ZORUNLU — bekçi bunu okur)")
    p.add_argument("--zincir", action="store_true",
                   help="(geriye uyum — NO-OP) illiyet zinciri güven analizi "
                        "v0.5.8.4'ten beri VARSAYILANDIR (372 sahası: bayrak 0 kez "
                        "verildi, analiz hiç üretilmedi); kapatmak için --zincirsiz")
    p.add_argument("--zincirsiz", action="store_true",
                   help="v0.5.8.4: zincir güven analizini (bölüm 8 + json "
                        "'zincirler' alanı) bilinçli olarak KAPATIR")
    a = p.parse_args()
    if not a.graf:
        print("Kullanım: python grafik_denetim.py graf.json --json out.json [--zincirsiz]")
        print("Çıkış: 0 temiz · 1 kullanım · 2 DENETİM ÇÖKTÜ · 3 çevrim/şema hatası")
        sys.exit(1)
    # --zincir kabul edilir ama okunmaz (no-op) — tek etkili bayrak --zincirsiz.
    sys.exit(rapor(a.graf, json_yol=a.json_yol, zincir=not a.zincirsiz))
