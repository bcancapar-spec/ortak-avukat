# -*- coding: utf-8 -*-
"""2026-10-15 denetimi — EKLENTİ VİTRİNİ (B-7 devamı): katmanlı düzen + ölçülü parça tablosu.

NEDEN VAR: `plugins/ortak-avukat/README.md` ikinci vitrindir — kök README script düzeyi
ayrıntı için oraya gönderir. Kök README katmanlı düzene geçerken (`cf425d9`) eklenti
README'si eski düzende kaldı; "Parça dizini" tablosundaki script sayıları elle yazılmıştı
ve üçü bayattı (ölçüm 2026-10-15: oa-pipeline 10 → diskte 11, oa-ingest 5 → 6, çekirdek
"—" → 1, v0.5.18'in kurulum motoru). B-35 dersi: vitrindeki her sayı ÖLÇÜMDÜR, beyan
değil. Bu dosya kilitler:
  - tablodaki her satırın script sayısı `skills/<parça>/scripts/*.py` sayımıyla birebir
    (sıfır "—" yazılır; motor tanımı `test_b37` ile aynıdır: scripts/ altındaki her .py),
  - yirmi parçanın her biri tabloda tam bir kez, bağlantı klasörü parça adıyla aynı,
  - katmanlı düzen: "Bir bakışta" ve özet tablo kurulumdan ve tam katalogdan ÖNCE; tam
    katalog katlanır blokta (üst kısım tek ekranda taranır),
  - v0.6.0 yetenek belgesine ve 2026-10-15 denetim notuna bağlantı (hedefin varlığını
    `test_belge_baglantilari` ayrıca kilitler).
Ağsız; yalnız depo metnini ve dizin listesini okur. Sentetik veri (anayasa m.7).
"""
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "ortak-avukat"
SKILLS = PLUGIN / "skills"
README = PLUGIN / "README.md"

TABLO_BASLIGI = "## Parça dizini"
# | [`oa-x`](skills/oa-x/) | Rol | Hatta yeri | 3 script |   ·   … | — |
_SATIR_RE = re.compile(
    r"^\| \[`([a-z][a-z-]*)`\]\(skills/([a-z][a-z-]*)/\) \|(?:[^|]*\|){2}\s*(—|(\d+) script)\s*\|\s*$")


def _oku(p=README):
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def tablo_sayilari(metin):
    """'## Parça dizini' başlığından ilk katlanır bloğa kadarki tablodan {parça: script sayısı}."""
    bas = metin.index(TABLO_BASLIGI)
    son = metin.find("<details>", bas)
    govde = metin[bas:son if son >= 0 else None]
    sayilar = {}
    for satir in govde.splitlines():
        m = _SATIR_RE.match(satir)
        if not m:
            continue
        ad, klasor, _ifade, n = m.groups()
        assert ad == klasor, "bağlantı klasörü parça adıyla aynı olmalı: %s ≠ %s" % (ad, klasor)
        assert ad not in sayilar, "parça tabloda iki kez: %s" % ad
        sayilar[ad] = int(n) if n is not None else 0
    return sayilar


def diskteki_sayilar(skills=SKILLS):
    """Parça başına `scripts/*.py` sayısı — `test_b37`'nin motor tanımıyla aynı."""
    return {d.name: len(list((d / "scripts").glob("*.py")))
            for d in sorted(skills.iterdir()) if d.is_dir() and (d / "SKILL.md").is_file()}


# ── ayrıştırıcı ölü olmasın ──────────────────────────────────────────────────────────

def test_tablo_ayristiricisi_sentetik_ornekte_calisir():
    metin = (
        "## Parça dizini\n\n| Parça | Rol | Hatta yeri | Script |\n|---|---|---|---|\n"
        "| [`oa-bir`](skills/oa-bir/) | Rol `a` | 1. ALIM | 3 script |\n"
        "| [`oa-iki`](skills/oa-iki/) | Rol | saran katman | — |\n"
        "| `oa-uc` | bağlantısız satır sayılmaz | — | 9 script |\n"
        "<details>\n| [`oa-dort`](skills/oa-dort/) | katalog içi | — | 1 script |\n</details>\n")
    assert tablo_sayilari(metin) == {"oa-bir": 3, "oa-iki": 0}
    with pytest.raises(AssertionError):
        tablo_sayilari(metin.replace("<details>", "| [`oa-bir`](skills/oa-bir/) | yine | — | 3 script |\n<details>"))
    with pytest.raises(AssertionError):
        tablo_sayilari(metin.replace("(skills/oa-bir/)", "(skills/oa-baska/)"))


# ── her sayı ölçümdür: tablo ↔ disk ──────────────────────────────────────────────────

def test_parca_tablosu_script_sayilari_olcumle_ayni():
    disk = diskteki_sayilar()
    assert len(disk) == 20, "aile 20 parçadır: %s" % sorted(disk)
    tablo = tablo_sayilari(_oku())
    eksik = sorted(set(disk) - set(tablo))
    fazla = sorted(set(tablo) - set(disk))
    assert not eksik and not fazla, "tablo ↔ skills/ ayrıştı: eksik=%s fazla=%s" % (eksik, fazla)
    bayat = {ad: (tablo[ad], disk[ad]) for ad in disk if tablo[ad] != disk[ad]}
    assert not bayat, (
        "BAYAT SCRIPT SAYISI (B-35 sınıfı) — tabloda yazan ≠ `skills/<parça>/scripts/*.py` sayımı "
        "{parça: (tablo, disk)}: %s" % bayat)


# ── katmanlı düzen: özet önce, tam katalog katlanır ──────────────────────────────────

def test_katmanli_duzen_ozet_once_tam_katalog_katlanir():
    metin = _oku()
    bir_bakista = metin.index("## Bir bakışta")
    kurulum = metin.index("## Kurulum")
    tablo = metin.index(TABLO_BASLIGI)
    katalog_bas = metin.index("### Çekirdek ve orkestra")
    son_parca = metin.index("#### `oa-usta`")
    acilis = metin.find("<details>", tablo)
    kapanis = metin.find("</details>", son_parca)
    assert bir_bakista < kurulum < tablo, "sıra: Bir bakışta → Kurulum → Parça dizini (özet tablo)"
    assert 0 <= acilis < katalog_bas < son_parca < kapanis, (
        "tam katalog, özet tablodan sonra TEK katlanır blokta olmalı (üst kısım taranabilir kalsın)")
    assert metin.count("## Parça dizini") == 1 and metin.count("### Çekirdek ve orkestra") == 1


def test_v060_yetenek_belgesine_ve_denetim_notuna_baglanti_var():
    metin = _oku()
    for hedef in ("docs/SURUM-0.6.0-YETENEKLER.md", "docs/DENETIM-2026-10-15.md"):
        assert hedef in metin, "eklenti vitrini %s belgesine bağlanmıyor" % hedef
        assert (REPO / hedef).is_file(), hedef
