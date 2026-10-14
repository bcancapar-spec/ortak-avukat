# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — eklenti metinlerinde HAM kontrol / görünmez biçim karakteri YOK.

NEDEN VAR: SKILL.md, references ve betikler modelin bağlamına girer. Görünmez karakter
(TAG, RLO/LRO, sıfır genişlik, dikey sekme…) OA'nın KENDİ metninde gizli talimat yolu ya da
bozuk belge demektir — B-22 belge güvenlik kapısının aynası (karşı tarafın evrakını tarıyoruz;
kendi metnimiz de temiz olmalı). Saha dersi (2026-10-05): bir değişiklik günlüğüne kaçış
hatasıyla İKİ KEZ ham dikey sekme yazıldı ve elle yapılan taramalar ikincisini kaçırdı.
Kural: görünmez karakter gerekiyorsa kaynakta KAÇIŞLA yazılır (ör. "\\u200b", "\\u00ad").

İSTİSNA YOK (2026-10-15 denetimi B-3): v0.5.18'de `oa-ingest/scripts/udf_md.py` `_CF_RE`
ifadesi tek bilinçli istisnaydı — Unicode biçim karakterlerini ham olarak listeliyordu.
Kural "kaçışla yazılır" dediği için ifade `\\uXXXX` kaçışına çevrildi (desen özdeş;
`test_udf_md.py` `unicodedata`'ya karşı kilitli) ve istisna KALDIRILDI: kapı artık
istisnasızdır. Kapsam: plugins/**, docs/**, kök *.md. Testler ve tools/ için kardeş kapı
`tests/test_kaynak_hijyeni.py`'dedir (ruff yapılandırması + CI lint işi ile birlikte).
"""
import pathlib
import unicodedata

REPO = pathlib.Path(__file__).resolve().parents[1]
UZANTILAR = (".py", ".md", ".json", ".txt", ".yml", ".yaml", ".toml")


def _yasak(ch):
    o = ord(ch)
    return (o < 32 and ch not in "\t\n\r") or o == 0x7F or unicodedata.category(ch) == "Cf"


def _taranacaklar():
    yollar = [p for p in (REPO / "plugins").rglob("*")] + [p for p in (REPO / "docs").rglob("*")]
    yollar += sorted(REPO.glob("*.md"))
    return [p for p in yollar if p.is_file() and p.suffix in UZANTILAR and "__pycache__" not in p.parts]


def test_eklenti_metinlerinde_ham_gorunmez_karakter_yok():
    bulunan = []
    for p in _taranacaklar():
        for i, satir in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for ch in satir:
                if _yasak(ch):
                    bulunan.append("%s:%d U+%04X" % (p.relative_to(REPO), i, ord(ch)))
                    break
    assert bulunan == [], bulunan


def test_cf_regexi_artik_kacisla_yazili_istisna_gerekmiyor():
    """2026-10-15 B-3: eski istisnanın dayanağı ortadan kalktı — `_CF_RE` satırları
    ham biçim karakteri TAŞIMAZ; kapı bu dosyayı da istisnasız tarar."""
    udf_md = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "udf_md.py"
    satirlar = udf_md.read_text(encoding="utf-8").splitlines()
    bas = next(i for i, s in enumerate(satirlar) if s.startswith("_CF_RE = re.compile("))
    govde = satirlar[bas:bas + 6]
    assert any("\\\\u200b" in s or "\\u200b" in s for s in govde), "regex kaçışlı yazılmalı"
    assert not any(_yasak(ch) for s in govde for ch in s)
