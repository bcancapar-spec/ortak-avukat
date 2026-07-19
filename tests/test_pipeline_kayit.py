# -*- coding: utf-8 -*-
"""oa-pipeline / pipeline_kayit.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
CLI çağrıları subprocess ile yapılır (main() argparse + sys.exit kullanıyor);
her test kendi tmp_path kökünü kullanarak izole çalışır.

Odak: append-only jsonl olay defteri + --denetle'nin BEKLİYOR/kanıtsız adımda
TESLİM ENGELİ (exit 1) vermesi — fiziksel işletim protokolünün garantörü.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _load():
    assert SCRIPT.is_file(), f"pipeline_kayit.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("pipeline_kayit", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pk = _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


# ── --baslat sonra --denetle: hiç işlenmemiş adımlar BEKLİYOR → exit 1 ─────

def test_baslat_sonra_denetle_bekliyor_exit1(tmp_path):
    kod, _cikti = _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 1, "hiçbir adım işlenmemişken denetle TESLİM ENGELİ vermeli"
    assert "TESLİM ENGELİ" in cikti
    assert "statü YOK" in cikti or "BEKLIYOR" in cikti.upper() or "BEKLİYOR" in cikti


def test_defter_hic_acilmadan_denetle_hata(tmp_path):
    """--baslat hiç yapılmamışsa --denetle 'defter bulunamadı' ile durmalı."""
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod != 0
    assert "defter bulunamadı" in cikti


def test_kanitsiz_uygulandi_reddedilir(tmp_path):
    """UYGULANDI statüsü kanıt olmadan (veya kısa kanıtla) yazılamaz — RET."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", "kısa", "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod != 0
    assert "kanıtsız" in cikti.lower() or "RET" in cikti


def test_jsonl_append_only_iki_olay_ikisi_de_kalir(tmp_path):
    """Append-only garanti: iki ayrı --isle çağrısı defterde İKİ AYRI satır
    olarak kalmalı (eski satır silinmez/üzerine yazılmaz)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kanit_1 = "Skill çağrısı yapıldı; ictihat_ara 'istihkak muvazaa' 12.HD → 3 künye teyitli"
    kanit_2 = "oa-vakia scripti koşuldu; kronoloji + delil matrisi üretildi (12 kalem)"
    kod1, _c1 = _cli(
        ["--isle", "--adim", "3", "--parca", "oa-ictihat", "--durum", "UYGULANDI",
         "--kanit", kanit_1, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    kod2, _c2 = _cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "UYGULANDI",
         "--kanit", kanit_2, "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod1 == 0 and kod2 == 0

    olaylar_yol = tmp_path / "_oa" / "defter" / "pipeline-olaylar.jsonl"
    assert olaylar_yol.is_file()
    satirlar = [json.loads(s) for s in olaylar_yol.read_text(encoding="utf-8").splitlines() if s.strip()]
    # baslat + 2 x isle = en az 3 olay; İKİSİ de (adım 3 ve adım 4) korunmuş olmalı
    adimlar = [o.get("adim") for o in satirlar if o.get("tip") == "adim"]
    assert 3 in adimlar and 4 in adimlar, f"append-only olay defteri satır kaybetti: {satirlar}"


def test_tum_zorunlu_adimlar_uygulandi_ve_katmanlar_denetle_gecer(tmp_path):
    """Tüm adım/parça + tüm katmanlar UYGULANDI/GEREKSIZ statüsündeyse
    --denetle TEMİZ geçmeli (exit 0) — pozitif kontrast vaka."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    uzun_kanit = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
    for no, (_ad, parcalar) in pk.ADIMLAR.items():
        for parca in parcalar:
            kod, cikti = _cli(
                ["--isle", "--adim", str(no), "--parca", parca, "--durum", "UYGULANDI",
                 "--kanit", uzun_kanit + " script", "--kok", str(tmp_path)],
                cwd=tmp_path,
            )
            assert kod == 0, f"adım {no}/{parca} işlenemedi: {cikti}"
    for katman in pk.KATMANLAR:
        kod, cikti = _cli(
            ["--katman", katman, "--durum", "UYGULANDI", "--kanit", uzun_kanit + " script",
             "--kok", str(tmp_path)],
            cwd=tmp_path,
        )
        assert kod == 0, f"katman {katman} işlenemedi: {cikti}"
    kod, cikti = _cli(["--denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"tüm adım/katman işlenmişken denetle TEMİZ geçmeli:\n{cikti}"
    assert "DENETİM TEMİZ" in cikti
