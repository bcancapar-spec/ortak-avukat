# -*- coding: utf-8 -*-
"""2026-10-15 denetimi — EKLENTİ VİTRİNİ (B-7 devamı): katmanlı düzen + ölçülü parça tablosu ve kök katalog.

NEDEN VAR: `plugins/ortak-avukat/README.md` ikinci vitrindir — kök README script düzeyi
ayrıntı için oraya gönderir. Kök README katmanlı düzene geçerken (`cf425d9`) eklenti
README'si eski düzende kaldı; "Parça dizini" tablosundaki script sayıları elle yazılmıştı
ve üçü bayattı (ölçüm 2026-10-15: oa-pipeline 10 → diskte 11, oa-ingest 5 → 6, çekirdek
"—" → 1, v0.5.18'in kurulum motoru). Aynı üç bayatlık kök README'nin katlanır kataloğunda
("Skill seti" bölümü, parça başına bir h4 başlığı) da duruyordu — aynı ölçüm:
`oa-pipeline` başlığı "· 10 script" → diskte 11, `oa-ingest` "· 5 script" → 6,
`ortak-avukat` başlığında sayı yoktu → "· 1 script". Eklenti tablosu düzelince iki vitrin
birbirini yalanladı (tablo 11, kök başlık 10); bu yüzden iki yüzey de aynı disk sayımına
kilitlidir. B-35 dersi: vitrindeki her sayı ÖLÇÜMDÜR, beyan değil. Bu dosya kilitler:
  - tablodaki her satırın script sayısı `skills/<parça>/scripts/*.py` sayımıyla birebir
    (sıfır "—" yazılır; motor tanımı `test_b37` ile aynıdır: scripts/ altındaki her .py),
  - kök katalogdaki her h4 başlığı: " · N script" son eki varsa N aynı sayımla birebir;
    son ek yoksa parça scriptsiz demektir, disk sayımı 0 olmalı,
  - yirmi parçanın her biri tabloda ve kök katalogda tam bir kez, bağlantı klasörü parça
    adıyla aynı,
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

KOK_README = REPO / "README.md"
KOK_KATALOG_BASLIGI = "## Skill seti"
# #### [`oa-x`](plugins/ortak-avukat/skills/oa-x/) — rol · 3 script   (scriptsiz parçada son ek yok)
_KOK_BASLIK_RE = re.compile(
    r"^#### \[`([a-z][a-z-]*)`\]\(plugins/ortak-avukat/skills/([a-z][a-z-]*)/\) — (.+?)(?: · (\d+) script)?\s*$")


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


def kok_katalog_sayilari(metin):
    """Kök README '## Skill seti' bölümünün h4 başlıklarından {parça: script sayısı ya da None}.

    " · N script" son eki varsa N; yoksa None (scriptsiz parça iddiası — `bayat_sayilar`
    bunu 0 sayar). Bölüm bir sonraki '## ' başlığında biter; tablo satırı ve bağlantısız
    başlık sayılmaz.
    """
    bas = metin.index(KOK_KATALOG_BASLIGI)
    son = metin.find("\n## ", bas)
    govde = metin[bas:son if son >= 0 else None]
    sayilar = {}
    for satir in govde.splitlines():
        m = _KOK_BASLIK_RE.match(satir)
        if not m:
            continue
        ad, klasor, rol, n = m.groups()
        assert ad == klasor, "bağlantı klasörü parça adıyla aynı olmalı: %s ≠ %s" % (ad, klasor)
        assert ad not in sayilar, "parça kök katalogda iki kez: %s" % ad
        # "· 3 scripts" gibi bozuk son ek sessizce "scriptsiz" sayılmasın; rolde "scriptsiz"
        # sözcüğü ya da "Layer 0" gibi rakam serbesttir — yalnız "·" ile başlayan kalıntı bakılır
        assert n is not None or not re.search(r"·[^·]*(?:\d|script)", rol, re.I), (
            "biçim dışı script son eki: %s" % satir)
        sayilar[ad] = int(n) if n is not None else None
    return sayilar


def diskteki_sayilar(skills=SKILLS):
    """Parça başına `scripts/*.py` sayısı — `test_b37`'nin motor tanımıyla aynı."""
    return {d.name: len(list((d / "scripts").glob("*.py")))
            for d in sorted(skills.iterdir()) if d.is_dir() and (d / "SKILL.md").is_file()}


def bayat_sayilar(yazilan, disk):
    """Vitrinde yazan ≠ disk olan parçalar: {parça: (yazılan, disk)}.

    None = son ek yok: parça scriptsiz iddiasındadır, disk sayımı 0 olmalı.
    """
    return {ad: (yazilan[ad], disk[ad]) for ad in sorted(set(disk) & set(yazilan))
            if (0 if yazilan[ad] is None else yazilan[ad]) != disk[ad]}


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
    # kök README kataloğu: h4 başlığı; son ek varsa sayı, yoksa None (scriptsiz iddiası)
    kok = (
        "# Vitrin\n\n## Skill seti — iki parça\n\n| Parça | Görevi |\n|---|---|\n"
        "| [`oa-bes`](plugins/ortak-avukat/skills/oa-bes/) | tablo satırı başlık değildir |\n\n"
        "<details>\n\n### Grup\n\n"
        "#### [`oa-bir`](plugins/ortak-avukat/skills/oa-bir/) — rol `a` · 3 script\n"
        "#### [`oa-iki`](plugins/ortak-avukat/skills/oa-iki/) — scriptsiz rol\n"
        "#### `oa-uc` — bağlantısız başlık sayılmaz · 9 script\n"
        "</details>\n\n## Sonraki bölüm\n\n"
        "#### [`oa-dort`](plugins/ortak-avukat/skills/oa-dort/) — kapsam dışı · 1 script\n")
    assert kok_katalog_sayilari(kok) == {"oa-bir": 3, "oa-iki": None}
    with pytest.raises(AssertionError):  # yinelenen parça
        kok_katalog_sayilari(kok.replace(
            "</details>", "#### [`oa-iki`](plugins/ortak-avukat/skills/oa-iki/) — yine · 1 script\n</details>"))
    with pytest.raises(AssertionError):  # bağlantı klasörü ≠ parça adı
        kok_katalog_sayilari(kok.replace("skills/oa-bir/) —", "skills/oa-baska/) —"))
    with pytest.raises(AssertionError):  # bozuk son ek "scriptsiz" sayılmaz
        kok_katalog_sayilari(kok.replace("· 3 script", "· 3 scripts"))
    # karşılaştırma kuralı: son ek varsa birebir, yoksa disk 0 olmalı
    assert bayat_sayilar({"oa-bir": 3, "oa-iki": None}, {"oa-bir": 3, "oa-iki": 0}) == {}
    assert bayat_sayilar({"oa-bir": 2, "oa-iki": None}, {"oa-bir": 3, "oa-iki": 1}) == {
        "oa-bir": (2, 3), "oa-iki": (None, 1)}


# ── her sayı ölçümdür: tablo ↔ disk ──────────────────────────────────────────────────

def test_parca_tablosu_script_sayilari_olcumle_ayni():
    disk = diskteki_sayilar()
    assert len(disk) == 20, "aile 20 parçadır: %s" % sorted(disk)
    # İki vitrin yüzeyi aynı ölçüme bağlıdır — biri düzelip öteki bayat kalırsa vitrinler
    # birbirini yalanlar. Eklenti tablosunda "—" = 0; kök başlıkta son ek yoksa None (= 0).
    yuzeyler = (
        ("plugins/ortak-avukat/README.md", "tabloda", tablo_sayilari(_oku())),
        ("README.md", "başlıkta", kok_katalog_sayilari(_oku(KOK_README))),
    )
    bayat = []
    for dosya, yer, yazilan in yuzeyler:
        eksik = sorted(set(disk) - set(yazilan))
        fazla = sorted(set(yazilan) - set(disk))
        assert not eksik and not fazla, (
            "%s ↔ skills/ ayrıştı (her parça tam bir kez): eksik=%s fazla=%s" % (dosya, eksik, fazla))
        bayat += ["%s · %s: %s %s ↔ diskte %d" % (
                      dosya, ad, yer, "son ek yok (= 0)" if y is None else "%d script" % y, d)
                  for ad, (y, d) in bayat_sayilar(yazilan, disk).items()]
    assert not bayat, (
        "BAYAT SCRIPT SAYISI (B-35 sınıfı) — vitrinde yazan ≠ `skills/<parça>/scripts/*.py` sayımı:\n  "
        + "\n  ".join(bayat))


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
