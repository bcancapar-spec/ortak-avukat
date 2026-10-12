#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-pipeline — capraz_denetim.py
ORTAK KİMLİK UZAYI çapraz-referans denetçisi (DETERMİNİSTİK).

Üç ayrı motorun (`_oa/cikti/` altındaki illiyet grafı + vakıa matrisi + kıyas)
çıktıları TEK bir kimlik uzayında tutarlı mı? Her motor kendi dosyasını denetler;
bu script motorlar ARASINDAKİ kopuk referansları yakalar:

  1. Bir delil vakıa matrisinde var ama illiyet grafında düğümü yok.
  2. Kıyasın küçük önermesindeki vakıa vakia.json'da yok.
  3. Bir olgu hiçbir evrak/belgeye bağlı değil (yetim olgu).
  4. Kıyasta anılan delil ne grafta ne vakıada tanınıyor.
  5. Graf kenarındaki dayanak_delil, karşılığı olan delil düğümüne bağlı değil.
  6. Kıyas vakıasının 'karsilar' alanı tanımsız bir norm unsuruna işaret ediyor.

Felsefe (Ortak Avukat anayasası): script HUKUKİ karar VERMEZ. Yalnızca üç dosyanın
birbirini tuttuğunu YAPISAL olarak denetler. Yorum ve nihai karar avukata aittir.

Dosyalardan biri henüz üretilmemişse çökmez; "henüz üretilmemiş" der ve o dosyaya
bağlı denetimleri atlar. Kopuk referans bulunursa exit 1.

ORTAK KİMLİK UZAYI (v0.5.18 — B-3, S5): eşleştirme ÖNCE kimlikle yapılır —
vakıa `olaylar[].id` ↔ kıyas `kucuk_onerme.vakialar[].vakia_id` (opsiyonel
alanlar; yoksa şema hatası değil). Kimlik yoksa ad eşleşmesi KELİME SINIRLI
çalışır (eski ≥4 karakter alt-dize kapsaması 'delil-1' ⊂ 'delil-12' gibi
sahte eşleşme üretiyordu); birebir olmayan ad eşleşmesi kopuk SAYILMAZ ama
«ad-eşleşmesi (belirsiz)» etiketiyle GÖRÜNÜR (`belirsiz_eslesmeler`) — karar
avukatın. Damgalı (`arac`) denetim çıktıları model GİRDİSİ sayılmaz.
pipeline_kayit bu modülü İN-PROCESS yükler (`caprazla_ayrintili`) ve DURUM.md
«Çapraz Denetim» hattına taşır (B-2).

Kullanım:
    python capraz_denetim.py                       # varsayılan _oa/cikti
    python capraz_denetim.py --cikti-dizin _oa/cikti
    python capraz_denetim.py --graf g.json --vakia v.json --kiyas k.json
    python capraz_denetim.py --json _oa/cikti/capraz-denetim.json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import json
import os
import re
import sys

VARSAYILAN_CIKTI = os.path.join("_oa", "cikti")

# Dosya adı anahtarları (numaralı konvansiyon: 01-illiyet-graf / 04-vakia / 05-kiyas)
ANAHTAR = {
    "graf": ("illiyet-graf", "graf"),
    "vakia": ("vakia", "vakıa"),
    "kiyas": ("kiyas", "kıyas"),
}

# belgesiz kalması meşru olan (ispat yükünü kaydıran) ispat türleri
BELGESIZ_MESRU = {"karine", "ikrar", "yemin"}

_TR_LOWER = str.maketrans({
    "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ", "Ü": "ü", "Ö": "ö", "Ç": "ç",
})


def _norm(s):
    """Türkçe-duyarlı normalize: küçült, boşluk sıkıştır, tırnak/nokta kırp."""
    if s is None:
        return ""
    t = str(s).translate(_TR_LOWER).lower().strip()
    t = " ".join(t.split())
    return t.strip("\"'“”‘’.,;:()[]{}")


_KELIME_RE = re.compile(r"\w+")


def _kelime_karakteri(ch):
    """regex `\\w` karşılığı: harf/rakam (Unicode, Türkçe dahil) ya da alt çizgi."""
    return ch.isalnum() or ch == "_"


def _kelime_sinirli_icerir(uzun, kisa):
    """`kisa` (norm) `uzun` (norm) içinde KELİME SINIRINDA geçiyor mu —
    `(?<!\\w)kisa(?!\\w)` ile eşdeğer. Alt-dize değil: 'delil-1' ∉ 'delil-12',
    'fatura' ∉ 'faturalar'. REGEX KULLANILMAZ: token başına dinamik desen
    derlemek `re` önbelleğini (512) taşırıyor ve 3000 olaylı dosyada sürenin
    %45'ini derlemeye harcıyordu (cProfile ile ölçüldü); `str.find` + komşu
    karakter denetimi aynı sonucu derlemesiz verir."""
    if not kisa or not uzun or len(kisa) > len(uzun):
        return False
    bas = uzun.find(kisa)
    n = len(kisa)
    while bas != -1:
        son = bas + n
        if ((bas == 0 or not _kelime_karakteri(uzun[bas - 1]))
                and (son == len(uzun) or not _kelime_karakteri(uzun[son]))):
            return True
        bas = uzun.find(kisa, bas + 1)
    return False


class _Indeks:
    """Bir norm-dize kümesi için KELİME İNDEKSİ (kelime → o kelimeyi içeren
    dizeler). NEDEN VAR: 3000 olaylı vakıa × 12.000 delil kimliğinde her
    token için kümenin tamamını regex'le taramak (36M işlem) DURUM.md yazımını
    dakikalara çıkarıyordu (ölçüldü: 300 s'de bitmedi). Kelime-sınırlı kapsama
    ancak iki dizenin kelimeleri kesişiyorsa mümkündür; aday kümesi indeksten
    küçük çıkar, regex yalnız adaylarda koşar. Sonuç kümesinden bağımsız
    deterministiktir (adaylar sıralanır)."""

    __slots__ = ("kume", "kelime_dizeler", "kumeli_dizeler")
    ALT_KUME_SINIRI = 10   # token kelime sayısı bunu aşarsa alt-küme sayımı yerine tarama

    def __init__(self, kume):
        self.kume = set(s for s in kume if s)
        self.kelime_dizeler = {}      # kelime → o kelimeyi içeren dizeler
        self.kumeli_dizeler = {}      # frozenset(kelimeler) → aynı kelime kümeli dizeler
        for s in self.kume:
            kelimeler = frozenset(_KELIME_RE.findall(s))
            self.kumeli_dizeler.setdefault(kelimeler, []).append(s)
            for k in kelimeler:
                self.kelime_dizeler.setdefault(k, set()).add(s)

    def kapsayanlar(self, token):
        """token kelime sınırında İÇİNDE geçen dizeler (token ⊂ s) — sıralı.
        Kesişim EN KÜÇÜK kelime kümesinden başlar (yaygın kelime — 'evrak' —
        6000 dize taşıyabilir; nadir kelime adayı tek başına küçültür)."""
        kelimeler = _KELIME_RE.findall(token)
        if not kelimeler:
            return []
        kumeler = []
        for k in kelimeler:
            kume = self.kelime_dizeler.get(k)
            if not kume:
                return []
            kumeler.append(kume)
        kumeler.sort(key=len)
        adaylar = set(kumeler[0])
        for kume in kumeler[1:]:
            adaylar &= kume
            if not adaylar:
                return []
        return sorted(s for s in adaylar if s != token and _kelime_sinirli_icerir(s, token))

    def kapsananlar(self, token):
        """token'ın kelime sınırında İÇERDİĞİ dizeler (s ⊂ token) — sıralı.
        s'nin kelime kümesi token'ın kelime kümesinin ALT KÜMESİ olmak
        zorundadır: alt kümeler (2^k, k ≤ ALT_KUME_SINIRI) doğrudan aranır —
        maliyet küme boyutundan bağımsız. Çok kelimeli token'da (nadir)
        birleşim taraması."""
        kelimeler = frozenset(_KELIME_RE.findall(token))
        if not kelimeler:
            return []
        adaylar = []
        if len(kelimeler) <= self.ALT_KUME_SINIRI:
            from itertools import combinations
            sirali = sorted(kelimeler)
            for n in range(1, len(sirali) + 1):
                for alt in combinations(sirali, n):
                    adaylar.extend(self.kumeli_dizeler.get(frozenset(alt), ()))
        else:
            gorulen = set()
            for k in kelimeler:
                for s in self.kelime_dizeler.get(k, ()):
                    if s not in gorulen and self.kumeli_kelimeler(s) <= kelimeler:
                        gorulen.add(s)
            adaylar = list(gorulen)
        return sorted(s for s in adaylar if s != token and _kelime_sinirli_icerir(token, s))

    def kumeli_kelimeler(self, s):
        return frozenset(_KELIME_RE.findall(s))

    def belirsiz_esler(self, token):
        """Kesin olmayan (kelime sınırlı kapsama) eşler — iki yön, sıralı, tekil."""
        return sorted(set(self.kapsayanlar(token)) | set(self.kapsananlar(token)))

    def tur_ve_esler(self, token):
        """(tur, esler) tek geçişte: "kesin" → [] · "belirsiz" → eşler · None → []."""
        if not token:
            return None, []
        if token in self.kume:
            return "kesin", []
        if len(token) < 4:
            return None, []
        esler = self.belirsiz_esler(token)
        return ("belirsiz", esler) if esler else (None, [])

    def tur(self, token):
        return self.tur_ve_esler(token)[0]


def _indeksle(kume):
    return kume if isinstance(kume, _Indeks) else _Indeks(kume)


def _eslesme_turu(token, kume):
    """token (norm) için eşleşme türü: "kesin" (birebir) | "belirsiz" (≥4
    karakter, kelime sınırlı tek yönlü kapsama) | None. Kapsama eşleşmesi
    hukuki bir aynılık hükmü DEĞİLDİR — bu yüzden ayrı adla döner ve çağıran
    onu görünür etiketle taşır (B-3). `kume` bir set ya da `_Indeks` olabilir
    (çağıran döngüde indeksi bir kez kurar)."""
    return _indeksle(kume).tur(token)


def _eslesir(token, kume):
    """token (norm) kümede eşit VEYA (len>=4) KELİME SINIRLI tek yönlü kapsama
    ile var mı (v0.5.18: alt-dize kapsaması kaldırıldı — B-3)."""
    return _eslesme_turu(token, kume) is not None


def _damgali_denetim_ciktisi_mi(yol):
    """`arac` damgalı JSON bir motorun DENETİM ÇIKTISIDIR, model girdisi değil
    (B-3): `04-vakia-denetim.json` sıralamada `04-vakia.json`dan önce gelir ve
    eski `_dosya_bul` onu girdi sanıyordu. Çözülemeyen JSON damgalı SAYILMAZ
    ki aday kalsın ve `main` onu 'okunamadı' diye GÖRÜNÜR raporlasın."""
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
    except Exception:
        return False
    return isinstance(veri, dict) and bool(veri.get("arac"))


def _dosya_bul(cikti_dizin, override, anahtarlar):
    """override verilmişse onu; yoksa dizinde anahtar içeren, damgalı denetim
    çıktısı OLMAYAN ilk .json'u döndür."""
    if override:
        return override if os.path.isfile(override) else False  # False = verildi ama yok
    if not cikti_dizin or not os.path.isdir(cikti_dizin):
        return None
    for ad in sorted(os.listdir(cikti_dizin)):
        low = ad.lower()
        if low.endswith(".json") and any(a in low for a in anahtarlar):
            yol = os.path.join(cikti_dizin, ad)
            if os.path.isfile(yol) and not _damgali_denetim_ciktisi_mi(yol):
                return yol
    return None


def _yukle(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- #
#  Kimlik uzayı çıkarımı
# --------------------------------------------------------------------------- #
def graf_kimlik(g):
    delil_ad = set()          # tip=delil düğümlerinin id + ad (norm)
    kenar_delil_ref = set()   # kenar dayanak_delil token'ları (norm)
    tum_dugum_id = set()      # ham (norm) tüm düğüm id
    delil_dugum_id = set()    # ham (norm) tip=delil düğüm id
    askida = []               # (kenar_index, token) düğümü olmayan dayanak_delil
    for d in g.get("dugumler", []):
        did_n = _norm(d.get("id"))          # bir kez normalize (ölçek: 6000 düğüm)
        tum_dugum_id.add(did_n)
        if d.get("tip") == "delil":
            delil_dugum_id.add(did_n)
            delil_ad.add(did_n)
            if d.get("ad"):
                delil_ad.add(_norm(d.get("ad")))
    for i, k in enumerate(g.get("kenarlar", [])):
        for t in (k.get("dayanak_delil") or []):
            tn = _norm(t)
            kenar_delil_ref.add(tn)
            if tn not in tum_dugum_id:
                askida.append((i, t))
    return {
        "delil_bilinen": delil_ad | kenar_delil_ref,  # grafın tanıdığı tüm delil
        "delil_dugum_id": delil_dugum_id,
        "tum_dugum_id": tum_dugum_id,
        "askida_dayanak_delil": askida,
    }


def vakia_kimlik(v):
    iddia_id = set()
    olay_id = set()       # S5 (v0.5.18): olaylar[].id — opsiyonel kimlik
    metin_havuz = set()   # olgu + iddia metinleri (norm) — kıyas vakıası buraya eşlenir
    belge_norm = set()    # dolu belge (norm)
    yetim_olgu = []       # (olgu, ispat_durumu, mesru_mu) belgesiz olaylar
    for it in v.get("iddialar", []):
        iddia_id.add(it.get("id"))
        metin_havuz.add(_norm(it.get("metin")))
    for o in v.get("olaylar", []):
        if isinstance(o.get("id"), str) and o["id"].strip():
            olay_id.add(o["id"].strip())
        olgu = o.get("olgu", "")
        metin_havuz.add(_norm(olgu))
        belge = (o.get("belge") or "").strip()
        ispat = o.get("ispat_durumu", "")
        if belge:
            belge_norm.add(_norm(belge))
        else:
            yetim_olgu.append((olgu, ispat, ispat in BELGESIZ_MESRU))
    metin_havuz.discard("")
    iddia_id.discard(None)
    return {
        "iddia_id": iddia_id,
        "olay_id": olay_id,
        "metin_havuz": metin_havuz,
        "belge_norm": belge_norm,
        "yetim_olgu": yetim_olgu,
    }


def kiyas_kimlik(k):
    buyuk = k.get("buyuk_onerme", {})
    unsur_id = set()
    for u in buyuk.get("unsurlar", []):
        unsur_id.add(u.get("id") if isinstance(u, dict) else u)
    vakialar = []
    for v in k.get("kucuk_onerme", {}).get("vakialar", []):
        vid = v.get("vakia_id")
        vakialar.append({
            "metin": v.get("metin", ""),
            "vakia_id": vid.strip() if isinstance(vid, str) and vid.strip() else None,
            "karsilar": v.get("karsilar", []) or [],
            "dayanak_delil": v.get("dayanak_delil", []) or [],
        })
    return {"unsur_id": unsur_id, "vakialar": vakialar}


# --------------------------------------------------------------------------- #
#  Çapraz denetimler  (her biri kopukluk listesine ekler)
# --------------------------------------------------------------------------- #
def caprazla_ayrintili(graf, vakia, kiyas):
    """(kopuk, belirsiz) — kopuk: referans karşılıksız (exit 1 sebebi);
    belirsiz: kimliksiz, birebir olmayan ama kelime sınırlı AD eşleşmesi —
    kopuk sayılmaz, «ad-eşleşmesi (belirsiz)» etiketiyle GÖRÜNÜR (B-3). Her
    iki liste de deterministik sıralıdır."""
    kopuk, belirsiz = [], []

    def ekle(tip, mesaj):
        kopuk.append({"tip": tip, "mesaj": mesaj})

    def belirsiz_ekle(tip, aranan, esler):
        belirsiz.append({"tip": tip,
                         "mesaj": f"ad-eşleşmesi (belirsiz): '{aranan}' ↔ "
                                  + " / ".join(f"'{e}'" for e in esler[:3])
                                  + " — birebir değil; aynı kavram mı? Karar avukatın"
                                    " (kimlik alanı — id/vakia_id — verilirse kesinleşir)"})

    def esle_veya_isaretle(tip, aranan, indeks):
        """Eşleşme türünü ayırır: kesin → sessiz; belirsiz → etiket; yok → False."""
        tur, esler = indeks.tur_ve_esler(aranan)
        if tur == "belirsiz":
            belirsiz_ekle(tip, aranan, esler)
        return tur is not None

    gk = graf_kimlik(graf) if graf is not None else None
    vk = vakia_kimlik(vakia) if vakia is not None else None
    kk = kiyas_kimlik(kiyas) if kiyas is not None else None
    # Kelime indeksleri döngü DIŞINDA bir kez kurulur (ölçek: 3000 olay ×
    # 12.000 delil kimliği — bkz. _Indeks).
    graf_delil_ix = _Indeks(gk["delil_bilinen"]) if gk else _Indeks(())
    vakia_metin_ix = _Indeks(vk["metin_havuz"]) if vk else _Indeks(())
    vakia_delil_ix = _Indeks(vk["belge_norm"]) if vk else _Indeks(())

    # 1. DELİL: vakıada var, illiyet grafında düğümü yok
    if gk and vk:
        for belge in sorted(vk["belge_norm"]):
            if not esle_veya_isaretle("DELIL", belge, graf_delil_ix):
                ekle("DELIL_GRAFTA_YOK",
                     f"Vakıa delili '{belge}' illiyet grafında düğüm/dayanak olarak yok")

    # 2. KIYAS küçük önerme vakıası vakia.json'da yok — ÖNCE KİMLİK (S5)
    if kk and vk:
        kimlikler = vk["olay_id"] | vk["iddia_id"]
        for v in kk["vakialar"]:
            vid = v.get("vakia_id")
            if vid is not None:
                if vid not in kimlikler:
                    ekle("KIYAS_VAKIA_VAKIADA_YOK",
                         f"Kıyas vakıası '{v['metin']}' kimliği '{vid}' vakia.json'da "
                         "(olaylar[].id / iddialar[].id) yok")
                continue
            if not esle_veya_isaretle("KIYAS_VAKIA", _norm(v["metin"]), vakia_metin_ix):
                ekle("KIYAS_VAKIA_VAKIADA_YOK",
                     f"Kıyas vakıası '{v['metin']}' vakia.json'da (olgu/iddia) yok")

    # 3. YETİM OLGU: hiçbir evrak/belgeye bağlı değil
    if vk:
        for olgu, ispat, mesru in vk["yetim_olgu"]:
            if mesru:
                # karine/ikrar/yemin belgesiz olabilir — kopukluk saymıyoruz, not düşüyoruz
                continue
            ekle("OLGU_EVRAKSIZ",
                 f"Olgu '{olgu}' hiçbir evrak/belgeye bağlı değil (yetim; ispat={ispat or '?'})")

    # 4. KIYAS delili ne grafta ne vakıada tanınıyor
    if kk and (gk or vk):
        for v in kk["vakialar"]:
            for t in v["dayanak_delil"]:
                tn = _norm(t)
                tur_g, esler_g = graf_delil_ix.tur_ve_esler(tn)
                tur_v, esler_v = vakia_delil_ix.tur_ve_esler(tn)
                if tur_g is None and tur_v is None:
                    ekle("KIYAS_DELIL_BILINMIYOR",
                         f"Kıyas delili '{t}' ne grafta ne vakıada tanınıyor")
                elif "kesin" not in (tur_g, tur_v):
                    belirsiz_ekle("KIYAS_DELIL", tn, sorted(set(esler_g) | set(esler_v)))

    # 5. GRAF dayanak_delil askıda (delil düğümü yok)
    if gk:
        for i, t in gk["askida_dayanak_delil"]:
            ekle("GRAF_DELIL_DUGUMU_YOK",
                 f"Graf kenar #{i}: dayanak_delil '{t}' düğümü tanımsız")

    # 6. KIYAS karsilar askıda unsur
    if kk and kk["unsur_id"]:
        for v in kk["vakialar"]:
            for u in v["karsilar"]:
                if u not in kk["unsur_id"]:
                    ekle("KIYAS_UNSUR_YOK",
                         f"Kıyas vakıası '{v['metin']}' tanımsız unsur '{u}'a bağlanmış")

    kopuk.sort(key=lambda x: (x["tip"], x["mesaj"]))
    belirsiz.sort(key=lambda x: (x["tip"], x["mesaj"]))
    return kopuk, belirsiz


def caprazla(graf, vakia, kiyas):
    """Geriye uyumlu arayüz: yalnız kopukluk listesi (bkz. caprazla_ayrintili)."""
    return caprazla_ayrintili(graf, vakia, kiyas)[0]


# --------------------------------------------------------------------------- #
def main():
    p = argparse.ArgumentParser(description="OA ortak kimlik uzayı çapraz-referans denetçisi")
    p.add_argument("--cikti-dizin", default=VARSAYILAN_CIKTI,
                   help=f"çıktı dizini (varsayılan: {VARSAYILAN_CIKTI})")
    p.add_argument("--graf", help="illiyet graf.json (dizin taramasını ezer)")
    p.add_argument("--vakia", help="vakia.json (dizin taramasını ezer)")
    p.add_argument("--kiyas", help="kiyas.json (dizin taramasını ezer)")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="çapraz-denetim sonucunu makine-okur JSON olarak bu yola yaz")
    a = p.parse_args()

    cizgi = "=" * 60
    print(cizgi)
    print("OA-PIPELINE — ORTAK KİMLİK UZAYI ÇAPRAZ DENETİMİ")
    print(cizgi)

    dosyalar = {}
    durum = {}   # ad -> "yuklendi" | "yok" | "okunamadi"
    for ad, ov in (("graf", a.graf), ("vakia", a.vakia), ("kiyas", a.kiyas)):
        yol = _dosya_bul(a.cikti_dizin, ov, ANAHTAR[ad])
        if yol is None or yol is False:
            dosyalar[ad] = None
            durum[ad] = "yok"
            neden = "belirtilen yolda yok" if yol is False else "henüz üretilmemiş"
            print(f"  [-] {ad:6s}: {neden} — bu dosyaya bağlı denetimler atlanıyor")
            continue
        try:
            dosyalar[ad] = _yukle(yol)
            durum[ad] = "yuklendi"
            print(f"  [OK] {ad:6s}: {yol}")
        except Exception as e:
            dosyalar[ad] = None
            durum[ad] = "okunamadi"
            print(f"  [!] {ad:6s}: okunamadı ({e}) — atlanıyor")
    print()

    var = [ad for ad, s in durum.items() if s == "yuklendi"]
    if len(var) < 2:
        print("  Çapraz denetim için en az iki dosya gerekli. "
              f"Mevcut: {', '.join(var) if var else 'yok'}.")
        print(cizgi)
        if a.json_yol:
            _json_yaz(a.json_yol, durum, [], [])
        sys.exit(0)

    kopuk, belirsiz = caprazla_ayrintili(dosyalar["graf"], dosyalar["vakia"], dosyalar["kiyas"])

    if kopuk:
        print(f"### KOPUK REFERANSLAR ({len(kopuk)})")
        for k in kopuk:
            print(f"  [KOPUK] ({k['tip']}) {k['mesaj']}")
    else:
        print("### KOPUK REFERANS YOK")
        print("  Üç dosya ortak kimlik uzayında tutarlı (mevcut dosyalar arası).")
    if belirsiz:
        # B-3: kopukluk DEĞİL, ama sessiz de değil — etiketli görünürlük.
        print(f"### BELİRSİZ EŞLEŞMELER ({len(belirsiz)}) — ad-eşleşmesi (belirsiz), kopukluk sayılmadı")
        for b in belirsiz:
            print(f"  [BELİRSİZ] ({b['tip']}) {b['mesaj']}")
    print()

    print(cizgi)
    print("NOT: Bu rapor YAPISAL çapraz-tutarlılığı gösterir. Referansın hukuki "
          "yeterliliği ve nihai karar avukata aittir.")
    print(cizgi)

    if a.json_yol:
        _json_yaz(a.json_yol, durum, kopuk, belirsiz)
        print(f"[JSON] Makine-okur sonuc yazildi: {a.json_yol}")

    sys.exit(1 if kopuk else 0)


def _json_yaz(yol, durum, kopuk, belirsiz=()):
    sonuc = {
        "arac": "capraz_denetim",
        "dosya_durum": durum,
        "kopuk_referanslar": kopuk,
        "kopuk_sayisi": len(kopuk),
        "belirsiz_eslesmeler": list(belirsiz),
        "belirsiz_sayisi": len(belirsiz),
        "tutarli": not kopuk,
    }
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        try:
            _sys.stderr.close()
        except Exception:
            pass
