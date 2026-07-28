# -*- coding: utf-8 -*-
"""P0-2 (v0.5.5) — doktrin/kod ayrışması regresyon kilidi.

`oa_hafiza.py teyit --arac ictihat_getir` (GETİR sınıfı) P0-2'den beri
`--damga` OLMADAN hard-fail (exit 1) verir. Bu test, ailenin herhangi bir
SKILL.md dosyasının hâlâ `--damga` İÇERMEYEN bir `ictihat_getir` teyit
örneği ÖĞRETMEDİĞİNİ doğrular — aksi hâlde model kendi talimatını izlerken
sert RET yer (görev notundaki 61→0 aktivasyon çöküşünün aynı üretim
mekanizması: kırık talimat → model ritüeli tamamen bırakır)."""
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"

# 'teyit ... --arac ictihat_getir ...' (veya tersi sırayla) çağrısını satır/
# tek-parça olarak yakalar; sonrasında AYNI çağrı içinde (bir sonraki satır
# sonuna/backtick'e kadar) '--damga' geçip geçmediğini denetler.
_CAGRI_RE = re.compile(
    r"teyit[^`\n]{0,400}?--arac[ \t]+ictihat_getir[^`\n]{0,400}", re.M
)


def _skill_md_dosyalari():
    return sorted(SKILLS.glob("*/SKILL.md")) + sorted(SKILLS.glob("*/references/*.md"))


def test_hicbir_skill_md_damgasiz_ictihat_getir_teyit_ornegi_ogretmiyor():
    ihlaller = []
    for dosya in _skill_md_dosyalari():
        metin = dosya.read_text(encoding="utf-8", errors="replace")
        for m in _CAGRI_RE.finditer(metin):
            cagri = m.group(0)
            if "--damga" not in cagri:
                ihlaller.append(f"{dosya.relative_to(REPO)}: {cagri.strip()[:160]}")
    assert not ihlaller, (
        "P0-2 REGRESYONU — aşağıdaki SKILL.md örnek(ler)i 'ictihat_getir' için "
        "--damga İÇERMEYEN bir teyit çağrısı öğretiyor (artık hard-fail verir):\n"
        + "\n".join(ihlaller)
    )


def test_en_az_bir_skill_md_damgali_ornek_ogretiyor():
    """Regresyon kilidinin kendisi köreltilmediğini doğrular (tautoloji riski
    — dosya kalıbı bulunamazsa yukarıdaki test SESSİZCE 'geçer' olurdu)."""
    bulundu = False
    for dosya in _skill_md_dosyalari():
        metin = dosya.read_text(encoding="utf-8", errors="replace")
        for m in _CAGRI_RE.finditer(metin):
            if "--damga" in m.group(0):
                bulundu = True
    assert bulundu, "hiçbir SKILL.md ictihat_getir+teyit örneği içermiyor — kalıp değişmiş olabilir"
