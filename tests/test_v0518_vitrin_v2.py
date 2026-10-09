# -*- coding: utf-8 -*-
"""v0.5.18 — VİTRİN V2 (avukat talimatı 2026-10-07: "vitrini de güncel olarak yayımla — GitHub
Ortak Avukat projesine").

NEDEN VAR: vitrindeki her sayı ve her iddia ölçümden gelir, beyan değil. 2026-10-07/08 son turunda
kural kataloğu 48'den 50'ye çıktı ama dört belge "27 → 48" diyordu; CLAUDE.md "176 dosya" ve
"2340 test" gibi bayat sayılar ve `PYTHONDONTWRITEBYTECODE` için yanlış bir kural taşıyordu
("ayarlı olmamalı" — oysa Claude uygulaması onu kendisi verir; kazanç compileall ile alınır).
Bu dosya kilitler:
  - belgelerdeki kural kataloğu sayısı `sure_kurallari.json`'daki gerçek sayıyla AYNI,
  - README sürüm notları son turu (zincir, iki kusur, ifşa, DOCX, kurulum motoru, m.11) taşır,
  - CLAUDE.md bayat sayı taşımaz ve PYTHONDONTWRITEBYTECODE gerçeğini doğru söyler,
  - SOZLUK son turun terimlerini tanımlar.
Yalnız depo metnini okur; ağsız ve deterministiktir.
"""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
SURE = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure" / "scripts" / "sure_kurallari.json"
BELGELER = (REPO / "README.md", REPO / "plugins" / "ortak-avukat" / "README.md",
            REPO / "docs" / "YARGI-PRO-UYARLAMA-PLANI.md", REPO / "CHANGELOG.md")


def _oku(p):
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_kural_katalogu_sayisi_olcumle_ayni():
    gercek = len(json.loads(_oku(SURE))["kurallar"])
    for yol in BELGELER:
        sayilar = [int(s) for s in re.findall(r"27\s*→\s*(\d+)", _oku(yol))]
        assert sayilar, "%s: kural kataloğu sayısı belgede yok" % yol.name
        assert all(s == gercek for s in sayilar), "%s: belgede %s, katalogda %d" % (yol.name, sayilar, gercek)


def test_surum_notlari_son_turu_tasir():
    metin = _oku(REPO / "README.md")
    bas = metin.index("### v0.5.18")
    notlar = metin[bas:metin.index("### Güncelleyenin yapacakları", bas)]
    for parca in ("Zincirleme tepki", "iki hukuki kusur", "gizli talimatı dilekçede ifşa", "DOCX",
                  "kurulum motoru", "m.11", "CI'nın yakaladığı"):
        assert parca in notlar, "v0.5.18 notlarında yok: %r" % parca


def test_claude_md_bayat_sayi_tasimaz_ve_bytecode_gercegini_soyler():
    metin = _oku(REPO / "CLAUDE.md")
    assert "176 dosya" not in metin and "2340 test" not in metin, "bayat sayı (ölçüm aracına işaret edilmeli)"
    assert "ayarlı olmamalı" not in metin, "PYTHONDONTWRITEBYTECODE'u uygulama kendisi verir — kural yanlıştı"
    blok = metin[metin.index("PYTHONDONTWRITEBYTECODE` gerçeği"):]
    assert "compileall" in blok[:600] and "ZORUNLUDUR" in blok[:600]


def test_guncelleyen_notu_onbellek_surumlerini_sabitten_tasir():
    """Güncelleyen avukat ilk okumanın neden uzadığını bilmeli — sürüm sayıları elle değil SABİTTEN:
    `belge_guvenlik.SURUM` ve `oa_ingest.DOCX_CIKARIM_SURUMU` değişirse not da değişmek zorunda."""
    scripts = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts"
    bg = re.search(r'^SURUM = "([^"]+)"', _oku(scripts / "belge_guvenlik.py"), re.M).group(1)
    docx = re.search(r'^DOCX_CIKARIM_SURUMU = "([^"]+)"', _oku(scripts / "oa_ingest.py"), re.M).group(1)
    metin = _oku(REPO / "README.md")
    bas = metin.index("### Güncelleyenin yapacakları")
    blok = metin[bas:metin.index("### Dürüst sınırlar", bas)]
    assert "Belge güvenlik kaydı (%s)" % bg in blok and "Word çıkarımı (sürüm %s)" % docx in blok, blok[-900:]
    assert "yeniden OCR'lanmaz" in blok


def test_sozluk_son_turun_terimlerini_tanimlar():
    metin = _oku(REPO / "SOZLUK.md")
    for terim in ("**Zincirleme tepki / bayat zincir:**", "**İfşa bölümü (gizli talimat ifşası):**",
                  "**Kurulum motoru:**", "**Künye — fikir ve dizayn babası, kâtip:**"):
        assert terim in metin, "SOZLUK'ta yok: %s" % terim
