# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — eklenti metinlerinde HAM kontrol / görünmez biçim karakteri YOK.

NEDEN VAR: SKILL.md, references ve betikler modelin bağlamına girer. Görünmez karakter
(TAG, RLO/LRO, sıfır genişlik, dikey sekme…) OA'nın KENDİ metninde gizli talimat yolu ya da
bozuk belge demektir — B-22 belge güvenlik kapısının aynası (karşı tarafın evrakını tarıyoruz;
kendi metnimiz de temiz olmalı). Saha dersi (2026-10-05): bir değişiklik günlüğüne kaçış
hatasıyla İKİ KEZ ham dikey sekme yazıldı ve elle yapılan taramalar ikincisini kaçırdı.
Kural: görünmez karakter gerekiyorsa kaynakta KAÇIŞLA yazılır (ör. "\\u200b", "\\u00ad").

Tek bilinçli istisna: `oa-ingest/scripts/udf_md.py` `_CF_RE` ifadesi — Unicode biçim
karakterlerini bilerek listeleyen sınıf (`test_udf_md.py` ile `unicodedata`'ya karşı kilitli).
Kapsam: plugins/**, docs/**, kök *.md (testler kapsam DIŞI: fikstür olarak görünmez karakter
taşıyabilirler; yine de kaçış önerilir).
"""
import pathlib
import unicodedata

REPO = pathlib.Path(__file__).resolve().parents[1]
UZANTILAR = (".py", ".md", ".json", ".txt", ".yml", ".yaml", ".toml")
UDF_MD = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "udf_md.py"


def _yasak(ch):
    o = ord(ch)
    return (o < 32 and ch not in "\t\n\r") or o == 0x7F or unicodedata.category(ch) == "Cf"


def _istisna_satirlari():
    """udf_md.py içinde `_CF_RE = re.compile(` ifadesinin kapsadığı satırlar."""
    satirlar = UDF_MD.read_text(encoding="utf-8").splitlines()
    bas = next(i for i, s in enumerate(satirlar, 1) if s.startswith("_CF_RE = re.compile("))
    son = next(i for i, s in enumerate(satirlar, 1) if i > bas and s.rstrip().endswith(")"))
    return set(range(bas, son + 1))


def _taranacaklar():
    yollar = [p for p in (REPO / "plugins").rglob("*")] + [p for p in (REPO / "docs").rglob("*")]
    yollar += sorted(REPO.glob("*.md"))
    return [p for p in yollar if p.is_file() and p.suffix in UZANTILAR and "__pycache__" not in p.parts]


def test_eklenti_metinlerinde_ham_gorunmez_karakter_yok():
    istisna = _istisna_satirlari()
    bulunan = []
    for p in _taranacaklar():
        for i, satir in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if p == UDF_MD and i in istisna:
                continue
            for ch in satir:
                if _yasak(ch):
                    bulunan.append("%s:%d U+%04X" % (p.relative_to(REPO), i, ord(ch)))
                    break
    assert bulunan == [], bulunan


def test_istisna_gercekten_bicim_karakteri_tasiyor():
    """İstisna boş bir izin olmasın: _CF_RE satırları gerçekten biçim karakteri içermeli ve
    istisna yalnız o ifadeyi kapsamalı (birkaç satır)."""
    istisna = _istisna_satirlari()
    assert 2 <= len(istisna) <= 8, istisna
    satirlar = UDF_MD.read_text(encoding="utf-8").splitlines()
    assert any(_yasak(ch) for i in istisna for ch in satirlar[i - 1])
