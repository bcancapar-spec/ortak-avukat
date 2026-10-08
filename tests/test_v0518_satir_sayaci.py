# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — VİTRİN KÜNYESİ + KOD SATIRI SAYACI (avukat talimatı, Av. Bayram Can
ÇAPAR, 2026-10-07: "kod satırlarının sayısını da repoda başta belirt ki emek Claude ile
yaptığımız ortaya çıksın"; "fikir ve dizayn babası Av. Bayram Can ÇAPAR, kâtip Claude").

NEDEN VAR: vitrindeki her sayı ÖLÇÜMDÜR, beyan değil (B-35 dersi: elle yazılan sayı üç yerde
üç ayrı ve üçü de yanlıştı). Satır sayıları `tools/satir_sayaci.py` ile git'te izlenen
dosyalardan sayılır, AŞAĞI yuvarlanıp (10.000 altı yüze, üstü bine) "NN.000+" biçiminde yazılır; test sayısı tek
kaynaktan (`tests/README.md` OA-SUIT-SAYISI) TAM yazılır (o işaretçi zaten `test_b35` ile
gerçek toplamaya kilitli). Bu dosya şunları kilitler:
  - künye avukatın biçiminde ve "**Sürüm:**" satırının hemen altında,
  - README'deki hiçbir satır sayısı gerçeğin aşağı yuvarlanmış alt sınırından BÜYÜK değil (abartı yok),
  - bayatlık sınırlı: gerçek < ifade + max(2000, %10) (eski sayı sessizce kalamaz),
  - test sayısı OA-SUIT-SAYISI ile birebir,
  - araç deterministik, `--yaz` idempotent ve yalnız işaretçili satıra dokunur.
Ağsız; yalnız depo metnini ve `git ls-files` çıktısını okur (anayasa m.7: gerçek veri yok).
İskeleti Görev 12 yazdı (kırmızı aşamada kaldı); ana oturum yerleşimi ve test sayısını uyarladı.
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ARAC = REPO / "tools" / "satir_sayaci.py"
KOK_README = REPO / "README.md"
EKLENTI_README = REPO / "plugins" / "ortak-avukat" / "README.md"
TESTS_README = REPO / "tests" / "README.md"

KUNYE = "**Fikir ve dizayn babası:** Av. Bayram Can ÇAPAR · **Kâtip:** Claude (Anthropic — Claude Code)"
ISARETCI = "<!-- OA-SATIR-SAYACI -->"
_SATIR_RE = re.compile(r"\*\*(\d{1,3}(?:\.\d{3})*)\+\*\*")
_TEST_RE = re.compile(r"\*\*(\d{1,3}(?:\.\d{3})*)\*\* test")
_SUIT_RE = re.compile(r"<!--\s*OA-SUIT-SAYISI:\s*(\d+)\s*-->")


def _oku(p):
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def _arac():
    spec = importlib.util.spec_from_file_location("_v0518_satir_sayaci", ARAC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _isaretci_satiri(metin):
    satirlar = [s for s in metin.splitlines() if ISARETCI in s]
    assert len(satirlar) == 1, "işaretçi satırı tam BİR kez olmalı, bulunan: %d" % len(satirlar)
    return satirlar[0]


def _sayi(ifade):
    return int(ifade.replace(".", ""))


# ── künye: avukatın biçimi, "**Sürüm:**" satırının hemen altında ──────────────────────

def test_kunye_avukat_biciminde_ve_surum_satirinin_altinda():
    for yol in (KOK_README, EKLENTI_README):
        satirlar = _oku(yol).splitlines()
        surum = [i for i, s in enumerate(satirlar) if s.startswith("**Sürüm:**")]
        assert len(surum) == 1, "%s: tek '**Sürüm:**' satırı olmalı" % yol.name
        blok = satirlar[surum[0] + 1: surum[0] + 5]
        assert KUNYE in blok, "%s: künye avukatın biçiminde ve Sürüm satırının hemen altında olmalı" % yol.name
        assert any(s.rstrip().endswith(ISARETCI) for s in blok), \
            "%s: ölçüm satırı künyenin yanında ve işaretçi SATIR SONUNDA olmalı" % yol.name
        # Satır başındaki HTML yorumu Markdown'da ham HTML bloğu açar, ** kalınlığı bozulur.
        assert not any(s.lstrip().startswith("<!--") for s in blok if ISARETCI in s)


# ── sayaç: deterministik, kategoriler ve toplam ────────────────────────────────────────

def test_sayac_deterministik_ve_toplam_kategorilerin_toplami():
    mod = _arac()
    a = mod.say()
    b = mod.say()
    assert a == b, "aynı depo → aynı sayım olmalı (determinizm)"
    assert list(a["kategoriler"]) == ["eklenti_python", "test_python", "araclar", "beceri_metin", "kural_veri"]
    assert a["toplam"]["satir"] == sum(k["satir"] for k in a["kategoriler"].values())
    assert a["toplam"]["dosya"] == sum(k["dosya"] for k in a["kategoriler"].values())
    for ad, k in a["kategoriler"].items():
        assert k["dosya"] > 0 and k["satir"] > 0, ad
    assert a["test_sayisi"] == int(_SUIT_RE.search(_oku(TESTS_README)).group(1))


def test_json_ciktisi_bayt_ozdes():
    ciktilar = []
    for _ in range(2):
        cp = subprocess.run([sys.executable, str(ARAC), "--json"], capture_output=True,
                            cwd=str(REPO), timeout=120)
        assert cp.returncode == 0, cp.stderr.decode("utf-8", "replace")
        ciktilar.append(cp.stdout)
    assert ciktilar[0] == ciktilar[1]
    veri = json.loads(ciktilar[0].decode("utf-8"))
    assert veri["yontem"]["kaynak"] == "git ls-files -z"
    assert veri["yontem"]["bos_satirlar_dahil"] is True


def test_asagi_yuvarlama_ve_turkce_binlik_ayrac():
    mod = _arac()
    assert mod.alt_sinir(3501) == 3500 and mod.alt_sinir(963) == 900 and mod.alt_sinir(9999) == 9900
    assert mod.alt_sinir(10000) == 10000 and mod.alt_sinir(45937) == 45000 and mod.alt_sinir(140210) == 140000
    assert mod.ifade(140210) == "140.000+" and mod.ifade(3501) == "3.500+" and mod.ifade(963) == "900+"
    assert mod.tr_sayi(3508) == "3.508" and mod.tr_sayi(1234567) == "1.234.567" and mod.tr_sayi(12) == "12"


# ── README sayıları: abartısız (≤ aşağı yuvarlanmış gerçek), bayat değil, test sayısı tam ──

def test_readme_sayilari_gercegi_asmaz_ve_bayat_degil():
    mod = _arac()
    olcum = mod.say()
    gercekler = [k["satir"] for k in olcum["kategoriler"].values()] + [olcum["toplam"]["satir"]]
    for yol in (KOK_README, EKLENTI_README):
        satir = _isaretci_satiri(_oku(yol))
        ifadeler = [_sayi(x) for x in _SATIR_RE.findall(satir)]
        assert len(ifadeler) == len(gercekler), (
            "%s: ölçüm satırında %d satır sayısı bekleniyordu, %d var" % (yol.name, len(gercekler), len(ifadeler)))
        for ifade, gercek in zip(ifadeler, gercekler):
            assert ifade <= mod.alt_sinir(gercek), (
                "%s: ABARTI — ifade %d > gerçeğin aşağı yuvarlanmış alt sınırı %d" % (yol.name, ifade, mod.alt_sinir(gercek)))
            assert gercek < ifade + max(2000, ifade // 10), (
                "%s: BAYAT — gerçek %d, ifade %d; `python tools/satir_sayaci.py --yaz` koş" % (yol.name, gercek, ifade))
        testler = _TEST_RE.findall(satir)
        assert testler == [mod.tr_sayi(olcum["test_sayisi"])], (
            "%s: test sayısı OA-SUIT-SAYISI ile birebir olmalı; `python tools/satir_sayaci.py --yaz` koş" % yol.name)


# ── --yaz: idempotent, yalnız işaretçili satıra dokunur ───────────────────────────────

def test_yaz_idempotent_ve_yalniz_isaretcili_satira_dokunur():
    mod = _arac()
    olcum = mod.say()
    for yol in (KOK_README, EKLENTI_README):
        eski = yol.read_text(encoding="utf-8")
        bir = mod.tazele(eski, olcum)
        iki = mod.tazele(bir, olcum)
        assert bir == iki, "%s: --yaz idempotent değil" % yol.name
        e, b = eski.splitlines(True), bir.splitlines(True)
        assert len(e) == len(b)
        farkli = [i for i, (x, y) in enumerate(zip(e, b)) if x != y]
        assert all(ISARETCI in e[i] for i in farkli), "%s: işaretçisiz satır değişti: %s" % (yol.name, farkli)
        assert KUNYE in bir
