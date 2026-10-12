# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — dış araç SÜRÜM SABİTİ depo genelinde tek kaynaktan (kullanıcı kararı
2026-10-05: "Layer 0'a dahil + sürüm sabitle").

NEDEN VAR: `npx -y <paket>@latest` her çağrıda denetlenmemiş yeni bir upstream yayınını
(ağ + oturumla) okuma/teslim zincirine sokuyordu. oa-dilekce kendi kapsamını
`test_v0518_dilekce_udf_surum.py` ile kilitler; bu dosya ONUN DIŞINI kilitler:
  (1) oa-pipeline/udf_metin.py sürümü udf_yaz.py `UDF_CLI_SURUM` satırından okur;
  (2) sabit okunamazsa FAIL-CLOSED: dış süreç HİÇ çağrılmaz, `@latest`'e düşülmez;
  (3) çağrı sabitlenmiş paketi kullanır (sahte npx — gerçek npx/ağ YOK);
  (4) eklenti, README, docs ve testlerde hiçbir `npx … <paket>@latest` kalmaz;
  (5) README'deki komut örnekleri sabitle aynı sürümü gösterir.
Tarihsel kayıtlar (CHANGELOG.md, STATUS.md, _gorus/) MUAFTIR: geçmişi anlatırlar.
"""
import importlib.util
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
UDF_YAZ = SKILLS / "oa-dilekce" / "scripts" / "udf_yaz.py"
UDF_METIN = SKILLS / "oa-pipeline" / "scripts" / "udf_metin.py"
SABITSIZ = re.compile(r"[A-Za-z0-9][\w.-]*@" + "latest" + r"\b")   # parçalı: bu dosya kendine takılmasın


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def uy():
    return _yukle("v0518_tk_udf_yaz", UDF_YAZ)


@pytest.fixture
def um():
    return _yukle("v0518_tk_udf_metin", UDF_METIN)


def test_udf_metin_surumu_udf_yaz_sabitinden_okur(uy, um):
    assert um.udf_cli_paketi() == uy.UDF_CLI_PAKET == "udf-cli@" + uy.UDF_CLI_SURUM


def test_sabit_okunamazsa_dis_surec_hic_cagrilmaz(um, tmp_path, monkeypatch):
    sahte = tmp_path / "udf_yaz.py"
    sahte.write_text('UDF_CLI_SURUM = "latest"\n', encoding="utf-8")   # biçim dışı → yok sayılır
    assert um.udf_cli_paketi(str(sahte)) is None
    assert um.udf_cli_paketi(str(tmp_path / "yok.py")) is None
    monkeypatch.setattr(um, "_UDF_YAZ", str(tmp_path / "yok.py"))
    cagrilar = []
    monkeypatch.setattr(um.shutil, "which", lambda _a: "npx-sahte")
    monkeypatch.setattr(um.subprocess, "run", lambda *a, **k: cagrilar.append(a))
    metin, hata = um.udf2md_ile_metin_cikar(str(tmp_path / "x.udf"))
    assert metin is None and "UDF_CLI_SURUM" in hata
    assert cagrilar == []


def test_cagri_sabitlenmis_paketi_kullanir(uy, um, tmp_path, monkeypatch):
    cagrilar = []

    class _P:
        returncode, stdout, stderr = 0, "sentetik metin", ""

    def _run(args, **_k):
        cagrilar.append(list(args))
        return _P()

    monkeypatch.setattr(um.shutil, "which", lambda _a: "npx-sahte")
    monkeypatch.setattr(um.subprocess, "run", _run)
    metin, hata = um.udf2md_ile_metin_cikar(str(tmp_path / "x.udf"))
    assert (metin, hata) == ("sentetik metin", None)
    assert cagrilar == [["npx-sahte", "-y", uy.UDF_CLI_PAKET, "udf2md", str(tmp_path / "x.udf")]]


def _taranacaklar():
    """(yol, katı_mı): eklenti + README + docs KATI (her geçiş — model bu metinleri komut
    diye okur); testlerde yalnız ÇALIŞTIRILABİLİR biçim (`-y`/`npx` argümanıyla aynı satır)
    — "…@latest kalmadı" diyen olumsuz doğrulamalar meşrudur."""
    yollar = [(p, True) for p in (REPO / "plugins").rglob("*")
              if p.is_file() and p.suffix in (".py", ".md", ".json", ".txt") and "__pycache__" not in p.parts]
    yollar += [(REPO / "README.md", True)] + [(p, True) for p in sorted((REPO / "docs").glob("**/*.md"))]
    yollar += [(p, False) for p in sorted((REPO / "tests").glob("*.py"))]
    return yollar


def test_depoda_sabitsiz_npx_surumu_kalmadi():
    bulunan = []
    for p, kati in _taranacaklar():
        for i, satir in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if SABITSIZ.search(satir) and (kati or '"-y"' in satir or "'-y'" in satir or "npx" in satir):
                bulunan.append("%s:%d" % (p.relative_to(REPO), i))
    assert bulunan == [], bulunan


def test_readme_komut_ornekleri_sabitle_ayni(uy):
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    surumler = re.findall(r"udf-cli@([0-9][0-9A-Za-z.\-]*[0-9A-Za-z])", readme)
    assert surumler and set(surumler) == {uy.UDF_CLI_SURUM}, surumler
