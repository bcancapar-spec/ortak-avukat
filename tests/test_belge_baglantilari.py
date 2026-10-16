# -*- coding: utf-8 -*-
"""2026-10-15 denetimi — BAĞLANTI KAPISI (docs/DENETIM-2026-10-15.md B-7, B-11).

NEDEN VAR: tarihî kayıtlar `docs/arsiv/`'e taşınırken yüzden fazla göreli
bağlantı yeniden yazıldı; hedef dosyası olmayan bağlantı hiçbir testte
görünmüyordu. Vitrin okuyucusu (avukat, hâkim, savcı) kırık bağlantıyı
tıkladığında sistemin "her iddiası kanıtlı" sözüne olan güvenini kaybeder.
Bu kapı yalnız DEPO-İÇİ dosya hedeflerini denetler: http(s) ve mailto
bağlantıları yoklanmaz (ağ kapısı yok, testler ağsızdır), salt-çapa (`#…`)
bağlantıları ve çitli kod blokları atlanır. Sentetik veri (anayasa m.7).
"""
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]

_FENCE_RE = re.compile(r"```.*?```", re.S)
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_DIS_ONEK = ("http://", "https://", "mailto:", "#")


def taranan_belgeler(kok=REPO):
    """Vitrin ve belge dosyaları: kök *.md, docs/**/*.md, eklenti README'si, .github/*.md."""
    yollar = sorted(kok.glob("*.md"))
    yollar += sorted((kok / "docs").rglob("*.md"))
    yollar += [kok / "plugins" / "ortak-avukat" / "README.md"]
    yollar += sorted((kok / ".github").glob("*.md"))
    return [y for y in yollar if y.is_file()]


def kirik_baglantilar(yol):
    """Dosyadaki göreli Markdown bağlantılarından hedefi var olmayanlar:
    [(satır_no, hedef), …]. Çitli kod blokları ve dış bağlantılar atlanır."""
    metin = yol.read_text(encoding="utf-8", errors="replace")
    metin = _FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), metin)
    kirik = []
    for no, satir in enumerate(metin.splitlines(), 1):
        for m in _LINK_RE.finditer(satir):
            hedef = m.group(1)
            if hedef.startswith(_DIS_ONEK) or hedef.startswith("<"):
                continue
            dosya = hedef.split("#", 1)[0]
            if not dosya:
                continue
            if not (yol.parent / dosya).exists():
                kirik.append((no, hedef))
    return kirik


def test_kapi_kirik_baglantiyi_yakalar_saglamini_ve_disi_atlar(tmp_path):
    """Kapı ölü olmasın: var olmayan hedef yakalanır; var olan dosya, http(s),
    mailto, salt çapa ve kod bloğu içindeki `[x](y)` yakalanmaz."""
    (tmp_path / "var.md").write_text("# var\n", encoding="utf-8")
    belge = tmp_path / "belge.md"
    belge.write_text(
        "[sağlam](var.md) · [çapalı](var.md#bolum) · [yok](yok.md)\n"
        "[dış](https://example.invalid/x) · [posta](mailto:a@b.c) · [çapa](#bolum)\n"
        "```text\n[kod](kod-icinde-yok.md)\n```\n",
        encoding="utf-8")
    assert kirik_baglantilar(belge) == [(1, "yok.md")]


def test_depo_belgelerinde_kirik_baglanti_yok():
    hatalar = []
    for yol in taranan_belgeler():
        for no, hedef in kirik_baglantilar(yol):
            hatalar.append("%s:%d → %s" % (yol.relative_to(REPO).as_posix(), no, hedef))
    assert hatalar == [], (
        "KIRIK BAĞLANTI (B-11) — hedef dosya yok; taşınan belgeyse bağlantıyı yeni "
        "yola çevirin:\n  " + "\n  ".join(hatalar))
