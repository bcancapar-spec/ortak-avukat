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
Çıktı:  insan-okunur deterministik denetim raporu (stdout)

Kullanım:
    python grafik_denetim.py graf.json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import json
import sys
from collections import defaultdict

ILISKI_KATEGORI = "iliski"
ILLIYET_KATEGORI = "illiyet"


def yukle(yol):
    with open(yol, "r", encoding="utf-8") as f:
        g = json.load(f)
    dugumler = {d["id"]: d for d in g.get("dugumler", [])}
    kenarlar = g.get("kenarlar", [])
    return dugumler, kenarlar


def dogrula_sema(dugumler, kenarlar):
    """Şema bütünlüğü — eksik zorunlu alan = hata (UYAP/Anthropic output_schema mantığı)."""
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
        if k.get("kategori") == ILLIYET_KATEGORI and "illiyet_tipi" not in k:
            hatalar.append(f"Kenar #{i} (illiyet): 'illiyet_tipi' eksik")
    return hatalar


def yetim_dugumler(dugumler, kenarlar):
    """Hiçbir kenara bağlı olmayan düğüm — dosyada neden var?"""
    bagli = set()
    for k in kenarlar:
        bagli.add(k.get("kaynak"))
        bagli.add(k.get("hedef"))
    return [kid for kid in dugumler if kid not in bagli]


def desteksiz_kenarlar(kenarlar):
    """dogrulama=iddia ve dayanak_delil boş → ispat boşluğu (oa-vakia'ya)."""
    out = []
    for i, k in enumerate(kenarlar):
        if k.get("dogrulama") == "iddia" and not k.get("dayanak_delil"):
            out.append((i, k))
    return out


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


def kopru_dugumler(dugumler, kenarlar):
    """
    Articulation point (kesme noktası) tespiti — TÜM ilişki+illiyet kenarları yönsüz.
    İki ayrı kümeyi bağlayan tek düğüm = MUVAZAA / tüzel kişilik perdesi sinyali.
    (Örn. iki şirketi bağlayan tek müdür düğümü.)
    """
    adj = _komsuluk(kenarlar, yonsuz=True)
    dugum_listesi = list(dugumler.keys())
    if len(dugum_listesi) < 3:
        return []

    def bilesem_sayisi(haric):
        gorulen = set()
        sayac = 0
        for basla in dugum_listesi:
            if basla == haric or basla in gorulen:
                continue
            sayac += 1
            yigin = [basla]
            while yigin:
                u = yigin.pop()
                if u in gorulen:
                    continue
                gorulen.add(u)
                for v in adj.get(u, ()):
                    if v != haric and v not in gorulen:
                        yigin.append(v)
        return sayac

    taban = bilesem_sayisi(haric=None)
    koprular = []
    for d in dugum_listesi:
        if bilesem_sayisi(haric=d) > taban:
            koprular.append(d)
    return koprular


def cevrim_var_mi(kenarlar):
    """İlliyet kenarlarında dairesel bağ (yönlü çevrim) = mantık hatası."""
    adj = _komsuluk(kenarlar, kategori=ILLIYET_KATEGORI)
    BEYAZ, GRI, SIYAH = 0, 1, 2
    renk = defaultdict(int)
    cevrimler = []

    def dfs(u, yol):
        renk[u] = GRI
        for v in adj.get(u, ()):
            if renk[v] == GRI:
                cevrimler.append(yol + [v])
            elif renk[v] == BEYAZ:
                dfs(v, yol + [v])
        renk[u] = SIYAH

    for d in list(adj.keys()):
        if renk[d] == BEYAZ:
            dfs(d, [d])
    return cevrimler


def yuk_tasiyan_kenarlar(dugumler, kenarlar):
    """
    Çıkarıldığında illiyet zincirinin uçtan uca bağlantısını koparan kenar.
    = ispatlanmazsa dava düşen kritik bağ (oa-strateji hedefi).
    Basit yaklaşım: illiyet alt-grafında köprü-kenar (bridge) tespiti.
    """
    illiyet_kenar = [(k["kaynak"], k["hedef"], i)
                     for i, k in enumerate(kenarlar)
                     if k.get("kategori") == ILLIYET_KATEGORI]
    if not illiyet_kenar:
        return []
    adj = defaultdict(set)
    for a, b, _ in illiyet_kenar:
        adj[a].add(b)
        adj[b].add(a)

    def baglanti_sayisi(haric_idx):
        kenar_set = [(a, b) for a, b, i in illiyet_kenar if i != haric_idx]
        lokal = defaultdict(set)
        dugum = set()
        for a, b in kenar_set:
            lokal[a].add(b); lokal[b].add(a); dugum.add(a); dugum.add(b)
        gorulen = set(); sayac = 0
        for s in dugum:
            if s in gorulen:
                continue
            sayac += 1; yig = [s]
            while yig:
                u = yig.pop()
                if u in gorulen: continue
                gorulen.add(u)
                for v in lokal.get(u, ()):
                    if v not in gorulen: yig.append(v)
        return sayac

    taban = baglanti_sayisi(haric_idx=-1)
    out = []
    for a, b, i in illiyet_kenar:
        if baglanti_sayisi(haric_idx=i) > taban:
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


def json_sonuc(dugumler, kenarlar, hatalar, yetim, dk, kopru, cevrimler, kesme, yuk):
    """Denetim sonucunu makine-okur sözlük olarak topla (çapraz-denetçi bunu okur)."""
    return {
        "arac": "grafik_denetim",
        "ozet": {"dugum": len(dugumler), "kenar": len(kenarlar)},
        "sema_hatalari": hatalar,
        "yetim_dugumler": [{"id": kid, "ad": _ad(dugumler, kid)} for kid in yetim],
        "desteksiz_kenarlar": [_kenar_ref(dugumler, i, k) for i, k in dk],
        "kopru_dugumler": [{"id": kid, "ad": _ad(dugumler, kid)} for kid in kopru],
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


def rapor(yol, json_yol=None):
    dugumler, kenarlar = yukle(yol)
    cizgi = "=" * 60
    print(cizgi)
    print("OA-ILLIYET — DETERMİNİSTİK GRAF DENETİM RAPORU")
    print(cizgi)
    print(f"Düğüm: {len(dugumler)}  |  Kenar: {len(kenarlar)}")
    print()

    hatalar = dogrula_sema(dugumler, kenarlar)
    print("### 1. ŞEMA DENETİMİ")
    if hatalar:
        for h in hatalar:
            print(f"  ✗ {h}")
        print("\n  ⚠ Şema hataları var — diğer denetimler eksik çalışabilir.")
    else:
        print("  ✓ Şema bütün.")
    print()

    print("### 2. YETİM DÜĞÜM (hiçbir bağı yok)")
    yetim = yetim_dugumler(dugumler, kenarlar)
    if yetim:
        for kid in yetim:
            print(f"  ⚠ {_ad(dugumler, kid)} ({kid}) — dosyada neden var? bağ kur veya çıkar")
    else:
        print("  ✓ Yetim düğüm yok.")
    print()

    print("### 3. DESTEKSİZ KENAR (iddia + delilsiz → ispat boşluğu)")
    dk = desteksiz_kenarlar(kenarlar)
    if dk:
        for i, k in dk:
            print(f"  ⚠ {_ad(dugumler, k['kaynak'])} —[{k['tur']}]→ "
                  f"{_ad(dugumler, k['hedef'])}  → oa-vakia ile delil tespiti")
    else:
        print("  ✓ Her kenar delil-teyitli veya karine.")
    print()

    print("### 4. KÖPRÜ DÜĞÜM (muvazaa / tüzel kişilik perdesi sinyali)")
    kopru = kopru_dugumler(dugumler, kenarlar)
    if kopru:
        for kid in kopru:
            print(f"  ⚑ {_ad(dugumler, kid)} ({kid}) iki kümeyi bağlıyor "
                  f"→ muvazaa / perdeyi kaldırma incele; karşı taraf buraya vurabilir")
    else:
        print("  ✓ Tek-nokta köprü yok.")
    print()

    print("### 5. ÇEVRİM (dairesel illiyet = mantık hatası)")
    cevrimler = cevrim_var_mi(kenarlar)
    if cevrimler:
        for c in cevrimler:
            print(f"  ✗ {' → '.join(_ad(dugumler, x) for x in c)}")
    else:
        print("  ✓ İlliyet zinciri dairesel değil.")
    print()

    print("### 6. KESME ADAYLARI (→ oa-antitez)")
    kesme = kesme_adaylari(kenarlar)
    if kesme:
        for i, k in kesme:
            print(f"  ⚑ {_ad(dugumler, k['kaynak'])} —[{k['tur']}]→ "
                  f"{_ad(dugumler, k['hedef'])}  KESME: {k['kesme_flag']} "
                  f"→ oa-antitez ile çürüt veya kabul et")
    else:
        print("  — Kesme adayı işaretlenmemiş. (mücbir sebep / mağdur / üçüncü kişi "
              "kusuru ihtimalini elle gözden geçir.)")
    print()

    print("### 7. YÜK TAŞIYAN KENAR (→ oa-strateji; ispatlanmazsa zincir kopar)")
    yuk = yuk_tasiyan_kenarlar(dugumler, kenarlar)
    if yuk:
        for i, k in yuk:
            print(f"  ★ {_ad(dugumler, k['kaynak'])} —[{k['tur']}]→ "
                  f"{_ad(dugumler, k['hedef'])}  → stratejik öncelik: bu bağı sağlamlaştır")
    else:
        print("  — Belirgin tek yük taşıyan kenar yok (zincir paralel/dağıtık).")
    print()

    print(cizgi)
    print("NOT: Bu rapor YAPISAL boşlukları gösterir. İlliyetin hukuki niteliği "
          "(uygun illiyet / objektif isnadiyet / kesilme) ve nihai karar avukata aittir.")
    print(cizgi)

    if json_yol:
        sonuc = json_sonuc(dugumler, kenarlar, hatalar, yetim, dk, kopru,
                           cevrimler, kesme, yuk)
        sonuc["girdi"] = yol
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="OA-illiyet deterministik graf denetimi")
    p.add_argument("graf", nargs="?", help="graf.json yolu")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="denetim sonucunu makine-okur JSON olarak bu yola yaz (opsiyonel)")
    a = p.parse_args()
    if not a.graf:
        print("Kullanım: python grafik_denetim.py graf.json [--json out.json]")
        sys.exit(1)
    rapor(a.graf, json_yol=a.json_yol)
